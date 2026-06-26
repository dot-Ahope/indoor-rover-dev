/**
 * @file    integrated_bldc_driver.c
 * @brief   통합 드라이버형 모터 드라이버 구현 (i_motor_driver.h).
 *
 * 제어 방식:
 *   - 속도: 청색선에 50Hz PWM duty 인가 (duty 크기 = 속도 크기)
 *   - 방향: 백색선(레벨 방식) GPIO 로 결정 (duty 부호 = 방향)
 *   - 피드백(FG/황색)은 본 파일에서 다루지 않음 (step 5)
 *
 * 핀 매핑 (사용자 실배선 확정):
 *   RIGHT(M1): M1A=PC6=TIM3_CH1=PWM, M1B=PC7=방향GPIO,        H1A=PA15=FG
 *   LEFT (M3): M3A=PA11=TIM1_CH4=PWM, M3B=PA8=방향GPIO,       H3A=PA0 =FG
 *
 * .ioc 는 AM2861(PWM 2채널) 기준 그대로 두고, init 에서 핀을 런타임 재설정:
 *   - PC7(구 TIM3_CH2)/PA8(구 TIM1_CH1) → 방향 GPIO 출력
 *   - 속도 PWM 채널: RIGHT=TIM3_CH1(PC6), LEFT=TIM1_CH4(PA11)
 *   - TIM1/TIM3 prescaler·ARR → 50Hz
 */
#include "motor_config.h"

#if MOTOR_TYPE == MOTOR_TYPE_INTEGRATED_BLDC

#include "integrated_bldc_driver.h"
#include "main.h"
#include "tim.h"
#include <math.h>

/* ── 속도지령(청색) PWM: 50Hz duty (사용자 확정 ①) ──────────
 * 1MHz tick 으로 prescaler 설정 → ARR=19999 → 정확히 50Hz, duty 분해능 20000 step.
 *   RIGHT(M1): TIM3 (APB1 timer 84MHz)  PSC=83  → 84M/84 =1MHz, CH1(PC6)
 *   LEFT (M3): TIM1 (APB2 timer 168MHz) PSC=167 → 168M/168=1MHz, CH4(PA11)
 */
#define PWM_TICK_HZ    1000000u
#define PWM_FREQ_HZ    50u
#define PWM_ARR        ((PWM_TICK_HZ / PWM_FREQ_HZ) - 1u)  /* 19999 */
#define TIM1_PSC_1MHZ  167u
#define TIM3_PSC_1MHZ  83u

/* 속도 PWM 채널 (실배선 기준) */
#define PWM_RIGHT_CH   TIM_CHANNEL_1   /* PC6 */
#define PWM_LEFT_CH    TIM_CHANNEL_4   /* PA11 */

/* duty 상한. 통합 컨트롤러가 자체 전류제한을 한다는 전제로 기본 1.0.
 * TODO(production): 컨트롤러 전류 거동(④) 확인 후 필요 시 하향. */
#define BLDC_DUTY_MAX  1.0f
/* TODO(production): duty 0%=정지 여부 / 최소 기동 duty(deadband)(①) 실측 확인. */

/* ── 방향선(백색) GPIO ─────────────────────────────────────
 * 레벨 방식(사용자 확정 ②). "백색을 흑색(GND)에 접촉 시 방향 전환" →
 * 컨트롤러 내부 풀업 전제로 open-drain 구동:
 *     LOW(드라이브)  = GND 접촉   → 한쪽 방향
 *     HIGH(개방=풀업)             → 반대 방향
 * 어느 레벨이 전진인지는 F2 실측으로 확정 → *_FWD_LEVEL 한 줄로 반전. */
#define DIR_RIGHT_GPIO_Port  GPIOC
#define DIR_RIGHT_Pin        GPIO_PIN_7   /* M1B = PC7 (구 TIM3_CH2) */
#define DIR_LEFT_GPIO_Port   GPIOA
#define DIR_LEFT_Pin         GPIO_PIN_8   /* M3B = PA8 (구 TIM1_CH1) */

/* +duty(전진) 일 때 방향핀 레벨. F2 검증 후 조정. */
#define DIR_RIGHT_FWD_LEVEL  GPIO_PIN_SET
#define DIR_LEFT_FWD_LEVEL   GPIO_PIN_SET

/* CCR = |duty| * (ARR+1). duty=1.0 → CCR=ARR+1 (항상 High = 100% duty). */
static inline uint32_t duty_to_ccr(float duty_abs)
{
    if (duty_abs > BLDC_DUTY_MAX) duty_abs = BLDC_DUTY_MAX;
    return (uint32_t)(duty_abs * (float)(PWM_ARR + 1u));
}

/* duty 부호로 방향핀 레벨 결정 (전진 레벨 기준 반전). */
static inline GPIO_PinState dir_level(float duty, GPIO_PinState fwd_level)
{
    if (duty >= 0.0f) return fwd_level;
    return (fwd_level == GPIO_PIN_SET) ? GPIO_PIN_RESET : GPIO_PIN_SET;
}

/* PC7/PA8 을 방향 GPIO(open-drain)로 재설정. CubeMX MSP 의 AF 설정을 override. */
static void dir_gpio_init(void)
{
    GPIO_InitTypeDef g = {0};
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();

    g.Mode  = GPIO_MODE_OUTPUT_OD;  /* open-drain (컨트롤러 풀업 가정) */
    g.Pull  = GPIO_NOPULL;
    g.Speed = GPIO_SPEED_FREQ_LOW;

    g.Pin = DIR_RIGHT_Pin;
    HAL_GPIO_Init(DIR_RIGHT_GPIO_Port, &g);
    g.Pin = DIR_LEFT_Pin;
    HAL_GPIO_Init(DIR_LEFT_GPIO_Port, &g);

    /* 초기 방향 = 전진 */
    HAL_GPIO_WritePin(DIR_RIGHT_GPIO_Port, DIR_RIGHT_Pin, DIR_RIGHT_FWD_LEVEL);
    HAL_GPIO_WritePin(DIR_LEFT_GPIO_Port,  DIR_LEFT_Pin,  DIR_LEFT_FWD_LEVEL);
}

bool motor_driver_init(void)
{
    /* 1) 방향선 GPIO 구성 (PC7/PA8) */
    dir_gpio_init();

    /* 2) 속도 PWM 50Hz 재튜닝 — CubeMX 기본(20kHz) override.
     *    prescaler 변경은 update 이벤트에 latch → UG 로 즉시 반영. */
    __HAL_TIM_SET_PRESCALER(&htim1, TIM1_PSC_1MHZ);
    __HAL_TIM_SET_PRESCALER(&htim3, TIM3_PSC_1MHZ);
    __HAL_TIM_SET_AUTORELOAD(&htim1, PWM_ARR);
    __HAL_TIM_SET_AUTORELOAD(&htim3, PWM_ARR);
    htim1.Instance->EGR = TIM_EGR_UG;
    htim3.Instance->EGR = TIM_EGR_UG;
    __HAL_TIM_SET_COUNTER(&htim1, 0);
    __HAL_TIM_SET_COUNTER(&htim3, 0);

    /* 3) 속도지령 PWM 채널만 start. 방향은 GPIO 담당.
     *    RIGHT M1A=TIM3_CH1(PC6), LEFT M3A=TIM1_CH4(PA11).
     *    TIM1 은 어드밴스드 타이머 → HAL_TIM_PWM_Start 가 MOE set. */
    if (HAL_TIM_PWM_Start(&htim3, PWM_RIGHT_CH) != HAL_OK) return false;
    if (HAL_TIM_PWM_Start(&htim1, PWM_LEFT_CH)  != HAL_OK) return false;

    motor_driver_stop_all();
    return true;
}

void motor_driver_set_duty(MotorChannel ch, float duty)
{
    const uint32_t ccr = duty_to_ccr(fabsf(duty));

    if (ch == MOTOR_LEFT) {
        /* 좌측 휠 = M3 : 방향=PA8, 속도=TIM1_CH4(PA11) */
        HAL_GPIO_WritePin(DIR_LEFT_GPIO_Port, DIR_LEFT_Pin,
                          dir_level(duty, DIR_LEFT_FWD_LEVEL));
        __HAL_TIM_SET_COMPARE(&htim1, PWM_LEFT_CH, ccr);
    } else if (ch == MOTOR_RIGHT) {
        /* 우측 휠 = M1 : 방향=PC7, 속도=TIM3_CH1(PC6) */
        HAL_GPIO_WritePin(DIR_RIGHT_GPIO_Port, DIR_RIGHT_Pin,
                          dir_level(duty, DIR_RIGHT_FWD_LEVEL));
        __HAL_TIM_SET_COMPARE(&htim3, PWM_RIGHT_CH, ccr);
    }
    /* TODO(production): 회전 중 방향 전환 시 컨트롤러가 0속도 선행을 요구하는지 확인(②).
     *   필요 시 set_duty 레벨에서 brake-before-reverse 시퀀스 추가. */
}

void motor_driver_stop_all(void)
{
    /* duty 0 = 정지. 방향핀은 현재 상태 유지. */
    __HAL_TIM_SET_COMPARE(&htim3, PWM_RIGHT_CH, 0);
    __HAL_TIM_SET_COMPARE(&htim1, PWM_LEFT_CH,  0);
}

#endif /* MOTOR_TYPE == MOTOR_TYPE_INTEGRATED_BLDC */
