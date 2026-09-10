#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 현재 map→odom 보정량 (0 이면 SLAM 보정 없음) ==="
timeout 10 ros2 run tf2_ros tf2_echo map odom 2>/dev/null | grep -aE "Translation|Rotation: in RPY \(degree\)" | tail -2 | sed 's/^/  /'
echo "=== 현재 로버 위치 ==="
timeout 8 ros2 run tf2_ros tf2_echo map base_link 2>/dev/null | grep -aE "Translation" | tail -1 | sed 's/^/  /'
echo "=== 지금 보이는 장애물 (base_link) ==="
python3 /tmp/job62c_boxdim.py 2>/dev/null | grep -aE "^    y |장애물층" | head -6 | sed 's/^/  /'
echo "=== 카메라 포인트클라우드 생존 ==="
printf "  %-34s " /camera/camera/depth/color/points; timeout 8 ros2 topic hz /camera/camera/depth/color/points 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo 무발행
echo "=== 건전성 ==="
echo "  EKF 위반: $(grep -ac 'Failed to meet update rate' /tmp/sensors.log 2>/dev/null)회 | slam 폐기: $(grep -ac 'Message Filter dropping' /tmp/slam.log 2>/dev/null)회 | load: $(cut -d' ' -f1-3 /proc/loadavg)"
echo "  배터리: $(timeout 5 ros2 topic echo /battery --once 2>/dev/null | grep -aoE 'voltage: [0-9.]+')"
