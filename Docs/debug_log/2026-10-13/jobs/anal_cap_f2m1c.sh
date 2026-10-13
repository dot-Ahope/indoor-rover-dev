#!/bin/bash
# (오늘만) f2m1 포화 시작 구간(10:19:38 부터 4 s)을 0.2 s 칸으로 — 로버 안 움직임
python3 -u /tmp/anal_rtps_onset.py /tmp/cap_f2m1.pcap 10:19:38 4 --step 0.2 --netlog /tmp/net_f2m1.log 2>&1
