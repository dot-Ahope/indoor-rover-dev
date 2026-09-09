#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== TF 발행 주체 ==="
timeout 8 ros2 topic info /tf --verbose 2>/dev/null | grep -aE "Publisher count|Node name" | head -8 | sed 's/^/  /'
echo "=== 각 토픽 ==="
for t in /tf /odometry/filtered /map /wheel_odom /wheel_odom/conditioned /imu/data /scan; do
  printf "  %-26s " "$t"; timeout 8 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo 무발행
done
echo "=== 프로세스 생존 ==="
for p in ekf_node slam_toolbox sensor_conditioner rplidar realsense robot_state_publisher; do
  pid=$(pgrep -f "$p" | head -1)
  printf "  %-22s %s\n" "$p" "$([ -n "$pid" ] && ps -p $pid -o %cpu=,stat= | tr -s ' ' || echo 없음)"
done
echo "=== 노드 목록 ==="
ros2 node list 2>/dev/null | tr '\n' ' '
echo ""
echo "=== SHM ==="
echo "  fastrtps 파일: $(ls /dev/shm 2>/dev/null | grep -c fastrtps)  SHM오류: $(grep -ac RTPS_TRANSPORT_SHM /tmp/sensors.log /tmp/slam.log /tmp/nav2.log 2>/dev/null | tr '\n' ' ')"
echo "=== 로그 마지막 ==="
echo "-- sensors:"; tail -3 /tmp/sensors.log | cut -c1-140 | sed 's/^/    /'
echo "-- slam:";    tail -3 /tmp/slam.log    | cut -c1-140 | sed 's/^/    /'
echo "=== 부하/메모리 ==="
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg)"
free -m | head -2 | sed 's/^/  /'
top -b -n2 -d1 -o %CPU 2>/dev/null | awk '/PID +USER/{f++} f==2' | head -6 | awk '{printf "    %-18s %6s%%\n", $12, $9}'
