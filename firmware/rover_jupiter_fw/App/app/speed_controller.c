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

/* 적분 클램프. BLDC 는 steady duty(0.3m/s≈45%) - deadzone(13%) ≈ 0.32 필요 → 상향.
 * ⚠ 모터 교체(2026-08-26, 56:1→1:90): 아래 steady duty·deadzone·게인 수치는 전부
 *   구모터(56:1) 실측 기준 → 새 모터로 재튜닝 필요. TODO(측정): F4 절차 재수행. */
#if MOTOR_TYPE == MOTOR_TYPE_INTEGRATED_BLDC
/* 1:90 모터 바닥 실주행(2026-08-26): 필요 duty 가 구모터보다 훨씬 높음(50mm/s 지령에
 * 70% 포화 관측). ff(0.13)+I 로 OUT_MAX(0.95)까지 도달 가능해야 함 → 0.85로 상향.
 * 0.55 클램프 시 duty 70% 에서 포화 → PID 개방루프화 → 좌우 개체차로 사행 발생했음. */
#define I_MAX          0.85f
#else
#define I_MAX          0.30f      /* AM2861 (F4 실측) */
#endif
/* duty 상한. 모터 타입별 분리:
 *   - 통합 BLDC: 컨트롤러가 자체 전류제한 → 0.98 (2026-08-26 상향, 정상 동작 확인).
 *     1.0(연속 HIGH, PWM 에지 소멸)은 드라이버 해석 미확인 → 실측 후에만 시도.
 *   - AM2861:    스톨 전류(2.3A) 보호로 0.80 유지 (CLAUDE.md 안전 요구). */
#if MOTOR_TYPE == MOTOR_TYPE_INTEGRATED_BLDC
#define OUT_MAX        0.98f
#else
#define OUT_MAX        0.80f
#endif
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
/* 2026-09-07 PWM 50Hz→20kHz 전환 후 재실측 (받침대 무부하, 폐루프 정착점):
 *   40mm/s→54%, 60→63%, 80→72%, 98%→117~120 (무부하 최고속). 50Hz 시절의 강한 비선형이 사라지고
 *   선형: duty ≈ 0.36 + 4.5·v. 절편 0.36 을 dz 로(50Hz 의 0.13 은 무효), 기동 duty 실측은 별도. */
static const float DEADZONE[MOTOR_COUNT] = { 0.34f, 0.34f };
/* 속도 feedforward (1:90 모터): 지령 즉시 정상상태 duty 근처를 인가해
 * 적분 wind-up 대기 제거 + 스톨 오탐 방지. 적분은 잔차만 보정.
 *
 * duty-속도 특성 (2026-08-26 받침대·바닥 실측 — **부하 무관**, 모터 내장 속도제어 추정):
 *   30mm/s→72%, 50→92%, 70→94%, 80→95%, 98%→115±5 (최고속).
 *   0~72% 완만 / 92~98% 가파름 — 강한 비선형이라 선형 KV 는 절충값.
 * KV=19(30mm/s 점 기준)는 tgt≥90mm/s 에서 과다 → 필요 적분 −0.88 이 I_MAX(0.85)
 *   초과 → duty 하한 97% 고착, 정착 실패 관측. → KV=12 로 하향:
 *   tgt 30 필요 I=+0.23 / 50 +0.19 / 70 −0.03 / 100 −0.36 — 전 구간 클램프 내.
 * 부족분은 적분이 채움 → Ki 3→6 상향으로 수렴 시간 보상.
 * 검증(2026-08-26 바닥): 50/70/90/100 모두 정착 ✓, L/R 이동거리 일치 ✓, 스톨 오탐 없음.
 *   단 지령 ≥110(포화)에선 duty 98% 고착 → 개방루프화 → L/R 5% 사행. V_MAX=100 근거. */
#define KV_DUTY_PER_MPS  4.5f   /* 2026-09-07 20kHz 실측 기울기 (50Hz: 12.0). 09-07 SUMMARY */
/* BLDC 1차 튜닝: 기존 4/5 는 초기 duty 슬램·진동 → 대폭 하향. (구모터 기준 주석:
 * steady 0.15→24% / 0.30→45%.) KV 도입 후 Kp 는 외란 보정용으로 유지.
 * Ki 6.0: KV 하향(19→12) 보상 — 잔차를 적분이 메우는 속도 확보 (2026-08-26). */
#define PID_KP_INIT   0.7f
#define PID_KI_INIT   6.0f
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
#if MOTOR_TYPE == MOTOR_TYPE_INTEGRATED_BLDC
        /* 속도 feedforward — 정상상태 duty 를 즉시 인가 (KV_DUTY_PER_MPS 주석 참조) */
        float duty = ff + KV_DUTY_PER_MPS * p->target_mps
                     + p->kp * err + p->integral + d_term;
#else
        float duty = ff + p->kp * err + p->integral + d_term;
#endif

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
