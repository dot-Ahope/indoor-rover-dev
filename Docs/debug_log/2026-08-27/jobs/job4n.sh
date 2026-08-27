#!/bin/bash
# job4m 검증부 재실행 (텍스트 안전)
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===PROCS==="; pgrep -af "realsense2_camera_node|ekf_node|sensor_conditioner|rplidar_node" | cut -c1-90
echo "===camera imu hz==="; timeout 6 ros2 topic hz /camera/camera/imu 2>&1 | grep -aE "average|does not" | tail -1
echo "===conditioner log==="; grep -aE "bias|stationary" /tmp/ekf.log | tail -2 | cut -c1-200
echo "===/imu/data hz==="; timeout 6 ros2 topic hz /imu/data 2>&1 | grep -aE "average|does not" | tail -1
echo "===/imu/data frame==="; timeout 5 ros2 topic echo /imu/data --once --field header.frame_id 2>/dev/null
echo "===filtered hz==="; timeout 6 ros2 topic hz /odometry/filtered 2>&1 | grep -aE "average|does not" | tail -1
echo "===TF base_link->camera_imu_optical_frame==="; timeout 6 ros2 run tf2_ros tf2_echo base_link camera_imu_optical_frame 2>&1 | grep -aE "Translation|RPY \(degree\)" | head -2
echo "===EKF warnings==="; grep -aiE "warn|error|could not|transform" /tmp/ekf.log | grep -av conditioner | tail -3 | cut -c1-200; echo "(end)"
echo "===STATIC 40s yaw==="
timeout 5 ros2 topic echo /odometry/filtered --once --field pose.pose.orientation 2>/dev/null | grep -aE "^[zw]"
sleep 40
timeout 5 ros2 topic echo /odometry/filtered --once --field pose.pose.orientation 2>/dev/null | grep -aE "^[zw]"
echo "-- filtered vyaw:"; timeout 5 ros2 topic echo /odometry/filtered --once --field twist.twist.angular.z 2>/dev/null
