/**
 * @file    f4_pid_test.c
 * @brief   F4 step response 시퀀스. 휠 받침대 전제.
 */
#include "f4_pid_test.h"

#include <stdio.h>
#include "cmsis_os.h"

#include "speed_controller.h"
#include "safety_monitor.h"

static void seg(const char *label, float l_mps, float r_mps, uint32_t ms)
{
    printf("[F4] %s  tgt L=%+dmm/s R=%+dmm/s\r\n",
           label, (int)(l_mps * 1000.0f), (int)(r_mps * 1000.0f));
    speed_controller_set_target(MOTOR_LEFT,  l_mps);
    speed_controller_set_target(MOTOR_RIGHT, r_mps);
    osDelay(ms);
}

void f4_pid_test_run(void *arg)
{
    (void)arg;

    /* 안전 확인 시간 + sanity init 완료 대기. */
    printf("[F4] start in 3s — 휠 받침대 상태 확인\r\n");
    osDelay(3000);
    printf("[F4] sequence begin\r\n");

    /* --- 1) LEFT 단독 step response --- */
    seg("L  0.20 m/s", +0.20f, 0.0f, 3000);
    seg("L  0.40 m/s", +0.40f, 0.0f, 3000);
    seg("L  stop",      0.0f,  0.0f, 1000);
    seg("L -0.20 m/s", -0.20f, 0.0f, 3000);
    seg("L  stop",      0.0f,  0.0f, 1000);

    /* --- 2) RIGHT 단독 step response --- */
    seg("R  0.20 m/s", 0.0f, +0.20f, 3000);
    seg("R  0.40 m/s", 0.0f, +0.40f, 3000);
    seg("R  stop",     0.0f,  0.0f,  1000);
    seg("R -0.20 m/s", 0.0f, -0.20f, 3000);
    seg("R  stop",     0.0f,  0.0f,  1000);

    /* --- 3) 양쪽 동시 — 좌·우 균일성 관찰 --- */
    seg("both  0.30 m/s", +0.30f, +0.30f, 3000);
    seg("both  stop",      0.0f,  0.0f,   1000);
    seg("both -0.30 m/s", -0.30f, -0.30f, 3000);
    seg("both  stop",      0.0f,  0.0f,   1000);

    /* --- 4) 부드러운 방향 전환 (PID 안정성 관찰) --- */
    seg("both +0.20", +0.20f, +0.20f, 2000);
    seg("both -0.20", -0.20f, -0.20f, 2000);
    seg("both  stop",  0.0f,   0.0f,  1000);

    /* --- 5) Steady 구간 — 사용자가 손으로 휠 잡아 stall 테스트 가능 --- */
    printf("[F4] STEADY 0.20 m/s for 30s — try blocking a wheel by hand to trigger STALL\r\n");
    speed_controller_set_target(MOTOR_LEFT,  +0.20f);
    speed_controller_set_target(MOTOR_RIGHT, +0.20f);
    osDelay(30000);

    speed_controller_set_target(MOTOR_LEFT,  0.0f);
    speed_controller_set_target(MOTOR_RIGHT, 0.0f);
    printf("[F4] sequence done\r\n");

    for (;;) osDelay(1000);
}
