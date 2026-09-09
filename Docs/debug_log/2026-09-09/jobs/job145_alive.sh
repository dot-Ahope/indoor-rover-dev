#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 살아있는 프로세스 ==="
for p in robot_state_publisher ekf_node sensor_conditioner realsense rplidar scan_deskew slam_toolbox foxglove micro_ros; do
  printf "  %-22s %s\n" "$p" "$(pgrep -fc "$p" 2>/dev/null || echo 0)"
done
echo "  docker: $(docker ps -q | wc -l)"
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg)"
echo ""
echo "=== 토픽 발행률 ==="
for t in /tf /odometry/filtered /wheel_odom /scan /map; do
  printf "  %-20s " "$t"; timeout 8 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo 무발행
done
echo ""
echo "=== sensors.log 에서 ekf/노드 사망 흔적 ==="
grep -aiE "died|exit code|Failed to meet update rate" /tmp/sensors.log 2>/dev/null | tail -6 | cut -c1-140
echo ""
echo "=== /dev/shm 사용량 (FastDDS SHM) ==="
df -h /dev/shm | tail -1
ls /dev/shm 2>/dev/null | wc -l | sed 's/^/  파일 수: /'
echo ""
echo "=== 시스템 메모리 ==="
free -m | head -2
