#!/bin/bash
# 견고한 detach 실행 + 즉시 초기 확인
pkill -f "map_spin" 2>/dev/null; sleep 1; rm -f /tmp/spin.log
setsid bash /tmp/job7k.sh </dev/null >/dev/null 2>&1 &
disown 2>/dev/null
sleep 6
echo "=== 6초 후: 프로세스 $(pgrep -f map_spin | wc -l)개, 로그: ==="
cat /tmp/spin.log 2>/dev/null | tail -5
echo "(회전은 detach로 계속됩니다. WiFi 끊겨도 완주. 40초 뒤 로그 재확인.)"
