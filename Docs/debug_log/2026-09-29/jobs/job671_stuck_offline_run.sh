#!/bin/bash
# 09-29 §13 G3: stuck_monitor 오프라인 재생 OLD/NEW
python3 /tmp/job670_stuck_offline.py $(ls -d /tmp/bag_f0a? /tmp/bag_f0b? /tmp/bag_s1 /tmp/bag_s2 /tmp/bag_r1 /tmp/bag_r1b /tmp/bag_r2 /tmp/bag_r2b /tmp/bag_r3 /tmp/bag_l1 /tmp/bag_l2 /tmp/bag_s_fb1 /tmp/bag_s_fb2) 2>&1 | grep -av "^\["
