/**
 * @file    speed_controller.h
 * @brief   F4 — 좌·우 휠 폐루프 속도 PID 컨트롤러.
 *
 * 100Hz 호출 가정 (encoder_update_velocity 직후, 같은 task).
 * 입력: target_mps (set_target). 출력: motor_driver_set_duty 자동 호출.
 *
 * Dead-zone 보상: 명령이 있는데 PID 출력이 정지마찰 미만이면 최소 회전 duty 인가.
 * 좌·우 비대칭 정지마찰(LEFT~30%, RIGHT~55% — F2 실측)에 맞춰 채널별 설정.
 */
#ifndef APP_APP_SPEED_CONTROLLER_H
#define APP_APP_SPEED_CONTROLLER_H

#include "i_motor_driver.h"

#ifdef __cplusplus
extern "C" {
#endif

void  speed_controller_init(void);
void  speed_controller_update(void);   /* 100 Hz 호출 */

void  speed_controller_set_target(MotorChannel ch, float target_mps);
float speed_controller_get_target(MotorChannel ch);
float speed_controller_get_duty(MotorChannel ch);  /* 마지막 인가 duty (디버그용) */

/** 적분 누적 강제 0 — 정지·fault 진입 시 호출. */
void  speed_controller_reset(void);

#ifdef __cplusplus
}
#endif

#endif
