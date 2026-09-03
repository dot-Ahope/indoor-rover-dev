/**
 * @file    safety_monitor.h
 * @brief   F4 — 스톨 감지 + latching fault. F8 에서 cmd_vel watchdog 등 추가 예정.
 *
 * 100Hz 호출 가정 (control task 내 speed_controller_update 직후).
 *
 * 스톨 판정: 비정지 지령 AND |duty| ≥ STALL_DUTY_THRESH(0.60) 인 휠이 600ms 창에서 3mm 미만 이동.
 *           (지령 속도가 아니라 실제 인가 노력 기준 — 저속 지령의 진짜 구속도 잡음)
 * 진입 동작: 양쪽 target 강제 0, PID reset, motor_driver_stop_all().
 * 정책(2026-09-03): 일시 정지(STALL_HOLD_MS) 후 자동 재무장. 10초 내 3회 재발 시 하드 래치
 *           → safety_monitor_clear() 호출 전까지 유지. has_fault()=정지 중, is_latched()=하드 래치.
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
bool safety_monitor_has_fault(void);   /* 스톨 정지 중 (일시 또는 래치) */
bool safety_monitor_is_latched(void);  /* 하드 래치 — 리셋/clear 필요 */
void safety_monitor_clear(void);

/* F8: cmd_vel watchdog. cmd_vel 콜백에서 매번 호출 → 마지막 수신 시각 갱신.
 * 500ms 미수신 시 motors 강제 정지 + fault flag. */
void safety_monitor_cmdvel_received(void);
bool safety_monitor_cmdvel_timeout(void);

#ifdef __cplusplus
}
#endif

#endif
