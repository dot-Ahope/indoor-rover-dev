#!/bin/bash
# 10-26 §10.2 재현 시험: 시뮬 구동계를 펌웨어 바퀴 포화(비례 축소, wheel_max 0.085)로 — w_gain 0.7(회전만 줄임)은 곡률을 바꿔 깎기를 가렸음. 로버 안 움직임
source /opt/ros/humble/setup.bash; cd /tmp
TA=1792988302.0; B=/tmp/bag_f2sh2
COM="vx_std=0.08 wz_std=0.4 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2 cycles=${CYC:-160} lag_steps=1 w_acc=1.2 humble=1 temperature=0.15 near_thr=0.5 dyn_path=2 dyn_cost=1 obst=1 seed=1 fwd_w=15 vx_min=-0.06 fpchk=1 resample=0.03"
for v in "W07_old w_gain=0.7" "SAT w_gain=1.0 wheel_max=0.085" "SAT_s2 w_gain=1.0 wheel_max=0.085 seed=2" "SAT_s3 w_gain=1.0 wheel_max=0.085 seed=3"; do set -- $v; L=$1; shift
  echo "#### $L"; python3 /tmp/anal_mppi_sim.py $B 0 label=$L t_abs=$TA $COM "$@" 2>&1 | grep -aE "굽은 곳|후보 전부|→ |Traceback|Error"; done
echo "#### 끝 $(date +%T)"
