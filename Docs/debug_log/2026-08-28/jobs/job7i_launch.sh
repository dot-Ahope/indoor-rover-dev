#!/bin/bash
# 회전을 detach 실행: WiFi 끊겨도 Jetson에서 독립 완주. 스크립트 자체 안전장치(가드/360°/타임아웃).
pkill -f "map_spin" 2>/dev/null; pkill -f "job7f" 2>/dev/null; sleep 1
rm -f /tmp/spin.log
setsid nohup bash /tmp/job7f.sh > /tmp/spin.log 2>&1 &
echo "SPIN_LAUNCHED_DETACHED (log: /tmp/spin.log). 회전은 네트워크와 무관하게 진행됩니다."
sleep 5
echo "=== 5초 후 로그 ==="; cat /tmp/spin.log 2>/dev/null | grep -av "^$" | tail -3
