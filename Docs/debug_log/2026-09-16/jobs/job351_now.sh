#!/bin/bash
echo "host $(hostname) $(date +%T) ip $(ip -4 -o addr show wlP1p1s0 | awk '{print $4}')"
echo "agent: $(docker ps --format '{{.Names}} {{.Status}}' | grep -a micro || echo 없음)"
echo "세션: $(grep -ac 'session established' /tmp/base.log 2>/dev/null)  base.log 줄: $(wc -l < /tmp/base.log 2>/dev/null)"
echo "프로세스: sensors $(pgrep -fc sensors.launch) slam $(pgrep -fc slam.launch) nav2 $(pgrep -fc navigation.launch) job240 $(pgrep -fc job240_clean) job156 $(pgrep -fc job156_stop)"
echo "job240 출력 흔적(/tmp/sensors.log 줄): $(wc -l < /tmp/sensors.log 2>/dev/null)"
ps -eo etimes,args --sort=-etimes | grep -a "job240\|job156\|ros2 launch" | grep -av grep | head -5 | cut -c1-100
