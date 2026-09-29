#!/bin/bash
# 09-29 §3: L1·L2 bag 을 정지 스캔 직접 정합(job567)으로 분석 — 정답(실제 중심 이동)
for B in l1 l2; do echo "=== bag_$B"; python3 /tmp/job567_scanmatch.py /tmp/bag_$B 2>&1 | grep -av "^\["; done
