/**
 * @file    f4_pid_test.h
 * @brief   F4 폐루프 PID + 스톨 감지 검증 시퀀스.
 *
 * step response → 정상오차/오버슈트 관찰. 마지막에 30초 steady 구간 두어
 * 사용자가 휠을 손으로 막아 stall fault 발동 확인 가능.
 */
#ifndef APP_APP_F4_PID_TEST_H
#define APP_APP_F4_PID_TEST_H

#ifdef __cplusplus
extern "C" {
#endif

void f4_pid_test_run(void *arg);

#ifdef __cplusplus
}
#endif

#endif
