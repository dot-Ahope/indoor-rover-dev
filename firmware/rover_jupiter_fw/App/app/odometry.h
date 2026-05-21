/**
 * @file    odometry.h
 * @brief   F6 — 차동구동 휠 오도메트리.
 *
 * 좌·우 휠 선속도 (encoder_read_velocity_mps) 를 적분하여
 * 차체 pose (x, y, yaw) 추정. odom 프레임 기준.
 *
 * 100 Hz 주기 호출 가정 (control task 안). dt 는 driver 내부 상수.
 * Pose 는 차체 시작 시점 = 원점 / yaw=0 으로 가정.
 */
#ifndef APP_APP_ODOMETRY_H
#define APP_APP_ODOMETRY_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    float    x;       /* m, odom 프레임 */
    float    y;       /* m */
    float    yaw;     /* rad, [-π, π] wrap */
    float    v;       /* m/s, 차체 선속도 */
    float    w;       /* rad/s, 차체 각속도 (+ = ccw) */
    uint32_t ts_ms;   /* HAL_GetTick() 시각 */
} OdomState;

void odometry_init(void);
void odometry_reset(void);

/** 주기적 호출 (100 Hz 권장). encoder velocity 읽어 pose 적분. */
void odometry_update(void);

/** 최신 상태 스냅샷 복사. */
void odometry_get(OdomState *out);

#ifdef __cplusplus
}
#endif

#endif
