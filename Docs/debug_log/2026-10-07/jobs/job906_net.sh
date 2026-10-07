#!/bin/bash
# 10-07: 연결 끊김 진단(읽기만) — 가동 시간, 현재 Wi-Fi, 끊김 기록
echo "uptime: $(uptime -p) · 부팅 $(uptime -s)"
nmcli -t -f NAME,DEVICE,STATE connection show --active | head -4
nmcli -t -f ACTIVE,SSID,SIGNAL,CHAN dev wifi | grep -E "WEB_DEV|ALOPS" | head -6
ip -4 -br addr | grep -v "^lo"
ls -t /var/log/wifi_mon/ 2>/dev/null | head -3; tail -25 $(ls -t /var/log/wifi_mon/* 2>/dev/null | head -1) 2>/dev/null | cut -c1-170
journalctl -b -u NetworkManager --no-pager 2>/dev/null | grep -aiE "WEB_DEV|deauth|reason|dhcp.*(timeout|fail)|state change.*(failed|disconnected)|activation" | tail -15 | cut -c1-200
