#!/bin/bash
# 10-26 §10.3 굽은 곳 깎기 변형 × 씨앗 1~6(바퀴 포화 구동계). 로버 안 움직임
source /opt/ros/humble/setup.bash; cd /tmp
TA=1792988302.0; B=/tmp/bag_f2sh2
COM="vx_std=0.08 wz_std=0.4 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2 cycles=160 lag_steps=1 w_acc=1.2 humble=1 temperature=0.15 near_thr=0.5 dyn_path=2 dyn_cost=1 obst=1 fwd_w=15 vx_min=-0.06 fpchk=1 resample=0.03 w_gain=1.0 wheel_max=0.085"
for v in "base" "Foff10 follow_off=10" "Foff5 follow_off=5" "Fw5 follow_w=5" "A28 align_w=28" "V06 vx_max=0.06" "T03 temperature=0.3"; do set -- $v; L=$1; shift
  for sd in 1 2 3 4 5 6; do r=$(python3 /tmp/anal_mppi_sim.py $B 0 label=$L t_abs=$TA $COM seed=$sd "$@" 2>&1 | grep -aE "굽은 곳|후보 전부" | tr '\n' ' '); echo "$L s$sd | $r"; done; done
echo "#### 끝 $(date +%T)"
