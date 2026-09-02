#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 카메라 토픽 목록 ==="
ros2 topic list 2>/dev/null | grep -E "camera" | head -40
echo ""
echo "=== 카메라 enable 파라미터 ==="
for p in enable_color enable_depth enable_gyro enable_accel enable_infra1 enable_infra2 pointcloud.enable enable_sync unite_imu_method; do
  echo -n "  $p: "; ros2 param get /camera/camera $p 2>/dev/null | grep -aoE "value is:.*|Boolean.*|String.*" | head -1 || echo "?"
done
echo ""
echo "=== 이미지 스트림 실제 발행 여부 (CPU 소비 확인) ==="
for t in /camera/camera/color/image_raw /camera/camera/depth/image_rect_raw /camera/camera/infra1/image_rect_raw; do
  echo -n "  $t: "; timeout 3 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1 || echo "무발행/없음"
done
echo ""
echo "=== 현재 CPU 상위 6 ==="
top -b -n 2 -d 1 -o %CPU | awk '/PID +USER/{f++} f==2' | head -8 | awk '{printf "  %-16s %5s%%\n",$12,$9}'
