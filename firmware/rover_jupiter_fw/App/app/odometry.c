/**
 * @file    odometry.c
 * @brief   F6 오도메트리 구현 — Euler 적분.
 *
 * 차동구동 정기구학:
 *   v = (v_l + v_r) / 2          [m/s]
 *   ω = (v_r − v_l) / B          [rad/s]   (B = WHEEL_BASE_M)
 * Pose 적분 (Euler 1차):
 *   x   += v · cos(yaw) · dt
 *   y   += v · sin(yaw) · dt
 *   yaw += ω · dt
 *
 * 미세개선 후보: 곡선 추적 보정 (mid-point yaw, runge-kutta 등) — F8 이후.
 */
#include "odometry.h"

#include <math.h>
#include <string.h>

#include "stm32f4xx_hal.h"
#include "i_encoder.h"
#include "rover_platform.h"

#define ODOM_HZ          100u
#define ODOM_DT_S        (1.0f / (float)ODOM_HZ)
#define INV_WHEEL_BASE   (1.0f / WHEEL_BASE_M)   /* = 4.082... (WT-600 실측 0.245m, 2026-08-27) */
#define TWO_PI           6.28318530718f
#define PI               3.14159265359f

static OdomState s_o;

void odometry_init(void) { memset(&s_o, 0, sizeof(s_o)); }
void odometry_reset(void) { memset(&s_o, 0, sizeof(s_o)); }

void odometry_update(void)
{
    const float v_l = encoder_read_velocity_mps(ENC_LEFT);
    const float v_r = encoder_read_velocity_mps(ENC_RIGHT);

    const float v = 0.5f * (v_l + v_r);
    const float w = (v_r - v_l) * INV_WHEEL_BASE;

    /* Euler 1차 — yaw 변화가 작을 때 충분. */
    s_o.x   += v * cosf(s_o.yaw) * ODOM_DT_S;
    s_o.y   += v * sinf(s_o.yaw) * ODOM_DT_S;
    s_o.yaw += w * ODOM_DT_S;

    /* yaw [-π, π] wrap. */
    if (s_o.yaw >  PI) s_o.yaw -= TWO_PI;
    else if (s_o.yaw < -PI) s_o.yaw += TWO_PI;

    s_o.v     = v;
    s_o.w     = w;
    s_o.ts_ms = HAL_GetTick();
}

void odometry_get(OdomState *out)
{
    if (!out) return;
    /* 단순 복사 — control task (100Hz) 작성, micro-ROS task (50Hz) 읽음.
     * 필드 단위 torn read 가능하나 odom 모니터링/Nav2 용도엔 허용 범위. */
    *out = s_o;
}
