#!/bin/bash
# 10-26 §10.4 굽은 곳 깎기 — 재계획 직후 13:18:10 부터 26 s, 변형 7 × 씨앗 10, 4 개씩 병렬. 로버 안 움직임
source /opt/ros/humble/setup.bash; cd /tmp; export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
TA=1792988290.0; B=/tmp/bag_f2sh2
COM="vx_std=0.08 wz_std=0.4 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2 cycles=260 lag_steps=1 w_acc=1.2 humble=1 temperature=0.15 near_thr=0.5 dyn_path=2 dyn_cost=1 obst=1 fwd_w=15 vx_min=-0.06 fpchk=1 resample=0.03 w_gain=1.0 wheel_max=0.085"
one() { L=$1; sd=$2; shift 2; r=$(python3 /tmp/anal_mppi_sim.py $B 0 label=$L t_abs=$TA $COM seed=$sd "$@" 2>&1 | grep -aE "굽은 곳|후보 전부" | tr '\n' ' '); echo "$L s$sd | $r"; }
export -f one; export B TA COM
{ for v in "base" "A28 align_w=28" "Fw5 follow_w=5" "A28Fw5 align_w=28 follow_w=5" "B2000 batch=2000" "WZ03 wz_std=0.3" "IT3 iters=3"; do for sd in 1 2 3 4 5 6 7 8 9 10; do echo "$v" | awk -v s=$sd '{printf "%s %s", $1, s; for(i=2;i<=NF;i++) printf " %s", $i; print ""}'; done; done; } | xargs -P 4 -L 1 bash -c 'one "$@"' _
echo "#### 끝 $(date +%T)"
