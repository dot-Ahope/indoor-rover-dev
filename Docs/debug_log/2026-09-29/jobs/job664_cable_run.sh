#!/bin/bash
# 09-29 §12.3 전선 밟기 영향 분석
python3 /tmp/job663_cable.py /tmp/bag_f0b1 2>&1 | grep -av "^\["
