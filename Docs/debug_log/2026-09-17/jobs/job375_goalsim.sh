#!/bin/bash
source /opt/ros/humble/setup.bash; cd /tmp
run() { T=$1; shift; python3 /tmp/job355_mppi_sim.py /tmp/bag_mp6 $T "$@" 2>&1 | grep -av 'Opened database' | grep -aE "^[A-Z]_|→|^ +(0|20|40|59) \|"; echo; }
B="vx_std=0.08 wz_std=0.4 temperature=0.15 iters=2 follow_w=10 follow_off=20 cycles=60 goal_yaw=0.0"
run 52 label=G1_현재값_목표근처 $B
run 52 label=G2_경로크리틱문턱0.2 $B follow_thr=0.2 align_thr=0.2 angle_thr=0.2
run 52 label=G3_goal_w10 $B goal_w=10
run 52 label=G4_G2+goal_w10 $B follow_thr=0.2 align_thr=0.2 angle_thr=0.2 goal_w=10
