/**
 * @file    speed_controller.c
 * @brief   F4 PID 구현. 100 Hz 호출.
 */
#include "speed_controller.h"

#include <math.h>
#include "i_encoder.h"

#define CTRL_HZ        100u
#define CTRL_DT_S      (1.0f / (float)CTRL_HZ)

/* 적분 클램프 — F4 1차 실측에서 0.16 이 정상오차 못 없애서 0.30 으로 상향. */
#define I_MAX          0.30f
#define OUT_MAX        0.80f      /* driver 측 동일 캡 */
#define TARGET_THRESH  0.01f      /* m/s — 이하면 정지 명령으로 간주 */

/* Feedforward dead-zone — target 방향으로 항상 더함 (정지마찰 base offset).
 * PID 는 그 위에서 fine-tuning. F4 1차 실측 결과 "강제 jump" 방식에서 변경:
 *   강제 jump: PID < dz 면 dz 로 끌어올림 → 정상오차 해소 불가능
 *   feedforward: duty = sign(tgt)·dz + Kp·err + I → PID 가 ±보정 자유
 * F2 정지마찰 측정: LEFT ~30%, RIGHT ~55%. dz 는 그보다 약간 낮게 잡고
 * 부족분은 P+I 가 채우도록 함. */
static const float DEADZONE[MOTOR_COUNT] = { 0.20f, 0.50f };

typedef struct {
    /* tune */
    float kp, ki, kd;
    /* state */
    float target_mps;
    float integral;
    float prev_err;
    float last_duty;
} pid_t;

/* 초기 게인 — 양쪽 동일. RIGHT 비대칭은 dead-zone 으로 1차 보정.
 * 진동/오버슈트 보이면 게인 조정. */
static pid_t s_pid[MOTOR_COUNT] = {
    [MOTOR_LEFT]  = { .kp = 4.0f, .ki = 5.0f, .kd = 0.0f },
    [MOTOR_RIGHT] = { .kp = 4.0f, .ki = 5.0f, .kd = 0.0f },
};

static inline float clampf(float x, float lo, float hi)
{
    return x < lo ? lo : (x > hi ? hi : x);
}

void speed_controller_init(void)
{
    for (int i = 0; i < MOTOR_COUNT; i++) {
        s_pid[i].target_mps = 0.0f;
        s_pid[i].integral   = 0.0f;
        s_pid[i].prev_err   = 0.0f;
        s_pid[i].last_duty  = 0.0f;
    }
}

void speed_controller_reset(void)
{
    for (int i = 0; i < MOTOR_COUNT; i++) {
        s_pid[i].integral  = 0.0f;
        s_pid[i].prev_err  = 0.0f;
        s_pid[i].last_duty = 0.0f;
    }
}

void speed_controller_set_target(MotorChannel ch, float target_mps)
{
    if (ch >= MOTOR_COUNT) return;
    s_pid[ch].target_mps = target_mps;
}

float speed_controller_get_target(MotorChannel ch)
{
    if (ch >= MOTOR_COUNT) return 0.0f;
    return s_pid[ch].target_mps;
}

float speed_controller_get_duty(MotorChannel ch)
{
    if (ch >= MOTOR_COUNT) return 0.0f;
    return s_pid[ch].last_duty;
}

void speed_controller_update(void)
{
    for (int i = 0; i < MOTOR_COUNT; i++) {
        pid_t *p = &s_pid[i];

        const float actual = encoder_read_velocity_mps((EncoderChannel)i);
        const float err    = p->target_mps - actual;

        /* 정지 명령: 출력·적분 모두 강제 0 — windup·전류 누설 방지. */
        if (fabsf(p->target_mps) < TARGET_THRESH) {
            p->integral  = 0.0f;
            p->prev_err  = 0.0f;
            p->last_duty = 0.0f;
            motor_driver_set_duty((MotorChannel)i, 0.0f);
            continue;
        }

        /* P + I + D */
        p->integral = clampf(p->integral + p->ki * err * CTRL_DT_S, -I_MAX, I_MAX);
        const float d_term = (p->kd > 0.0f)
            ? (p->kd * (err - p->prev_err) / CTRL_DT_S)
            : 0.0f;
        p->prev_err = err;

        /* Feedforward dead-zone: target 방향으로 base offset 항상 추가.
         * PID 출력이 ±보정으로 작동 → 정상오차 해소 가능. */
        const float ff = (p->target_mps > 0.0f) ? +DEADZONE[i] : -DEADZONE[i];
        float duty = ff + p->kp * err + p->integral + d_term;

        duty = clampf(duty, -OUT_MAX, OUT_MAX);

        p->last_duty = duty;
        motor_driver_set_duty((MotorChannel)i, duty);
    }
}
