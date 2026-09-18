#!/bin/bash
# syslog 를 채우는 프로그램 (읽기 전용): 최근 7 일 날짜별 크기, 9/17 하루 프로그램별 줄 수·바이트
L=/var/log/syslog
echo "== 날짜별 줄·MB (최근 10 일)"
grep -aE '^Sep ( [0-9]|1[0-8]) ' $L | awk '{d=$1" "$2; n[d]++; b[d]+=length($0)+1} END {for (k in n) printf "  %-7s %7d 줄 %6.1f MB\n", k, n[k], b[k]/1048576}' | sort -k2,2n | tail -10
echo "== 9/17 하루 프로그램별 상위"
grep -a '^Sep 17 ' $L | awk '{p=$5; sub(/\[[0-9]+\]:?$/, "", p); sub(/:$/, "", p); n[p]++; b[p]+=length($0)+1} END {for (k in n) printf "  %8d 줄 %6.2f MB  %s\n", n[k], b[k]/1048576, k}' | sort -rn | head -12
echo "== 반복 메시지 상위(9/17)"
grep -a '^Sep 17 ' $L | cut -d' ' -f5- | sed -E 's/\[[0-9]+\]//; s/[0-9]+/N/g' | cut -c1-110 | sort | uniq -c | sort -rn | head -8
