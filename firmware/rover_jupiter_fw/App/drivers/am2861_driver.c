/**
 * @file    am2861_driver.c
 * @brief   AM2861 sign-magnitude PWM 드라이버 구현.
 *
 * 동작표 (FIRMWARE_DEV_PLAN §2.1):
 *   전진: IA=PWM, IB=Low
 *   후진: IA=Low, IB=PWM
 *   정지: IA=Low, IB=Low
 *
 * F1 단계: PWM start + 듀티 0 유지. 실제 모터 회전은 F2에서.
 */
#include "motor_config.h"

#if MOTOR_TYPE == MOTOR_TYPE_AM2861

#include "am2861_driver.h"
#include "main.h"
#include "tim.h"
#include <math.h>

/* 안전 클램프 — AM2861 스톨 전류(2.3A) > 드라이버 한계 대응 (§7) */
#define MOTOR_DUTY_MAX 0.80f

/* PWM 20 kHz 목표 (가청대 이상). 타이머 클럭은 §F0 setup §3:
 *   TIM1 → APB2 timer = 168 MHz  → ARR = 168M/20k - 1 = 8399
 *   TIM3 → APB1 timer =  84 MHz  → ARR =  84M/20k - 1 = 4199
 * Prescaler 는 0 그대로 사용. */
#define TIM1_ARR_20K  8399u   /* TIM1 (M3, RIGHT) */
#define TIM3_ARR_20K  4199u   /* TIM3 (M1, LEFT)  */

/* CCR = |duty| * (ARR+1). duty=1.0 → CCR=ARR+1 (항상 High). */
static inline uint32_t duty_to_ccr(float duty_abs, uint32_t arr)
{
    if (duty_abs > MOTOR_DUTY_MAX) duty_abs = MOTOR_DUTY_MAX;
    return (uint32_t)(duty_abs * (float)(arr + 1u));
}

bool motor_driver_init(void)
{
    /* 20 kHz 재튜닝 — CubeMX 가 생성한 ARR=65535 를 런타임 override. */
    __HAL_TIM_SET_AUTORELOAD(&htim1, TIM1_ARR_20K);
    __HAL_TIM_SET_AUTORELOAD(&htim3, TIM3_ARR_20K);
    __HAL_TIM_SET_COUNTER(&htim1, 0);
    __HAL_TIM_SET_COUNTER(&htim3, 0);

    /* 멱등: main(부팅 조기) + f1_sanity_init 2회 호출 대비. 이미 start 된 채널에
     * 재호출 시 HAL 이 ERROR 반환 → s_started 가드로 1회만 start. */
    static bool s_started = false;
    if (!s_started) {
        /* TIM3 (M1: PC6/PC7) — LEFT */
        if (HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1) != HAL_OK) return false;
        if (HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_2) != HAL_OK) return false;

        /* TIM1 (M3: PA11=CH4, PA8=CH1) — RIGHT
         * TIM1은 어드밴스드 타이머 → 출력 활성에 MOE 필요.
         * HAL_TIM_PWM_Start가 내부에서 BDTR.MOE를 set 함. */
        if (HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1) != HAL_OK) return false;
        if (HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_4) != HAL_OK) return false;
        s_started = true;
    }

    motor_driver_stop_all();
    return true;
}

void motor_driver_set_duty(MotorChannel ch, float duty)
{
    const float duty_abs = fabsf(duty);

    if (ch == MOTOR_LEFT) {
        /* 좌측 휠 = M3 (TIM1: CH1=PA8, CH4=PA11).
         * F2 실측: CH4=PWM 시 차량 후진 확인 → +duty=전진 되도록 CH1 에 PWM 인가. */
        const uint32_t ccr = duty_to_ccr(duty_abs, TIM1_ARR_20K);
        if (duty >= 0.0f) {
            __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, ccr);
            __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_4, 0);
        } else {
            __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, 0);
            __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_4, ccr);
        }
    } else if (ch == MOTOR_RIGHT) {
        /* 우측 휠 = M1 (TIM3: CH1=PC6, CH2=PC7). 방향 미검증 — F2 후속 테스트로 확정. */
        const uint32_t ccr = duty_to_ccr(duty_abs, TIM3_ARR_20K);
        if (duty >= 0.0f) {
            __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, ccr);
            __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_2, 0);
        } else {
            __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, 0);
            __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_2, ccr);
        }
    }
}

void motor_driver_stop_all(void)
{
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, 0);
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_2, 0);
    __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, 0);
    __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_4, 0);
}

#endif /* MOTOR_TYPE == MOTOR_TYPE_AM2861 */
