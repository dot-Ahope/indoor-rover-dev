#!/bin/bash
# 10-07: G4 재생 5 개 동시 중 Jetson 부하(배속 가능 여부 판단용, 읽기만)
top -b -n 2 -d 3 | awk '/^top -/{n++} n==2' | head -5 | tail -3
top -b -n 2 -d 3 -o %CPU | awk '/^top -/{n++} n==2 && /^ *[0-9]/' | head -14 | awk '{printf "%6s %5s%% %s\n",$1,$9,$12}'
for d in 81 85; do echo "도메인 $d: $(grep -a '게이트 통과' /tmp/occ_launch_$d.log | tail -1 | grep -oE '통과.*' | cut -c1-80)"; done
