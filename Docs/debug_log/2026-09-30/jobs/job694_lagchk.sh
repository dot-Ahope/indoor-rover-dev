#!/bin/bash
# 09-30: 매핑 중 Foxglove 에서 로버 위치가 멈췄다 점프한 원인 — 브리지·SLAM·EKF 로그와 현재 부하
echo "== foxglove_bridge 로그(sensors.log) 경고·버퍼"
grep -a "foxglove" /tmp/sensors.log | grep -aiE "warn|error|buffer|drop|limit|slow|connect" | cut -c1-200 | tail -12
echo "  send buffer limit 건수: $(grep -aic 'send buffer limit' /tmp/sensors.log) | 연결/해제: $(grep -aicE 'client .* connected|connection .* closed|disconnect' /tmp/sensors.log)"
echo "== SLAM(slam.log)"
echo "  Message Filter dropping: $(grep -ac 'Message Filter dropping' /tmp/slam.log) | 시작 뒤 경과 $(($(date +%s) - $(stat -c %Y /tmp/slam.log))) s 전 마지막 기록"
grep -aE "dropping|Failed|queue|delay|exceed" /tmp/slam.log | cut -c1-180 | tail -5
echo "== EKF(sensors.log)"
echo "  Failed to meet update rate: $(grep -ac 'Failed to meet update rate' /tmp/sensors.log)"
grep -a "Failed to meet update rate" /tmp/sensors.log | tail -3 | cut -c1-160
echo "== 지금 부하(top 3 회 평균, 코어 1 = 100)"
for i in 1 2 3; do top -b -n1 -w 200 | head -22 | tail -15; sleep 1; done | awk '{c[$NF]+=$9; n[$NF]++} END {for (k in c) if (c[k]/n[k] > 5) printf "  %-24s %.1f\n", k, c[k]/n[k]}' | sort -k2 -nr | head -12
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg) | Wi-Fi: $(iw dev wlan0 link 2>/dev/null | grep -aE 'signal|tx bitrate' | tr -s ' ' | tr '\n' ' ')"
