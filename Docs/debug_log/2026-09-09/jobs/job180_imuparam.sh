#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 배포 파일 내용 ==="
grep -nE "gyro_fps|accel_fps|unite_imu" ~/ros2_ws/install/rover_bringup/share/rover_bringup/launch/camera.launch.py | sed 's/^/  /'
echo "=== 실행 중 카메라 노드 파라미터 ==="
for p in gyro_fps accel_fps unite_imu_method enable_gyro enable_accel; do
  printf "  %-20s " "$p"; timeout 6 ros2 param get /camera/camera "$p" 2>/dev/null | sed 's/^.*is: //' || echo "?"
done
echo "=== 카메라 로그의 IMU 프로파일 ==="
grep -aiE "Open profile.*(Accel|Gyro)" /tmp/sensors.log 2>/dev/null | tail -4 | cut -c1-150 | sed 's/^/  /'
echo "=== 지원되는 IMU 프로파일 ==="
grep -aiE "Gyro|Accel" /tmp/sensors.log 2>/dev/null | grep -aiE "FPS" | tail -6 | cut -c1-150 | sed 's/^/  /'
echo ""
echo "=== /tf 발행 주체 (중복 확인) ==="
timeout 8 ros2 topic info /tf --verbose 2>/dev/null | grep -aE "Node name" | sort | uniq -c | sed 's/^/  /'
