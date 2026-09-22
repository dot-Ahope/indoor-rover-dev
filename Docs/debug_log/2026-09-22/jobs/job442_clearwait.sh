#!/bin/bash
# 사람 흔적 셀 제거(09-18): 로컬·전역 코스트맵을 비우고 8 s 동안 현재 센서로 다시 채운다(상자는 카메라 앞이라 곧바로 재마킹)
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
timeout 10 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1 && echo "local 클리어"
timeout 10 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1 && echo "global 클리어"
sleep 8; echo "8 s 재마킹 대기 끝"
