#!/bin/bash
# 09-29 §12: f0a7 bag 의 마지막 지도 추출
python3 /tmp/job655_mapdump.py /tmp/bag_f0a7 /tmp/map_f0a7.npz 2>&1 | grep -av "^\["
