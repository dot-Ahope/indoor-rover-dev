#!/bin/bash
# 10-07 §9.2: 영상 6 개 전체 구간 bag 추출(읽기만) — f2d1 13:02:50~13:06:30, f2d2 13:11:35~13:19:00
e() { echo $(( 1791346297 + $(date -d "1970-01-01 $1 UTC" +%s) - $(date -d "1970-01-01 13:11:37 UTC" +%s) )); }
python3 /tmp/job930_extract.py /tmp/bag_f2d1 $(e 13:02:50) $(e 13:06:30) /tmp/fz_f2d1.npz 2>&1 | grep -v rosbag2_storage
python3 /tmp/job930_extract.py /tmp/bag_f2d2 $(e 13:11:35) $(e 13:19:00) /tmp/fz_f2d2.npz 2>&1 | grep -v rosbag2_storage
ls -la /tmp/fz_*.npz
