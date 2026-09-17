#!/bin/bash
# 온도 A/B — 구동계 모델(지연 1 주기·ω 이득 0.7·ω 가속 1.2) 포함. 통로(mp11 bag t=19), 입구(mp4 t=17), 목표 근처(mp8 t=33)
source /opt/ros/humble/setup.bash; cd /tmp
run() { B=$1; T=$2; shift 2; python3 /tmp/job410_mppi_sim_lag.py /tmp/bag_$B $T "$@" 2>&1 | grep -av 'Opened database' | grep -aE "^[A-Z0-9]+_|→|목표\(|흔들림"; echo; }
BASE="vx_std=0.08 wz_std=0.4 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2 lag_steps=1 w_gain=0.7 w_acc=1.2"
echo "######## 통로 (mp11 t=19, 60 주기)"
for seed in 1 2 3; do
  run mp11 19 label=Q${seed}_T0.15현재 $BASE temperature=0.15 cycles=60 seed=$seed
  run mp11 19 label=Q${seed}_T0.22 $BASE temperature=0.22 cycles=60 seed=$seed
  run mp11 19 label=Q${seed}_T0.3 $BASE temperature=0.3 cycles=60 seed=$seed
done
echo "######## 입구 (mp4 t=17, 60 주기)"
for seed in 1 2; do
  run mp4 17 label=E${seed}_T0.15현재 $BASE temperature=0.15 cycles=60 seed=$seed
  run mp4 17 label=E${seed}_T0.3 $BASE temperature=0.3 cycles=60 seed=$seed
done
echo "######## 목표 근처 (mp8 t=33, 120 주기)"
run mp8 33 label=G_T0.15현재 $BASE temperature=0.15 cycles=120 seed=1
run mp8 33 label=G_T0.3 $BASE temperature=0.3 cycles=120 seed=1
echo "######## 끝 $(date +%T)"
