#!/bin/bash
# Step 3: EKF 구성 반영 → 빌드 → static TF(imu_link) + ekf_node 기동 → 정적 검증
set -e
source /opt/ros/humble/setup.bash

cp -r /tmp/rover_src/rover_description /tmp/rover_src/rover_bringup ~/ros2_ws/src/
cd ~/ros2_ws
echo "===COLCON_BUILD==="
colcon build --symlink-install 2>&1 | tail -4

source ~/ros2_ws/install/setup.bash

# 임시 static TF: base_link -> imu_link (URDF 반영은 다음 bringup 재시작 시)
if ! pgrep -f "static_transform_publisher.*imu_link" > /dev/null; then
  setsid nohup ros2 run tf2_ros static_transform_publisher --x -0.01 --y 0.01 --z 0.08 --frame-id base_link --child-frame-id imu_link > /tmp/imu_tf.log 2>&1 &
  echo "static TF started"
fi

# EKF 기동 (기존 인스턴스 정리 후)
pkill -f "ekf_node" 2>/dev/null || true
sleep 1
setsid nohup ros2 launch rover_bringup ekf.launch.py > /tmp/ekf.log 2>&1 &
echo $! > /tmp/ekf.pid
sleep 12

echo "===NODE_LIST==="
ros2 node list
echo "===EKF_LOG_TAIL==="
tail -5 /tmp/ekf.log
echo "===HZ_FILTERED==="
timeout 10 ros2 topic hz /odometry/filtered 2>&1 | tail -2 || true
echo "===FILTERED_POSE==="
timeout 6 ros2 topic echo /odometry/filtered --once --field pose.pose 2>/dev/null || echo NO_FILTERED_MSG
echo "===QOS_WHEEL_ODOM==="
ros2 topic info /wheel_odom --verbose 2>/dev/null | grep -E "Node name|Reliability|Endpoint type" | head -12
