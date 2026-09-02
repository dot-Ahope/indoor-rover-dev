#!/bin/bash
# 세션 확인 + slam_toolbox 재시작(깨끗한 맵)
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===세션 확인==="
echo -n "wheel_odom: "; timeout 6 ros2 topic hz /wheel_odom 2>&1 | grep -aE "average|does not" | tail -1
echo -n "battery: "; timeout 5 ros2 topic echo /battery --once --field voltage 2>/dev/null || echo NONE
echo "===slam_toolbox 재시작 (맵 초기화)==="
pkill -f slam_toolbox 2>/dev/null; sleep 2
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 12
ros2 node list | grep slam || echo NO_SLAM
echo -n "map→odom TF: "; timeout 6 ros2 run tf2_ros tf2_echo map odom 2>&1 | grep -aE "Translation" | head -1
echo -n "/scan: "; timeout 5 ros2 topic hz /scan 2>&1 | grep -aE "average|does not" | tail -1
echo "READY"
