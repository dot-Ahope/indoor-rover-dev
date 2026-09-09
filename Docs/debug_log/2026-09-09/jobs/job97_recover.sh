#!/bin/bash
# 보드 RESET 후 복구: ① 보드 토픽 규정 주기 확인(실패 시 중단) ② EKF/SLAM/Nav2 재기동
# agent 컨테이너와 base.launch 는 건드리지 않는다 (건드리면 또 RESET 이 필요해짐).
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash

echo "=== ① 보드 토픽 규정 주기 확인 ==="
rate() { timeout 10 ros2 topic hz "$1" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 | grep -aoE "[0-9.]+$"; }
WO=$(rate /wheel_odom); IM=$(rate /imu/data_raw); ST=$(rate /rover/status); BT=$(rate /battery)
printf "  %-16s %s  (기대 ~29)\n" /wheel_odom   "${WO:-0}"
printf "  %-16s %s  (기대 ~29)\n" /imu/data_raw "${IM:-0}"
printf "  %-16s %s  (기대 5.0)\n" /rover/status "${ST:-0}"
printf "  %-16s %s  (기대 1.0)\n" /battery      "${BT:-0}"
OK=$(python3 -c "print(1 if float('${WO:-0}')>20 and float('${IM:-0}')>20 else 0)")
if [ "$OK" != "1" ]; then
  echo ""
  echo "!! 큰 메시지가 아직 규정 주기가 아님 — 세션이 여전히 반쪽입니다. 재기동 중단."
  echo "   (RESET 이 먹지 않았거나 agent 재생성이 필요할 수 있음)"
  exit 2
fi
echo "  → 세션 정상. 재기동 진행."
echo ""

echo "=== ② 발산 EKF·오염 SLAM 맵 폐기 (sensors/slam/nav2 종료) ==="
pkill -f "navigation_launch\|controller_server\|planner_server\|bt_navigator\|behavior_server\|velocity_smoother\|smoother_server\|waypoint_follower\|lifecycle_manager_navigation\|stuck_monitor" 2>/dev/null
pkill -f "slam.launch\|slam_toolbox" 2>/dev/null
pkill -f "sensors.launch\|realsense\|rplidar\|scan_deskew\|ekf_node\|sensor_conditioner\|foxglove" 2>/dev/null
sleep 5
echo "  잔여 프로세스: $(pgrep -fc 'slam_toolbox|ekf_node|realsense|rplidar|controller_server' 2>/dev/null || echo 0)"
echo ""

echo "=== ③ sensors.launch (자이로 캘리브 ~10s, 로버 정지 유지) ==="
setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 24
grep -a "gyro bias\|not stationary" /tmp/sensors.log | tail -1 || echo "  (캘리브 로그 없음)"

echo "=== ④ slam.launch ==="
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 12

echo "=== ⑤ navigation.launch ==="
setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &
sleep 25

echo ""
echo "=== ⑥ 검증 ==="
for t in /wheel_odom /wheel_odom/conditioned /odometry/filtered /scan /map /camera/camera/depth/color/points; do
  printf "  %-38s " "$t"; timeout 8 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo "무발행"
done
echo -n "  map->odom : "; timeout 5 ros2 run tf2_ros tf2_echo map odom 2>/dev/null | grep -aE "Translation" | head -1
echo -n "  odom->base: "; timeout 5 ros2 run tf2_ros tf2_echo odom base_link 2>/dev/null | grep -aE "Translation" | head -1
echo "  lifecycle:"
for nd in /controller_server /planner_server /bt_navigator /behavior_server /velocity_smoother; do
  printf "    %-22s " "$nd"; timeout 6 ros2 lifecycle get "$nd" 2>/dev/null || echo "?"
done
echo "  nav2 오류: $(grep -aiE 'error|fail|exception' /tmp/nav2.log | tail -3 | tr '\n' ' ')"
echo "  배터리: $(timeout 5 ros2 topic echo /battery --once 2>/dev/null | grep -aoE 'voltage: [0-9.]+' | head -1)"
