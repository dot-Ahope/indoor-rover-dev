#!/bin/bash
# EKF가 /imu/data 를 실제로 융합하는지 진단: 타임스탬프 정합, 구독 QoS, 값 분포
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===NOW==="; date +%s.%N
echo "===/imu/data stamp==="; timeout 5 ros2 topic echo /imu/data --once --field header.stamp 2>/dev/null
echo "===/camera/camera/imu stamp==="; timeout 5 ros2 topic echo /camera/camera/imu --once --field header.stamp 2>/dev/null
echo "===/wheel_odom/conditioned stamp==="; timeout 5 ros2 topic echo /wheel_odom/conditioned --once --field header.stamp 2>/dev/null
echo "===/odometry/filtered stamp==="; timeout 5 ros2 topic echo /odometry/filtered --once --field header.stamp 2>/dev/null
echo "===/imu/data subscribers==="; ros2 topic info /imu/data --verbose 2>/dev/null | grep -aE "Node name|Endpoint type|Reliability|Durability" 
echo "===gyro z samples (10, conditioned)==="; timeout 6 ros2 topic echo /imu/data --field angular_velocity.z 2>/dev/null | grep -av -- "---" | head -10 | tr '\n' ' '; echo
echo "===filtered vyaw samples (10)==="; timeout 6 ros2 topic echo /odometry/filtered --field twist.twist.angular.z 2>/dev/null | grep -av -- "---" | head -10 | tr '\n' ' '; echo
echo "===camera global time param==="; ros2 param get /camera/camera global_time_enabled 2>/dev/null
echo "===EKF params==="; ros2 param get /ekf_filter_node imu0 2>/dev/null; ros2 param get /ekf_filter_node imu0_config 2>/dev/null | cut -c1-120
