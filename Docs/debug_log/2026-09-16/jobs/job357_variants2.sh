#!/bin/bash
source /opt/ros/humble/setup.bash; cd /tmp
run() { python3 /tmp/job355_mppi_sim.py /tmp/bag_mp4 ${T:-17} "$@" 2>&1 | grep -av 'Opened database' | grep -aE "^[A-Z]_|→|^ +(0|10|20|30|40|50|59) \|"; echo; }
B="vx_std=0.08 wz_std=0.4 temperature=0.15 iters=2 cycles=60"
run label=C_B+follow_off20 $B follow_off=20
run label=D_B+follow_off20+align6 $B follow_off=20 align_w=6
run label=E_B+align6 $B align_w=6
run label=F_B+follow_w10_off20 $B follow_off=20 follow_w=10
run label=G_D+rep0.5 $B follow_off=20 align_w=6 rep_w=0.5
run label=H_A기준+follow_off20 follow_off=20 cycles=60
