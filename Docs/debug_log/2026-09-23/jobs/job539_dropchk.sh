#!/bin/bash
echo "## 지금 $(date +%T) | $(nmcli -t -f NAME,DEVICE con show --active | grep wl) | IP $(ip -4 -o addr show dev wlP1p1s0 | awk '{print $4}')"
echo "## mon.log 11:5x (LINK 변화·EVENT·ARP_DUP)"; grep -aE "^2026-09-23 11:(5|4[5-9])" /var/log/wifi_mon/mon.log | grep -avE "LINK bssid=b0:38:6c:37:1b:4c ssid=WEB_DEV_5G freq=5180 sig=-5[0-9] rx=[0-9.]+_MBit/s(_VHT[^ ]*)? tx=[^ ]+ ip=192" | tail -20 | cut -c1-170
echo "## ARP_DUP 누적: $(grep -ac ARP_DUP /var/log/wifi_mon/mon.log)"
echo "## wpa 이벤트 11:4x~5x"; grep -aE "^Sep 23 11:(4[5-9]|5[0-9])" /var/log/wifi_mon/wpa_debug.log | grep -aE "CTRL-EVENT|deauth|disassoc|reason=|BEACON-LOSS|SA Query|Trying to associate" | tail -15 | cut -c1-170
echo "## NM 11:4x~5x"; journalctl -u NetworkManager --since "11:40" --no-pager 2>/dev/null | grep -aiE "duplicate|dad|dhcp4|state change|deauth|disconnect|activated" | tail -15 | cut -c1-170
echo "## 커널"; journalctl -k --since "11:40" --no-pager 2>/dev/null | grep -aiE "wlP1p1s0|rtw|mt79|wlan|deauth|disassoc" | tail -8 | cut -c1-170
echo "## 스택: agent $(docker ps --format '{{.Names}}' | grep -c micro) camera $(pgrep -fc realsense2_camera_node) slam $(pgrep -fc slam_toolbox) controller $(pgrep -fc controller_server) nvblox_up $(pgrep -fc 'bash .*nvblox_up.sh')"
