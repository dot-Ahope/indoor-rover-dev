/**
 * @file    fg_encoder_driver.c
 * @brief   FG 단일펄스 속도 피드백 (Input Capture) — 통합 BLDC 전용, i_encoder.h 구현.
 *
 * 매핑:  ENC_RIGHT ← TIM2_CH1 (PA15 = H1A, 우측 FG)
 *        ENC_LEFT  ← TIM5_CH1 (PA0  = H3A, 좌측 FG)
 *
 * 동작 (방식 B):
 *   - 두 타이머를 1MHz(PSC=83) 내부클럭 + CH1 Input Capture(상승에지)로 재설정.
 *   - 캡처 인터럽트마다 직전 캡처와의 차이 = 펄스 주기(ticks) 저장, 카운트 ±1.
 *   - encoder_update_velocity(100Hz): 최신 주기로 순시 속도 = MPC / (period/1MHz).
 *     펄스가 뜸해지면 마지막 캡처 이후 경과시간으로 상한을 걸어 감쇠, 타임아웃 시 0.
 *   - 부호(방향)는 FG 에 없으므로 bldc_last_dir_sign() 에서 주입.
 *
 * .ioc 는 AM2861(엔코더 모드) 기준 그대로. init 에서 런타임 재설정.
 * TIM2/TIM5 global IRQ 핸들러는 stm32f4xx_it.c 에 추가됨(HAL_TIM_IRQHandler 포워딩).
 */
#include "rover_platform.h"   /* MOTOR_TYPE, METERS_PER_COUNT */

#if MOTOR_TYPE == MOTOR_TYPE_INTEGRATED_BLDC

#include "fg_encoder_driver.h"
#include "tim.h"
#include "integrated_bldc_driver.h"   /* bldc_last_dir_sign */
#include <math.h>

/* 캡처 타이머 tick: TIM2/TIM5 = APB1 84MHz, PSC=83 → 1MHz (1 tick = 1us). */
#define FG_TICK_HZ        1000000u
#define FG_PSC            83u

/* 속도 샘플 (encoder_update_velocity 호출 주기, freertos control task 100Hz). */
#define V_SAMPLE_HZ       100u
#define V_EMA_ALPHA       0.30f            /* 주기측정이라 필터 약하게 */
/* 정지 판정: 이 tick 수 동안 새 펄스 없으면 v=0. 100Hz 기준 6 = 60ms. */
#define STOP_IDLE_TICKS   6u

/* ── ISR 공유 상태 (volatile) ── */
static volatile uint32_t s_cap_prev[ENC_COUNT];    /* 직전 캡처값 (ticks) */
static volatile uint32_t s_period[ENC_COUNT];      /* 최근 펄스 주기 (ticks) */
static volatile uint32_t s_cap_seq[ENC_COUNT];     /* 캡처마다 증가 (task 감지용) */
static volatile int32_t  s_count[ENC_COUNT];       /* 부호 있는 누적 펄스 */
static volatile bool     s_have_prev[ENC_COUNT];

/* ── task 전용 상태 ── */
static uint32_t s_seq_last[ENC_COUNT];
static uint32_t s_idle[ENC_COUNT];
static float    s_v_filt[ENC_COUNT];

static inline TIM_HandleTypeDef *tim_of(EncoderChannel ch)
{
    return (ch == ENC_RIGHT) ? &htim2 : &htim5;   /* 우=TIM2(PA15), 좌=TIM5(PA0) */
}

/* FG 입력 핀을 AF(타이머 입력) + 내부 풀업으로 (오픈컬렉터 FG 대비). */
static void fg_gpio_init(void)
{
    GPIO_InitTypeDef g = {0};
    __HAL_RCC_GPIOA_CLK_ENABLE();
    g.Mode  = GPIO_MODE_AF_PP;
    g.Pull  = GPIO_PULLUP;
    g.Speed = GPIO_SPEED_FREQ_LOW;

    g.Pin = GPIO_PIN_15; g.Alternate = GPIO_AF1_TIM2;  /* 우 H1A */
    HAL_GPIO_Init(GPIOA, &g);
    g.Pin = GPIO_PIN_0;  g.Alternate = GPIO_AF2_TIM5;  /* 좌 H3A */
    HAL_GPIO_Init(GPIOA, &g);
}

/* 엔코더 모드 → CH1 Input Capture(1MHz, 상승에지) 재설정 + IRQ start. */
static bool fg_ic_init(TIM_HandleTypeDef *htim)
{
    HAL_TIM_Encoder_Stop(htim, TIM_CHANNEL_ALL);
    htim->Instance->SMCR &= ~TIM_SMCR_SMS;          /* 엔코더 슬레이브모드 해제 → 내부클럭 */

    __HAL_TIM_SET_PRESCALER(htim, FG_PSC);          /* 84MHz/84 = 1MHz */
    __HAL_TIM_SET_AUTORELOAD(htim, 0xFFFFFFFFu);
    htim->Instance->EGR = TIM_EGR_UG;               /* PSC/ARR latch */
    __HAL_TIM_SET_COUNTER(htim, 0);

    TIM_IC_InitTypeDef sic = {0};
    sic.ICPolarity  = TIM_ICPOLARITY_RISING;
    sic.ICSelection = TIM_ICSELECTION_DIRECTTI;
    sic.ICPrescaler = TIM_ICPSC_DIV1;
    sic.ICFilter    = 0x0F;                          /* 최대 필터 — FG 노이즈 디바운스 */
    if (HAL_TIM_IC_ConfigChannel(htim, &sic, TIM_CHANNEL_1) != HAL_OK) return false;
    if (HAL_TIM_IC_Start_IT(htim, TIM_CHANNEL_1) != HAL_OK) return false;
    return true;
}

bool encoder_init(void)
{
    for (int i = 0; i < ENC_COUNT; i++) {
        s_cap_prev[i] = 0; s_period[i] = 0; s_cap_seq[i] = 0;
        s_count[i] = 0; s_have_prev[i] = false;
        s_seq_last[i] = 0; s_idle[i] = STOP_IDLE_TICKS; s_v_filt[i] = 0.0f;
    }
    fg_gpio_init();
    bool ok = true;
    ok &= fg_ic_init(&htim2);
    ok &= fg_ic_init(&htim5);

    /* 캡처 인터럽트 NVIC 활성 (ISR 은 FreeRTOS API 미사용 → 우선순위 자유, 5로 지정). */
    HAL_NVIC_SetPriority(TIM2_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(TIM2_IRQn);
    HAL_NVIC_SetPriority(TIM5_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(TIM5_IRQn);
    return ok;
}

/* HAL 캡처 콜백 (TIM2/TIM5 CC1). */
void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim)
{
    EncoderChannel ch;
    if      (htim->Instance == TIM2) ch = ENC_RIGHT;
    else if (htim->Instance == TIM5) ch = ENC_LEFT;
    else return;

    const uint32_t cap = htim->Instance->CCR1;
    if (s_have_prev[ch]) {
        s_period[ch] = cap - s_cap_prev[ch];        /* 32-bit wrap-safe */
    }
    s_cap_prev[ch]  = cap;
    s_have_prev[ch] = true;
    s_cap_seq[ch]++;
    s_count[ch] += (bldc_last_dir_sign((MotorChannel)ch) >= 0) ? 1 : -1;
}

int32_t encoder_read_count(EncoderChannel ch)
{
    return (ch < ENC_COUNT) ? s_count[ch] : 0;
}

void encoder_reset(EncoderChannel ch)
{
    if (ch >= ENC_COUNT) return;
    s_count[ch]   = 0;
    s_v_filt[ch]  = 0.0f;
    s_idle[ch]    = STOP_IDLE_TICKS;
}

void encoder_update_velocity(void)
{
    for (int ch = 0; ch < ENC_COUNT; ch++) {
        const float sgn = (bldc_last_dir_sign((MotorChannel)ch) >= 0) ? 1.0f : -1.0f;
        const uint32_t seq = s_cap_seq[ch];
        float v_raw;

        if (seq != s_seq_last[ch]) {
            /* 새 펄스 도착 — 최신 주기로 순시 속도 */
            s_seq_last[ch] = seq;
            s_idle[ch]     = 0;
            const uint32_t period = s_period[ch];
            v_raw = (period > 0u)
                  ? sgn * METERS_PER_COUNT * (float)FG_TICK_HZ / (float)period
                  : 0.0f;
        } else {
            /* 새 펄스 없음 — 마지막 캡처 이후 경과로 속도 상한을 걸어 감쇠 */
            if (++s_idle[ch] >= STOP_IDLE_TICKS) {
                s_v_filt[ch] = 0.0f;                 /* 정지 확정 */
                continue;
            }
            const uint32_t elapsed = __HAL_TIM_GET_COUNTER(tim_of((EncoderChannel)ch))
                                     - s_cap_prev[ch];
            const float v_bound = (elapsed > 0u)
                  ? sgn * METERS_PER_COUNT * (float)FG_TICK_HZ / (float)elapsed
                  : 0.0f;
            /* 크기가 줄어드는 쪽으로만 (감쇠) */
            v_raw = (fabsf(v_bound) < fabsf(s_v_filt[ch])) ? v_bound : s_v_filt[ch];
        }
        s_v_filt[ch] = V_EMA_ALPHA * v_raw + (1.0f - V_EMA_ALPHA) * s_v_filt[ch];
    }
}

float encoder_read_velocity_mps(EncoderChannel ch)
{
    return (ch < ENC_COUNT) ? s_v_filt[ch] : 0.0f;
}

float encoder_read_distance_m(EncoderChannel ch)
{
    return (float)encoder_read_count(ch) * METERS_PER_COUNT;
}

#endif /* MOTOR_TYPE == MOTOR_TYPE_INTEGRATED_BLDC */
