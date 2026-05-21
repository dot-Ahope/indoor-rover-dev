/**
 * @file    stm32_encoder_driver.h
 * @brief   STM32 TIM 엔코더 모드 드라이버.
 *
 * 매핑 (F2 실측 확정 — 모터 매핑과 동일하게 좌·우 결정):
 *   ENC_LEFT  ← TIM5 (PA0/PA1)  — 좌측 휠 엔코더, 좌측 모터(M3/TIM1)와 페어
 *   ENC_RIGHT ← TIM2 (PA15/PB3) — 우측 휠 엔코더, 우측 모터(M1/TIM3)와 페어
 *
 * ENC_LEFT 는 좌측 모터 +duty=전진 방향 보정에 맞춰 카운트 부호 반전.
 * (TIM5 CNT 자체가 음수로 가도록 IC polarity 변경 대신 read 시 negate.)
 */
#ifndef APP_DRIVERS_STM32_ENCODER_DRIVER_H
#define APP_DRIVERS_STM32_ENCODER_DRIVER_H

#include "i_encoder.h"

#endif
