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
  /* FG 휠 1회전당 펄스 — 전원구동 실측값(FG는 구동 중에만 펄스 발생, 손 회전 불가).
   * 실측 2026-07-08(교체 모터 56:1): 20턴 → L=4280(214.0), R=4305(215.25) → 평균 215.
   *   L/R 0.6% 차이는 회전수 카운팅 오차 범위 → 단일값 사용. 필요 시 채널별 분리 가능.
   * 참고: 기어비는 30:1→56:1 이지만 FG펄스/모터회전이 모터마다 달라(옛 6 → 새 ~3.8)
   *   기어비 스케일로는 예측 불가. 반드시 실측. 옛 180(0.611mm)과 스케일 유사한 건 우연.
   * TODO(production): 저속 재측정으로 펄스 유실 없음 확인 권장(아래 주의 참조). */
  #define FG_PULSES_PER_REV       215u             /* 실측 2026-07-08 (교체 모터 56:1) */
  #define METERS_PER_COUNT        (WHEEL_CIRCUMFERENCE_M / (float)FG_PULSES_PER_REV)  /* ≈ 0.585 mm */
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

/* ---- 모터 / 운영 한계 ---- */
/* /cmd_vel 명령 saturation(microros_task.c V_MAX_MPS)에 사용됨 → 실제 도달가능 최고속 근처여야
 * windup 없음. 모터 교체(2026-07-08)로 기어비 30:1→56:1 → 출력속도 30/56 배로 감소.
 * TODO(production): 통합 BLDC 최고속은 실측된 적 없음(기존 0.654 는 AM2861 Ø50/250RPM 유물값).
 *   개방루프 램프(bldc_ramp_test)로 95% duty 정상속도 실측 후 확정할 것. 아래는 보수적 임시값. */
#define MAX_LINEAR_SPEED_MPS      0.350f       /* 임시 추정 (실측 필요) */

#ifdef __cplusplus
}
#endif

#endif /* APP_APP_ROVER_PLATFORM_H */
