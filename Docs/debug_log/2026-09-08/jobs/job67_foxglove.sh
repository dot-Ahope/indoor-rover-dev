#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
pkill -9 -f foxglove_bridge 2>/dev/null; sleep 2
setsid nohup ros2 launch rover_bringup foxglove.launch.py > /tmp/foxglove.log 2>&1 &
sleep 8
echo -n "foxglove 프로세스: "; pgrep -fc foxglove_bridge
echo -n "포트 8765: "; ss -tln 2>/dev/null | grep -c ":8765"
echo "서빙 토픽(코스트맵/경로):"; grep -aoE "/(local|global)_costmap/costmap[a-z_]*|/plan|/local_plan" /tmp/foxglove.log | sort -u | sed "s/^/  /"
echo -n "IP: "; hostname -I | awk '{print $1}'
