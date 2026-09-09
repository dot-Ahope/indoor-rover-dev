#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 각 노드 프로세스의 FASTRTPS 프로파일 적용 여부 ==="
for p in slam_toolbox ekf_node sensor_conditioner rplidar realsense controller_server; do
  pid=$(pgrep -f "$p" | head -1)
  if [ -n "$pid" ]; then
    v=$(tr '\0' '\n' < /proc/$pid/environ 2>/dev/null | grep -a FASTRTPS_DEFAULT_PROFILES_FILE | head -1)
    printf "  %-20s pid %-7s %s\n" "$p" "$pid" "${v:-미설정}"
  fi
done
echo ""
echo "=== slam_toolbox 상세 ==="
pid=$(pgrep -f slam_toolbox | head -1)
echo "  상태: $(ps -p $pid -o stat=,%cpu=,%mem=,etime= 2>/dev/null)"
echo "  스레드: $(ls /proc/$pid/task 2>/dev/null | wc -l)"
echo "  최근 로그 전체 유형:"
grep -aoE "\[(INFO|WARN|ERROR|FATAL)\]" /tmp/slam.log 2>/dev/null | sort | uniq -c | sed 's/^/    /'
echo "  마지막 non-dropping 로그:"
grep -av "Message Filter dropping" /tmp/slam.log 2>/dev/null | tail -3 | cut -c1-140 | sed 's/^/    /'
echo ""
echo "=== EKF 주기 위반 빈도 ==="
echo "  총 발생: $(grep -ac 'Failed to meet update rate' /tmp/sensors.log 2>/dev/null)회"
grep -a 'Failed to meet update rate' /tmp/sensors.log 2>/dev/null | grep -aoE "Took [0-9.]+" | awk '{s+=$2; if($2>m)m=$2; n++} END{printf "  평균 %.3fs 최대 %.3fs (n=%d)\n", s/n, m, n}'
echo ""
echo "=== IMU 입력 부하 ==="
printf "  %-24s " /camera/camera/imu; timeout 8 ros2 topic hz /camera/camera/imu 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
printf "  %-24s " /imu/data; timeout 8 ros2 topic hz /imu/data 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
