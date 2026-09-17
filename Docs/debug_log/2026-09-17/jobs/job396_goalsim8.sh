#!/bin/bash
# mp8 목표 앞 정지 재현·대안 시뮬레이션 (t=33 s: 상자 통과 직후, 목표까지 약 0.5 m)
source /opt/ros/humble/setup.bash; cd /tmp
run() { python3 /tmp/job355_mppi_sim.py /tmp/bag_mp8 33 "$@" 2>&1 | grep -av 'Opened database' | grep -aE "^[A-Z0-9]+_|→|목표\(|^ +(0|40|80|119) \|"; echo; }
B="vx_std=0.08 wz_std=0.4 temperature=0.15 iters=2 follow_w=10 follow_off=20 cycles=120 goal_yaw=0.0"
FWNOW="eps=0.003 promote=0.008 db=0.010"
FWFIX="eps=0.003 promote=0.012 db=0.010"
run label=S1_현재값_현재펌웨어 $B $FWNOW
run label=S2_현재값_펌웨어수정 $B $FWFIX
run label=S3_경로크리틱문턱0.2_현재펌웨어 $B $FWNOW follow_thr=0.2 align_thr=0.2 angle_thr=0.2
run label=S4_경로크리틱문턱0.2_펌웨어수정 $B $FWFIX follow_thr=0.2 align_thr=0.2 angle_thr=0.2
run label=S5_S4+goal_w10 $B $FWFIX follow_thr=0.2 align_thr=0.2 angle_thr=0.2 goal_w=10
