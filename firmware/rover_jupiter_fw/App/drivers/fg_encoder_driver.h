/**
 * @file    fg_encoder_driver.h
 * @brief   FG 단일펄스 기반 속도 피드백 드라이버 (통합 BLDC 전용).
 *
 * i_encoder.h 인터페이스 구현. 방식 B(Input Capture): TIM2_CH1(PA15=우 H1A),
 * TIM5_CH1(PA0=좌 H3A) 로 FG 펄스 주기를 캡처 → 순시 속도 산출.
 * FG 는 방향정보가 없어 부호는 모터 드라이버의 지령 방향([[bldc_last_dir_sign]])에서 주입.
 *
 * AM2861 모델은 stm32_encoder_driver.c(쿼드러처) 사용 — MOTOR_TYPE 로 택일.
 */
#ifndef APP_DRIVERS_FG_ENCODER_DRIVER_H
#define APP_DRIVERS_FG_ENCODER_DRIVER_H

#include "i_encoder.h"

#endif /* APP_DRIVERS_FG_ENCODER_DRIVER_H */
