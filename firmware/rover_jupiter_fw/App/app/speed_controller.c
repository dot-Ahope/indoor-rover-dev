/**
 * @file    speed_controller.c
 * @brief   F4 PID 구현. 100 Hz 호출.
 */
#include "speed_controller.h"

#include <math.h>
#include <stdbool.h>
#include "i_encoder.h"

#define CTRL_HZ        100u
#define CTRL_DT_S      (1.0f / (float)CTRL_HZ)

/* 적분 클램프 — F4 1차 실측에서 0.16 이 정상오차 못 없애서 0.30 으로 상향. */
#define I_MAX          0.30f
#define OUT_MAX        0.80f      /* driver 측 동일 캡 */
#define TARGET_THRESH  0.01f      /* m/s — 이하면 정지 명령으로 간주 */

/* 정지 명령 시 target_mps 를 0 쪽으로 감속시키는 최대 가속도.
 * 예: 0.2 m/s 에서 SPACE → 100ms 만에 0 도달. PID 가 ramp 추종하며 능동 제동.
 * 너무 크면 coast 와 동일해지고 (감속 한 tick 안에 끝남), 너무 작으면 stop 지연. */
#define STOP_RAMP_MPS2  4.0f

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
    bool  stop_ramp;      /* true 면 update() 가 target_mps 를 0 쪽으로 감속 */
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
        s_pid[i].stop_ramp  = false;
        s_pid[i].integral   = 0.0f;
        s_pid[i].prev_err   = 0.0f;
        s_pid[i].last_duty  = 0.0f;
    }
}

void speed_controller_reset(void)
{
    /* fault / watchdog 진입에서 호출 — target 과 ramp 상태도 청소해야
     * 후속 PID tick 이 옛 target 으로 모터를 다시 깨우지 않음.
     * motor_driver_stop_all() 와 짝지어 호출 가정. */
    for (int i = 0; i < MOTOR_COUNT; i++) {
        s_pid[i].target_mps = 0.0f;
        s_pid[i].stop_ramp  = false;
        s_pid[i].integral   = 0.0f;
        s_pid[i].prev_err   = 0.0f;
        s_pid[i].last_duty  = 0.0f;
    }
}

void speed_controller_set_target(MotorChannel ch, float target_mps)
{
    if (ch >= MOTOR_COUNT) return;
    /* 정지 명령: target_mps 즉시 0 으로 두지 않고 ramp 모드 진입.
     * PID 가 STOP_RAMP_MPS2 감속을 추종하며 능동 제동, ramp 종료 후 coast. */
    if (fabsf(target_mps) < TARGET_THRESH) {
        s_pid[ch].stop_ramp = true;
        /* target_mps 는 현재값 유지 — update() 가 한 tick 단위로 감속 */
    } else {
        s_pid[ch].target_mps = target_mps;
        s_pid[ch].stop_ramp  = false;
    }
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

        /* 정지 ramp: target_mps 를 0 쪽으로 한 tick 분만큼 끌어내림.
         * PID 가 이 ramp 를 추종해서 능동 제동 (역 duty 인가). */
        if (p->stop_ramp) {
            const float step = STOP_RAMP_MPS2 * CTRL_DT_S;
            if (p->target_mps >  step)        p->target_mps -= step;
            else if (p->target_mps < -step)   p->target_mps += step;
            else {
                p->target_mps = 0.0f;
                p->stop_ramp  = false;        /* 도달 — coast 단계로 인계 */
            }
        }

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
