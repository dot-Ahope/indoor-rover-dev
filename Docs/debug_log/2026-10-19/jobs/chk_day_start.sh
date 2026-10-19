#!/bin/bash
# (10-19) 하루 시작 상태: 가동 시간 · /tmp prep 스크립트 · 디스크 · 실행 중 스택 · 배터리 — 로버 안 움직임
echo "가동: $(uptime -p) · 부팅 $(uptime -s)"
for f in prep_fast.sh prep_patrol.sh prep_patrol_pad.sh pad_relief.py chk_prep.py; do [ -f /tmp/$f ] && echo "있음 $f" || echo "없음 $f"; done
df -h / /tmp | tail -2
echo "스택 프로세스: $(pgrep -fc 'controller_server|realsense2_camera|nvblox_node|micro_ros_agent')"
pgrep -fa micro_ros_agent | head -2 | cut -c1-120
