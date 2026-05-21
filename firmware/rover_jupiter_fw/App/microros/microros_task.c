/**
 * @file    microros_task.c
 * @brief   F5b/F5c/F6 micro-ROS 노드.
 *
 *   F5b — heartbeat publisher: /rover/f5b_heartbeat (std_msgs/Int32 @ 1Hz)
 *   F5c — cmd_vel subscriber:  /cmd_vel (geometry_msgs/Twist)
 *         차동구동 역기구학 → speed_controller_set_target(L/R)
 *   F6  — wheel_odom publisher: /wheel_odom (nav_msgs/Odometry @ 50Hz)
 *         OdomState (control task 가 100Hz 적분) → ROS msg 변환·발행
 *
 * 실행 루프: 20ms 마다 spin (cmd_vel 콜백 처리) + odom 발행, 매 50회 heartbeat.
 *
 * 안전: cmd_vel timeout watchdog 미구현 (F8 예정). agent/통신 끊기면 모터가
 * 마지막 명령 유지 → 사용 시 휠 받침대 또는 짧은 명령으로 검증.
 */
#include "microros_task.h"

#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

#include "cmsis_os.h"
#include "stm32f4xx_hal.h"
#include "usart.h"

#include <rcl/rcl.h>
#include <rcl/error_handling.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>
#include <rcutils/allocator.h>
#include <uxr/client/transport.h>
#include <rmw_microxrcedds_c/config.h>
#include <rmw_microros/rmw_microros.h>

#include <std_msgs/msg/int32.h>
#include <geometry_msgs/msg/twist.h>
#include <nav_msgs/msg/odometry.h>

#include "rover_platform.h"
#include "speed_controller.h"
#include "odometry.h"

/* extra_sources/ 함수들 (Makefile 빌드). */
extern void *microros_allocate(size_t size, void *state);
extern void  microros_deallocate(void *pointer, void *state);
extern void *microros_reallocate(void *pointer, size_t size, void *state);
extern void *microros_zero_allocate(size_t number_of_elements, size_t size_of_element, void *state);

extern bool   cubemx_transport_open(struct uxrCustomTransport *transport);
extern bool   cubemx_transport_close(struct uxrCustomTransport *transport);
extern size_t cubemx_transport_write(struct uxrCustomTransport *transport, const uint8_t *buf, size_t len, uint8_t *err);
extern size_t cubemx_transport_read(struct uxrCustomTransport *transport, uint8_t *buf, size_t len, int timeout, uint8_t *err);

#define HALF_WHEEL_BASE  (WHEEL_BASE_M * 0.5f)   /* = 0.095 m */
#define V_MAX_MPS        MAX_LINEAR_SPEED_MPS    /* 0.654 — 명령 saturation */

static rcl_publisher_t       s_heartbeat_pub;
static std_msgs__msg__Int32  s_heartbeat_msg;

static rcl_subscription_t          s_cmdvel_sub;
static geometry_msgs__msg__Twist   s_cmdvel_msg;

static rcl_publisher_t           s_odom_pub;
static nav_msgs__msg__Odometry   s_odom_msg;
/* 정적 프레임 ID 문자열 — micro-ROS String 구조체 init 용. */
static char s_frame_odom[]      = "odom";
static char s_frame_base_link[] = "base_link";

static rclc_support_t   s_support;
static rcl_allocator_t  s_allocator;
static rcl_node_t       s_node;
static rclc_executor_t  s_executor;

static volatile uint32_t s_cmdvel_count = 0;   /* 디버그·watchdog 후보 */

/* /cmd_vel 콜백 — Twist (linear.x, angular.z) → 좌·우 휠 속도. */
static void cmdvel_callback(const void *msg_in)
{
    const geometry_msgs__msg__Twist *m = (const geometry_msgs__msg__Twist *)msg_in;

    /* 차동구동 역기구학 (FIRMWARE_DEV_PLAN §2.2):
     *   v_left  = lin − ω·(B/2)
     *   v_right = lin + ω·(B/2)  */
    float v_lin = (float)m->linear.x;
    float w_ang = (float)m->angular.z;

    /* 입력 saturation — 휠 한쪽 명령이 운영한계 초과 못 하게. */
    if (v_lin >  V_MAX_MPS) v_lin =  V_MAX_MPS;
    if (v_lin < -V_MAX_MPS) v_lin = -V_MAX_MPS;

    float v_l = v_lin - w_ang * HALF_WHEEL_BASE;
    float v_r = v_lin + w_ang * HALF_WHEEL_BASE;

    /* 회전 명령으로 한쪽이 최대 초과 시 둘 다 비례 스케일 다운 — 회전 방향 보존. */
    float peak = fmaxf(fabsf(v_l), fabsf(v_r));
    if (peak > V_MAX_MPS) {
        const float scale = V_MAX_MPS / peak;
        v_l *= scale;
        v_r *= scale;
    }

    speed_controller_set_target(MOTOR_LEFT,  v_l);
    speed_controller_set_target(MOTOR_RIGHT, v_r);
    s_cmdvel_count++;
}

void microros_task_run(void *arg)
{
    (void)arg;

    osDelay(500);

    /* 1) Transport. */
    rmw_uros_set_custom_transport(
        true, (void *)&huart1,
        cubemx_transport_open, cubemx_transport_close,
        cubemx_transport_write, cubemx_transport_read);

    /* 2) Allocator (FreeRTOS heap 공유 — microros_heap_freertos.c). */
    rcl_allocator_t mr_alloc = rcutils_get_zero_initialized_allocator();
    mr_alloc.allocate      = microros_allocate;
    mr_alloc.deallocate    = microros_deallocate;
    mr_alloc.reallocate    = microros_reallocate;
    mr_alloc.zero_allocate = microros_zero_allocate;
    if (!rcutils_set_default_allocator(&mr_alloc)) {
        printf("[uROS] set_default_allocator FAIL\r\n");
    }

    /* 3) Agent 대기. */
    printf("[uROS] waiting for agent...\r\n");
    while (rmw_uros_ping_agent(1000, 1) != RMW_RET_OK) {
        printf("[uROS] no agent. retrying...\r\n");
        osDelay(1000);
    }
    printf("[uROS] agent OK\r\n");

    /* 4) Support / Node. */
    s_allocator = rcl_get_default_allocator();

    rcl_ret_t rc;
    rc = rclc_support_init(&s_support, 0, NULL, &s_allocator);
    if (rc != RCL_RET_OK) { printf("[uROS] support_init rc=%ld\r\n", (long)rc); goto idle; }

    rc = rclc_node_init_default(&s_node, "rover_jupiter", "", &s_support);
    if (rc != RCL_RET_OK) { printf("[uROS] node_init rc=%ld\r\n", (long)rc); goto idle; }

    /* 5) Heartbeat publisher (F5b 호환 유지). */
    rc = rclc_publisher_init_default(
        &s_heartbeat_pub, &s_node,
        ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
        "rover/f5b_heartbeat");
    if (rc != RCL_RET_OK) { printf("[uROS] heartbeat_pub rc=%ld\r\n", (long)rc); goto idle; }

    /* 6) cmd_vel subscriber. */
    rc = rclc_subscription_init_default(
        &s_cmdvel_sub, &s_node,
        ROSIDL_GET_MSG_TYPE_SUPPORT(geometry_msgs, msg, Twist),
        "cmd_vel");
    if (rc != RCL_RET_OK) { printf("[uROS] cmdvel_sub rc=%ld\r\n", (long)rc); goto idle; }

    /* 7) wheel_odom publisher (F6). */
    rc = rclc_publisher_init_default(
        &s_odom_pub, &s_node,
        ROSIDL_GET_MSG_TYPE_SUPPORT(nav_msgs, msg, Odometry),
        "wheel_odom");
    if (rc != RCL_RET_OK) { printf("[uROS] odom_pub rc=%ld\r\n", (long)rc); goto idle; }

    /* Odometry msg 정적 필드 1회 초기화. */
    memset(&s_odom_msg, 0, sizeof(s_odom_msg));
    s_odom_msg.header.frame_id.data     = s_frame_odom;
    s_odom_msg.header.frame_id.size     = sizeof(s_frame_odom) - 1;
    s_odom_msg.header.frame_id.capacity = sizeof(s_frame_odom);
    s_odom_msg.child_frame_id.data      = s_frame_base_link;
    s_odom_msg.child_frame_id.size      = sizeof(s_frame_base_link) - 1;
    s_odom_msg.child_frame_id.capacity  = sizeof(s_frame_base_link);
    /* covariance: 0 그대로 — Nav2 가 "unknown" 으로 해석. F8 에서 추정값 반영. */

    /* 8) Executor (subscriber 1개). */
    rc = rclc_executor_init(&s_executor, &s_support.context, 1, &s_allocator);
    if (rc != RCL_RET_OK) { printf("[uROS] executor_init rc=%ld\r\n", (long)rc); goto idle; }
    rc = rclc_executor_add_subscription(
        &s_executor, &s_cmdvel_sub, &s_cmdvel_msg,
        cmdvel_callback, ON_NEW_DATA);
    if (rc != RCL_RET_OK) { printf("[uROS] executor_add rc=%ld\r\n", (long)rc); goto idle; }

    printf("[uROS] ready — pub /rover/f5b_heartbeat /wheel_odom, sub /cmd_vel\r\n");

    /* 9) Spin loop — 20ms 마다: executor + odom 발행 (50Hz). 50 cycle = 1s heartbeat. */
    s_heartbeat_msg.data = 0;
    int hb_counter = 0;
    rcl_ret_t pr;
    for (;;) {
        rclc_executor_spin_some(&s_executor, RCL_MS_TO_NS(10));

        /* Odometry 스냅샷 → msg 변환 → 발행. */
        OdomState o;
        odometry_get(&o);
        s_odom_msg.header.stamp.sec     = (int32_t)(o.ts_ms / 1000u);
        s_odom_msg.header.stamp.nanosec = (uint32_t)((o.ts_ms % 1000u) * 1000000u);
        s_odom_msg.pose.pose.position.x = (double)o.x;
        s_odom_msg.pose.pose.position.y = (double)o.y;
        s_odom_msg.pose.pose.position.z = 0.0;
        /* Quaternion from yaw (Z axis only). */
        const float half = o.yaw * 0.5f;
        s_odom_msg.pose.pose.orientation.x = 0.0;
        s_odom_msg.pose.pose.orientation.y = 0.0;
        s_odom_msg.pose.pose.orientation.z = (double)sinf(half);
        s_odom_msg.pose.pose.orientation.w = (double)cosf(half);
        s_odom_msg.twist.twist.linear.x  = (double)o.v;
        s_odom_msg.twist.twist.linear.y  = 0.0;
        s_odom_msg.twist.twist.linear.z  = 0.0;
        s_odom_msg.twist.twist.angular.x = 0.0;
        s_odom_msg.twist.twist.angular.y = 0.0;
        s_odom_msg.twist.twist.angular.z = (double)o.w;
        pr = rcl_publish(&s_odom_pub, &s_odom_msg, NULL); (void)pr;

        if (++hb_counter >= 50) {   /* 50 × 20ms = 1s */
            pr = rcl_publish(&s_heartbeat_pub, &s_heartbeat_msg, NULL); (void)pr;
            s_heartbeat_msg.data++;
            hb_counter = 0;
        }
        osDelay(10);   /* executor 10ms + delay 10ms ≈ 20ms = 50Hz */
    }

idle:
    for (;;) osDelay(1000);
}
