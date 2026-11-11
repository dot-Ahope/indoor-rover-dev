#!/bin/bash
# prep_patrol — 순회 구성으로 빠른 prep. 로버 안 움직임. 인자: VIZ(lite|true|off, 기본 lite) [FWD=15.0]
#   공통: 그림자 EKF 끔 + 전역 nvblox(map 프레임) + 정체 감시 관찰 모드. (10-12 운용 구성은 VIZ=lite, FWD=15.0)
#   ★ 2026-11-11 §7(사용자 "표준으로 바꿔"): 계획 = Smac Hybrid → 실패 시 NavFn(PLANNER 기본 smac) · 재계획 0.01 Hz(REPLAN_HZ 기본 0.01 = 목표당 1 회 + PathBlockedAhead).
#     근거 = 같은 구성 연속 3 회 8/8 · 주행 중 TF 실패 0 · 접촉 0(f2tt1 10-27 · f2tt2 10-28 · f2rr1 11-11, Docs/debug_log/2026-11-11/SUMMARY.md §4 · §5).
#     그 전 기본(navfn · 0.5 Hz, 11-04 정의)은 미검증 조합이었고 첫 주행 f2dm1 에서 실패(2026-11-10 §9). B0 로 돌리려면 PLANNER=navfn REPLAN_HZ=0.01.
#   ★ 2026-10-23 §16(사용자 결정 "vslam on 기본으로 채택"): 오도메트리 기본 = cuVSLAM 병진 속도(ekf.launch vslam:=on) + 프로젝터 상시 끔(10-21 결정) + 카메라↔cuVSLAM SHM.
#     근거 f2von1 · f2von2(Docs/debug_log/2026-10-23/SUMMARY.md §10~§11): W3 회전 창 13.2~16.8 cm(rf2o 주 EKF 21.5~30.7), 멈칫 5(12~14), CPU 70 %(75~76).
#     예전 구성(rf2o + G4 게이트)은 ODOM=rf2o, 그때 그림자 cuVSLAM 까지 쓰려면 SENSORS_ADD="vslam:=shadow".
#   환경: ODOM(vslam|rf2o, 기본 vslam) · PLANNER(smac|navfn, 기본 smac) · REPLAN_HZ(기본 0.01 — 11-11 전 기본은 0.5)
VIZ=${1:-lite}; FWD=${2:-15.0}
case "$VIZ" in off) V="";; lite|true) V="mppi_viz:=$VIZ";; *) echo "VIZ 는 lite|true|off"; exit 1;; esac
case "${ODOM:-vslam}" in
  vslam) S="emitter_off:=true vslam:=on dds_shm:=true";;
  rf2o)  S="rf2o:=true shadow:=false gate_v:=on gate_vref:=wheel vslam:=off emitter_off:=false dds_shm:=false";;   # 11-04: launch 기본이 vslam on · 프로젝터 끔 · SHM 이 돼 옛 구성 값을 명시
  *) echo "ODOM 은 vslam|rf2o"; exit 1;;
esac
# 10-19 §16: SENSORS_ADD 로 센서 인자 추가(예: "emitter_flash:=true stereo_fps:=30" — 프로젝터 번갈이 · 분리 노드). 뒤에 오므로 같은 인자는 덮어씀.
# 2026-10-26 §7: NAV_ADD 로 navigation.launch 인자 추가(예 "planner:=smac" — Smac Hybrid → 실패 시 NavFn)
export EXTRA_SENSORS="$S ${SENSORS_ADD:-}" EXTRA_NAV="global_camera:=nvblox planner:=${PLANNER:-smac} replan_hz:=${REPLAN_HZ:-0.01} $V ${NAV_ADD:-}" STUCK_SHADOW=true FWD
echo "  prep_patrol: 오도메트리 ${ODOM:-vslam} · 계획 ${PLANNER:-smac} · 재계획 ${REPLAN_HZ:-0.01} Hz · 궤적 발행 $VIZ · PreferForward $FWD · 추가 nav 인자 ${NAV_ADD:-없음}"
bash /tmp/prep_fast.sh
