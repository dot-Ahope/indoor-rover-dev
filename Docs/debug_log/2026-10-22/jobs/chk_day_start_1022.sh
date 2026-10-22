#!/bin/bash
# 10-22 하루 시작 점검(읽기만): 신원 · 재부팅 · 주소 · prep 파일 · camera.launch 판 · 컨테이너 · 스택 · 디스크 · Wi-Fi 기록
echo "== 신원: $(hostname) · wlan MAC $(cat /sys/class/net/wlan0/address 2>/dev/null) · 가동 $(uptime -p) (부팅 $(uptime -s))"
ip -4 -o addr show wlan0 | awk '{print "== 주소", $4}'; nmcli -t -f ACTIVE,SSID dev wifi 2>/dev/null | grep '^yes' | head -1
echo "== /tmp prep 파일:"; for f in prep_fast.sh prep_patrol.sh prep_patrol_pad.sh pad_relief.py chk_prep.py; do [ -f /tmp/$f ] && echo "  있음 $f" || echo "  없음 $f"; done
F=~/ros2_ws/src/rover_bringup/launch/camera.launch.py; echo "== camera.launch.py sha $(sha256sum < $F | cut -c1-12) · depth_preset 줄 $(grep -c depth_preset $F)"
echo "== 컨테이너:"; docker ps -a --format '  {{.Names}} {{.Status}}'
echo "== 스택 프로세스: realsense $(pgrep -fc realsense2_camera) · slam $(pgrep -fc slam_toolbox) · controller $(pgrep -fc controller_server) · ekf $(pgrep -fc ekf_node) · agent $(docker ps --format '{{.Names}}' | grep -c microros) · base $(systemctl --user is-active rover-base)"
df -h / | awk 'NR==2{print "== 디스크 여유", $4, "(사용", $5")"}'; free -m | awk 'NR==2{print "== 메모리 사용", $3, "MB /", $2}'
echo "== Wi-Fi 기록(최근 8):"; tail -8 /var/log/wifi_mon 2>/dev/null | sed 's/^/  /'
