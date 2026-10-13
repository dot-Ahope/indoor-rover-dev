#!/bin/bash
# 상태 확인(로버 안 움직임): 재부팅 여부·IP·스택·/tmp 스크립트·캡처 도구 권한. 10-13 세션 시작용
echo "  $(hostname) · 가동 $(uptime -p) · 부하 $(cut -d' ' -f1-3 /proc/loadavg)"
echo "  IP: $(ip -4 -o addr show | grep -v ' lo ' | awk '{print $2, $4}' | tr '\n' ' ')"
echo "  /tmp 스크립트 $(ls /tmp/job*.sh /tmp/job*.py 2>/dev/null | wc -l) 개 · 에이전트 컨테이너 $(docker ps --format '{{.Names}}' | grep -c microros_agent) · ROS 프로세스 $(pgrep -fc '/opt/ros|ros2_ws')"
echo "  /dev/rover → $(readlink -f /dev/rover 2>&1) · 배터리는 스택 기동 뒤 확인"
echo "  tcpdump: $(which tcpdump || echo 없음) · 권한 $(getcap $(which tcpdump) 2>/dev/null || echo '(setcap 없음)') · 암호 없는 sudo $(sudo -n true 2>/dev/null && echo 가능 || echo 불가)"
echo "  수신 버퍼 rmem_max $(cat /proc/sys/net/core/rmem_max) · 설치본 PreferForward $(grep -a 'PreferForwardCritic: {' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml | grep -o 'cost_weight: [0-9.]*')"
echo "  디스크 /tmp 여유 $(df -h /tmp | tail -1 | awk '{print $4}')"
