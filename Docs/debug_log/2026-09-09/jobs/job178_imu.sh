#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
sed -i 's/\r$//' /tmp/camera.launch.py
cp /tmp/camera.launch.py ~/ros2_ws/src/rover_bringup/launch/
cp /tmp/camera.launch.py ~/ros2_ws/install/rover_bringup/share/rover_bringup/launch/
echo "배포: $(grep -aoE \"'gyro_fps': [0-9]+\" ~/ros2_ws/install/rover_bringup/share/rover_bringup/launch/camera.launch.py)"
echo "=== sensors + slam + nav2 재기동 (SIGTERM) ==="
for p in navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense foxglove; do pkill -TERM -f "$p" 2>/dev/null; done
pkill -TERM -f "sensors.launch" 2>/dev/null; pkill -TERM -f "slam.launch" 2>/dev/null; pkill -TERM -f "navigation.launch" 2>/dev/null
for i in $(seq 1 15); do
  [ "$(pgrep -fc 'ekf_node|slam_toolbox|realsense|rplidar|foxglove|sensor_conditioner|controller_server' 2>/dev/null || echo 0)" = "0" ] && break; sleep 1
done
echo "  잔존: $(pgrep -fc 'ekf_node|slam_toolbox|realsense|rplidar|foxglove|sensor_conditioner|controller_server' 2>/dev/null || echo 0)"
: > /tmp/sensors.log; : > /tmp/slam.log
setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 28
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 14
setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &
sleep 30
echo "=== 효과 검증 ==="
printf "  %-24s " /camera/camera/imu; timeout 8 ros2 topic hz /camera/camera/imu 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
printf "  %-24s " /imu/data;          timeout 8 ros2 topic hz /imu/data 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
printf "  %-24s " /odometry/filtered; timeout 8 ros2 topic hz /odometry/filtered 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
printf "  %-24s " /map;               timeout 12 ros2 topic hz /map 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
printf "  %-24s " /tf;                timeout 8 ros2 topic hz /tf 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
echo "  /tf 퍼블리셔: $(timeout 6 ros2 topic info /tf 2>/dev/null | grep -aoE 'Publisher count: [0-9]+')  (3 이 정상)"
echo "  slam 노드: $(ros2 node list 2>/dev/null | grep -a slam_toolbox || echo '없음!')"
echo "  EKF 주기 위반: $(grep -ac 'Failed to meet update rate' /tmp/sensors.log 2>/dev/null)회"
echo "  slam 스캔 폐기: $(grep -ac 'Message Filter dropping' /tmp/slam.log 2>/dev/null)회"
echo "  sensor_conditioner CPU: $(ps -p $(pgrep -f sensor_conditioner | head -1) -o %cpu= 2>/dev/null | tr -d ' ')%"
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg)"
top -b -n2 -d1 -o %CPU 2>/dev/null | awk '/PID +USER/{f++} f==2' | head -6 | awk '{printf "    %-18s %6s%%\n", $12, $9}'
