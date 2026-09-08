#!/bin/bash
# stale stuck_monitor 정리(최신 1개만 유지) + 현재 CPU 측정(top 기준)
source /opt/ros/humble/setup.bash
PIDS=$(pgrep -f "stuck_monitor.py" | sort -n); N=$(echo "$PIDS" | wc -w)
echo "stuck_monitor 인스턴스: $N"
if [ "$N" -gt 1 ]; then KEEP=$(echo "$PIDS" | tail -1); for p in $PIDS; do [ "$p" != "$KEEP" ] && kill -9 $p; done; sleep 1; fi
echo "정리 후: $(pgrep -fc stuck_monitor.py)"
echo "== 현재 CPU (top 3초 평균) =="; top -bn4 -d1 | awk '/^top/{i++} i>=3 && /python3|realsen|depthimag|async_s|rplidar|ekf_node|controller/ {c[$12]+=$9; n[$12]++} END{for(k in c) printf "%5.1f%% %s\n", c[k]/n[k], k}' | sort -rn | head -8
echo -n "stuck_monitor 현재 CPU: "; top -bn2 -d2 -p $(pgrep -f stuck_monitor.py | tail -1) | awk '/^top/{i++} i==2 && /python3/ {print $9"%"}'
echo -n "load: "; cut -d" " -f1-3 /proc/loadavg
