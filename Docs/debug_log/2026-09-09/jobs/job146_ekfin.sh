#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== EKF 입력 계통 ==="
for t in /wheel_odom /wheel_odom/conditioned /camera/camera/imu /imu/data /odometry/filtered /tf /map /scan; do
  printf "  %-28s " "$t"; timeout 9 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo 무발행
done
echo ""
echo "=== 각 노드 CPU ==="
for p in ekf_node sensor_conditioner slam_toolbox realsense rplidar foxglove; do
  pid=$(pgrep -f "$p" | head -1)
  [ -n "$pid" ] && printf "  %-20s pid %-7s CPU %s%%  상태 %s\n" "$p" "$pid" "$(ps -p $pid -o %cpu= | tr -d ' ')" "$(ps -p $pid -o stat= | tr -d ' ')"
done
echo ""
echo "=== sensor_conditioner 최근 로그 ==="
grep -a "conditioner" /tmp/sensors.log 2>/dev/null | tail -6 | cut -c1-150
echo ""
echo "=== 카메라 최근 로그 ==="
grep -aiE "realsense|camera" /tmp/sensors.log 2>/dev/null | tail -6 | cut -c1-150
