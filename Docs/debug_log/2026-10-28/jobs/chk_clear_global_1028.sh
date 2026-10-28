#!/bin/bash
# §13 전역 코스트맵 비우기 → 5 s · 20 s 뒤 로버 둘레 다시 보기(치명 띠가 nvblox 기억에서 되살아나는지). 로버 안 움직임
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
date +%T; timeout 15 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" 2>&1 | tail -1
sleep 5; echo "== +5 s"; python3 /tmp/chk_costmap_robot.py 2>&1 | grep -av "^\["
sleep 15; echo "== +20 s"; python3 /tmp/chk_costmap_robot.py 2>&1 | grep -av "^\["
