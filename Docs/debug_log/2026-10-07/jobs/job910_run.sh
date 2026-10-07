#!/bin/bash
# 10-07 §2.3: f2c1 bag 에서 목표 4 구간(11:00:50~11:02:15) 로컬 코스트맵·라이다·cmd_vel 추출(읽기만)
B=/tmp/bag_f2c1; [ -f $B/metadata.yaml ] || { mkdir -p /tmp/x910 && tar xzf /tmp/bag_f2c1.tgz -C /tmp/x910 && B=$(dirname $(find /tmp/x910 -name metadata.yaml | head -1)); }
echo "bag $B"; python3 /tmp/job910_g4cost.py $B 1791338450 1791338535
