#!/bin/bash
# 10-06 §12.1: G4(회전 중 병진 타당성) 켜고 5 조건, 도메인 81~85 — 1 분마다 진행 줄(current.log 에 보이게)
export GV=on GQ=off
run() { bash /tmp/occ_run.sh $1 $3 /tmp/g4_$2.npz $4 $5 "$6" > /tmp/g4_run_$1.txt 2>&1; }
run 81 clean 0.0 20.0 0.6 "" &
run 82 A_walk08 0.0 0.0 0.8 "-p legs:=true -p amp:=1.0 -p period:=12.0 -p move_deg:=90.0" &
run 83 C_sway 0.5 20.0 0.6 "-p amp:=0.15 -p period:=4.0 -p move_deg:=110.0" &
run 84 D_inout 0.3 20.0 0.6 "-p amp:=0.2 -p period:=3.0 -p move_deg:=20.0" &
run 85 E_fast 0.5 20.0 0.5 "-p amp:=0.3 -p period:=3.0 -p move_deg:=110.0" &
T0=$(date +%s); sleep 20
while [ $(ps aux | grep -c "[b]ag play /tmp/bag_step1") -gt 0 ]; do
  echo "  [$(( ($(date +%s) - T0) / 60 )) 분] 재생 남음 $(ps aux | grep -c "[b]ag play /tmp/bag_step1")/5 | $(for d in 81 83 85; do printf "%s:%s " $d "$(grep -a "게이트 통과" /tmp/occ_launch_$d.log | tail -1 | grep -oE "통과 [0-9]+.*" | tr -d ' ' | cut -c1-60)"; done)"; sleep 60; done
wait; echo "=== 끝"
