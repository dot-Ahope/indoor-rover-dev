#!/bin/bash
# chk_drive_tail_1110 — 11-10 §6: 주행 중 러너 로그 끝을 읽음(읽기만 · 로버 영향 없음 · DDS 참여자 안 만듦).
#   왜: PC 쪽 tee 는 grep 버퍼 때문에 러너가 끝나야 써짐 → Jetson /tmp/f0_<이름>.log 를 직접 봄.
#   인자: $1 = 주행 이름(기본 f2dm1), $2 = 줄 수(기본 25). 출력: 표준 출력.
N=${1:-f2dm1}; K=${2:-25}
echo "== $(date +%T) /tmp/f0_$N.log ($(wc -l < /tmp/f0_$N.log 2>/dev/null) 줄)"
tail -n $K /tmp/f0_$N.log 2>/dev/null | cut -c1-200
