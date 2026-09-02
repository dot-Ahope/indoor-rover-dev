#!/bin/bash
# 세션 초기화: base(agent+rsp)+sensors(camera+lidar+ekf+foxglove)+slam. 보드 RESET됨. 로버 정지!
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== stale 정리 ==="
for p in "base.launch" "sensors.launch" "slam.launch" "joy_teleop" realsense rplidar scan_deskew ekf_node sensor_conditioner foxglove robot_state_publisher slam_toolbox joy_linux teleop; do pkill -9 -f "$p" 2>/dev/null; done
docker rm -f microros_agent >/dev/null 2>&1; sleep 3
echo "=== base.launch (agent+rsp) ==="
setsid nohup ros2 launch rover_bringup base.launch.py > /tmp/base.log 2>&1 &
sleep 10
docker ps --format '{{.Names}} {{.Status}}' | grep microros || echo "AGENT_DOWN!"
echo -n "보드 /wheel_odom: "; timeout 5 ros2 topic hz /wheel_odom 2>&1 | grep -aE "average rate" | head -1 || echo "무발행(보드 미연결?)"
echo "=== sensors.launch (자이로 캘리브 ~10s, 로버 정지!) ==="
setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 16
grep -a "gyro bias\|not stationary" /tmp/sensors.log | tail -1
echo "=== slam.launch ==="
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 10
echo "=== 검증 ==="
echo "노드: $(ros2 node list 2>/dev/null | grep -E 'rover_jupiter|ekf|slam|conditioner|camera|rplidar|scan_deskew|foxglove' | tr '\n' ' ')"
echo -n "/odometry/filtered: "; timeout 4 ros2 topic hz /odometry/filtered 2>&1 | grep -aE "average rate" | head -1
echo -n "/scan: "; timeout 4 ros2 topic hz /scan 2>&1 | grep -aE "average rate" | head -1
echo -n "map->odom TF: "; timeout 4 ros2 run tf2_ros tf2_echo map odom 2>/dev/null | grep -aE "Translation" | head -1 || echo "없음"
echo "vx보정: $(grep -a 'VX_SCALE = ' ~/ros2_ws/src/rover_bringup/scripts/sensor_conditioner.py | grep -v '#' | head -1)"
echo "완료 — Foxglove fixed_frame=odom에서 관찰 준비됨"
