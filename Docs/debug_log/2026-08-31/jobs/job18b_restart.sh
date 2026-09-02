#!/bin/bash
# sensors+slam 깨끗이 재시작 (base/agent 유지 → 보드 RESET 불필요). 로버 정지 유지!
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== base/agent 유지 확인 ==="
docker ps --format '{{.Names}}' | grep -q microros && echo "  agent 살아있음(보드 RESET 불필요)" || echo "  !! agent 없음 — base 재기동 필요"
echo "=== sensors/slam 계열만 종료 (base.launch·RSP는 보존) ==="
pkill -f "sensors.launch"; pkill -f "slam.launch"
for p in realsense rplidar scan_deskew ekf_node sensor_conditioner slam_toolbox foxglove joy_linux teleop_twist_joy; do pkill -9 -f "$p" 2>/dev/null; done
sleep 4
echo "  남은 관련 노드: $(ros2 node list 2>/dev/null | grep -E 'camera|rplidar|deskew|ekf|slam|conditioner|foxglove' | tr '\n' ' ')"
echo "=== sensors.launch 기동 (자이로 캘리브 ~10s, 로버 정지!) ==="
setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 20
grep -a "gyro bias\|not stationary" /tmp/sensors.log | tail -1 || echo "  (캘리브 로그 대기중)"
echo "=== slam.launch 기동 ==="
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 10
echo "=== 검증 ==="
echo "  노드: $(ros2 node list 2>/dev/null | grep -E 'rover_jupiter|camera|rplidar|scan_deskew|ekf|conditioner|slam|foxglove' | tr '\n' ' ')"
echo -n "  /odometry/filtered: "; timeout 4 ros2 topic hz /odometry/filtered 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1
echo -n "  /scan: "; timeout 4 ros2 topic hz /scan 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1
echo -n "  odom 원점 확인: "; timeout 4 ros2 topic echo /odometry/filtered --once 2>/dev/null | grep -aA2 "position:" | grep -aoE "x: [-0-9.e]+" | head -1
echo -n "  map->odom: "; timeout 5 ros2 run tf2_ros tf2_echo map odom 2>/dev/null | grep -aE "Translation" | head -1 || echo "대기중"
echo "  foxglove: $(pgrep -f foxglove_bridge | wc -l)개, deskew: $(pgrep -f scan_deskew | wc -l)"
