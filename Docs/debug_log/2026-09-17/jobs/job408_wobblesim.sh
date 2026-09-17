#!/bin/bash
# 흔들림 A/B 시뮬레이션 (백그라운드): 통로 장면 bag_mp11 t=10, 입구 장면 bag_mp4 t=17, 목표 근처 장면 bag_mp8 t=33
source /opt/ros/humble/setup.bash; cd /tmp
run() { B=$1; T=$2; shift 2; python3 /tmp/job355_mppi_sim.py /tmp/bag_$B $T "$@" 2>&1 | grep -av 'Opened database' | grep -aE "^[A-Z0-9]+_|→|목표\(|흔들림"; echo; }
BASE="vx_std=0.08 temperature=0.15 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005"
echo "######## 통로 (mp11 t=10, 60 주기) — seed 1~3"
for seed in 1 2 3; do
  run mp11 10 label=P${seed}_현재_wz0.4_T0.15_it2 $BASE wz_std=0.4 iters=2 cycles=60 seed=$seed
  run mp11 10 label=P${seed}_wz0.3 $BASE wz_std=0.3 iters=2 cycles=60 seed=$seed
  run mp11 10 label=P${seed}_wz0.2 $BASE wz_std=0.2 iters=2 cycles=60 seed=$seed
  run mp11 10 label=P${seed}_T0.3 $BASE wz_std=0.4 temperature=0.3 iters=2 cycles=60 seed=$seed
done
echo "######## 입구 (mp4 t=17, 60 주기) — 과거 표본 붕괴 장면"
run mp4 17 label=E_현재 $BASE wz_std=0.4 iters=2 cycles=60 seed=1
run mp4 17 label=E_wz0.3 $BASE wz_std=0.3 iters=2 cycles=60 seed=1
run mp4 17 label=E_wz0.2 $BASE wz_std=0.2 iters=2 cycles=60 seed=1
echo "######## 목표 근처 (mp8 t=33, 120 주기)"
run mp8 33 label=G_현재 $BASE wz_std=0.4 iters=2 cycles=120 seed=1
run mp8 33 label=G_wz0.3 $BASE wz_std=0.3 iters=2 cycles=120 seed=1
echo "######## 끝 $(date +%T)"
