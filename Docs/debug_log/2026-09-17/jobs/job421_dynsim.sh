#!/bin/bash
# 동적 입력 재생 (2026-09-17 §14): 재가지치기만 / +/plan·map->odom 시간 재생 / +코스트맵 시간 재생 — 흔들림이 실측 수준·온도 무관으로 되는지
source /opt/ros/humble/setup.bash; cd /tmp
run() { B=$1; T=$2; shift 2; python3 /tmp/job419_mppi_sim_humble.py /tmp/bag_$B $T "$@" 2>&1 | grep -av 'Opened database' | grep -aE "^[A-Z0-9]+_|→|흔들림|유효 표본|동적 입력|Traceback|Error"; echo; }
COM="vx_std=0.08 wz_std=0.4 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2 cycles=60 lag_steps=1 w_gain=0.7 w_acc=1.2 humble=1"
for sc in "mp11 19" "mp12 19"; do set -- $sc; B=$1; AT=$2
  echo "######## $B t=$AT"
  for seed in 1 2; do for T in 0.15 0.3; do
    run $B $AT label=R${seed}_${B}_재가지치기_T$T $COM temperature=$T seed=$seed dyn_path=1
    run $B $AT label=D${seed}_${B}_경로재생_T$T $COM temperature=$T seed=$seed dyn_path=2
    run $B $AT label=C${seed}_${B}_경로+코스트맵재생_T$T $COM temperature=$T seed=$seed dyn_path=2 dyn_cost=1
  done; done
done
echo "######## 끝 $(date +%T)"
