#!/bin/bash
source /opt/ros/humble/setup.bash; cd /tmp
run() { T=$1; shift; python3 /tmp/job355_mppi_sim.py /tmp/bag_mp4 $T "$@" 2>&1 | grep -av 'Opened database' | grep -aE "^[A-Z]_|→|^ +(0|20|40|59) \|"; echo; }
B="vx_std=0.08 wz_std=0.4 temperature=0.15 iters=2 cycles=60"
run 17 label=I_F+angle_max0.3 $B follow_off=20 follow_w=10 angle_max=0.3
run 17 label=J_I+angle_w4 $B follow_off=20 follow_w=10 angle_max=0.3 angle_w=4
run 17 label=K_F+off30 $B follow_off=30 follow_w=10
run 17 label=L_F+align6+rep0.5 $B follow_off=20 follow_w=10 align_w=6 rep_w=0.5
run 12 label=F_t12 $B follow_off=20 follow_w=10
run 20 label=F_t20 $B follow_off=20 follow_w=10
run 20 label=B_t20 $B
