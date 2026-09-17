#!/bin/bash
# regenerate_noises A/B (2026-09-17 §14): 고정 잡음(현재 기본) vs 매 반복 새 잡음, temperature 0.15/0.3, seed 여러 개(잡음 뽑기 편차)
source /opt/ros/humble/setup.bash; cd /tmp
run() { local BAG_=$1 AT_=$2; shift 2; python3 /tmp/job419_mppi_sim_humble.py /tmp/bag_$BAG_ $AT_ "$@" 2>&1 | grep -av 'Opened database' | grep -aE "^[A-Z0-9]+_|→|흔들림|유효 표본|Traceback|Error"; echo; }
COM="vx_std=0.08 wz_std=0.4 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2 cycles=60 lag_steps=1 w_gain=0.7 w_acc=1.2 humble=1 dyn_path=1"
for sc in "mp11 19 1 2 3 4 5 6" "mp12 19 1 2 3"; do set -- $sc; B=$1; AT=$2; shift 2
  echo "######## $B t=$AT"
  for seed in "$@"; do for TEMP in 0.15 0.3; do for RG in 0 1; do
    run $B $AT label=G${seed}_${B}_regen${RG}_T$TEMP $COM temperature=$TEMP regen=$RG seed=$seed
  done; done; done
done
echo "######## 끝 $(date +%T)"
