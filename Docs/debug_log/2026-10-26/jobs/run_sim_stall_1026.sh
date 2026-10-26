#!/bin/bash
# 10-26 §10.6 f2pa2 정지 장면 — A14 · A28 · A28Fw5 × 씨앗 10, 4 병렬. 로버 안 움직임
source /opt/ros/humble/setup.bash; cd /tmp; export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
B=/tmp/bag_f2pa2
COM="vx_std=0.08 wz_std=0.4 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2 cycles=160 lag_steps=1 w_acc=1.2 humble=1 temperature=0.15 near_thr=0.5 dyn_path=2 dyn_cost=1 obst=1 fwd_w=15 vx_min=-0.06 fpchk=1 w_gain=1.0 wheel_max=0.085 path_topic=smoothed"
one() { L=$1; sd=$2; shift 2; r=$(python3 /tmp/anal_mppi_sim.py $B 94 label=$L $COM seed=$sd "$@" 2>&1 | grep -aE "굽은 곳|후보 전부|→ " | tr '\n' ' '); echo "@@ $L s$sd | $r"; }
export -f one; export B COM
{ for v in "A14 align_w=14" "A28 align_w=28" "A28Fw5 align_w=28 follow_w=5"; do for sd in 1 2 3 4 5 6 7 8 9 10; do echo "$v" | awk -v s=$sd '{printf "%s %s", $1, s; for(i=2;i<=NF;i++) printf " %s", $i; print ""}'; done; done; } | xargs -P 4 -L 1 bash -c 'one "$@"' _
echo "#### 끝 $(date +%T)"
