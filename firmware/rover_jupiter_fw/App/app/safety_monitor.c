/**
 * @file    safety_monitor.c
 * @brief   F4 스톨 감지 구현.
 */
#include "safety_monitor.h"

#include <math.h>
#include <stdint.h>

#include "stm32f4xx_hal.h"
#include "i_encoder.h"
#include "speed_controller.h"

#define CTRL_HZ            100u
#define STALL_WIN_SAMPLES  20u    /* 200 ms */

#define V_TARGET_THRESH    0.05f  /* 50 mm/s — 이상 명령 시에만 stall 의심 */
#define V_ACTUAL_THRESH    0.02f  /* 20 mm/s — 미만이면 정지로 간주 */

#define CMDVEL_TIMEOUT_MS  500u   /* §7 통신 watchdog — 500ms 미수신 시 정지 */

typedef struct {
    uint16_t stall_counter;
    bool     stalled;
} mon_t;

static mon_t s_mon[MOTOR_COUNT];
static bool  s_fault;
static volatile uint32_t s_last_cmdvel_ms = 0;
static volatile bool     s_cmdvel_ever_received = false;
static bool s_cmdvel_timeout = false;

void safety_monitor_init(void)
{
    for (int i = 0; i < MOTOR_COUNT; i++) {
        s_mon[i].stall_counter = 0;
        s_mon[i].stalled       = false;
    }
    s_fault = false;
    s_last_cmdvel_ms = 0;
    s_cmdvel_ever_received = false;
    s_cmdvel_timeout = false;
}

void safety_monitor_cmdvel_received(void)
{
    s_last_cmdvel_ms = HAL_GetTick();
    s_cmdvel_ever_received = true;
    s_cmdvel_timeout = false;
}

bool safety_monitor_cmdvel_timeout(void)
{
    return s_cmdvel_timeout;
}

void safety_monitor_update(void)
{
    /* cmd_vel watchdog — fault 와 무관하게 항상 평가.
     * cmd_vel 한 번도 안 받으면 timeout 비활성 (boot 초기 상태). */
    if (s_cmdvel_ever_received) {
        const uint32_t since = HAL_GetTick() - s_last_cmdvel_ms;
        if (since > CMDVEL_TIMEOUT_MS) {
            if (!s_cmdvel_timeout) {
                /* 진입 transition — 모터 정지, 적분 reset, fault 표시 X (latch 안 함). */
                speed_controller_set_target(MOTOR_LEFT,  0.0f);
                speed_controller_set_target(MOTOR_RIGHT, 0.0f);
                speed_controller_reset();
                motor_driver_stop_all();
            }
            s_cmdvel_timeout = true;
        } else {
            s_cmdvel_timeout = false;
        }
    }

    if (s_fault) return;   /* stall latching — clear() 전까지 미평가 */

    bool any_stall = false;
    for (int i = 0; i < MOTOR_COUNT; i++) {
        const float tgt = speed_controller_get_target((MotorChannel)i);
        const float act = encoder_read_velocity_mps((EncoderChannel)i);

        if (fabsf(tgt) > V_TARGET_THRESH && fabsf(act) < V_ACTUAL_THRESH) {
            if (++s_mon[i].stall_counter >= STALL_WIN_SAMPLES) {
                s_mon[i].stalled = true;
                any_stall = true;
            }
        } else {
            s_mon[i].stall_counter = 0;
            s_mon[i].stalled = false;
        }
    }

    if (any_stall) {
        s_fault = true;
        speed_controller_set_target(MOTOR_LEFT,  0.0f);
        speed_controller_set_target(MOTOR_RIGHT, 0.0f);
        speed_controller_reset();
        motor_driver_stop_all();
    }
}

bool safety_monitor_is_stalled(MotorChannel ch)
{
    if (ch >= MOTOR_COUNT) return false;
    return s_mon[ch].stalled;
}

bool safety_monitor_has_fault(void)
{
    return s_fault;
}

void safety_monitor_clear(void)
{
    safety_monitor_init();
    speed_controller_reset();
}
