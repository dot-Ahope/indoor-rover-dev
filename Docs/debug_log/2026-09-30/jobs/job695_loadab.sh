#!/bin/bash
# 09-30: Foxglove 연결 유무 부하 A/B — 30 s 동안 EKF 주기 미달·SLAM 스캔 버림 증가, 부하, 주요 프로세스 CPU. 인자: 라벨
L=${1:-A}
e0=$(grep -ac 'Failed to meet update rate' /tmp/sensors.log); s0=$(grep -ac 'Message Filter dropping' /tmp/slam.log)
(for i in $(seq 1 6); do top -b -n1 -w 200 | head -30 | tail -23; sleep 5; done > /tmp/top_$L.log 2>&1) &
l0=$(cut -d' ' -f1 /proc/loadavg); sleep 30
e1=$(grep -ac 'Failed to meet update rate' /tmp/sensors.log); s1=$(grep -ac 'Message Filter dropping' /tmp/slam.log)
echo "[$L] 30 s: EKF 주기 미달 +$((e1-e0)) · SLAM 스캔 버림 +$((s1-s0)) · load 1분 $(cut -d' ' -f1 /proc/loadavg)(시작 $l0)"
echo "  브리지 클라이언트 연결 수: $(ss -tn state established '( sport = :8765 )' 2>/dev/null | tail -n +2 | wc -l)"
awk '{c[$NF]+=$9; n[$NF]++} END {for (k in c) if (c[k]/n[k] > 8) printf "  %-22s %.1f\n", k, c[k]/n[k]}' /tmp/top_$L.log | sort -k2 -nr | head -10
