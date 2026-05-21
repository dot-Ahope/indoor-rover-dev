/**
 * @file    f1_sanity_task.h
 * @brief   F1 단계 페리페럴 sanity 검증.
 *
 * 모든 드라이버 init 호출 → 결과 콘솔 출력.
 * 주기적으로 엔코더 카운트·ADC·IMU WHO_AM_I 등 dump.
 *
 * F2 이후 단계에서는 제거하거나 비활성.
 */
#ifndef APP_APP_F1_SANITY_TASK_H
#define APP_APP_F1_SANITY_TASK_H

/* 보드 옵션 — RM3100 자기계 미실장 시 0. ICM-20948 내장 AK09916 으로 대체. */
#ifndef F1_RM3100_PRESENT
#define F1_RM3100_PRESENT 0
#endif

#ifdef __cplusplus
extern "C" {
#endif

/** RTOS 시작 후 1회 호출. 모든 드라이버 초기화하고 결과 콘솔 출력. */
void f1_sanity_init(void);

/** 1Hz로 호출. 페리페럴 라이브 상태 dump. */
void f1_sanity_tick(void);

#ifdef __cplusplus
}
#endif

#endif /* APP_APP_F1_SANITY_TASK_H */
