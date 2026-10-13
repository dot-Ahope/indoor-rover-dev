#!/bin/bash
# (오늘만) f2m1 포화 직전 15 s 의 /tf HEARTBEAT·ACKNACK 맞춰 보기 — 로버 안 움직임
python3 -u /tmp/anal_rtps_acklag.py /tmp/cap_f2m1.pcap 10:19:27 15 --netlog /tmp/net_f2m1.log 2>&1
