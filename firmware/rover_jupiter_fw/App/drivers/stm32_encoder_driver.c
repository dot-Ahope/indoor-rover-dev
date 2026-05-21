/**
 * @file    stm32_encoder_driver.c
 * @brief   STM32 TIM 엔코더 모드 드라이버 구현.
 *
 * TIM2/TIM5 모두 32-bit, ARR=0xFFFFFFFF. CNT 부호 해석으로 양·음 방향 모두 처리.
 */
#include "stm32_encoder_driver.h"
#include "tim.h"

bool encoder_init(void)
{
    if (HAL_TIM_Encoder_Start(&htim2, TIM_CHANNEL_ALL) != HAL_OK) return false;
    if (HAL_TIM_Encoder_Start(&htim5, TIM_CHANNEL_ALL) != HAL_OK) return false;
    __HAL_TIM_SET_COUNTER(&htim2, 0);
    __HAL_TIM_SET_COUNTER(&htim5, 0);
    return true;
}

int32_t encoder_read_count(EncoderChannel ch)
{
    /* ENC_LEFT  = TIM5 (좌측 휠). 좌측 모터 방향 반전 적용으로 부호 negate.
     * ENC_RIGHT = TIM2 (우측 휠). 방향 미검증 — RIGHT 휠 회전 가능해진 후 확정. */
    if (ch == ENC_LEFT)  return -(int32_t)__HAL_TIM_GET_COUNTER(&htim5);
    if (ch == ENC_RIGHT) return  (int32_t)__HAL_TIM_GET_COUNTER(&htim2);
    return 0;
}

void encoder_reset(EncoderChannel ch)
{
    if (ch == ENC_LEFT)  __HAL_TIM_SET_COUNTER(&htim5, 0);
    if (ch == ENC_RIGHT) __HAL_TIM_SET_COUNTER(&htim2, 0);
}
