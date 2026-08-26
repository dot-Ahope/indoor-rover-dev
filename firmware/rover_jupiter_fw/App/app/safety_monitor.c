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
#define V_TARGET_THRESH    0.015f /* 15 mm/s — 이상 명령 시에만 stall 의심 */
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
static bool  s_fault;
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
        /* stall latch 중 강제 정지 유지 — clear('c') 전까지 신규 지령 차단.
         * (구현 버그 수정 2026-08-26: 이전엔 return 만 해서 latch 후 재지령이
         *  보호를 우회해 구동됐음 → 스톨 보호 무력화) */
        speed_controller_reset();
        motor_driver_stop_all();
        return;
    }

    bool any_stall = false;
    for (int i = 0; i < MOTOR_COUNT; i++) {
        const float tgt  = speed_controller_get_target((MotorChannel)i);
        const float dist = encoder_read_distance_m((EncoderChannel)i);

        if (fabsf(tgt) > V_TARGET_THRESH) {
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
        s_fault = true;
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

void safety_monitor_clear(void)
{
    safety_monitor_init();
    speed_controller_reset();
}
