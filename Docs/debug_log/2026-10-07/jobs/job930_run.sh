#!/bin/bash
# 10-07 §9: 쇼케이스 영상용 bag 구간 추출(읽기만) — 시각은 Jetson epoch(13:11:37 KST = 1791346297)
e() { echo $(( 1791346297 + $(date -d "1970-01-01 $1 UTC" +%s) - $(date -d "1970-01-01 13:11:37 UTC" +%s) )); }
python3 /tmp/job930_extract.py /tmp/bag_f2d2 $(e 13:16:38) $(e 13:18:55) /tmp/sc_box.npz 2>&1 | grep -v rosbag2_storage
ls -la /tmp/sc_*.npz
