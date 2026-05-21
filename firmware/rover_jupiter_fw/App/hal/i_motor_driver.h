/**
 * @file    i_motor_driver.h
 * @brief   HAL — 모터 드라이버 인터페이스
 *
 * App Layer(MotionController)가 호출하는 모터 제어 인터페이스.
 * 구현체는 App/drivers/ 하위 (현재: am2861_driver.c).
 * 양산기 이식 시 다른 드라이버 .c 로 교체되며 이 헤더는 유지.
 *
 * 참조: docs/FIRMWARE_DEV_PLAN.md §3.1 (계층 구조)
 */
#ifndef APP_HAL_I_MOTOR_DRIVER_H
#define APP_HAL_I_MOTOR_DRIVER_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/** 휠 채널. ROS REP-103: X 전방, Y 좌측 → 좌측 휠이 +Y. */
typedef enum {
    MOTOR_LEFT  = 0,
    MOTOR_RIGHT = 1,
    MOTOR_COUNT
} MotorChannel;

/**
 * @brief 모터 드라이버 초기화 (PWM 타이머 start 포함).
 * @return true 성공
 */
bool motor_driver_init(void);

/**
 * @brief 채널별 듀티 지령.
 * @param ch    채널
 * @param duty  -1.0 ~ +1.0. 부호 = 회전 방향. 절댓값 = PWM 듀티.
 *
 * 내부에서 안전 클램프 (절댓값 ≤ 0.80) 적용.
 * 참조: FIRMWARE_DEV_PLAN §7 (PWM 최대 80% 제한, 스톨 보호).
 */
void motor_driver_set_duty(MotorChannel ch, float duty);

/** 모든 채널 즉시 정지 (IA=Low, IB=Low). watchdog·E-stop 경로. */
void motor_driver_stop_all(void);

#ifdef __cplusplus
}
#endif

#endif /* APP_HAL_I_MOTOR_DRIVER_H */
