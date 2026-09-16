#!/bin/bash
source /opt/ros/humble/setup.bash
echo "=== IP ==="; ip -4 -o addr show | awk '{print $2, $4}' | tr '\n' ' '; echo
echo "=== agent(docker) 로그 끝 ==="; docker logs --tail 3 microros_agent 2>&1 | cut -c1-120
echo "=== sensors.log 끝(EKF/컨디셔너) ==="; grep -aE "WARN|ERROR" /tmp/sensors.log | tail -4 | cut -c1-170
echo "=== nav2.log lifecycle ==="; grep -a "lifecycle_manager" /tmp/nav2.log | tail -5 | cut -c1-170
echo "=== 새 셸에서 옛 노드 데이터 수신 시험 ==="
printf "  /wheel_odom(agent, 옛):   "; timeout 6 ros2 topic echo /wheel_odom --once 2>/dev/null | grep -c "header" || echo 0
printf "  /scan(rplidar, 옛):       "; timeout 6 ros2 topic echo /scan --once 2>/dev/null | grep -c "header" || echo 0
printf "  /rover/stuck(nav2, 새):   "; timeout 6 ros2 topic echo /diagnostics --once 2>/dev/null | grep -c "header" || echo 0
echo "=== 프로세스 시작 시각 ==="; ps -o lstart=,args= -p $(pgrep -f "rplidar_node" | head -1) $(pgrep -f "ekf_node" | head -1) $(pgrep -f "controller_server" | head -1) $(pgrep -f "micro_ros_agent|docker-proxy|containerd-shim" | head -1) 2>/dev/null | cut -c1-90
echo "wifi 전환: 16:00:58 (syslog)"
