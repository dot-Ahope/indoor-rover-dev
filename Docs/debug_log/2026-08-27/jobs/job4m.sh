#!/bin/bash
# D455f 자이로 → EKF 복원 배포·검증
source /opt/ros/humble/setup.bash
cp -r /tmp/rover_src/rover_bringup ~/ros2_ws/src/
chmod +x ~/ros2_ws/src/rover_bringup/scripts/sensor_conditioner.py
cd ~/ros2_ws && colcon build --symlink-install --packages-select rover_bringup 2>&1 | tail -1
source ~/ros2_ws/install/setup.bash

echo "===START camera (IMU only, USB2 대역 절약)==="
pkill -f realsense2_camera_node 2>/dev/null; sleep 1
setsid nohup ros2 launch rover_bringup camera.launch.py enable_depth:=false enable_color:=false > /tmp/camera.log 2>&1 &
sleep 12
timeout 6 ros2 topic hz /camera/camera/imu 2>&1 | grep -E "average|does not" | tail -1

echo "===RESTART ekf (conditioner ← D455f)==="
pkill -f "ekf.launch" 2>/dev/null; pkill -f ekf_node 2>/dev/null; pkill -f sensor_conditioner 2>/dev/null; sleep 1
setsid nohup ros2 launch rover_bringup ekf.launch.py > /tmp/ekf.log 2>&1 &
sleep 20
echo "-- conditioner log:"; grep -aE "bias|stationary" /tmp/ekf.log | tail -2
echo "-- /imu/data hz:"; timeout 6 ros2 topic hz /imu/data 2>&1 | grep -E "average|does not" | tail -1
echo "-- /imu/data frame:"; timeout 5 ros2 topic echo /imu/data --once --field header.frame_id 2>/dev/null
echo "-- filtered hz:"; timeout 6 ros2 topic hz /odometry/filtered 2>&1 | grep -E "average|does not" | tail -1
echo "-- TF base_link -> camera_imu_optical_frame:"
timeout 6 ros2 run tf2_ros tf2_echo base_link camera_imu_optical_frame 2>&1 | grep -E "Translation|Rotation: in RPY \(degree\)" | head -2
echo "-- EKF warnings:"; grep -aiE "warn|error|could not|transform" /tmp/ekf.log | grep -v conditioner | tail -3 || echo none
echo "===STATIC 40s yaw drift==="
timeout 5 ros2 topic echo /odometry/filtered --once --field pose.pose.orientation 2>/dev/null | grep -E "^[zw]"
sleep 40
timeout 5 ros2 topic echo /odometry/filtered --once --field pose.pose.orientation 2>/dev/null | grep -E "^[zw]"
timeout 5 ros2 topic echo /odometry/filtered --once --field twist.twist.angular.z 2>/dev/null
