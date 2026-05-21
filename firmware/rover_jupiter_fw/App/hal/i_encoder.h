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
 * 카운트당 거리 = 0.131 mm (Ø55 mm, 1320 CPR · ×4 = 5280 cnt/rev / 둘레 0.1728 m).
 * 자세한 계산은 FIRMWARE_DEV_PLAN §2.2.
 */
int32_t encoder_read_count(EncoderChannel ch);

/** 카운트 0으로 리셋 (oдometry 초기화용). */
void encoder_reset(EncoderChannel ch);

#ifdef __cplusplus
}
#endif

#endif /* APP_HAL_I_ENCODER_H */
