#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== BT XML 설치 ==="; cp /tmp/nav_to_pose_no_spin.xml ~/ros2_ws/src/rover_navigation/config/ && cp /tmp/nav_to_pose_no_spin.xml ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/ && echo "  raw_path: $(grep -c raw_path ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav_to_pose_no_spin.xml)"
echo "=== robot_state_publisher 재기동(되돌린 프로파일) ==="; pkill -TERM -f robot_state_publisher; pkill -TERM -f description.launch; sleep 2
setsid nohup ros2 launch rover_description description.launch.py > /tmp/description.log 2>&1 &
sleep 8; echo "  rsp: $(pgrep -fc robot_state_publisher)"
printf "  base_link->lidar_link: "; timeout 8 ros2 run tf2_ros tf2_echo base_link lidar_link 2>&1 | grep -a Translation | head -1
echo "  tf_static 발행자: $(timeout 8 ros2 topic info -v /tf_static 2>/dev/null | grep -a 'Node name' | grep -av transform_listener | tr '\n' ' ')"
