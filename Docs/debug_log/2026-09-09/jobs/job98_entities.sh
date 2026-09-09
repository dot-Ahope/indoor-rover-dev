#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== agent: 세션 수립 이력 (client_key 별) ==="
docker logs microros_agent 2>&1 | grep -aE "establish_session|create_client" | sed -E 's/\x1b\[[0-9;]*m//g' | tail -10
echo ""
echo "=== agent: 최근 세션의 엔티티 생성 개수 ==="
LAST=$(docker logs microros_agent 2>&1 | grep -a "establish_session" | tail -1 | sed -E 's/.*client_key: (0x[0-9A-Fa-f]+).*/\1/')
echo "  최근 client_key = $LAST"
docker logs microros_agent 2>&1 | sed -E 's/\x1b\[[0-9;]*m//g' | grep -a "$LAST" | grep -acE "create_datawriter" | sed 's/^/  datawriter 생성 수: /'
docker logs microros_agent 2>&1 | sed -E 's/\x1b\[[0-9;]*m//g' | grep -a "$LAST" | grep -aE "create_datawriter|create_datareader|create_topic" | tail -20
echo ""
echo "=== agent: 에러/경고 전체 ==="
docker logs microros_agent 2>&1 | sed -E 's/\x1b\[[0-9;]*m//g' | grep -aiE "error|warn|wrong|fail|drop|out of|full" | tail -20
echo ""
echo "=== 현재 퍼블리셔 (rover_jupiter 가 실제로 광고 중인 토픽) ==="
ros2 node info /rover_jupiter 2>/dev/null | sed -n '/Publishers/,/Service Servers/p' | head -20
echo ""
echo "=== /wheel_odom 퍼블리셔 수 ==="
ros2 topic info /wheel_odom 2>/dev/null | sed 's/^/  /'
echo "=== /imu/data_raw 퍼블리셔 수 ==="
ros2 topic info /imu/data_raw 2>/dev/null | sed 's/^/  /'
echo ""
echo "=== UART 오류 카운터 ==="
dmesg 2>/dev/null | grep -aiE "ttyUSB|ch341|overrun|usb" | tail -10
