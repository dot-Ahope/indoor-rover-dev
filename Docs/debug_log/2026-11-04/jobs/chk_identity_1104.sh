#!/bin/bash
# 11-04 §10: 새 주소의 기기가 우리 Jetson 인지 확인(읽기만) — 호스트 · 커널 · L4T · 보드 별칭 · 작업공간 · 주소 · 연결 SSID
echo "host $(hostname) · user $(whoami) · $(uname -r) · $(head -1 /etc/nv_tegra_release | cut -c1-30)"
echo "rover -> $(readlink /dev/rover) · rplidar -> $(readlink /dev/rplidar) · ws $(ls -d ~/ros2_ws/src/rover_navigation 2>/dev/null)"
echo "주소: $(ip -4 -o addr show | awk '{print $2, $4}' | grep -v '^lo' | tr '\n' ' ')"
echo "SSID: $(nmcli -t -f active,ssid dev wifi 2>/dev/null | grep '^yes' | cut -d: -f2)"
uptime -p
