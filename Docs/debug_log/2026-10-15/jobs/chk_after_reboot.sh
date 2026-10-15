#!/bin/bash
# (10-15 §2) 재부팅 뒤 상태 확인 — 신원(호스트 이름·Jetson 릴리스·작업 폴더) · /tmp 기동 스크립트 · 컨테이너 · 망. 로버 안 움직임
echo "호스트 $(hostname) · $(head -1 /etc/nv_tegra_release 2>/dev/null | cut -c1-60) · ros2_ws $( [ -d ~/ros2_ws/src/rover_navigation ] && echo 있음 || echo 없음) · 지도 $(ls ~/maps/office/office_v3.posegraph 2>/dev/null | wc -l)"
echo "uptime: $(uptime -p) · 부팅 $(uptime -s)"
for f in prep_fast.sh prep_patrol.sh prep_patrol_pad.sh pad_relief.py chk_prep.py job551_f0drive.sh; do [ -e /tmp/$f ] && echo "  있음 /tmp/$f" || echo "  없음 /tmp/$f"; done
echo "docker: $(docker ps -a --format '{{.Names}}:{{.State}}' 2>/dev/null | tr '\n' ' ')"
echo "wlan0: $(ip -4 addr show wlan0 2>/dev/null | grep -o 'inet [0-9./]*') · SSID $(iwgetid -r 2>/dev/null)"
