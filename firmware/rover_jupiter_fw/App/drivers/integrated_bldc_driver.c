/**
 * @file    integrated_bldc_driver.c
 * @brief   통합 드라이버형 모터 드라이버 구현 (i_motor_driver.h).
 *
 * 제어 방식:
 *   - 속도: 청색선에 20kHz PWM duty 인가 (duty 크기 = 속도 크기) — 2026-09-07 50Hz→20kHz
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

/* ── 속도지령(청색) PWM ──────────
 * (구) 50Hz, 1MHz tick, ARR=19999 — 56:1 구모터 실측 확정값이었음.
 *   RIGHT(M1): TIM3 (APB1 timer 84MHz)  PSC=83  → 84M/84 =1MHz, CH1(PC6)
 *   LEFT (M3): TIM1 (APB2 timer 168MHz) PSC=167 → 168M/168=1MHz, CH4(PA11)
 */
/* 2026-09-07: 50Hz → 20kHz. 근거: MOTOR_1TO90_MIGRATION_PLAN.md §3.1 (신규 1:90 모터 권장 15~25kHz)
 * 이 항목(T1)이 미적용 상태로 남아 구모터(56:1) 값 50Hz 로 구동되고 있었음 → 받침대 실험에서
 * 50Hz 토크 맥동에 의한 회전자 떨림·FG 기저 펄스(50/100Hz 고정 주기)·진동 관측(09-07 SUMMARY).
 * 롤백: PWM_FREQ_HZ 50u, PSC 167/83, ARR 19999 (1MHz tick). 20kHz 에서 1MHz tick 은 50 step 뿐이라 tick 상향:
 *   RIGHT TIM3 84MHz  PSC=0 → 84MHz tick,  ARR=4199 → 20kHz, 4200 step
 *   LEFT  TIM1 168MHz PSC=1 → 84MHz tick,  ARR=4199 → 20kHz, 4200 step
 * ⚠ speed_controller 의 dz/KV/PID 는 50Hz 에서 튜닝된 값 — 20kHz 전환 후 재실측 필요. */
#define PWM_TICK_HZ    84000000u
#define PWM_FREQ_HZ    20000u
#define PWM_ARR        ((PWM_TICK_HZ / PWM_FREQ_HZ) - 1u)  /* 4199 */
#define TIM1_PSC_1MHZ  1u    /* (이름은 레거시) 168MHz/2 = 84MHz tick */
#define TIM3_PSC_1MHZ  0u    /* 84MHz tick */

/* 속도 PWM 채널 (실배선 기준) */
#define PWM_RIGHT_CH   TIM_CHANNEL_1   /* PC6 */
#define PWM_LEFT_CH    TIM_CHANNEL_4   /* PA11 */

/* duty 상한. 통합 컨트롤러가 자체 전류제한을 한다는 전제로 기본 1.0.
 * TODO(production): 컨트롤러 전류 거동(④) 확인 후 필요 시 하향. */
#define BLDC_DUTY_MAX  1.0f
/* TODO(production): duty 0%=정지 여부 / 최소 기동 duty(deadband)(①) 실측 확인. */

/* ── 방향선(백색) GPIO — push-pull ─────────────────────────
 * 레벨 방식(사용자 확정 ②). 처음엔 "컨트롤러 풀업 전제 open-drain" 으로 했으나
 * 램프 실측 결과 좌측 백색선엔 풀업이 없어 high-Z 가 LOW 로 떠 좌측이 전진만 됨.
 * → push-pull 로 HIGH(3.3V)/LOW 둘 다 능동 구동, 풀업 유무 무관하게 확정.
 *
 * 전진(+duty) 레벨은 컨트롤러별로 달라 좌·우 따로 지정 (램프 실측):
 *   RIGHT: HIGH=전진 (기존 정상),  LEFT: LOW=전진 (PA8=LOW 일 때 전진 관측). */
#define DIR_RIGHT_GPIO_Port  GPIOC
#define DIR_RIGHT_Pin        GPIO_PIN_7   /* M1B = PC7 (구 TIM3_CH2) */
#define DIR_LEFT_GPIO_Port   GPIOA
#define DIR_LEFT_Pin         GPIO_PIN_8   /* M3B = PA8 (구 TIM1_CH1) */

/* +duty(전진) 일 때 방향핀 레벨. 램프 실측 후 좌·우 개별 확정.
 * ⚠ 모터 교체(2026-08-26, 1:90)로 극성 반전 실측: b +50 → 양쪽 후진 → 둘 다 반전.
 *   (구 56:1: RIGHT HIGH=전진 / LEFT LOW=전진 — 모터별로 다르니 교체 시 반드시 실측) */
#define DIR_RIGHT_FWD_LEVEL  GPIO_PIN_RESET   /* LOW  = 전진 (1:90 실측) */
#define DIR_LEFT_FWD_LEVEL   GPIO_PIN_SET     /* HIGH = 전진 (1:90 실측) */

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

/* 마지막 지령 방향 부호 (+1 전진 / -1 후진). FG 엔코더가 속도 부호 주입에 사용
 * (FG 는 방향정보 없음). duty=0 일 때는 직전 값 유지. 초기값 전진(+1). */
static volatile int s_dir_sign[MOTOR_COUNT] = { +1, +1 };

int bldc_last_dir_sign(MotorChannel ch)
{
    return (ch < MOTOR_COUNT) ? s_dir_sign[ch] : +1;
}

/* PC7/PA8 을 방향 GPIO(push-pull)로 재설정. CubeMX MSP 의 AF 설정을 override. */
static void dir_gpio_init(void)
{
    GPIO_InitTypeDef g = {0};
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();

    g.Mode  = GPIO_MODE_OUTPUT_PP;  /* push-pull — HIGH/LOW 능동 구동 */
    g.Pull  = GPIO_PULLUP;
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
     *    TIM1 은 어드밴스드 타이머 → HAL_TIM_PWM_Start 가 MOE set.
     *    멱등: main(부팅 조기) + f1_sanity_init 에서 2회 호출되므로, 이미 start 된
     *    채널에 재호출 시 HAL 이 ERROR 반환 → s_started 가드로 1회만 start. */
    static bool s_started = false;
    if (!s_started) {
        if (HAL_TIM_PWM_Start(&htim3, PWM_RIGHT_CH) != HAL_OK) return false;
        if (HAL_TIM_PWM_Start(&htim1, PWM_LEFT_CH)  != HAL_OK) return false;
        s_started = true;
    }

    motor_driver_stop_all();
    return true;
}

void motor_driver_set_duty(MotorChannel ch, float duty)
{
    const uint32_t ccr = duty_to_ccr(fabsf(duty));

    /* 방향 부호 기록 (duty=0 이면 직전 유지) — FG 엔코더 속도 부호용 */
    if (ch < MOTOR_COUNT && duty != 0.0f) {
        s_dir_sign[ch] = (duty > 0.0f) ? +1 : -1;
    }

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
