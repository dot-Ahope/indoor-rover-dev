#!/bin/bash
# (10-14 §25) prep_fast 의 기록 보관 부분만 실행해 시험 — 기록을 비우지 않음, 로버 안 움직임
# 10-14 §24: 비우기 전에 직전 기록을 보관 — 재기동이 앞 주행의 Nav2 기록(계획기·코스트맵 경고)을 지워 이상 경로 원인을 못 봤다.
#   /tmp/logkeep/<보관시각>_{nav2,slam,sensors}.log, 최근 8 벌만 남김(nav2.log 가 주행당 수 MB 라 /tmp 를 채우지 않게). /tmp 라 재부팅하면 사라진다.
K=/tmp/logkeep; mkdir -p $K; TS=$(date +%m%d_%H%M%S)
for f in nav2 slam sensors; do [ -s /tmp/$f.log ] && cp /tmp/$f.log $K/${TS}_$f.log; done
ls -1t $K/*_nav2.log 2>/dev/null | tail -n +9 | sed 's/_nav2\.log$//' | while read p; do rm -f ${p}_*.log; done
echo "  직전 기록 보관: $K/${TS}_*.log ($(ls $K/${TS}_*.log 2>/dev/null | wc -l) 개) · 보관 벌 수 $(ls $K/*_nav2.log 2>/dev/null | wc -l)"
ls -la /tmp/logkeep | tail -5; df -h /tmp | tail -1
