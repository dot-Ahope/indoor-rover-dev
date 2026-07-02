/**
 * @file    speed_controller.c
 * @brief   F4 PID 구현. 100 Hz 호출.
 */
#include "speed_controller.h"

#include <math.h>
#include <stdbool.h>
#include "i_encoder.h"
#include "motor_config.h"   /* MOTOR_TYPE — 게인/deadzone 모델별 분리 */

#define CTRL_HZ        100u
#define CTRL_DT_S      (1.0f / (float)CTRL_HZ)

/* 적분 클램프. BLDC 는 steady duty(0.3m/s≈45%) - deadzone(13%) ≈ 0.32 필요 → 상향. */
#if MOTOR_TYPE == MOTOR_TYPE_INTEGRATED_BLDC
#define I_MAX          0.55f
#else
#define I_MAX          0.30f      /* AM2861 (F4 실측) */
#endif
#define OUT_MAX        0.80f      /* driver 측 동일 캡 */
#define TARGET_THRESH  0.01f      /* m/s — 이하면 정지 명령으로 간주 */

/* 정지 명령 시 target_mps 를 0 쪽으로 감속시키는 최대 가속도.
 * 예: 0.2 m/s 에서 SPACE → 100ms 만에 0 도달. PID 가 ramp 추종하며 능동 제동.
 * 너무 크면 coast 와 동일해지고 (감속 한 tick 안에 끝남), 너무 작으면 stop 지연. */
#define STOP_RAMP_MPS2  4.0f

/* Feedforward dead-zone — target 방향으로 항상 더함 (정지마찰 base offset).
 * PID 는 그 위에서 fine-tuning. duty = sign(tgt)·dz + Kp·err + I.
 * 모델별 분리:
 *   - 통합 BLDC: 최소 기동 duty 실측 ~15%(좌·우 대칭) → dz 살짝 아래 0.13.
 *   - AM2861:    정지마찰 실측 LEFT ~30% / RIGHT ~55% → 비대칭 0.20/0.50. */
#if MOTOR_TYPE == MOTOR_TYPE_INTEGRATED_BLDC
static const float DEADZONE[MOTOR_COUNT] = { 0.13f, 0.13f };
/* BLDC 1차 튜닝: 기존 4/5 는 초기 duty 슬램·진동 → 대폭 하향. steady duty 실측
 * 0.15→24% / 0.30→45% 기준. ff(0.13)+Kp·err 초기값이 steady 근처가 되도록 Kp≈0.7. */
#define PID_KP_INIT   0.7f
#define PID_KI_INIT   3.0f
#else
static const float DEADZONE[MOTOR_COUNT] = { 0.20f, 0.50f };
#define PID_KP_INIT   4.0f
#define PID_KI_INIT   5.0f
#endif

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
    [MOTOR_LEFT]  = { .kp = PID_KP_INIT, .ki = PID_KI_INIT, .kd = 0.0f },
    [MOTOR_RIGHT] = { .kp = PID_KP_INIT, .ki = PID_KI_INIT, .kd = 0.0f },
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

#if MOTOR_TYPE == MOTOR_TYPE_INTEGRATED_BLDC
        /* 통합 BLDC: 방향선 액추에이터 → 역 duty(제동)가 방향/FG부호 thrash 유발.
         * 출력을 target 방향 부호로 제한 (오버슈트 감속은 coast). */
        if (p->target_mps > 0.0f && duty < 0.0f) duty = 0.0f;
        if (p->target_mps < 0.0f && duty > 0.0f) duty = 0.0f;
#endif

        p->last_duty = duty;
        motor_driver_set_duty((MotorChannel)i, duty);
    }
}
