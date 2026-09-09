#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 전체 토픽 주기 (460800) ==="
for t in /wheel_odom /imu/data_raw /imu/mag /rover/status /battery /wheel_odom/conditioned /odometry/filtered /scan /map /camera/camera/depth/color/points; do
  printf "  %-38s " "$t"
  r=$(timeout 9 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1)
  echo "${r:-무발행}"
done
echo ""
echo "=== TF / EKF ==="
echo -n "  map->odom : "; timeout 5 ros2 run tf2_ros tf2_echo map odom 2>/dev/null | grep -aE "Translation" | head -1
echo -n "  odom->base: "; timeout 5 ros2 run tf2_ros tf2_echo odom base_link 2>/dev/null | grep -aE "Translation" | head -1
echo "  배터리: $(timeout 5 ros2 topic echo /battery --once 2>/dev/null | grep -aoE 'voltage: [0-9.]+' | head -1)"
echo ""
echo "=== ch341 드라이버 오류/오버런 흔적 (무비용 확인) ==="
dmesg 2>/dev/null | grep -aiE "ch341|ch34x|usb 1-2|overrun|frame error|parity" | tail -12
echo "  (위가 비어있으면 커널이 보고한 오류 없음)"
echo ""
echo "=== USB 장치 오류 카운터 ==="
for d in /sys/bus/usb/devices/1-2.1; do
  [ -d "$d" ] || continue
  echo "  speed=$(cat $d/speed 2>/dev/null) Mbps  product=$(cat $d/product 2>/dev/null)"
done
echo "  URB 오류(가능 시): $(cat /sys/kernel/debug/usb/devices 2>/dev/null | grep -ac . || echo '접근불가')"
