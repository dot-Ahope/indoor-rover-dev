/**
 * @file    stm32_encoder_driver.c
 * @brief   STM32 TIM 엔코더 모드 드라이버 구현.
 *
 * TIM2/TIM5 모두 32-bit, ARR=0xFFFFFFFF. CNT 부호 해석으로 양·음 방향 모두 처리.
 */
#include "rover_platform.h"   /* MOTOR_TYPE (motor_config.h 경유) */

#if MOTOR_TYPE == MOTOR_TYPE_AM2861

#include "stm32_encoder_driver.h"
#include "tim.h"

/* 속도 산출 설정 — encSample task 가 100Hz 로 호출 (freertos.c). */
#define V_SAMPLE_HZ      100u
#define V_SAMPLE_DT_S    (1.0f / (float)V_SAMPLE_HZ)
#define V_EMA_ALPHA      0.2f   /* time constant ≈ 40 ms */

static struct {
    int32_t prev_cnt;
    float   v_filt_mps;
} s_v[ENC_COUNT];

bool encoder_init(void)
{
    if (HAL_TIM_Encoder_Start(&htim2, TIM_CHANNEL_ALL) != HAL_OK) return false;
    if (HAL_TIM_Encoder_Start(&htim5, TIM_CHANNEL_ALL) != HAL_OK) return false;
    __HAL_TIM_SET_COUNTER(&htim2, 0);
    __HAL_TIM_SET_COUNTER(&htim5, 0);
    for (int i = 0; i < ENC_COUNT; i++) {
        s_v[i].prev_cnt   = 0;
        s_v[i].v_filt_mps = 0.0f;
    }
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
    if (ch < ENC_COUNT) {
        s_v[ch].prev_cnt   = 0;
        s_v[ch].v_filt_mps = 0.0f;
    }
}

void encoder_update_velocity(void)
{
    for (int i = 0; i < ENC_COUNT; i++) {
        const int32_t now = encoder_read_count((EncoderChannel)i);
        /* int32_t 뺄셈은 modulo-2^32 wrap 안전. 100Hz 샘플·~3000cnt/s 면 |d| ≪ 2^31. */
        const int32_t d   = now - s_v[i].prev_cnt;
        s_v[i].prev_cnt   = now;
        const float v_raw = (float)d * METERS_PER_COUNT / V_SAMPLE_DT_S;
        s_v[i].v_filt_mps = V_EMA_ALPHA * v_raw +
                            (1.0f - V_EMA_ALPHA) * s_v[i].v_filt_mps;
    }
}

float encoder_read_velocity_mps(EncoderChannel ch)
{
    if (ch >= ENC_COUNT) return 0.0f;
    return s_v[ch].v_filt_mps;
}

float encoder_read_distance_m(EncoderChannel ch)
{
    /* count × m/cnt. count 자체가 부호 처리되므로 거리도 자동 부호. */
    return (float)encoder_read_count(ch) * METERS_PER_COUNT;
}

/* 펄스 통계는 FG 드라이버 전용 — 쿼드러처 구성에서는 0 반환 (인터페이스 호환용 스텁). */
void encoder_get_pulse_stats(EncoderChannel ch, uint32_t *pps, uint32_t *period_us, uint32_t *cv_pct,
                             uint32_t *width_us)
{
    (void)ch; *pps = 0; *period_us = 0; *cv_pct = 0; *width_us = 0;
}

#endif /* MOTOR_TYPE == MOTOR_TYPE_AM2861 */
