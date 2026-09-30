#!/bin/bash
# 09-30 §3: prep(새 footprint) → footprint 적용 확인 → 0.70 m 직진 SLAM 치우침 시험
set +u
bash /tmp/job657_prep_f0b.sh 2>&1 | grep -aE "wheel_odom|gyro bias|odometry/filtered|map->odom|_server|상자:|icr|rot_cov|배터리"
echo "  footprint(local): $(timeout 10 ros2 param get /local_costmap/local_costmap footprint 2>&1 | tail -1)"
echo "  stuck_monitor: $(grep -a "stuck_monitor 시작" /tmp/nav2.log | tail -1 | grep -ao "ACTIVE\|SHADOW")"
sleep 2
python3 /tmp/job680_slambias.py 0.70 2>&1 | grep -av "^\["
