#!/bin/bash
# lidar_yaw=π 반영 → RSP 재빌드·재시작 → TF 확인
source /opt/ros/humble/setup.bash
cp /tmp/rover_src/rover_description/urdf/rover.urdf ~/ros2_ws/src/rover_description/urdf/rover.urdf
cd ~/ros2_ws && colcon build --symlink-install --packages-select rover_description 2>&1 | tail -1
source ~/ros2_ws/install/setup.bash
pkill -f robot_state_publisher 2>/dev/null; sleep 2
setsid nohup ros2 launch rover_description description.launch.py > /tmp/rsp.log 2>&1 &
sleep 6
echo "===lidar_link TF (yaw 확인)==="; timeout 5 ros2 run tf2_ros tf2_echo base_link lidar_link 2>&1 | grep -aE "Translation|RPY \(degree\)" | head -2
echo "===nodes==="; ros2 node list | grep -E "state_publisher|slam" | tr '\n' ' '; echo
echo "READY_FOR_VERIFY"
