#!/bin/bash
# conditioner vx보정 반영: 소스갱신 → 재빌드 → EKF+SLAM 새로 재시작. 로버 정지 유지!
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
cp /tmp/sensor_conditioner.py ~/ros2_ws/src/rover_bringup/scripts/sensor_conditioner.py
echo "=== 재빌드 ==="
cd ~/ros2_ws && colcon build --packages-select rover_bringup 2>&1 | tail -3
source ~/ros2_ws/install/setup.bash
echo "=== 기존 EKF/SLAM 종료 ==="
pkill -f sensor_conditioner; pkill -f ekf_node; pkill -f slam_toolbox; sleep 3
echo "=== EKF 재시작 (자이로 캘리브 ~10s, 로버 정지!) ==="
setsid nohup ros2 launch rover_bringup ekf.launch.py > /tmp/ekf2.log 2>&1 &
sleep 14
grep -a "gyro bias\|not stationary" /tmp/ekf2.log | tail -1
echo "=== SLAM 재시작 ==="
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam2.log 2>&1 &
sleep 10
echo "=== 검증 ==="
echo "노드: $(ros2 node list 2>/dev/null | grep -E 'ekf|slam|conditioner|camera|rplidar|scan_deskew' | tr '\n' ' ')"
echo -n "/odometry/filtered: "; timeout 4 ros2 topic hz /odometry/filtered 2>&1 | grep -aE "average rate" | head -1
echo -n "map->odom TF: "; timeout 4 ros2 run tf2_ros tf2_echo map odom 2>/dev/null | grep -aE "Translation" | head -1
echo "conditioner vx보정: $(grep -a VX_SCALE ~/ros2_ws/src/rover_bringup/scripts/sensor_conditioner.py | grep -v '#' | head -1)"
