#!/bin/bash
# 10-07 §4 B: f2c2 bag(430 s) 재생 — G4 abs(라이브 재현 확인) vs wheel(잔차) 동시, 도메인 91·92, 약 8 분, 로버 안 움직임. 1 분마다 진행 줄
GVREF=abs bash /tmp/rp_run.sh 91 /tmp/bag_f2c2 /tmp/rp_f2c2_abs.npz > /tmp/rp_91.txt 2>&1 &
GVREF=wheel bash /tmp/rp_run.sh 92 /tmp/bag_f2c2 /tmp/rp_f2c2_wheel.npz > /tmp/rp_92.txt 2>&1 &
T0=$(date +%s); sleep 20
while [ $(ps aux | grep -c "[b]ag play /tmp/bag_f2c2") -gt 0 ]; do echo "  [$(( ($(date +%s) - T0) / 60 )) 분] 재생 중 $(ps aux | grep -c "[b]ag play /tmp/bag_f2c2")/2"; sleep 60; done
wait; cat /tmp/rp_91.txt /tmp/rp_92.txt | grep -a 도메인; echo "=== 끝"
