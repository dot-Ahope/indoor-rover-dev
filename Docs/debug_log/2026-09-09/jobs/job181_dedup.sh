#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
sed -i 's/\r$//' /tmp/camera.launch.py
cp /tmp/camera.launch.py ~/ros2_ws/src/rover_bringup/launch/
cp /tmp/camera.launch.py ~/ros2_ws/install/rover_bringup/share/rover_bringup/launch/
PATS="navigation.launch slam.launch sensors.launch navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense2_camera foxglove_bridge"
cnt() { local n=0 c; for p in $PATS; do c=$(pgrep -fc "$p" 2>/dev/null | head -1); c=${c:-0}; n=$((n+c)); done; echo $n; }
echo "정리 전 프로세스 합계: $(cnt)"
for p in $PATS; do pkill -TERM -f "$p" 2>/dev/null; done
for i in $(seq 1 15); do [ "$(cnt)" = "0" ] && break; sleep 1; done
echo "SIGTERM 후: $(cnt)"
if [ "$(cnt)" != "0" ]; then
  for p in $PATS; do pkill -9 -f "$p" 2>/dev/null; done; sleep 3
  echo "SIGKILL 후: $(cnt)"
fi
: > /tmp/sensors.log; : > /tmp/slam.log; : > /tmp/nav2.log
setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 30
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 14
setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &
sleep 30
echo "=== 검증 ==="
echo "  slam 인스턴스: $(pgrep -fc slam_toolbox) 개 (1 이 정상)"
echo "  /tf 발행 노드: $(timeout 8 ros2 topic info /tf --verbose 2>/dev/null | grep -a 'Node name' | sed 's/.*: //' | sort | uniq -c | tr '\n' ' ')"
for t in /camera/camera/imu /imu/data /odometry/filtered /map /scan; do
  printf "  %-24s " "$t"; timeout 10 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo 무발행
done
echo "  EKF 주기 위반: $(grep -ac 'Failed to meet update rate' /tmp/sensors.log 2>/dev/null)회"
echo "  slam 스캔 폐기: $(grep -ac 'Message Filter dropping' /tmp/slam.log 2>/dev/null)회"
echo "  Accel/Gyro 프로파일: $(grep -aoE 'stream_type: (Accel|Gyro)\(0\)Format: MOTION_XYZ32F, FPS: [0-9]+' /tmp/sensors.log | tail -2 | tr '\n' ' ')"
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg)"
top -b -n2 -d1 -o %CPU 2>/dev/null | awk '/PID +USER/{f++} f==2' | head -6 | awk '{printf "    %-18s %6s%%\n", $12, $9}'
