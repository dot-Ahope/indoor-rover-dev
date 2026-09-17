#!/bin/bash
# job421 재실행 (2026-09-17 §14): job421 의 run() 이 전역 T 를 덮어써 경로재생·코스트맵재생 변형이 temperature=19 로 돌았다 → local 로 고침, 두 변형만
source /opt/ros/humble/setup.bash; cd /tmp
run() { local BAG_=$1 AT_=$2; shift 2; python3 /tmp/job419_mppi_sim_humble.py /tmp/bag_$BAG_ $AT_ "$@" 2>&1 | grep -av 'Opened database' | grep -aE "^[A-Z0-9]+_|→|흔들림|유효 표본|동적 입력|Traceback|Error"; echo; }
COM="vx_std=0.08 wz_std=0.4 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2 cycles=60 lag_steps=1 w_gain=0.7 w_acc=1.2 humble=1"
for sc in "mp11 19" "mp12 19"; do set -- $sc; B=$1; AT=$2
  echo "######## $B t=$AT"
  for seed in 1 2; do for TEMP in 0.15 0.3; do
    run $B $AT label=D${seed}_${B}_경로재생_T$TEMP $COM temperature=$TEMP seed=$seed dyn_path=2
    run $B $AT label=C${seed}_${B}_경로+코스트맵재생_T$TEMP $COM temperature=$TEMP seed=$seed dyn_path=2 dyn_cost=1
  done; done
done
echo "######## 끝 $(date +%T)"
