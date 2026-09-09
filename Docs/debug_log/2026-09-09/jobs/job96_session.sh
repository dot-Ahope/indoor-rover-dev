#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 보드 발행 토픽 생존 확인 (각 6초) ==="
for t in /wheel_odom /battery /rover/status /imu/data_raw /imu/mag; do
  printf "  %-16s " "$t"
  timeout 8 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo "무발행"
done
echo ""
echo "=== 보드 노드 존재 ==="
ros2 node list 2>/dev/null | grep -a rover_jupiter || echo "  rover_jupiter 없음"
echo ""
echo "=== agent 컨테이너 ==="
docker ps --format '{{.Names}} {{.Status}}' | grep -a microros || echo "  없음"
echo ""
echo "=== agent 로그: 세션 종료/에러 흔적 ==="
docker logs microros_agent 2>&1 | grep -aiE "delete|session|timeout|error|warn|heartbeat|reset|disconnect" | tail -25
echo ""
echo "=== agent 로그 마지막 8줄 ==="
docker logs --tail 8 microros_agent 2>&1
echo ""
echo "=== UART 장치 ==="
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
dmesg 2>/dev/null | grep -aiE "ch341|ttyUSB|usb.*disconnect" | tail -8
