#!/bin/bash
# 09-29 §12.2 f0b1 여유 계산
python3 /tmp/job660_clearance.py /tmp/bag_f0b1 2>&1 | grep -av "^\["
