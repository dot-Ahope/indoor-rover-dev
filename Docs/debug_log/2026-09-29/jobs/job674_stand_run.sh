#!/bin/bash
# 09-29 §13 G3b: prep(새 stuck_monitor, 그림자) → 받침대 시험
set +u
bash /tmp/job657_prep_f0b.sh 2>&1 | grep -aE "wheel_odom|gyro bias|odometry/filtered|_server|B2|icr|rot_cov|배터리"
echo -n "  stuck_monitor 모드: "; grep -ao "stuck_monitor 시작[^)]*)[^
]*" /tmp/nav2.log | tail -1
sleep 3
python3 /tmp/job673_stand.py 2>&1 | grep -av "^\["
