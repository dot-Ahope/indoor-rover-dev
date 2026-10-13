#!/bin/bash
# (오늘만) f2m1 캡처 재분석: 평상 창 10:19:36 부터 4 s, 포화 시작 10:19:40 — 로버 안 움직임
python3 -u /tmp/anal_rtps_pcap.py /tmp/cap_f2m1.pcap --netlog /tmp/net_f2m1.log --onset 10:19:40 --win 20 --base 10:19:36,4 2>&1 | grep -av "^2 s 칸"
