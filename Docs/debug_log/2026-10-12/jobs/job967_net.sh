#!/bin/bash
# 10-12 §8: 궤적 발행과 다른 프로세스의 충돌 여부 — UDP 버퍼 설정·누적 손실·구독자·DDS 전송 설정. 로버 안 움직임
echo "== 커널 소켓 버퍼: rmem_default $(cat /proc/sys/net/core/rmem_default) rmem_max $(cat /proc/sys/net/core/rmem_max) wmem_default $(cat /proc/sys/net/core/wmem_default) wmem_max $(cat /proc/sys/net/core/wmem_max) · lo MTU $(cat /sys/class/net/lo/mtu)"
echo "== UDP 누적 통계(부팅 뒤): $(awk '/^Udp:/{if(h){for(i=2;i<=NF;i++)printf "%s=%s ",hd[i],$i}else{for(i=1;i<=NF;i++)hd[i]=$i;h=1}}' /proc/net/snmp)"
echo "== 가동 $(uptime -p)"
echo "== DDS 전송 설정(fastdds_udp_only.xml):"; sed 's/^/   /' /home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml | head -40
echo "== /trajectories 끝점:"; timeout 12 ros2 topic info -v /trajectories 2>/dev/null | grep -aE "Node name|Endpoint type|Reliability|Durability|History|count" | paste -sd' ' | sed 's/Node name/\n   Node name/g' | cut -c1-200
echo "== foxglove 접속(8765): $(ss -tn 2>/dev/null | grep -c ':8765 .*ESTAB') 개 · foxglove_bridge CPU $(ps -o pcpu= -p $(pgrep -f foxglove_bridge | head -1) 2>/dev/null) %"
echo "== 소켓별 손실(현재 살아 있는 UDP 소켓 중 drops > 0, 프로세스 이름 붙임):"
declare -A own; for p in $(pgrep -u jetson); do for l in $(ls -l /proc/$p/fd 2>/dev/null | grep -o 'socket:\[[0-9]*\]' | tr -d 'socket:[]'); do own[$l]="$(cat /proc/$p/comm 2>/dev/null)"; done; done
awk 'NR>1 && $NF>0{print $2, $(NF-0), $(NF-3)}' /proc/net/udp | while read port drops ino; do echo "   포트 ${port##*:} drops $drops ${own[$ino]:-?}"; done | sort -k4 -t' ' -k3,3nr | head -30
