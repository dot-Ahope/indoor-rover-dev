#!/bin/bash
# 09-29 §12.5 f0b2 여유·전선 분석
python3 /tmp/job660_clearance.py /tmp/bag_f0b2 2>&1 | grep -av "^\["
echo ======
python3 /tmp/job663_cable.py /tmp/bag_f0b2 2>&1 | grep -av "^\[" | head -30
