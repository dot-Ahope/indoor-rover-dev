#!/bin/bash
# 부팅 후 full 스택 기동: base(agent+RSP) → sensors(camera/lidar/ekf/foxglove) → slam. 로버 정지!
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "날짜: $(date '+%Y-%m-%d %H:%M')"
echo "=== 잔여 정리 ==="
for p in "base.launch" "sensors.launch" "slam.launch" realsense rplidar scan_deskew ekf_node sensor_conditioner foxglove robot_state_publisher slam_toolbox joy_linux teleop; do pkill -9 -f "$p" 2>/dev/null; done
docker rm -f microros_agent >/dev/null 2>&1; sleep 2
echo "=== base.launch (agent+RSP) ==="
setsid nohup ros2 launch rover_bringup base.launch.py > /tmp/base.log 2>&1 &
sleep 12
docker ps --format '{{.Names}} {{.Status}}' | grep microros || echo "AGENT_DOWN!"
echo -n "보드 /wheel_odom: "; timeout 6 ros2 topic hz /wheel_odom 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1 || echo "무발행(보드 미연결)"
echo -n "배터리: "; timeout 5 ros2 topic echo /battery --once 2>/dev/null | grep -aoE "voltage: [0-9.]+" | head -1
echo "=== sensors.launch (자이로 캘리브 ~10s, 정지!) ==="
setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 22
grep -a "gyro bias\|not stationary" /tmp/sensors.log | tail -1 || echo "  (캘리브 로그 없음)"
echo "=== slam.launch ==="
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 10
echo "=== 검증 ==="
echo "  노드: $(ros2 node list 2>/dev/null | grep -E 'rover_jupiter|camera|rplidar|scan_deskew|ekf|conditioner|slam|foxglove' | tr '\n' ' ')"
echo -n "  /odometry/filtered: "; timeout 4 ros2 topic hz /odometry/filtered 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1
echo -n "  /scan: "; timeout 4 ros2 topic hz /scan 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1
echo "  VX_SCALE: $(grep -a '^VX_SCALE' ~/ros2_ws/src/rover_bringup/scripts/sensor_conditioner.py)"
echo -n "  odom 원점: "; timeout 4 ros2 topic echo /odometry/filtered --once 2>/dev/null | grep -aoE "x: [-0-9.e]+" | head -1
echo -n "  map->odom: "; timeout 5 ros2 run tf2_ros tf2_echo map odom 2>/dev/null | grep -aE "Translation" | head -1
