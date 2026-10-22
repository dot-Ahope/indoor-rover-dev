#!/bin/bash
# 10-22 §5.2 f2dr1 러너 기동 실패(No route) 뒤: 신원 · 가동 시간 · Wi-Fi 끊김 기록 · 스택 생존 — 로버 안 움직임
hostname; uptime -p; nmcli -t -f NAME,DEVICE con show --active 2>/dev/null | head -3; ip -4 -o addr show wlan0 2>/dev/null | awk '{print $4}'
tail -n 15 /var/log/wifi_mon/*.log 2>/dev/null | tail -15
pgrep -fc controller_server; pgrep -fc nvblox
