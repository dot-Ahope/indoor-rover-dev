/**
 * @file    safety_monitor.c
 * @brief   F4 스톨 감지 구현.
 */
#include "safety_monitor.h"

#include <math.h>
#include <stdint.h>

#include "i_encoder.h"
#include "speed_controller.h"

#define CTRL_HZ            100u
#define STALL_WIN_SAMPLES  20u    /* 200 ms */

#define V_TARGET_THRESH    0.05f  /* 50 mm/s — 이상 명령 시에만 stall 의심 */
#define V_ACTUAL_THRESH    0.02f  /* 20 mm/s — 미만이면 정지로 간주 */

typedef struct {
    uint16_t stall_counter;
    bool     stalled;
} mon_t;

static mon_t s_mon[MOTOR_COUNT];
static bool  s_fault;

void safety_monitor_init(void)
{
    for (int i = 0; i < MOTOR_COUNT; i++) {
        s_mon[i].stall_counter = 0;
        s_mon[i].stalled       = false;
    }
    s_fault = false;
}

void safety_monitor_update(void)
{
    if (s_fault) return;   /* latching — clear() 전까지 미평가 */

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
