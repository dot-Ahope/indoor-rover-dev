#!/bin/bash
# 09-29 §13 G1 준비: prep(stuck_monitor 작동·nav_guard) → 두 노드 모드 확인
set +u
bash /tmp/job657_prep_f0b.sh 2>&1 | grep -aE "wheel_odom|gyro bias|odometry/filtered|map->odom|_server|상자:|icr|rot_cov|배터리"
echo "  stuck_monitor: $(grep -a "stuck_monitor 시작" /tmp/nav2.log | tail -1 | grep -ao "ACTIVE[^ ]*\|SHADOW[^ ]*")"
echo "  nav_guard: $(grep -a "nav_guard 시작" /tmp/nav2.log | tail -1 | grep -ao "시간 =.*")"
