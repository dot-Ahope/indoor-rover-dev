#!/bin/bash
# 조향 흔들림 원인·대책 (2026-09-17): 이상 구동계 vs 실측 구동계(지연 1 주기·ω 이득 0.7·smoother ω 가속 1.2), temperature 0.15/0.22/0.3, wz_std 0.3
source /opt/ros/humble/setup.bash; cd /tmp
run() { B=$1; T=$2; shift 2; python3 /tmp/job410_mppi_sim_lag.py /tmp/bag_$B $T "$@" 2>&1 | grep -av 'Opened database' | grep -aE "^[A-Z0-9]+_|→|목표\(|흔들림"; echo; }
COM="vx_std=0.08 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2"
LAG="lag_steps=1 w_gain=0.7 w_acc=1.2"
echo "######## 통로 (mp11 t=19, 60 주기)"
for seed in 1 2 3; do
  run mp11 19 label=P${seed}_이상구동계_T0.15 $COM wz_std=0.4 temperature=0.15 cycles=60 seed=$seed
  run mp11 19 label=P${seed}_실측구동계_T0.15현재 $COM $LAG wz_std=0.4 temperature=0.15 cycles=60 seed=$seed
  run mp11 19 label=P${seed}_실측구동계_T0.15_wz0.3 $COM $LAG wz_std=0.3 temperature=0.15 cycles=60 seed=$seed
  run mp11 19 label=P${seed}_실측구동계_T0.22 $COM $LAG wz_std=0.4 temperature=0.22 cycles=60 seed=$seed
  run mp11 19 label=P${seed}_실측구동계_T0.3 $COM $LAG wz_std=0.4 temperature=0.3 cycles=60 seed=$seed
done
echo "######## 입구 (mp4 t=17, 60 주기)"
for seed in 1 2; do
  for T in 0.15 0.22 0.3; do run mp4 17 label=E${seed}_실측구동계_T$T $COM $LAG wz_std=0.4 temperature=$T cycles=60 seed=$seed; done
done
echo "######## 목표 근처 (mp8 t=33, 200 주기)"
for seed in 1 2; do
  for T in 0.15 0.22 0.3; do run mp8 33 label=G${seed}_실측구동계_T$T $COM $LAG wz_std=0.4 temperature=$T cycles=200 seed=$seed; done
done
echo "######## 끝 $(date +%T)"
