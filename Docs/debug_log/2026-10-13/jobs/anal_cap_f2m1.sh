#!/bin/bash
# (오늘만) f2m1 캡처를 Jetson 에서 분석 — 로버 안 움직임
ls -la /tmp/cap_f2m1.pcap | awk '{print "  캡처", $5, "B"}'
python3 -u /tmp/anal_rtps_pcap.py /tmp/cap_f2m1.pcap --netlog /tmp/net_f2m1.log 2>&1
