#!/bin/bash
# 10-07 §3: f2c1·f2c2 bag 추출(읽기만, 2~4 분)
for n in f2c1 f2c2; do python3 /tmp/job913_extract.py /tmp/bag_$n /tmp/x913_$n.npz 2>&1 | grep -v rosbag2_storage; done
