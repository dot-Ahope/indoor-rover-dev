/**
 * @file    safety_monitor.h
 * @brief   F4 — 스톨 감지 + latching fault. F8 에서 cmd_vel watchdog 등 추가 예정.
 *
 * 100Hz 호출 가정 (control task 내 speed_controller_update 직후).
 *
 * 스톨 판정: |target| > V_TARGET_THRESH AND |actual| < V_ACTUAL_THRESH
 *           이 상태가 200ms 지속되면 STALL.
 * 진입 동작: 양쪽 target 강제 0, PID reset, motor_driver_stop_all().
 *           fault 는 latching — safety_monitor_clear() 호출 전까지 유지.
 */
#ifndef APP_APP_SAFETY_MONITOR_H
#define APP_APP_SAFETY_MONITOR_H

#include <stdbool.h>
#include "i_motor_driver.h"

#ifdef __cplusplus
extern "C" {
#endif

void safety_monitor_init(void);
void safety_monitor_update(void);   /* 100 Hz */

bool safety_monitor_is_stalled(MotorChannel ch);
bool safety_monitor_has_fault(void);
void safety_monitor_clear(void);

/* F8: cmd_vel watchdog. cmd_vel 콜백에서 매번 호출 → 마지막 수신 시각 갱신.
 * 500ms 미수신 시 motors 강제 정지 + fault flag. */
void safety_monitor_cmdvel_received(void);
bool safety_monitor_cmdvel_timeout(void);

#ifdef __cplusplus
}
#endif

#endif
