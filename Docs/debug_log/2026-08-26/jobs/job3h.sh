#!/bin/bash
# 진단: 컨디셔너/EKF 중복 실행 여부 + /imu/data 발행자 수 + mag 상태
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
echo "===PROCESSES==="
pgrep -af "sensor_conditioner|ekf_node|static_transform" | sed 's/ --ros-args.*//'
echo "===IMU_DATA_PUBS==="
ros2 topic info /imu/data 2>/dev/null | grep -E "Publisher|Subscription"
echo "===NODE_LIST==="
ros2 node list
echo "===MAG_HZ==="
timeout 8 ros2 topic hz /imu/mag 2>&1 | tail -2 || true
