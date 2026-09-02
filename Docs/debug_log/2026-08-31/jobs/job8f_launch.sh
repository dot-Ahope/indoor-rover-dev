#!/bin/bash
pkill -f "map_spin" 2>/dev/null; sleep 1; rm -f /tmp/spin.log
setsid bash /tmp/job8f.sh </dev/null >/dev/null 2>&1 & disown 2>/dev/null
sleep 5; echo "=== 5초 후 로그 ==="; cat /tmp/spin.log 2>/dev/null | tail -4
echo "(180도 회전 detach 진행. Foxglove에서 밀림 관찰. 20초 뒤 결과 읽음.)"
