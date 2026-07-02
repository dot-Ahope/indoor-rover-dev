/**
 * @file    f4_pid_test.c
 * @brief   F4 속도 PID step response 시퀀스 (튜닝용). 휠 받침대 전제.
 *
 * 각 스텝마다 100ms(10Hz) 간격으로 목표 대비 실제속도·duty 를 UART5 로 로깅 →
 * rise time / 오버슈트 / 정상오차 / 진동을 관찰해 게인 튜닝.
 *
 * 통합 BLDC 튜닝: 전진 위주 (좌측 모터 후진 HW 이슈 → 좌 reverse 제외).
 * control task(speed_controller) 와 함께 활성해야 함 (F4 는 target 만 설정).
 */
#include "f4_pid_test.h"

#include <stdio.h>
#include "cmsis_os.h"

#include "speed_controller.h"
#include "safety_monitor.h"
#include "i_encoder.h"

/* 목표 설정 후 duration 동안 10Hz 로 실제속도·duty 로깅. */
static void seg(const char *label, float l_mps, float r_mps, uint32_t ms)
{
    printf("[F4] === %s  tgt L=%+d R=%+d mm/s ===\r\n",
           label, (int)(l_mps * 1000.0f), (int)(r_mps * 1000.0f));
    speed_controller_set_target(MOTOR_LEFT,  l_mps);
    speed_controller_set_target(MOTOR_RIGHT, r_mps);

    for (uint32_t t = 0; t < ms; t += 100u) {
        osDelay(100);
        const int vl = (int)(encoder_read_velocity_mps(ENC_LEFT)  * 1000.0f);
        const int vr = (int)(encoder_read_velocity_mps(ENC_RIGHT) * 1000.0f);
        const int dl = (int)(speed_controller_get_duty(MOTOR_LEFT)  * 100.0f);
        const int dr = (int)(speed_controller_get_duty(MOTOR_RIGHT) * 100.0f);
        printf("[F4] +%4lums  L v=%+4d d=%+3d%%   R v=%+4d d=%+3d%%\r\n",
               (unsigned long)(t + 100u), vl, dl, vr, dr);
    }
}

void f4_pid_test_run(void *arg)
{
    (void)arg;

    printf("[F4] start in 3s — 휠 받침대 상태 확인\r\n");
    osDelay(3000);
    printf("[F4] BLDC step response (전진). 좌측은 모터 장착 시 관찰.\r\n");

    /* RIGHT 단독 step (0.7/3.0 게인으로 튜닝 완료 — 회귀 확인용) */
    seg("R 0.10", 0.0f, +0.10f, 4000);
    seg("R stop", 0.0f,  0.0f,  1500);
    seg("R 0.20", 0.0f, +0.20f, 4000);
    seg("R stop", 0.0f,  0.0f,  1500);
    seg("R 0.30", 0.0f, +0.30f, 4000);
    seg("R stop", 0.0f,  0.0f,  1500);

    /* LEFT 단독 step (전진만 — 좌측 후진 HW 이슈). 모터 미장착 시 v=0. */
    seg("L 0.10", +0.10f, 0.0f, 4000);
    seg("L stop",  0.0f,  0.0f, 1500);
    seg("L 0.20", +0.20f, 0.0f, 4000);
    seg("L stop",  0.0f,  0.0f, 1500);

    printf("[F4] sequence done — motors stopped\r\n");
    speed_controller_set_target(MOTOR_LEFT,  0.0f);
    speed_controller_set_target(MOTOR_RIGHT, 0.0f);

    for (;;) osDelay(1000);
}
