/**
 * @file    safety_monitor.c
 * @brief   F4 스톨 감지 구현.
 */
#include "safety_monitor.h"

#include <math.h>
#include <stdint.h>

#include "stm32f4xx_hal.h"
#include "i_encoder.h"
#include "speed_controller.h"

#define CTRL_HZ            100u
/* 1:90 모터 재튜닝(2026-08-26): 기동이 느려(정지→20mm/s 에 300ms+) 200ms 창에서
 * 고속 지령 시 오탐 발생했음(b 100 즉시 FAULT). 창 600ms 로 확장.
 * 진짜 구속 시엔 드라이버 내장 3A 차단이 1차 방어 → 600ms 지연 허용 가능. */
#define STALL_WIN_SAMPLES  60u    /* 600 ms */

/* 구값 50mm/s 는 V_MAX 보다 커서 정상 운용에서 감지가 영영 비활성이었음. */
/* 스톨 판정 기준 변경 (2026-09-03): 지령 속도 → 실제 인가 duty(노력) 기준.
 * 문제: 데드밴드 승격(0.020)·선회 안쪽 휠(0.02~0.03 m/s)이 부하로 순간 정지하면 옛 기준(지령>0.015)은
 *   즉시 구속으로 오판 → Nav2 자율주행 중 래치 실발생(RPP/MPPI 각 1회, 접촉 없이).
 * 왜 duty 기준인가: 정지한 휠에는 PID 적분(I_MAX 0.85)이 쌓여 duty 가 계속 오른다. 그래도 안 움직이면
 *   "마찰 못 이김"이 아니라 진짜 구속이다. 즉 duty 는 지령보다 구속 여부를 잘 구분한다.
 *   지령 문턱만 올리는 안(0.040)은 그 미만 지령의 진짜 구속을 무한 방치 — 모터 드라이버의 과전류
 *   보호 사양은 확인된 것이 없어(CHR-GM37-BLDC3650, 출처 불명 '3A' 삭제) 펌웨어가 반드시 잡아야 함.
 * STALL_DUTY_THRESH 0.60 근거: 승격값 0.020 의 초기 duty ≈ dz 0.13 + KV 12×0.02 = 0.37 이며 이 값으로
 *   바닥 기동이 실측 확인됨. 0.60 에서도 무이동이면 정상 부하 범위 밖. (튜닝 가능값) */
#define V_TARGET_THRESH    0.010f /* 정지 지령(speed_controller TARGET_THRESH) 제외용 */
#define STALL_DUTY_THRESH  0.60f  /* |duty| 이상 인가 중 무이동이면 stall 의심 */

/* 스톨 정책 (2026-09-03): 무조건 래치 → 일시 정지 후 자동 복구, 재발 시 하드 래치.
 * ROS 측에 fault 해제 수단이 없어 옛 정책은 자율주행을 회복 불능으로 만들었음. */
#define STALL_HOLD_MS         1500u  /* 스톨 후 강제 정지 유지 → 이후 자동 재무장 */
#define STALL_LATCH_COUNT     3u     /* 이 횟수가 */
#define STALL_LATCH_WINDOW_MS 10000u /* 이 시간 내 재발하면 하드 래치(clear/리셋 필요) */
/* 판정을 순시속도→창 누적이동거리로 변경(2026-08-26): FG 속도 추정은 펄스 1개에도
 * ~30mm/s 스파이크가 떠 "연속 저속" 카운터가 리셋됨 → 구속 상태서도 미검출됐음.
 * 600ms 창 동안 3mm 미만 이동이면 구속. (정상 최저속 15mm/s → 창당 9mm ≫ 3mm) */
#define STALL_DIST_M       0.003f /* 창 동안 이동 < 3mm = 구속 */

#define CMDVEL_TIMEOUT_MS  500u   /* §7 통신 watchdog — 500ms 미수신 시 정지 */

typedef struct {
    uint16_t stall_counter;
    float    win_start_dist;  /* 감지창 시작 시점 누적거리 (m) */
    bool     stalled;
} mon_t;

static mon_t s_mon[MOTOR_COUNT];
static bool  s_fault;                 /* 스톨 정지 중 (일시 또는 래치) */
static bool  s_latched;               /* 하드 래치 — clear('c')/리셋 전까지 유지 */
static uint32_t s_fault_since_ms;
static uint32_t s_stall_times[STALL_LATCH_COUNT];
static uint8_t  s_stall_idx, s_stall_fill;
static volatile uint32_t s_last_cmdvel_ms = 0;
static volatile bool     s_cmdvel_ever_received = false;
static bool s_cmdvel_timeout = false;

void safety_monitor_init(void)
{
    for (int i = 0; i < MOTOR_COUNT; i++) {
        s_mon[i].stall_counter = 0;
        s_mon[i].stalled       = false;
    }
    s_fault = false;
    s_latched = false;
    s_fault_since_ms = 0;
    s_stall_idx = 0; s_stall_fill = 0;
    s_last_cmdvel_ms = 0;
    s_cmdvel_ever_received = false;
    s_cmdvel_timeout = false;
}

void safety_monitor_cmdvel_received(void)
{
    s_last_cmdvel_ms = HAL_GetTick();
    s_cmdvel_ever_received = true;
    s_cmdvel_timeout = false;
}

bool safety_monitor_cmdvel_timeout(void)
{
    return s_cmdvel_timeout;
}

void safety_monitor_update(void)
{
    /* cmd_vel watchdog — fault 와 무관하게 항상 평가.
     * cmd_vel 한 번도 안 받으면 timeout 비활성 (boot 초기 상태). */
    if (s_cmdvel_ever_received) {
        const uint32_t since = HAL_GetTick() - s_last_cmdvel_ms;
        if (since > CMDVEL_TIMEOUT_MS) {
            if (!s_cmdvel_timeout) {
                /* 진입 transition — 모터 정지, 적분 reset, fault 표시 X (latch 안 함). */
                speed_controller_set_target(MOTOR_LEFT,  0.0f);
                speed_controller_set_target(MOTOR_RIGHT, 0.0f);
                speed_controller_reset();
                motor_driver_stop_all();
            }
            s_cmdvel_timeout = true;
        } else {
            s_cmdvel_timeout = false;
        }
    }

    if (s_fault) {
        /* 스톨 정지 유지 — 신규 지령 차단. (2026-08-26: return 만 하던 버그 수정으로 강제 정지 유지)
         * 2026-09-03: 일시 정지 STALL_HOLD_MS 후 자동 재무장. 하드 래치면 clear('c')/리셋 전까지 유지. */
        speed_controller_reset();
        motor_driver_stop_all();
        if (!s_latched && (HAL_GetTick() - s_fault_since_ms) >= STALL_HOLD_MS) {
            for (int i = 0; i < MOTOR_COUNT; i++) {
                s_mon[i].stall_counter = 0;
                s_mon[i].stalled       = false;
            }
            s_fault = false;   /* 재무장 — 다음 cmd_vel 부터 구동 재개 */
        }
        return;
    }

    bool any_stall = false;
    for (int i = 0; i < MOTOR_COUNT; i++) {
        const float tgt  = speed_controller_get_target((MotorChannel)i);
        const float duty = speed_controller_get_duty((MotorChannel)i);
        const float dist = encoder_read_distance_m((EncoderChannel)i);

        if (fabsf(tgt) > V_TARGET_THRESH && fabsf(duty) >= STALL_DUTY_THRESH) {
            if (s_mon[i].stall_counter == 0u) {
                s_mon[i].win_start_dist = dist;   /* 감지창 시작 */
            }
            if (++s_mon[i].stall_counter >= STALL_WIN_SAMPLES) {
                if (fabsf(dist - s_mon[i].win_start_dist) < STALL_DIST_M) {
                    s_mon[i].stalled = true;      /* 창 내 이동 3mm 미만 = 구속 */
                    any_stall = true;
                } else {
                    s_mon[i].stall_counter = 0;   /* 정상 이동 — 창 재시작 */
                }
            }
            /* 주의: 창 진행 중 encoder_reset(CLI 'z') 시 기준거리가 어긋나
             * 1회 오판 가능 — 정지 상태에서만 z 사용 (현행 절차와 동일). */
        } else {
            s_mon[i].stall_counter = 0;
            s_mon[i].stalled = false;
        }
    }

    if (any_stall) {
        const uint32_t now = HAL_GetTick();
        s_fault = true;
        s_fault_since_ms = now;
        /* 재발 판정: 링버퍼의 가장 오래된 기록이 WINDOW 내면 COUNT 회 재발 → 하드 래치 */
        s_stall_times[s_stall_idx] = now;
        s_stall_idx = (uint8_t)((s_stall_idx + 1u) % STALL_LATCH_COUNT);
        if (s_stall_fill < STALL_LATCH_COUNT) s_stall_fill++;
        if (s_stall_fill >= STALL_LATCH_COUNT &&
            (now - s_stall_times[s_stall_idx]) <= STALL_LATCH_WINDOW_MS) {
            s_latched = true;
        }
        speed_controller_set_target(MOTOR_LEFT,  0.0f);
        speed_controller_set_target(MOTOR_RIGHT, 0.0f);
        speed_controller_reset();
        motor_driver_stop_all();
    }
}

bool safety_monitor_is_stalled(MotorChannel ch)
{
    if (ch >= MOTOR_COUNT) return false;
    return s_mon[ch].stalled;
}

bool safety_monitor_has_fault(void)
{
    return s_fault;
}

bool safety_monitor_is_latched(void)
{
    return s_latched;
}

void safety_monitor_clear(void)
{
    safety_monitor_init();
    speed_controller_reset();
}
