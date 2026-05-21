/**
 * @file    f2_motor_test.h
 * @brief   F2 단계 — 모터 개방루프 PWM 검증 시퀀스.
 *
 * 휠 받침대(공중) 상태에서 양쪽 모터의 정·역회전 동작과
 * 엔코더 카운트 부호 일치를 확인하는 자동 시퀀스.
 *
 * 안전: 듀티 절댓값은 driver 측에서 ≤ 80% 클램프.
 *       본 시퀀스 자체는 ≤ 20% 만 사용.
 */
#ifndef APP_APP_F2_MOTOR_TEST_H
#define APP_APP_F2_MOTOR_TEST_H

#ifdef __cplusplus
extern "C" {
#endif

/** FreeRTOS task entry. 부팅 3초 후 시퀀스 시작. */
void f2_motor_test_run(void *arg);

#ifdef __cplusplus
}
#endif

#endif
