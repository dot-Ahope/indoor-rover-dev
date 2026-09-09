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
#include <sensor_msgs/msg/imu.h>
#include <sensor_msgs/msg/magnetic_field.h>
#include <sensor_msgs/msg/battery_state.h>
#include <diagnostic_msgs/msg/diagnostic_array.h>
#include <diagnostic_msgs/msg/key_value.h>
#include <builtin_interfaces/msg/time.h>

#include "FreeRTOS.h"
#include "task.h"

#include "adc.h"
#include "rover_platform.h"
#include "speed_controller.h"
#include "safety_monitor.h"
#include "i_encoder.h"
#include "odometry.h"
#include "imu_processor.h"

/* extra_sources/ 함수들 (Makefile 빌드). */
extern void *microros_allocate(size_t size, void *state);
extern void  microros_deallocate(void *pointer, void *state);
extern void *microros_reallocate(void *pointer, size_t size, void *state);
extern void *microros_zero_allocate(size_t number_of_elements, size_t size_of_element, void *state);

extern bool   cubemx_transport_open(struct uxrCustomTransport *transport);
extern bool   cubemx_transport_close(struct uxrCustomTransport *transport);
extern size_t cubemx_transport_write(struct uxrCustomTransport *transport, const uint8_t *buf, size_t len, uint8_t *err);
extern size_t cubemx_transport_read(struct uxrCustomTransport *transport, uint8_t *buf, size_t len, int timeout, uint8_t *err);

#define HALF_WHEEL_BASE  (WHEEL_BASE_M * 0.5f)   /* = 0.2215 m (유효 게이지 0.443 — 스크럽 반영, 2026-09-07) */
#define V_MAX_MPS        MAX_LINEAR_SPEED_MPS    /* 0.100 (1:90 모터, duty 98%→115mm/s 실측) — 명령 saturation */

/* F8.5 — 배터리 전압 변환. 실측 캘리브레이션 (2026-05-28):
 *   V_battery = 11.9 V, ADC raw = 3645 → divider ratio = 11.9 / (3645 × 3.3/4095) = 4.05
 *   회로도 의도값은 4:1 (R1≈30k, R2≈10k) — 저항 tol·VDDA 편차로 4.05 측정.
 *   양산기 PCB 교체 시 동일 절차로 재캘리브레이션 필요. */
#define VIN_DIVIDER_RATIO   4.05f
#define ADC_REF_VOLTS       3.3f
#define ADC_LSB_TO_VOLTS    (ADC_REF_VOLTS * VIN_DIVIDER_RATIO / 4095.0f)

static rcl_publisher_t       s_heartbeat_pub;
static std_msgs__msg__Int32  s_heartbeat_msg;

static rcl_subscription_t          s_cmdvel_sub;
static geometry_msgs__msg__Twist   s_cmdvel_msg;

static rcl_publisher_t           s_odom_pub;
static nav_msgs__msg__Odometry   s_odom_msg;
/* 정적 프레임 ID 문자열 — micro-ROS String 구조체 init 용. */
static char s_frame_odom[]      = "odom";
static char s_frame_base_link[] = "base_link";
static char s_frame_imu_link[]  = "imu_link";

static rcl_publisher_t            s_imu_pub;
static sensor_msgs__msg__Imu      s_imu_msg;

/* F7.5 — 자기계 */
static rcl_publisher_t                  s_mag_pub;
static sensor_msgs__msg__MagneticField  s_mag_msg;

/* F8 토픽 */
static rcl_publisher_t                    s_battery_pub;
static sensor_msgs__msg__BatteryState     s_battery_msg;
static rcl_publisher_t                    s_status_pub;
static diagnostic_msgs__msg__DiagnosticArray  s_status_msg;
static diagnostic_msgs__msg__DiagnosticStatus s_status_array_storage[1];
static char s_status_name[]   = "rover_jupiter_fw";
static char s_status_hwid[]   = "F405";
static char s_status_message[64];
/* values[]: 휠별 텔레메트리 (2026-09-07). key "L"/"R", value 는 정수 필드 문자열
 *   tgt=목표 mm/s  v=측정 mm/s  d=duty %  pps=펄스/s  T=평균주기 us  cv=주기 변동계수 %  w=High폭 us  sc=스톨창 샘플
 * 목적: 구속(트랙 정지) 상태에서도 FG 가 펄스를 내는 현상의 서명(pps·cv vs duty) 수집. */
static diagnostic_msgs__msg__KeyValue s_status_kv[2];
static char s_status_kv_key[2][2] = { "L", "R" };
static char s_status_kv_val[2][72];
/* time sync 캐시 — boot 시 1회 계산 (rmw_uros_sync_session).
 * sync 실패 시 0 유지 → fill_stamp() 가 기존 boot-time stamp 그대로 출력. */
static int64_t s_time_offset_ns = 0;

/* header.stamp 채움: agent 와 동기 OK 면 epoch ns, 실패면 boot ms.
 * ts_ms 는 HAL_GetTick() 기반 boot millisec (odometry / imu / now_ms 공통). */
static inline void fill_stamp(builtin_interfaces__msg__Time *t, uint32_t ts_ms)
{
    const int64_t ns = (int64_t)ts_ms * 1000000LL + s_time_offset_ns;
    t->sec     = (int32_t)(ns / 1000000000LL);
    t->nanosec = (uint32_t)(ns % 1000000000LL);
}

static rclc_support_t   s_support;
static rcl_allocator_t  s_allocator;
static rcl_node_t       s_node;
static rclc_executor_t  s_executor;

static volatile uint32_t s_cmdvel_count = 0;   /* 디버그·watchdog 후보 */

/* 기동 데드밴드 보상 — rover_platform.h 의 MIN_WHEEL_SPEED_MPS 주석 참조.
 * 사실상 0(EPS 미만)은 0 유지, 그 외 최소 기동치 미만은 최소치로 승격(부호 보존). */
static float apply_min_wheel_speed(float v)
{
    if (fabsf(v) < WHEEL_SPEED_EPS_MPS) return 0.0f;
    if (fabsf(v) < MIN_WHEEL_SPEED_MPS) return copysignf(MIN_WHEEL_SPEED_MPS, v);
    return v;
}

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

    /* 기동 데드밴드 보상 (2026-09-02): 미세 비영 명령이 모터 무반응 구간에 갇혀
     * 상위 제어기가 영구 정체하는 문제의 펌웨어측 근본 보상. */
    v_l = apply_min_wheel_speed(v_l);
    v_r = apply_min_wheel_speed(v_r);

    speed_controller_set_target(MOTOR_LEFT,  v_l);
    speed_controller_set_target(MOTOR_RIGHT, v_r);
    s_cmdvel_count++;
    /* F8: watchdog 시각 갱신 — 500ms 동안 또 안 오면 motor stop. */
    safety_monitor_cmdvel_received();
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

    /* 5) Heartbeat publisher (F5b 호환 유지).
     *
     * QoS 결정 — 모든 텔레메트리 publisher 는 **BEST_EFFORT** 사용:
     *  - RELIABLE (init_default) 은 agent ack RTT 가 매 publish 마다 누적 →
     *    실측 spin loop 100ms+ (9.4Hz). best_effort 면 fire-and-forget 으로
     *    publish 호출이 즉시 반환 → cycle 단축 기대.
     *  - Nav2/EKF/RViz 모두 sensor 데이터는 best_effort 가 ROS 표준.
     *  - /cmd_vel subscription 만 default (reliable) 유지 — 명령 누락 방지. */
    rc = rclc_publisher_init_best_effort(
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

    /* 7) wheel_odom publisher (F6).
     * **BEST_EFFORT** — libmicroros 재빌드로 MTU 512→1024 확장 (Phase C, colcon.meta).
     *   Odometry ~720B 가 단일 frame 에 들어가 best_effort 가능 → ack RTT 제거
     *   → spin cycle 단축 → 50Hz+ 목표. */
    rc = rclc_publisher_init_best_effort(
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

    /* 7b) /imu/data_raw publisher (F7). */
    rc = rclc_publisher_init_best_effort(
        &s_imu_pub, &s_node,
        ROSIDL_GET_MSG_TYPE_SUPPORT(sensor_msgs, msg, Imu),
        "imu/data_raw");
    if (rc != RCL_RET_OK) { printf("[uROS] imu_pub rc=%ld\r\n", (long)rc); goto idle; }

    memset(&s_imu_msg, 0, sizeof(s_imu_msg));
    s_imu_msg.header.frame_id.data     = s_frame_imu_link;
    s_imu_msg.header.frame_id.size     = sizeof(s_frame_imu_link) - 1;
    s_imu_msg.header.frame_id.capacity = sizeof(s_frame_imu_link);
    /* orientation 제공 안 함 — covariance[0] = -1 표식 (REP-145). */
    s_imu_msg.orientation_covariance[0] = -1.0;

    /* 7b2) /imu/mag publisher (F7.5). */
    rc = rclc_publisher_init_best_effort(
        &s_mag_pub, &s_node,
        ROSIDL_GET_MSG_TYPE_SUPPORT(sensor_msgs, msg, MagneticField),
        "imu/mag");
    if (rc != RCL_RET_OK) { printf("[uROS] mag_pub rc=%ld\r\n", (long)rc); goto idle; }

    memset(&s_mag_msg, 0, sizeof(s_mag_msg));
    s_mag_msg.header.frame_id.data     = s_frame_imu_link;
    s_mag_msg.header.frame_id.size     = sizeof(s_frame_imu_link) - 1;
    s_mag_msg.header.frame_id.capacity = sizeof(s_frame_imu_link);
    /* magnetic_field_covariance: 0 (unknown) — Jetson 측 yaml 에서 override. */

    /* 7c) /battery publisher (F8). */
    rc = rclc_publisher_init_best_effort(
        &s_battery_pub, &s_node,
        ROSIDL_GET_MSG_TYPE_SUPPORT(sensor_msgs, msg, BatteryState),
        "battery");
    if (rc != RCL_RET_OK) { printf("[uROS] battery_pub rc=%ld\r\n", (long)rc); goto idle; }
    memset(&s_battery_msg, 0, sizeof(s_battery_msg));
    /* BatteryState: 미지 필드는 NaN 표시 (sensor_msgs convention). */
    s_battery_msg.current     = NAN;
    s_battery_msg.charge      = NAN;
    s_battery_msg.capacity    = NAN;
    s_battery_msg.design_capacity = NAN;
    s_battery_msg.percentage  = NAN;
    s_battery_msg.present     = true;

    /* 7d) /rover/status publisher (F8). */
    rc = rclc_publisher_init_best_effort(
        &s_status_pub, &s_node,
        ROSIDL_GET_MSG_TYPE_SUPPORT(diagnostic_msgs, msg, DiagnosticArray),
        "rover/status");
    if (rc != RCL_RET_OK) { printf("[uROS] status_pub rc=%ld\r\n", (long)rc); goto idle; }
    memset(&s_status_msg, 0, sizeof(s_status_msg));
    memset(&s_status_array_storage[0], 0, sizeof(s_status_array_storage[0]));
    s_status_msg.status.data     = s_status_array_storage;
    s_status_msg.status.size     = 1;
    s_status_msg.status.capacity = 1;
    s_status_array_storage[0].name.data     = s_status_name;
    s_status_array_storage[0].name.size     = sizeof(s_status_name) - 1;
    s_status_array_storage[0].name.capacity = sizeof(s_status_name);
    s_status_array_storage[0].hardware_id.data     = s_status_hwid;
    s_status_array_storage[0].hardware_id.size     = sizeof(s_status_hwid) - 1;
    s_status_array_storage[0].hardware_id.capacity = sizeof(s_status_hwid);
    s_status_array_storage[0].message.data     = s_status_message;
    s_status_array_storage[0].message.capacity = sizeof(s_status_message);
    /* values[]: 휠별 텔레메트리 KeyValue ×2 (정적 스토리지) */
    memset(s_status_kv, 0, sizeof(s_status_kv));
    for (int i = 0; i < 2; i++) {
        s_status_kv[i].key.data       = s_status_kv_key[i];
        s_status_kv[i].key.size       = 1;
        s_status_kv[i].key.capacity   = sizeof(s_status_kv_key[i]);
        s_status_kv[i].value.data     = s_status_kv_val[i];
        s_status_kv[i].value.size     = 0;
        s_status_kv[i].value.capacity = sizeof(s_status_kv_val[i]);
    }
    s_status_array_storage[0].values.data     = s_status_kv;
    s_status_array_storage[0].values.size     = 2;
    s_status_array_storage[0].values.capacity = 2;

    /* time sync — agent 와 boot offset 계산. 실패해도 진행. */
    if (rmw_uros_sync_session(1000) == RMW_RET_OK) {
        s_time_offset_ns = rmw_uros_epoch_nanos() - (int64_t)HAL_GetTick() * 1000000LL;
        printf("[uROS] time sync OK\r\n");
    } else {
        printf("[uROS] time sync FAIL — header.stamp 는 boot time 기준\r\n");
    }

    /* 8) Executor (subscriber 1개). */
    rc = rclc_executor_init(&s_executor, &s_support.context, 1, &s_allocator);
    if (rc != RCL_RET_OK) { printf("[uROS] executor_init rc=%ld\r\n", (long)rc); goto idle; }
    rc = rclc_executor_add_subscription(
        &s_executor, &s_cmdvel_sub, &s_cmdvel_msg,
        cmdvel_callback, ON_NEW_DATA);
    if (rc != RCL_RET_OK) { printf("[uROS] executor_add rc=%ld\r\n", (long)rc); goto idle; }

    printf("[uROS] ready — pub heartbeat/odom/imu/mag/battery/status, sub cmd_vel\r\n");

    /* 9) Spin loop — vTaskDelayUntil 로 20ms cycle.
     *
     *    대역 예산 (2026-09-09 실측으로 확정). 병목은 UART 가 아니라 **USB** 다:
     *      /dev/rover = ttyCH341USB0 (CH340, 1a86:7523), USB Full Speed 12Mbps,
     *      bulk 엔드포인트 wMaxPacketSize = 0x20 = 32 B → 실효 상한 약 32~40 kB/s.
     *      UART 는 2,000,000 bps (=200 kB/s) 로 설정돼 있지만 그 여유는 쓸 수 없다.
     *    실측: odom 단독으로 50.9 Hz × 720 B = 36.6 kB/s 가 최대치였고 그 위로는 못 올라갔다.
     *
     *    이전 구현은 odom/imu/mag 를 '매 cycle' 발행 했다 → 50 Hz 일 때 수요 60.5 kB/s
     *    (상한의 1.5배). imu_read() 성공 여부가 간헐적이라(imu_processor.c s_si.valid)
     *    보드 IMU 가 살아날 때마다 대역이 초과되고, 가장 큰 메시지인 odom 이 먼저 굶어
     *    수십 초간 사라졌다. 그 결과 EKF 가 유일한 속도 관측을 잃고 8.5 m 발산했다
     *    (2026-09-09 job92 → Nav2 ABORTED). → 아래처럼 전부 시간 게이트로 바꿈.
     *
     *      /wheel_odom    30 Hz  × 720 B = 21.6 kB/s   (EKF 필터 주기가 30 Hz — 그 이상은 낭비)
     *      /imu/data_raw   5 Hz  × 330 B =  1.7 kB/s   (EKF 미사용 — CLAUDE.md §4, 카메라 IMU 가 소스)
     *      /imu/mag        5 Hz  × 130 B =  0.7 kB/s   (미사용. 진단용으로만 유지)
     *      /rover/status   5 Hz  × 280 B =  1.4 kB/s
     *      /battery        1 Hz  × 100 B =  0.1 kB/s
     *      합계 약 25.4 kB/s ≈ 상한의 65% — 여유 확보.
     *    IMU/mag 를 완전히 지우지 않고 5 Hz 로 남기는 이유: '자이로 원인 규명 시 복귀
     *    검토'(CLAUDE.md §4) 를 위해 관측 가능성을 남겨둔다.
     *
     *    Heartbeat 는 cycle 가변에 안정적인 시간 기반 (HAL_GetTick) 으로 1Hz. */
    s_heartbeat_msg.data = 0;
    const uint32_t now0 = HAL_GetTick();
    uint32_t last_hb_ms      = now0;
    uint32_t last_battery_ms = now0;
    uint32_t last_status_ms  = now0;
    uint32_t last_sync_ms    = now0;   /* F8.5 — 주기 time resync */
    uint32_t last_odom_ms    = now0;   /* 2026-09-09 — 대역 예산 게이트 */
    uint32_t last_imu_ms     = now0;
    rcl_ret_t pr;
    TickType_t next_wake = xTaskGetTickCount();
    const TickType_t period_ticks = pdMS_TO_TICKS(20);
    for (;;) {
        rclc_executor_spin_some(&s_executor, RCL_MS_TO_NS(1));
        const uint32_t now_ms = HAL_GetTick();

        /* /wheel_odom 30Hz 게이트 (2026-09-09) — EKF 필터 주기와 일치. */
        if (now_ms - last_odom_ms >= 33u) {
            last_odom_ms = now_ms;
            /* Odometry 스냅샷 → msg 변환 → 발행. */
            OdomState o;
            odometry_get(&o);
            fill_stamp(&s_odom_msg.header.stamp, o.ts_ms);
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
            /* 첫 실패만 한 번 로깅 — 디버그 노이즈 방지. */
            static bool s_odom_err_logged = false;
            pr = rcl_publish(&s_odom_pub, &s_odom_msg, NULL);
            if (pr != RCL_RET_OK && !s_odom_err_logged) {
                printf("[uROS] odom publish FAIL rc=%ld (MTU? stream full?)\r\n", (long)pr);
                s_odom_err_logged = true;
            }
        }

        /* IMU/mag 5Hz 게이트 (2026-09-09) — EKF 미사용이므로 대역을 odom 에 양보. */
        if (now_ms - last_imu_ms >= 200u) {
            last_imu_ms = now_ms;
            /* IMU 발행 (F7). 2026-09-09: 매 cycle → 5Hz 게이트.
             * imu_read() 성공 여부가 간헐적이라(s_si.valid) 매 cycle 발행 시
             * 대역 수요가 튀어 odom 을 굶겼다. EKF 는 이 토픽을 쓰지 않는다. */
            ImuSi imu;
            imu_processor_get(&imu);
            if (imu.valid) {
                fill_stamp(&s_imu_msg.header.stamp, imu.ts_ms);
                s_imu_msg.linear_acceleration.x = (double)imu.ax;
                s_imu_msg.linear_acceleration.y = (double)imu.ay;
                s_imu_msg.linear_acceleration.z = (double)imu.az;
                s_imu_msg.angular_velocity.x    = (double)imu.gx;
                s_imu_msg.angular_velocity.y    = (double)imu.gy;
                s_imu_msg.angular_velocity.z    = (double)imu.gz;
                pr = rcl_publish(&s_imu_pub, &s_imu_msg, NULL); (void)pr;
            }

            /* Mag 발행 (F7.5). 2026-09-09: 매 cycle → IMU 와 같은 5Hz 게이트.
             * AK09916 측정 50Hz 이므로 5Hz 발행은 단순 다운샘플. 현재 미사용 토픽. */
            MagSi mag;
            imu_processor_get_mag(&mag);
            if (mag.valid) {
                fill_stamp(&s_mag_msg.header.stamp, mag.ts_ms);
                s_mag_msg.magnetic_field.x = (double)mag.mx;
                s_mag_msg.magnetic_field.y = (double)mag.my;
                s_mag_msg.magnetic_field.z = (double)mag.mz;
                pr = rcl_publish(&s_mag_pub, &s_mag_msg, NULL); (void)pr;
            }
        }

        /* now_ms 는 루프 상단에서 이미 취득 */
        if (now_ms - last_hb_ms >= 1000u) {
            pr = rcl_publish(&s_heartbeat_pub, &s_heartbeat_msg, NULL); (void)pr;
            s_heartbeat_msg.data++;
            last_hb_ms = now_ms;
        }

        /* F8: /battery 1Hz — ADC raw 만 우선 (voltage divider ratio 미정).
         * voltage 필드에 raw 값 그대로 (사용자가 실측 V 와 비교해 비율 산출 가능). */
        if (now_ms - last_battery_ms >= 1000u) {
            uint16_t adc_raw = 0;
            if (HAL_ADC_Start(&hadc1) == HAL_OK &&
                HAL_ADC_PollForConversion(&hadc1, 5) == HAL_OK) {
                adc_raw = (uint16_t)HAL_ADC_GetValue(&hadc1);
            }
            HAL_ADC_Stop(&hadc1);
            /* F8.5 적용 — divider ratio 4.05 (실측). 단위: V (sensor_msgs/BatteryState). */
            s_battery_msg.voltage = (float)adc_raw * ADC_LSB_TO_VOLTS;
            fill_stamp(&s_battery_msg.header.stamp, now_ms);
            pr = rcl_publish(&s_battery_pub, &s_battery_msg, NULL); (void)pr;
            last_battery_ms = now_ms;
        }

        /* F8: /rover/status 5Hz — fault flag 통합. */
        if (now_ms - last_status_ms >= 200u) {
            const bool stall_fault = safety_monitor_has_fault();
            const bool stall_latch = safety_monitor_is_latched();
            const bool cmdvel_to   = safety_monitor_cmdvel_timeout();
            uint8_t lvl;
            const char *msg;
            if (stall_latch)      { lvl = 2; msg = "STALL latched — reset required"; }
            else if (stall_fault) { lvl = 1; msg = "STALL — auto-recovering"; }
            else if (cmdvel_to)   { lvl = 1; msg = "cmd_vel timeout — motors stopped"; }
            else { lvl = 0; msg = "OK"; }
            s_status_array_storage[0].level = lvl;
            const size_t n = strlen(msg);
            const size_t cp = sizeof(s_status_message) - 1;
            const size_t cn = (n < cp) ? n : cp;
            memcpy(s_status_message, msg, cn);
            s_status_message[cn] = '\0';
            s_status_array_storage[0].message.size = cn;
            /* 휠별 텔레메트리 (정수 포맷 — nano printf 는 float 미지원) */
            for (int w = 0; w < 2; w++) {
                const MotorChannel  mc = (w == 0) ? MOTOR_LEFT : MOTOR_RIGHT;
                const EncoderChannel ec = (w == 0) ? ENC_LEFT : ENC_RIGHT;
                uint32_t pps, per_us, cv, wid;
                encoder_get_pulse_stats(ec, &pps, &per_us, &cv, &wid);
                const int tgt_mm = (int)lroundf(speed_controller_get_target(mc) * 1000.0f);
                const int v_mm   = (int)lroundf(encoder_read_velocity_mps(ec) * 1000.0f);
                const int duty_p = (int)lroundf(speed_controller_get_duty(mc) * 100.0f);
                const int len = snprintf(s_status_kv_val[w], sizeof(s_status_kv_val[w]),
                    "tgt=%d v=%d d=%d pps=%lu T=%lu cv=%lu w=%lu sc=%u",
                    tgt_mm, v_mm, duty_p, (unsigned long)pps, (unsigned long)per_us,
                    (unsigned long)cv, (unsigned long)wid, (unsigned)safety_monitor_get_stall_counter(mc));
                s_status_kv[w].value.size = (len > 0 && (size_t)len < sizeof(s_status_kv_val[w]))
                                          ? (size_t)len : sizeof(s_status_kv_val[w]) - 1;
            }
            fill_stamp(&s_status_msg.header.stamp, now_ms);
            pr = rcl_publish(&s_status_pub, &s_status_msg, NULL); (void)pr;
            last_status_ms = now_ms;
        }

        /* F8.5 — time resync 60s 주기. clock drift 보정 + agent 재연결 복구.
         * timeout 100ms 면 worst case 5 spin cycle 누락 (50Hz 운용에서 0.17%). */
        if (now_ms - last_sync_ms >= 60000u) {
            if (rmw_uros_sync_session(100) == RMW_RET_OK) {
                s_time_offset_ns = rmw_uros_epoch_nanos() - (int64_t)HAL_GetTick() * 1000000LL;
                /* 성공만 로그 — 실패는 흔할 수 있고 노이즈. */
                printf("[uROS] time resync OK\r\n");
            }
            last_sync_ms = now_ms;
        }

        vTaskDelayUntil(&next_wake, period_ticks);   /* 20ms 목표 (실측 ~34ms — XRCE framing 한계) */
    }

idle:
    for (;;) osDelay(1000);
}
