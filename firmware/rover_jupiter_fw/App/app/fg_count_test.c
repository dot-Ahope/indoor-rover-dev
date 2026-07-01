/**
 * @file    fg_count_test.c
 * @brief   FG PPR 측정용 펄스 카운터 진단 (방식②).
 *
 * FG 핀(우 H1A=PA15=TIM2_CH1, 좌 H3A=PA0=TIM5_CH1)을 "외부클럭 모드 1"
 * (TI1 상승에지마다 CNT++)로 재설정 → 1펄스=1카운트로 누적.
 * 휠을 손으로 정확히 N바퀴 돌린 뒤 count delta 를 읽어:
 *     PPR(휠 1회전당 펄스) = (count delta) / N
 *
 * 입력 내부 풀업 ON (오픈컬렉터 FG 대비). 입력 필터 최대(노이즈 디바운스).
 * 1초마다 UART5(115200) 로 현재 카운트 출력.
 *
 * ⚠ 임시 측정 도구. TIM2/TIM5 는 평소 엔코더(쿼드러처)용이라, 본 진단 활성 중
 *   encoder_read_* 값은 의미 없음(같은 타이머 점유). step5 에서 Input Capture
 *   기반 속도/odometry 로 정식 구현 예정.
 */
#include "fg_count_test.h"

#include <stdio.h>
#include "cmsis_os.h"
#include "main.h"
#include "tim.h"

/* 타이머를 TI1 외부클럭 카운터로 재설정 (인코더 모드 중지 후). */
static void fg_timer_to_counter(TIM_HandleTypeDef *htim)
{
    HAL_TIM_Encoder_Stop(htim, TIM_CHANNEL_ALL);

    TIM_ClockConfigTypeDef cs = {0};
    cs.ClockSource    = TIM_CLOCKSOURCE_TI1;
    cs.ClockPolarity  = TIM_CLOCKPOLARITY_RISING;
    cs.ClockPrescaler = TIM_CLOCKPRESCALER_DIV1;
    cs.ClockFilter    = 0x0F;   /* 최대 필터 — FG 채터/노이즈 디바운스 */
    HAL_TIM_ConfigClockSource(htim, &cs);

    __HAL_TIM_SET_COUNTER(htim, 0);
    HAL_TIM_Base_Start(htim);
}

/* FG 입력 핀을 AF(타이머 입력) + 내부 풀업 으로 재설정. */
static void fg_gpio_pullup(GPIO_TypeDef *port, uint16_t pin, uint8_t af)
{
    GPIO_InitTypeDef g = {0};
    g.Pin       = pin;
    g.Mode      = GPIO_MODE_AF_PP;
    g.Pull      = GPIO_PULLUP;       /* 오픈컬렉터 FG 대비 */
    g.Speed     = GPIO_SPEED_FREQ_LOW;
    g.Alternate = af;
    HAL_GPIO_Init(port, &g);
}

void fg_count_test_run(void *argument)
{
    (void)argument;

    osDelay(300);   /* f1_sanity_init() 의 encoder_init() 이후 */

    fg_gpio_pullup(GPIOA, GPIO_PIN_15, GPIO_AF1_TIM2);  /* 우 FG (H1A) */
    fg_gpio_pullup(GPIOA, GPIO_PIN_0,  GPIO_AF2_TIM5);  /* 좌 FG (H3A) */
    fg_timer_to_counter(&htim2);
    fg_timer_to_counter(&htim5);

    printf("[FG-count] start — 휠을 정확히 N바퀴 손으로 돌린 뒤 count delta 확인\r\n");
    printf("[FG-count] PPR(wheel) = (count delta) / N  (우측 휠 권장: 좌측 모터 HW 이슈)\r\n");

    for (;;) {
        const uint32_t r = __HAL_TIM_GET_COUNTER(&htim2);  /* PA15 우 */
        const uint32_t l = __HAL_TIM_GET_COUNTER(&htim5);  /* PA0  좌 */
        printf("[FG-count] R(PA15)=%lu  L(PA0)=%lu\r\n",
               (unsigned long)r, (unsigned long)l);
        osDelay(1000);
    }
}
