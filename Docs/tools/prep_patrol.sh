#!/bin/bash
# prep_patrol — 순회 구성으로 빠른 prep. 로버 안 움직임. 인자: VIZ(lite|true|off, 기본 lite) [FWD=15.0]
#   공통: 그림자 EKF 끔 + 전역 nvblox(map 프레임) + 재계획 0.5 Hz + 정체 감시 관찰 모드. (10-12 운용 구성은 VIZ=lite, FWD=15.0)
#   ★ 2026-10-23 §16(사용자 결정 "vslam on 기본으로 채택"): 오도메트리 기본 = cuVSLAM 병진 속도(ekf.launch vslam:=on) + 프로젝터 상시 끔(10-21 결정) + 카메라↔cuVSLAM SHM.
#     근거 f2von1 · f2von2(Docs/debug_log/2026-10-23/SUMMARY.md §10~§11): W3 회전 창 13.2~16.8 cm(rf2o 주 EKF 21.5~30.7), 멈칫 5(12~14), CPU 70 %(75~76).
#     예전 구성(rf2o + G4 게이트)은 ODOM=rf2o, 그때 그림자 cuVSLAM 까지 쓰려면 SENSORS_ADD="vslam:=shadow".
#   환경: ODOM(vslam|rf2o, 기본 vslam) · REPLAN_HZ(기본 0.5 — 10-23 §17 A 시험은 0.01 = 목표당 1 회 + PathBlockedAhead)
VIZ=${1:-lite}; FWD=${2:-15.0}
case "$VIZ" in off) V="";; lite|true) V="mppi_viz:=$VIZ";; *) echo "VIZ 는 lite|true|off"; exit 1;; esac
case "${ODOM:-vslam}" in
  vslam) S="emitter_off:=true vslam:=on dds_shm:=true";;
  rf2o)  S="rf2o:=true shadow:=false gate_v:=on gate_vref:=wheel";;
  *) echo "ODOM 은 vslam|rf2o"; exit 1;;
esac
# 10-19 §16: SENSORS_ADD 로 센서 인자 추가(예: "emitter_flash:=true stereo_fps:=30" — 프로젝터 번갈이 · 분리 노드). 뒤에 오므로 같은 인자는 덮어씀.
# 2026-10-26 §7: NAV_ADD 로 navigation.launch 인자 추가(예 "planner:=smac" — Smac Hybrid → 실패 시 NavFn)
export EXTRA_SENSORS="$S ${SENSORS_ADD:-}" EXTRA_NAV="global_camera:=nvblox replan_hz:=${REPLAN_HZ:-0.5} $V ${NAV_ADD:-}" STUCK_SHADOW=true FWD
echo "  prep_patrol: 오도메트리 ${ODOM:-vslam} · 재계획 ${REPLAN_HZ:-0.5} Hz · 궤적 발행 $VIZ · PreferForward $FWD · 추가 nav 인자 ${NAV_ADD:-없음}"
bash /tmp/prep_fast.sh
