/**
 * @file    rover_platform.h
 * @brief   차체·휠·엔코더 물리 파라미터 (양산기 이식 시 본 헤더만 교체).
 *
 * 출처: `Docs/rover.urdf`, `Docs/FIRMWARE_DEV_PLAN.md §2.2`
 */
#ifndef APP_APP_ROVER_PLATFORM_H
#define APP_APP_ROVER_PLATFORM_H

#ifdef __cplusplus
extern "C" {
#endif

/* ---- 휠 / 차체 ---- */
#define WHEEL_RADIUS_M            0.025f       /* Ø50 mm (실측 2026-05-21) */
#define WHEEL_CIRCUMFERENCE_M     0.1570796f   /* 2π × 0.025 */
#define WHEEL_BASE_M              0.190f       /* 트랙 베이스 폭 (좌·우 휠 중심 간) */

/* ---- 엔코더 ---- */
/* 출력축 기준 카운트/회전. STM32 TIM 엔코더 모드 TI1+TI2 (×4 quadrature 가정).
 * F3 단계에서 1회전 실측으로 검증할 것 — 만약 어긋나면 1320×4=5280 으로 조정. */
#define ENCODER_CPR               1320u

/* 카운트당 직선거리 ≈ 0.119 mm */
#define METERS_PER_COUNT          (WHEEL_CIRCUMFERENCE_M / (float)ENCODER_CPR)

/* ---- 모터 / 운영 한계 (참조용) ---- */
#define MAX_LINEAR_SPEED_MPS      0.654f       /* 250 RPM 정격 무부하 추정 */

#ifdef __cplusplus
}
#endif

#endif /* APP_APP_ROVER_PLATFORM_H */
