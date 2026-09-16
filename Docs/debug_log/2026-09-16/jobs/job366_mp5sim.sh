#!/bin/bash
source /opt/ros/humble/setup.bash; cd /tmp
echo "##### job345 (후보 궤적 분포)"; python3 /tmp/job345_traj.py /tmp/bag_mp5 24,27,29,31,34,40 2>&1 | grep -av 'Opened database' | cut -c1-200
echo "##### job354 (크리틱 재구성 t=29,32)"; python3 /tmp/job354_critics.py /tmp/bag_mp5 29,32 2>&1 | grep -av 'Opened database' | cut -c1-160
run() { T=$1; shift; python3 /tmp/job355_mppi_sim.py /tmp/bag_mp5 $T "$@" 2>&1 | grep -av 'Opened database' | grep -aE "^[A-Z]_|→|^ +(0|20|40|59) \|"; echo; }
B="vx_std=0.08 wz_std=0.4 temperature=0.15 iters=2 follow_w=10 follow_off=20 cycles=60"
echo "##### 시뮬레이션 (복귀 정체 t=29)"
run 29 label=M_현재값 $B
run 29 label=N_경로크리틱_목표근처유지 $B follow_thr=0.2 align_thr=0.2 angle_thr=0.2
run 29 label=O_N+GoalAngle끔 $B follow_thr=0.2 align_thr=0.2 angle_thr=0.2 ga_w=0
run 29 label=P_N+goal_w10 $B follow_thr=0.2 align_thr=0.2 angle_thr=0.2 goal_w=10
run 24 label=M_t24 $B
