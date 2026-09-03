#!/bin/bash
# 손 이동 후 초기화 — agent 는 절대 건드리지 않음(디버거 없어 RESET 불가)
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 보드 세션 확인 (유지되어야 함) ==="
echo -n "  agent: "; docker ps --format '{{.Names}}' | grep microros || echo "없음!"
echo -n "  /wheel_odom: "; timeout 6 ros2 topic hz /wheel_odom 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1 || echo "무발행 ★RESET 필요"
echo -n "  배터리: "; timeout 5 ros2 topic echo /battery --once 2>/dev/null | grep -aoE "voltage: [0-9.]+" | head -1
echo "=== EKF/slam 재시작 (자이로 캘리브 ~10s, 정지!) ==="
pkill -f sensor_conditioner; pkill -f ekf_node; pkill -f slam_toolbox; pkill -f "slam.launch"; sleep 3
setsid nohup ros2 launch rover_bringup ekf.launch.py > /tmp/ekf.log 2>&1 &
sleep 16
grep -a "gyro bias\|not stationary" /tmp/ekf.log | tail -1
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 10
echo "=== 검증 ==="
echo -n "  /odometry/filtered: "; timeout 5 ros2 topic hz /odometry/filtered 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1
echo -n "  odom 원점: "; timeout 4 ros2 topic echo /odometry/filtered --once 2>/dev/null | grep -aoE "x: [-0-9.e]+" | head -1
echo -n "  /scan: "; timeout 4 ros2 topic hz /scan 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1
