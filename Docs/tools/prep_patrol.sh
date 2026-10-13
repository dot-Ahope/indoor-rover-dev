#!/bin/bash
# prep_patrol — 순회 구성으로 빠른 prep. 로버 안 움직임. 인자: VIZ(lite|true|off, 기본 lite) [FWD=15.0]
#   공통: 그림자 EKF 끔 + rf2o·G4 잔차 + 전역 nvblox(map 프레임) + 재계획 0.5 Hz + 정체 감시 관찰 모드. (10-12 운용 구성은 VIZ=lite, FWD=15.0)
VIZ=${1:-lite}; FWD=${2:-15.0}
case "$VIZ" in off) V="";; lite|true) V="mppi_viz:=$VIZ";; *) echo "VIZ 는 lite|true|off"; exit 1;; esac
export EXTRA_SENSORS="rf2o:=true shadow:=false gate_v:=on gate_vref:=wheel" EXTRA_NAV="global_camera:=nvblox replan_hz:=0.5 $V" STUCK_SHADOW=true FWD
echo "  prep_patrol: 궤적 발행 $VIZ · PreferForward $FWD"
bash /tmp/prep_fast.sh
