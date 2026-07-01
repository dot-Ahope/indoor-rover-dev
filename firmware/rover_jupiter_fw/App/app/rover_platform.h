/**
 * @file    rover_platform.h
 * @brief   차체·휠·엔코더 물리 파라미터 (양산기 이식 시 본 헤더만 교체).
 *
 * 출처: `Docs/rover.urdf`, `Docs/FIRMWARE_DEV_PLAN.md §2.2`
 */
#ifndef APP_APP_ROVER_PLATFORM_H
#define APP_APP_ROVER_PLATFORM_H

#include "motor_config.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ---- 휠 / 엔코더 (모델별) ----
 * 모터 타입에 따라 휠·피드백 파라미터가 다름. 양산 이식 시 이 블록만 조정. */
#if MOTOR_TYPE == MOTOR_TYPE_INTEGRATED_BLDC
  /* 통합 BLDC 모델: Ø40 mm 휠 + FG 단일펄스 피드백.
   * 캘리브레이션(2026-06-26): 우측 휠 3회전 실측 ≈ 380mm → 둘레 ≈126.7mm ≈ Ø40mm.
   * TODO(production): 더 긴 거리(≥1m)로 정밀 재캘리브레이션 권장. */
  #define WHEEL_RADIUS_M          0.020f           /* Ø40 mm */
  #define WHEEL_CIRCUMFERENCE_M   0.12566371f      /* π × 0.040 */
  /* FG 휠 1회전당 펄스 (실측 2026-06-26: 우측 10턴 1815 → 반올림 180).
   * 기어비 포함 값이라 정수 아님이 정상. */
  #define FG_PULSES_PER_REV       180u
  #define METERS_PER_COUNT        (WHEEL_CIRCUMFERENCE_M / (float)FG_PULSES_PER_REV)  /* ≈ 0.611 mm */
#else
  /* AM2861 dev 보드: Ø50 mm 휠 + 쿼드러처 엔코더 */
  #define WHEEL_RADIUS_M          0.025f           /* Ø50 mm (실측 2026-05-21) */
  #define WHEEL_CIRCUMFERENCE_M   0.1570796f       /* 2π × 0.025 */
  /* 출력축 기준 카운트/회전 (TI1+TI2 ×4 quadrature 가정). */
  #define ENCODER_CPR             1320u
  #define METERS_PER_COUNT        (WHEEL_CIRCUMFERENCE_M / (float)ENCODER_CPR)        /* ≈ 0.119 mm */
#endif

/* ---- 차체 (공통) ---- */
#define WHEEL_BASE_M              0.190f       /* 트랙 베이스 폭. TODO(production): 새 차체 실측 */

/* ---- 모터 / 운영 한계 (참조용) ---- */
#define MAX_LINEAR_SPEED_MPS      0.654f       /* 250 RPM 정격 무부하 추정 */

#ifdef __cplusplus
}
#endif

#endif /* APP_APP_ROVER_PLATFORM_H */
