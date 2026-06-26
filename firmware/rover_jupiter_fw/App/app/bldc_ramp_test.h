/**
 * @file    bldc_ramp_test.h
 * @brief   통합 BLDC 개방루프 duty 램프 테스트 태스크.
 *
 * freertos.c 에서 osThreadNew 로 생성(평소 주석=비활성, 테스트 시만 해제).
 * ⚠ 활성 시 control task(speed_controller) 도 반드시 비활성 — 100Hz PID 가
 *   duty 0 으로 덮어쓰면 램프가 동작하지 않음.
 */
#ifndef APP_APP_BLDC_RAMP_TEST_H
#define APP_APP_BLDC_RAMP_TEST_H

#ifdef __cplusplus
extern "C" {
#endif

/** 받침대(공중) 전제 개방루프 램프 시퀀스. 무한 루프(끝나면 정지 유지). */
void bldc_ramp_test_run(void *argument);

#ifdef __cplusplus
}
#endif

#endif /* APP_APP_BLDC_RAMP_TEST_H */
