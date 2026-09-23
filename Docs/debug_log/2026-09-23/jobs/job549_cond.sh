#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash
echo "## 카메라 IMU 원본 covariance"; timeout 8 ros2 topic echo --once /camera/camera/imu 2>/dev/null | grep -aA1 "covariance:" | grep -av "^--" | head -8
echo "## 휠 오도 원본 twist covariance 0 아닌 개수"; timeout 8 ros2 topic echo --once /wheel_odom 2>/dev/null | sed -n "/twist:/,\$p" | grep -aA36 "covariance:" | grep -acE "^- [1-9]|^- 0\.0*[1-9]"
echo "## 원본/출력 Hz: $(timeout 6 ros2 topic hz /camera/camera/imu 2>&1 | grep -ao "average rate: [0-9.]*" | head -1) / $(timeout 6 ros2 topic hz /imu/data 2>&1 | grep -ao "average rate: [0-9.]*" | head -1)"
echo "## 컨디셔너 CPU: $(top -b -n2 -d5 | awk '/PID +USER/{f++} f==2' | while read p u pr ni v r s st c m t cmd; do [ "$cmd" = python3 ] && ps -o args= -p $p | grep -q sensor_conditioner && echo "$c %"; done)"
echo "## 설치된 대안 패키지: $(ros2 pkg list 2>/dev/null | grep -E "imu_complementary|imu_filter_madgwick|imu_tools" | tr "\n" " ")"
echo "## 최근 ZUPT 로그"; grep -a "ZUPT\|gyro bias" /tmp/sensors.log | tail -3 | cut -c1-170
