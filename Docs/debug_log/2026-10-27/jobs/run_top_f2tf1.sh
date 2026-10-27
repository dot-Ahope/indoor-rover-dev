#!/bin/bash
# §18 f2tf1 동안 프로세스별 CPU 1 s 간격 기록(약 11 분, DDS 참여자 아님). 끝나면 /tmp/top_f2tf1.txt
nohup bash -c 'top -b -d 1 -n 660 -w 200 -c > /tmp/top_f2tf1.txt 2>&1' >/dev/null 2>&1 &
sleep 2; echo "top 기록 시작 $(date +%T) · $(wc -l < /tmp/top_f2tf1.txt) 줄"
