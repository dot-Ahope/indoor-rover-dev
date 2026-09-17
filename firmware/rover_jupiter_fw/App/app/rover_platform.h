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
  /* 2026-09-07 재캘리브레이션 — 08-26 값(Ø51 / 0.16130)은 28.7% 과대였음.
   * 근거: 라이다 전방벽 변위를 GT 로 3회 측정 (원시 휠오도 / 실제이동):
   *   전진 0.06×25s → 1.2971,  후진 0.06×25s → 1.2754,  전진 0.10×12s → 1.2885  (평균 1.2870, 속도 무관)
   *   09-02·09-03 줄자 측정 1.2786 과도 일치 → 계통 스케일 오차 확정(트랙 슬립 아님).
   * 0.16130 / 1.2870 = 0.12533 m. 나사 Ø40 공칭 둘레 π×0.040 = 0.12566 과 0.3% 이내 일치
   *   → 이관 계획 §3.3 "휠 상수(Ø40mm) 유지"가 옳았고, 08-26 의 3.720m 실측 합산이 잘못이었음.
   * 파급: MAX_LINEAR_SPEED·KV_DUTY_PER_MPS·MIN_WHEEL_SPEED 및 Jetson VX_SCALE(0.783→1.0)·
   *   SLIP_PTS(0.46→0.592) 를 **동시에** 갱신해야 함 (한쪽만 바꾸면 이중 보정). */
  #define WHEEL_RADIUS_M          0.01995f         /* 유효 Ø39.9 mm (2026-09-07 라이다 GT 역산) */
  #define WHEEL_CIRCUMFERENCE_M   0.12533f         /* 0.16130 / 1.2870 (라이다 GT 3회 평균) */
  /* FG 휠 1회전당 펄스 — 전원구동 실측값(FG는 구동 중에만 펄스 발생, 손 회전 불가).
   * 모터 교체(2026-08-26): 56:1 → 1:90 (무부하 45rpm/정격 37rpm, 12V 7W).
   * 실측 2026-08-26(1:90 모터): 전원구동 20턴 → L≈R≈10830 → 541.5/회전 → 542 사용.
   *   해석: 6 FG/모터회전 × 실기어비 90.25 = 541.5 (명목 "1:90"의 실제비는 90.25 추정).
   *   1차 측정 7857(=392.85/회전)은 좌·우 재측정과 불일치 → 턴수 미스카운트로 기각.
   * 실측 이력(구모터 56:1, 2026-07-08): 20턴 → L=214.0, R=215.25 → 215 사용했음.
   * TODO(production): 저속 재측정으로 펄스 유실 없음 확인 권장(아래 주의 참조). */
  #define FG_PULSES_PER_REV       542u             /* 실측 2026-08-26 (1:90 모터, L/R 20턴, 541.5 반올림) */
  #define METERS_PER_COUNT        (WHEEL_CIRCUMFERENCE_M / (float)FG_PULSES_PER_REV)  /* ≈ 0.231 mm */
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
#define TRACK_GAUGE_GEOM_M        0.245f       /* 기하 트랙 게이지 (실측 2026-08-27, 3법 수렴). URDF·풋프린트 기준 */

/* 운동학용 **유효** 게이지 (2026-09-07 신설).
 * 배경: 스키드스티어 트랙은 제자리 회전 시 옆으로 문질러지므로(scrub) 기하 게이지로 계산한
 *   ω 가 실제보다 크게 나온다. 사무실 바닥 실측(자이로 y축 적분 기준, 휠 ω 0.15~0.59 rad/s 7회):
 *     실제ω / 기하ω = 0.600 (σ 0.043) → 1차 0.409 로 플래시 후 재측정.
 *   2차 실측(B=0.409 상태에서 7회, B_actual = Δv/ω_gyro): 0.400 0.410 0.426 0.444 0.459 0.472 0.487
 *     → 중앙값·평균 모두 0.443. 산포 ±8% 는 트랙 스크럽의 실제 변동(모델로 못 줄임).
 *     → B_eff = 0.443 확정 (운용 구간 Δv 0.06~0.16 m/s 기준)
 * 효과: cmd_vel 역기구학과 오도메트리 양쪽에 같은 B 를 쓰므로
 *   ① 지령 ω = 실제 ω  ② /wheel_odom 의 vyaw = 실제 vyaw (Jetson SLIP 보정 불필요 → 1.0)
 * 한계: 바닥 재질 의존. 카펫·타일 등에서 재측정 필요. 직진 기하에는 영향 없음.
 * 파급: 최대 실제 ω = 2 × MAX_LINEAR_SPEED / B_eff = 2×0.085/0.443 = 0.384 rad/s
 *   → Nav2 각속도 상한 0.38 로 동반 하향할 것. */
#define WHEEL_BASE_M              0.443f       /* 유효 게이지 (2026-09-07 2차 실측 7회 중앙값) */

/* ---- 모터 / 운영 한계 ---- */
/* /cmd_vel 명령 saturation(microros_task.c V_MAX_MPS)에 사용됨 → 실제 도달가능 최고속 근처여야
 * windup 없음. 모터 교체(2026-08-26): 56:1 → 1:90 (무부하 45rpm, 정격 37rpm).
 * 실측(2026-08-26, 받침대·바닥 동일): duty 98%(OUT_MAX)에서 ≈0.115 m/s.
 *   duty-속도 곡선이 부하 무관(내장 속도제어 추정) → 무부하 이론치 0.121 근접.
 *   여유 두고 0.100. (구값 0.070 은 OUT_MAX 0.95 시절 95% 정착점 0.080 기반이었음)
 * TODO(측정): 장시간 지속 주행으로 0.100 유지 가능(전압 처짐·발열) 확인. */
#define MAX_LINEAR_SPEED_MPS      0.085f       /* 2026-09-07: 스케일 정정으로 단위가 실속도로 바뀜.
                                                 * 20kHz 받침대 duty 98% → 구단위 0.117~0.120 = 실 0.091~0.093.
                                                 * 바닥 부하 여유 두어 0.085 (구 0.100 은 실 0.078 이었음) */

/* ---- 저속·정지 문턱 체계 (2026-09-17: 세 파일에 흩어져 있던 값을 이 헤더 한 곳으로 모음) ----
 * 같은 휠 속도 축을 세 층이 나눠 쓴다. 한 값만 바꾸면 층 사이가 어긋나므로 반드시 여기서 함께 본다.
 *   WHEEL_SPEED_EPS         microros_task  : |휠 지령| < EPS  → 0 (의도된 정지)
 *   MIN_WHEEL_SPEED         microros_task  : EPS ≤ |휠 지령| < MIN → MIN 으로 승격(부호 보존)
 *   SPEED_CTRL_STOP_THRESH  speed_controller: |목표| < STOP → 정지 명령(감속 ramp 후 출력·적분 0,
 *                                             windup·전류 누설 방지 — F4 2026-05-21 도입, 05-27 능동 제동 진입점)
 *   STALL_TARGET_THRESH     safety_monitor : |목표| > 이 값일 때만 스톨 판정 (= STOP, 따로 두지 않는다)
 * 불변식: EPS < STOP ≤ MIN (아래 #error 로 컴파일 시 검사).
 *
 * 사고(2026-09-17 mp6·mp8, debug_log/2026-09-17 §7): 09-07 에 MIN 을 0.010(구 스케일)→0.008(실 스케일)로
 *   환산하면서 STOP(당시 speed_controller.c 의 TARGET_THRESH 0.010)은 그대로 둬 MIN < STOP 이 됨 →
 *   휠 지령 3~10 mm/s 가 승격돼도 정지로 처리, MPPI 가 목표 앞에서 9 mm/s 로 기어가려다 51 s 무한 정지.
 *   STOP 0.010 의 원래 전제(구 모터 AM2861·PWM 50 Hz 에서 저속 제어 불가)는 새 모터·20 kHz 에서 유효하지 않다.
 *   조치: STOP·STALL 0.010 → 0.005 (사용자 결정 09-17 — 승격값을 올리는 대신 저속 분해능 보존).
 *   TODO(측정): 새 펌웨어로 정지 상태에서 8 mm/s 출발(직진·제자리 회전) 바닥 실측 — 아래 MIN 의 미검증 구간.
 *
 * 정수 µm/s 로 정의하는 이유: 전처리기 #if 비교(부동소수는 #if 에서 쓸 수 없음). */
#define WHEEL_SPEED_EPS_UMPS          3000   /* 3 mm/s — 이하는 사실상 0(정지 의도) */
#define SPEED_CTRL_STOP_THRESH_UMPS   5000   /* 5 mm/s — 2026-09-17: 10 → 5 */

/* 기동 데드밴드 보상 이력 (2026-09-02 도입):
 *  |휠속도 명령| 이 최소 기동치 미만이면 모터가 반응하지 않아 상위 제어기(Nav2)가 미세 명령을 반복하며 영구 정체
 *  (09-02 실측: ω=0.05 rad/s, 휠 ±6 mm/s 68 초 무반응). 보상: EPS ≤ |v| < MIN 은 MIN 으로 승격.
 *  09-03: 기동 임계 0.012~0.016 → 0.020 채택. ※ PWM 50 Hz 조건 측정 — 09-07 에 폐기.
 *  09-07 (8fd7618, PWM 20 kHz): 데드밴드 재실측용으로 0.010 임시 하향.
 *  09-07 바닥 스윕 job44a (새 모터 CHR-GM37 1:90, 20 kHz, 스텝마다 정지 후 출발·3 s 유지):
 *    지령 5/10/15/20/30 mm/s(구 스케일) → FG 10/10/15/20/30, duty 41/41/43/45/50 %, L/R 대칭, 전 스텝 기동.
 *    지령 5 는 당시 MIN 0.010 으로 승격돼 10 으로 돌았으므로 **구 10 mm/s(=실 7.8 mm/s) 미만은 미검증**
 *    (debug_log/2026-09-07 SUMMARY §데드밴드 스윕).
 *  09-07 (50444d5, 휠 둘레 0.16130→0.12533): 0.010(구) × 0.777 = 0.0078 → **0.008 은 환산값**(직접 지령한 값 아님).
 *  한계: 승격 구간은 지령 크기와 무관하게 같은 속도 → 저속 분해능 상실.
 *  TODO(improve): 고정 하한 대신 기동 보조(정지 감지 시 순간 승격 후 목표 복귀), 또는 전압 연동 하한. */
#define MIN_WHEEL_SPEED_UMPS          8000   /* 8 mm/s */

#define WHEEL_SPEED_EPS_MPS          ((float)WHEEL_SPEED_EPS_UMPS * 1.0e-6f)
#define SPEED_CTRL_STOP_THRESH_MPS   ((float)SPEED_CTRL_STOP_THRESH_UMPS * 1.0e-6f)
#define MIN_WHEEL_SPEED_MPS          ((float)MIN_WHEEL_SPEED_UMPS * 1.0e-6f)
#define STALL_TARGET_THRESH_MPS      SPEED_CTRL_STOP_THRESH_MPS

#if !(WHEEL_SPEED_EPS_UMPS < SPEED_CTRL_STOP_THRESH_UMPS)
#error "rover_platform.h: WHEEL_SPEED_EPS 는 SPEED_CTRL_STOP_THRESH 보다 작아야 한다 (EPS 이상 지령이 정지로 먹힘)"
#endif
#if !(SPEED_CTRL_STOP_THRESH_UMPS <= MIN_WHEEL_SPEED_UMPS)
#error "rover_platform.h: MIN_WHEEL_SPEED 가 SPEED_CTRL_STOP_THRESH 보다 작다 — 승격된 지령이 정지로 처리됨 (2026-09-17 mp8 사고)"
#endif

#ifdef __cplusplus
}
#endif

#endif /* APP_APP_ROVER_PLATFORM_H */
