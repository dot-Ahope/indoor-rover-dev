#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "배포 확인: $(grep -aoE \"gyro_fps.: [0-9]+\" ~/ros2_ws/install/rover_bringup/share/rover_bringup/launch/camera.launch.py | head -1)"
PATS="navigation.launch slam.launch sensors.launch navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense2_camera foxglove_bridge"
echo "=== 1단계 SIGTERM ==="
for p in $PATS; do pkill -TERM -f "$p" 2>/dev/null; done
for i in $(seq 1 15); do
  n=0; for p in $PATS; do n=$((n+$(pgrep -fc "$p" 2>/dev/null || echo 0))); done
  [ "$n" = "0" ] && break; sleep 1
done
n=0; for p in $PATS; do n=$((n+$(pgrep -fc "$p" 2>/dev/null || echo 0))); done
echo "  15초 후 잔존: $n"
if [ "$n" != "0" ]; then
  echo "=== 2단계 SIGKILL (SHM 비활성이라 잔재 위험 없음) ==="
  for p in $PATS; do pkill -9 -f "$p" 2>/dev/null; done
  sleep 3
  n=0; for p in $PATS; do n=$((n+$(pgrep -fc "$p" 2>/dev/null || echo 0))); done
  echo "  최종 잔존: $n"
  for p in $PATS; do c=$(pgrep -fc "$p" 2>/dev/null || echo 0); [ "$c" != "0" ] && echo "    남음: $p ($c)"; done
fi
echo "=== 재기동 ==="
: > /tmp/sensors.log; : > /tmp/slam.log; : > /tmp/nav2.log
setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 30
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 14
setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &
sleep 30
echo "=== 검증 ==="
printf "  %-24s " /camera/camera/imu; timeout 8 ros2 topic hz /camera/camera/imu 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
printf "  %-24s " /imu/data;          timeout 8 ros2 topic hz /imu/data 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
printf "  %-24s " /odometry/filtered; timeout 8 ros2 topic hz /odometry/filtered 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
printf "  %-24s " /map;               timeout 12 ros2 topic hz /map 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
echo "  /tf 퍼블리셔: $(timeout 6 ros2 topic info /tf 2>/dev/null | grep -aoE 'Publisher count: [0-9]+')"
echo "  slam 노드: $(ros2 node list 2>/dev/null | grep -a slam_toolbox || echo '없음!')"
echo "  EKF 주기 위반: $(grep -ac 'Failed to meet update rate' /tmp/sensors.log 2>/dev/null)회"
echo "  slam 스캔 폐기: $(grep -ac 'Message Filter dropping' /tmp/slam.log 2>/dev/null)회"
echo "  sensor_conditioner CPU: $(ps -p $(pgrep -f sensor_conditioner | head -1) -o %cpu= 2>/dev/null | tr -d ' ')%"
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg)"
top -b -n2 -d1 -o %CPU 2>/dev/null | awk '/PID +USER/{f++} f==2' | head -7 | awk '{printf "    %-18s %6s%%\n", $12, $9}'
