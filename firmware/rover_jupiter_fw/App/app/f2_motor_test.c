/**
 * @file    f2_motor_test.c
 * @brief   F2 개방루프 PWM 시퀀스. 휠 받침대(공중) 전제.
 */
#include "f2_motor_test.h"

#include <stdio.h>
#include "cmsis_os.h"

#include "main.h"
#include "tim.h"
#include "i_motor_driver.h"

/* duty 1단계당 정지 1초 + 구동 3초. 트위치/정지마찰 구분 위해 더 길게. */
#define PHASE_DRIVE_MS  3000
#define PHASE_REST_MS   1000

/* duty 를 정수 % 로 표시 — newlib-nano printf 가 float 미지원이라
 * %f 가 빈 문자열로 나오는 문제 회피. */
static int duty_pct(float d) { return (int)(d * 100.0f); }

static void drive(const char *label, float left, float right)
{
    printf("[F2] %s  L=%+d%% R=%+d%%\r\n", label, duty_pct(left), duty_pct(right));
    motor_driver_set_duty(MOTOR_LEFT,  left);
    motor_driver_set_duty(MOTOR_RIGHT, right);
    osDelay(PHASE_DRIVE_MS);

    printf("[F2] stop\r\n");
    motor_driver_stop_all();
    osDelay(PHASE_REST_MS);
}

/* 모터 init 직후 TIM 레지스터 덤프 — ARR override·CCR 가 실제로 적용됐는지 검증. */
static void dump_tim_regs(void)
{
    printf("[F2-diag] TIM1: CR1=0x%04lX BDTR=0x%08lX CCER=0x%04lX ARR=%lu CCR1=%lu CCR4=%lu\r\n",
           (unsigned long)(TIM1->CR1 & 0xFFFFu),
           (unsigned long)TIM1->BDTR,
           (unsigned long)(TIM1->CCER & 0xFFFFu),
           (unsigned long)TIM1->ARR,
           (unsigned long)TIM1->CCR1,
           (unsigned long)TIM1->CCR4);
    printf("[F2-diag] TIM3: CR1=0x%04lX CCER=0x%04lX ARR=%lu CCR1=%lu CCR2=%lu\r\n",
           (unsigned long)(TIM3->CR1 & 0xFFFFu),
           (unsigned long)(TIM3->CCER & 0xFFFFu),
           (unsigned long)TIM3->ARR,
           (unsigned long)TIM3->CCR1,
           (unsigned long)TIM3->CCR2);
}

void f2_motor_test_run(void *arg)
{
    (void)arg;

    /* sanity init 후 사용자 안전 확인 시간. */
    printf("[F2] start in 3s — 휠 받침대 상태 확인\r\n");
    osDelay(3000);

    /* 1) 레지스터 상태 덤프 — PWM 설정이 실제 하드웨어에 반영됐는지 확인. */
    dump_tim_regs();

    /* 2) 단독 채널 + 양방향 — 어느 휠이 어느 방향으로 도는지 격리.
     *    50% 부터 시작 — F2 1차 실측에서 30%는 정지마찰 못 넘김 확인됨. */
    drive("L fwd 50%",  +0.50f, 0.0f);
    drive("L rev 50%",  -0.50f, 0.0f);
    drive("R fwd 50%",  0.0f, +0.50f);
    drive("R rev 50%",  0.0f, -0.50f);

    /* 3) 양쪽 동시. 매핑·방향 정상이면 두 휠 같이 전·후진. */
    drive("fwd 50%",  +0.50f, +0.50f);
    drive("rev 50%",  -0.50f, -0.50f);

    /* 4) RIGHT 휠이 50% 에서도 안 돌면 정지마찰/하드웨어 진단 — 70% 시도.
     *    안전 클램프 80% 이내. */
    drive("R fwd 70%",  0.0f, +0.70f);
    drive("R rev 70%",  0.0f, -0.70f);

    /* 5) 정지 후 레지스터 상태 재확인. */
    drive("zero",  0.0f, 0.0f);
    dump_tim_regs();

    printf("[F2] sequence done — motors stopped, monitor encoder counts\r\n");
    motor_driver_stop_all();

    for (;;) {
        osDelay(1000);
    }
}
