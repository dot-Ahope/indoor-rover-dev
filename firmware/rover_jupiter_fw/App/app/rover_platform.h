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
  /* 통합 BLDC 모델: FG 단일펄스 피드백. 둘레는 **유효 구름 둘레**(트랙 두께 포함).
   * 캘리브레이션(2026-08-26, 바닥 직진 실주행): 2차 0.92m/3088 + 3차 2.80m/9412
   *   합산 3720mm ÷ 12500카운트 = 0.2976mm/카운트 → 유효 둘레 161.3mm (Ø51).
   *   (2·3차는 0.15% 내 일치. 1차 920/2997=0.307 은 +3% 이상치 → 기각.
   *    구값 Ø40(126.7mm)은 스프로킷 기준 → 과소였음.)
   * 검증: 3차 주행 표시 2846mm vs 실측 2800mm → 본 값 적용 시 ±0.2% 일치. */
  #define WHEEL_RADIUS_M          0.02567f         /* 유효 Ø51 mm (실측 역산) */
  #define WHEEL_CIRCUMFERENCE_M   0.16130f         /* 3.720m / 12500 × 542 (실측 합산) */
  /* FG 휠 1회전당 펄스 — 전원구동 실측값(FG는 구동 중에만 펄스 발생, 손 회전 불가).
   * 모터 교체(2026-08-26): 56:1 → 1:90 (무부하 45rpm/정격 37rpm, 12V 7W).
   * 실측 2026-08-26(1:90 모터): 전원구동 20턴 → L≈R≈10830 → 541.5/회전 → 542 사용.
   *   해석: 6 FG/모터회전 × 실기어비 90.25 = 541.5 (명목 "1:90"의 실제비는 90.25 추정).
   *   1차 측정 7857(=392.85/회전)은 좌·우 재측정과 불일치 → 턴수 미스카운트로 기각.
   * 실측 이력(구모터 56:1, 2026-07-08): 20턴 → L=214.0, R=215.25 → 215 사용했음.
   * TODO(production): 저속 재측정으로 펄스 유실 없음 확인 권장(아래 주의 참조). */
  #define FG_PULSES_PER_REV       542u             /* 실측 2026-08-26 (1:90 모터, L/R 20턴, 541.5 반올림) */
  #define METERS_PER_COUNT        (WHEEL_CIRCUMFERENCE_M / (float)FG_PULSES_PER_REV)  /* ≈ 0.298 mm */
#else
  /* AM2861 dev 보드: Ø50 mm 휠 + 쿼드러처 엔코더 */
  #define WHEEL_RADIUS_M          0.025f           /* Ø50 mm (실측 2026-05-21) */
  #define WHEEL_CIRCUMFERENCE_M   0.1570796f       /* 2π × 0.025 */
  /* 출력축 기준 카운트/회전 (TI1+TI2 ×4 quadrature 가정). */
  #define ENCODER_CPR             1320u
  #define METERS_PER_COUNT        (WHEEL_CIRCUMFERENCE_M / (float)ENCODER_CPR)        /* ≈ 0.119 mm */
#endif

/* ---- 차체 (공통) ---- */
/* WT-600 트랙 게이지(중심 간) = 0.245 m — 실측 확정 2026-08-27:
 * 바깥끝285−트랙40=245 / 안쪽끝205+40=245 / 중심간 직접 ~248 (3법 수렴, 트랙폭 40 캘리퍼 확인).
 * ※ 리스팅 전폭 330mm는 트랙 가이드 포함 값 — 게이지 계산에 쓰면 안 됨 (0.29 계산치 폐기).
 * 구값 0.190은 구형 소형 차체 — yaw 1.29배 과대 원인이었음.
 * TODO(production): 회전보정(제자리 360°)으로 유효 게이지 최종 확정. 변경 시 슬립 재캘리브레이션. */
#define WHEEL_BASE_M              0.245f       /* 트랙 게이지 (실측 2026-08-27) */

/* ---- 모터 / 운영 한계 ---- */
/* /cmd_vel 명령 saturation(microros_task.c V_MAX_MPS)에 사용됨 → 실제 도달가능 최고속 근처여야
 * windup 없음. 모터 교체(2026-08-26): 56:1 → 1:90 (무부하 45rpm, 정격 37rpm).
 * 실측(2026-08-26, 받침대·바닥 동일): duty 98%(OUT_MAX)에서 ≈0.115 m/s.
 *   duty-속도 곡선이 부하 무관(내장 속도제어 추정) → 무부하 이론치 0.121 근접.
 *   여유 두고 0.100. (구값 0.070 은 OUT_MAX 0.95 시절 95% 정착점 0.080 기반이었음)
 * TODO(측정): 장시간 지속 주행으로 0.100 유지 가능(전압 처짐·발열) 확인. */
#define MAX_LINEAR_SPEED_MPS      0.100f       /* duty 98% 실측 0.115 에 여유 (실측 기반) */

/* 기동 데드밴드 보상 (2026-09-02, Nav2 실측 — Docs/debug_log/2026-09-02):
 *  |휠속도 명령| 이 최소 기동치 미만이면 모터가 반응하지 않음(정지마찰·저속 제어한계).
 *  실측: ω=0.05 rad/s(휠 ±6 mm/s) 명령 68초간 무반응 → 상위 제어기(Nav2 RPP/MPPI)가
 *  측정속도 0 을 보고 미세 명령을 반복하며 영구 정체(데드락).
 *  보상 규칙: |v| < EPS 는 의도된 정지로 보고 0 유지, EPS ≤ |v| < MIN 은 MIN 으로 승격(부호 보존).
 *  부작용(곡률 소폭 증가)은 상위 피드백 루프가 흡수.
 *  TODO(측정): 플래시 후 실제 최소 기동 휠속도를 실측해 MIN 조정 (권장 탐색범위 0.015~0.030). */
#define MIN_WHEEL_SPEED_MPS       0.020f       /* 최소 기동 휠속도 — 미만 비영 명령을 이 값으로 승격 */
#define WHEEL_SPEED_EPS_MPS       0.003f       /* 이하는 사실상 0(정지 의도)으로 간주 */

#ifdef __cplusplus
}
#endif

#endif /* APP_APP_ROVER_PLATFORM_H */
