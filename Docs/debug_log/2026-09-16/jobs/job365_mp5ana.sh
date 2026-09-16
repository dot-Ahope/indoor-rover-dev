#!/bin/bash
source /opt/ros/humble/setup.bash; cd /tmp
echo "##### job327 (자세·경로·실현가능성·ASCII t=30)"; python3 /tmp/job327_mp2why.py /tmp/bag_mp5 0 0 0 30 2>&1 | grep -av 'Opened database' | grep -aE "^ +(2[0-9]|3[0-9]|4[05])\.0 \||^bag|===|^\+0\.[0-3]|^-0\.[0-3]|^\+0\.00" | cut -c1-150
echo "##### job345 (후보 궤적 분포)"; python3 /tmp/job345_traj.py /tmp/bag_mp5 20,24,26,28,30,34,40 2>&1 | grep -av 'Opened database' | cut -c1-210
echo "##### job354 (크리틱 재구성 t=28,32)"; python3 /tmp/job354_critics.py /tmp/bag_mp5 28,32 2>&1 | grep -av 'Opened database' | cut -c1-170
