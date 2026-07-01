/**
 * @file    fg_count_test.h
 * @brief   FG PPR 측정용 펄스 카운터 진단 태스크 (방식②).
 *
 * freertos.c 에서 osThreadNew 로 생성(평소 주석=비활성, 측정 시만 해제).
 * control task 와 공존 가능(모터 정지 상태에서 손으로 휠 회전).
 */
#ifndef APP_APP_FG_COUNT_TEST_H
#define APP_APP_FG_COUNT_TEST_H

#ifdef __cplusplus
extern "C" {
#endif

/** TIM2(PA15=우 FG)/TIM5(PA0=좌 FG) 를 외부클럭 카운터로 돌려 펄스 누적. */
void fg_count_test_run(void *argument);

#ifdef __cplusplus
}
#endif

#endif /* APP_APP_FG_COUNT_TEST_H */
