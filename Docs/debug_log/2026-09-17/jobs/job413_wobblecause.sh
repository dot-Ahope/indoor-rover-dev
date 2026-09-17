#!/bin/bash
# 조향 흔들림 기제 분리 (2026-09-17): 구동계 요소(smoother ω 가속 제한 / 지연·이득)를 하나씩 + softmax 유효 표본 수(ESS)
source /opt/ros/humble/setup.bash; cd /tmp
run() { B=$1; T=$2; shift 2; python3 /tmp/job410_mppi_sim_lag.py /tmp/bag_$B $T "$@" 2>&1 | grep -av 'Opened database' | grep -aE "^[A-Z0-9]+_|→|흔들림|유효 표본"; echo; }
COM="vx_std=0.08 wz_std=0.4 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2 cycles=60"
echo "######## 통로 (mp11 t=19, 60 주기)"
for seed in 1 2 3; do
  run mp11 19 label=S${seed}_이상_T0.15 $COM temperature=0.15 seed=$seed
  run mp11 19 label=S${seed}_가속제한만_T0.15 $COM w_acc=1.2 temperature=0.15 seed=$seed
  run mp11 19 label=S${seed}_지연이득만_T0.15 $COM lag_steps=1 w_gain=0.7 temperature=0.15 seed=$seed
  run mp11 19 label=S${seed}_이상_T0.3 $COM temperature=0.3 seed=$seed
  run mp11 19 label=S${seed}_실측_T0.15 $COM lag_steps=1 w_gain=0.7 w_acc=1.2 temperature=0.15 seed=$seed
  run mp11 19 label=S${seed}_실측_T0.22 $COM lag_steps=1 w_gain=0.7 w_acc=1.2 temperature=0.22 seed=$seed
  run mp11 19 label=S${seed}_실측_T0.3 $COM lag_steps=1 w_gain=0.7 w_acc=1.2 temperature=0.3 seed=$seed
done
echo "######## 끝 $(date +%T)"
