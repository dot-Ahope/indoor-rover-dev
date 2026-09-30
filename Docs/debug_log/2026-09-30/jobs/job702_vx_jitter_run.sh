#!/bin/bash
# 09-30 §7.4 EKF 직진 속도 흔들림 출처
for b in f0b1 f0b2; do echo "== $b"; python3 /tmp/job701_vx_jitter.py /tmp/bag_$b 2>&1 | grep -av "^\["; done
