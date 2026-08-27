#!/bin/bash
# imu0_config 축 수정 배포 → EKF 재시작 → filtered vyaw에 자이로 반영 확인 + 30s 정적 드리프트
source /opt/ros/humble/setup.bash
cp /tmp/rover_src/rover_bringup/config/ekf.yaml ~/ros2_ws/src/rover_bringup/config/ekf.yaml
cd ~/ros2_ws && colcon build --symlink-install --packages-select rover_bringup 2>&1 | tail -1
source ~/ros2_ws/install/setup.bash
grep -A4 "imu0_config" ~/ros2_ws/install/rover_bringup/share/rover_bringup/config/ekf.yaml | tail -2
pkill -f "ekf.launch" 2>/dev/null; pkill -f ekf_node 2>/dev/null; pkill -f sensor_conditioner 2>/dev/null; sleep 1
setsid nohup ros2 launch rover_bringup ekf.launch.py > /tmp/ekf.log 2>&1 &
sleep 20
echo "-- conditioner:"; grep -aE "bias|stationary" /tmp/ekf.log | tail -1 | cut -c60-200
echo "-- filtered vyaw samples (should be small NONZERO now):"
timeout 6 ros2 topic echo /odometry/filtered --field twist.twist.angular.z 2>/dev/null | grep -av -- "---" | head -8 | tr '\n' ' '; echo
echo "-- filtered hz:"; timeout 6 ros2 topic hz /odometry/filtered 2>&1 | grep -aE "average|does not" | tail -1
echo "===STATIC 30s yaw==="
timeout 5 ros2 topic echo /odometry/filtered --once --field pose.pose.orientation 2>/dev/null | grep -aE "^[zw]"
sleep 30
timeout 5 ros2 topic echo /odometry/filtered --once --field pose.pose.orientation 2>/dev/null | grep -aE "^[zw]"
