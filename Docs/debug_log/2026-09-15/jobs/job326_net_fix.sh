#!/bin/bash
# (sudo, 사용자 승인 09-16) 1) mavlink-router 비활성  2) Wi-Fi 자동접속 우선순위: <WIFI-B>(192.168.0.x) > <WIFI-A>  3) <WIFI-B> 로 전환 (nohup — 세션이 끊겨도 완료)
PW="$1"
echo "=== 1. mavlink-router ==="
echo "$PW" | sudo -S systemctl disable --now mavlink-router 2>&1 | grep -av password | tail -2
systemctl is-enabled mavlink-router 2>/dev/null; systemctl is-active mavlink-router 2>/dev/null
echo "=== 2. 우선순위 ==="
echo "$PW" | sudo -S nmcli con modify <WIFI-B> connection.autoconnect-priority 20 2>&1 | grep -av password
echo "$PW" | sudo -S nmcli con modify <WIFI-A> connection.autoconnect-priority 5 2>&1 | grep -av password
nmcli -t -f NAME,AUTOCONNECT-PRIORITY,AUTOCONNECT con show | grep -aE 'WEB_DEV|ALOPS|PTR'
echo "=== 3. <WIFI-B> 전환 (5 s 뒤, nohup) ==="
nohup bash -c "sleep 5; echo '$PW' | sudo -S nmcli con up <WIFI-B> > /tmp/nm_switch.log 2>&1; ip -4 -br addr >> /tmp/nm_switch.log; nmcli -t dev status >> /tmp/nm_switch.log" >/dev/null 2>&1 &
echo "전환 예약됨 — 결과는 /tmp/nm_switch.log"
