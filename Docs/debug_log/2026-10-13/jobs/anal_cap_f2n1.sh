#!/bin/bash
# (오늘만) f2n1 캡처: 10 s 칸으로 전체 패킷·/tf DATA·HEARTBEAT, 그리고 주행 중간 20 s 창의 종류별 집계 — 로버 안 움직임
python3 -u /tmp/anal_rtps_onset.py /tmp/cap_f2n1.pcap 10:52:00 250 --step 10 --netlog /tmp/net_f2n1.log 2>&1
echo ======
python3 -u /tmp/anal_rtps_pcap.py /tmp/cap_f2n1.pcap --netlog /tmp/net_f2n1.log --onset 10:53:30 --win 20 --base 10:52:10,10 2>&1 | head -40
