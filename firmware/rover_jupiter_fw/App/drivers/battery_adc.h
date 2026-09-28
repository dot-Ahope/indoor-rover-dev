/**
 * @file battery_adc.h
 * @brief 배터리 전압 읽기 (ADC1, 분압 4.05 실측) — 여러 태스크 공용, 뮤텍스로 보호 (2026-09-28).
 *
 * 왜 분리: 전에는 microros_task 가 hadc1 을 직접 Start/Poll/Stop 했다. OLED 표시 태스크도 전압을 읽어야 해서
 *   (micro-ROS 에이전트가 없을 때도 표시) 같은 ADC 를 두 태스크가 동시에 건드리지 않도록 한곳에 모은다.
 * 변환 상수는 microros_task.c 에 있던 F8.5 캘리브레이션 그대로(V = raw × 3.3 × 4.05 / 4095).
 */
#ifndef BATTERY_ADC_H
#define BATTERY_ADC_H

#include <stdbool.h>

/** 스케줄러 시작 전·후 아무 때나 한 번 호출(뮤텍스 생성). */
void battery_adc_init(void);
/** 전압(V). 변환 실패면 false 와 함께 *v 는 바뀌지 않음. 최대 약 10 ms 블로킹. */
bool battery_adc_read(float *v);

#endif /* BATTERY_ADC_H */
