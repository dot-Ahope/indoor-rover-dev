#!/bin/bash
# (10-14 §17) 주행 중: 러너 기록·최근 위치/속도(러너 csv)·CPU — 명령 없음
grep -a "목표 [0-9]" /tmp/f0_f2t1.log | tail -6 | cut -c1-150
echo "--- 최근 csv(1 s 간격 10 줄): t goal map_x map_y yaw v w"
tail -200 /tmp/f2t1.csv 2>/dev/null | awk -F, 'NR%20==0{printf "%s g%s (%.2f, %.2f) %+.0f° v %.3f w %+.2f\n",$1,$2,$3,$4,$5*57.3,$10,$11}'
echo "--- 부하"; top -b -n1 | head -12 | tail -8 | cut -c1-110; date +%T
