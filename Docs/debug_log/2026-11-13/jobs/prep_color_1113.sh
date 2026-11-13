#!/bin/bash
# prep_color_1113 — 11-13 §0: 표준 prep(Smac · 0.01 Hz · vslam · lite) + 컬러 5 fps(SENSORS_ADD="color_fps:=5"). 로버 안 움직임.
#   인자: $1 = 회차 이름(원문 /tmp/prep_full_color_$1.txt). 출력: rc + 원문 끝 40 줄.
N=${1:-1}
SENSORS_ADD="color_fps:=5" bash /tmp/prep_patrol.sh lite > /tmp/prep_full_color_$N.txt 2>&1; echo "rc $?"; tail -40 /tmp/prep_full_color_$N.txt
