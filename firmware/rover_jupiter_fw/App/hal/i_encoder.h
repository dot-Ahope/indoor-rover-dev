/**
 * @file    i_encoder.h
 * @brief   HAL — 직교 엔코더 인터페이스
 *
 * 구현체: App/drivers/stm32_encoder_driver.c (TIM2=좌, TIM5=우, 32-bit)
 * 양산기 이식 시 다른 MCU 또는 외장 엔코더 IC 로 교체 가능.
 *
 * CPR / 휠 반경 등 물리 파라미터는 App Layer(OdometryEstimator)가 보유.
 * 본 인터페이스는 raw 카운트만 노출.
 */
#ifndef APP_HAL_I_ENCODER_H
#define APP_HAL_I_ENCODER_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    ENC_LEFT  = 0,
    ENC_RIGHT = 1,
    ENC_COUNT
} EncoderChannel;

/** 엔코더 초기화 (HAL_TIM_Encoder_Start). */
bool encoder_init(void);

/**
 * @brief 현재 카운트 (signed). 32-bit TIM2/TIM5 의 CNT 그대로 부호 해석.
 *
 * 카운트당 거리 = 0.119 mm (Ø50 mm, 1320 CPR / 둘레 0.1571 m).
 * 자세한 계산은 FIRMWARE_DEV_PLAN §2.2.
 */
int32_t encoder_read_count(EncoderChannel ch);

/** 카운트 0으로 리셋 (oдometry 초기화용). */
void encoder_reset(EncoderChannel ch);

/**
 * @brief 주기적 샘플 함수. ΔCNT/Δt 로 휠 선속도 산출 후 EMA 필터 갱신.
 *        100 Hz 호출 권장 (driver 내부 상수 V_SAMPLE_DT_S 와 일치 필요).
 *        FreeRTOS 일반 태스크에서 호출 — HAL API 호출 가능.
 */
void encoder_update_velocity(void);

/**
 * @brief 마지막 update 시점 기준 EMA 필터된 휠 선속도 (m/s).
 *        +값 = 전진 방향. encoder_update_velocity() 호출 빈도가 정확도 결정.
 */
float encoder_read_velocity_mps(EncoderChannel ch);

/**
 * @brief 현재 카운트 기준 누적 직선거리 (m).
 *        encoder_reset() 시점부터의 누적. +값 = 전진.
 *        검증용: 휠을 손으로 일정 거리 굴려보고 자/줄자와 비교.
 */
float encoder_read_distance_m(EncoderChannel ch);

#ifdef __cplusplus
}
#endif

#endif /* APP_HAL_I_ENCODER_H */
