#!/bin/bash
# SLAM 기동·검증 (무동작). map->odom TF + /map 확인.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
if ros2 node list 2>/dev/null | grep -q slam_toolbox; then
  echo "slam_toolbox 이미 실행중"
else
  echo "slam.launch 기동..."
  setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
  sleep 15
fi
echo "노드: $(ros2 node list 2>/dev/null | grep -E 'slam' | tr '\n' ' ')"
echo -n "/map 발행: "; timeout 6 ros2 topic hz /map 2>&1 | grep -aE "average rate" | head -1 || echo "무발행!"
echo "map->odom TF:"
timeout 5 ros2 run tf2_ros tf2_echo map odom 2>/dev/null | grep -aE "Translation|RPY \(degree\)" | head -2 || echo "  TF 없음(아직 초기화중일 수 있음)"
echo "map->base_link TF:"
timeout 5 ros2 run tf2_ros tf2_echo map base_link 2>/dev/null | grep -aE "Translation|RPY \(degree\)" | head -2 || echo "  TF 없음"
