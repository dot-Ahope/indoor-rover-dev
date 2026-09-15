#!/bin/bash
source /opt/ros/humble/setup.bash
echo "uptime: $(uptime -p)"
echo "프로세스 job254/job125/bag record: $(ps -eo args | grep -aE 's4run|avoid3|bag record' | grep -av grep | wc -l)"
printf 'cmd_vel hz: '; timeout 3 ros2 topic hz /cmd_vel 2>&1 | grep -aoE 'average rate: [0-9.]+' | head -1; echo
printf '휠 odom v: '; timeout 3 ros2 topic echo /wheel_odom --once 2>/dev/null | grep -aA1 'linear:' | grep -a ' x:' | head -1
timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -a Translation | head -1
grep -aE 'Received goal|Goal (succeeded|failed)|Aborting handle|Begin navigating|Goal reached' /tmp/nav2.log | tail -4 | cut -c1-140
ls -d /tmp/bag_mp2 2>/dev/null && echo "bag_mp2 존재" || echo "bag_mp2 없음 → 주행 시작 안 됨"
