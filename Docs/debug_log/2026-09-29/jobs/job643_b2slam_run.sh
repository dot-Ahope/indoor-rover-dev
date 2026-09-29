#!/bin/bash
# 09-29 §5: f0a6(로컬에서 올린 사본)·f0a7 bag 으로 B2 추가량 vs SLAM 보정 대조(job642)
cd /tmp && [ -d bag_f0a6 ] || tar xzf bag_f0a6.tgz
ls -d /tmp/bag_f0a6 /tmp/bag_f0a7
python3 /tmp/job642_b2_vs_slam.py /tmp/bag_f0a6 /tmp/bag_f0a7 2>&1 | grep -av "^\["
