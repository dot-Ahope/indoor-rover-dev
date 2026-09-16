#!/bin/bash
# job355 변형 일괄 실행 (bag_mp4 t=17 정체 시작 장면)
source /opt/ros/humble/setup.bash; cd /tmp
run() { python3 /tmp/job355_mppi_sim.py /tmp/bag_mp4 ${T:-17} "$@" 2>&1 | grep -av 'Opened database'; echo; }
run label=A_mp4기준 cycles=40
run label=B_배포값 vx_std=0.08 wz_std=0.4 temperature=0.15 iters=2 cycles=40
