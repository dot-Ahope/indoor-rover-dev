#!/bin/bash
# EKF A 가 휠을 융합하지 않는 이유 확인 — f2b4 30 s 재생, /r2/wheel_A 와 /r2/ekfA 비교
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; export ROS_DOMAIN_ID=42
grep -A6 "odom0" /tmp/r2_ekfA.yaml | head -12
setsid python3 /tmp/r2_gate.py --ros-args -p use_sim_time:=true -p csv:=/tmp/dbg_gate.csv > /tmp/dbg_gate.log 2>&1 &
setsid ros2 run robot_localization ekf_node --ros-args -r __node:=ekfA --params-file /tmp/r2_ekfA.yaml -r odometry/filtered:=/r2/ekfA > /tmp/dbg_ekfA.log 2>&1 &
sleep 3
(ros2 bag play /tmp/bag_f2b4 --clock 100 --start-offset 60 --topics /scan /tf /tf_static /wheel_odom /imu/data /odometry/filtered > /dev/null 2>&1 &)
sleep 12
echo "== wheel_A"; timeout 5 ros2 topic echo --once /r2/wheel_A 2>&1 | grep -aE "frame_id|x:|covariance" | head -6
echo "== ekfA"; timeout 5 ros2 topic echo --once /r2/ekfA 2>&1 | grep -aE "frame_id|x:" | head -6
timeout 5 ros2 topic hz /r2/wheel_A 2>&1 | grep -a average | head -1
sleep 20; pkill -f r2_gate.py; pkill -f "__node:=ekfA"; pkill -f "ros2 bag play"
head -20 /tmp/dbg_ekfA.log
