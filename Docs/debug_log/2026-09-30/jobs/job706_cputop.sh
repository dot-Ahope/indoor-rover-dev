#!/bin/bash
# 09-30 §11: CPU 소비 상위(top 5 회 평균) + 브리지 설정 + 부하
for i in 1 2 3 4 5; do top -b -n1 -w 220 | tail -n +8 | head -30; sleep 1; done | awk '{c[$NF]+=$9; n[$NF]++} END {for (k in c) if (c[k]/5 > 3) printf "  %-26s %.1f\n", k, c[k]/5}' | sort -k2 -nr | head -18
echo "  합계(>3%%만): $(for i in 1; do top -b -n1 | awk 'NR>7 {s+=$9} END {print s}'; done) % / 600 %"
echo "  부하 $(cut -d' ' -f1-3 /proc/loadavg) | 브리지 whitelist: $(grep -ao "topic_whitelist[^]]*]" /tmp/sensors.log | tail -1 | cut -c1-150)"
