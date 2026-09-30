#!/bin/bash
# 09-30 §7: f0b1·f0b2 bag → 영상 프레임 데이터
cd /tmp; for b in f0b1 f0b2; do [ -d bag_$b ] || tar xzf bag_$b.tgz; python3 /tmp/job699_bag2frames.py /tmp/bag_$b /tmp/vid_$b.npz 2>&1 | grep -av "^\["; ls -la /tmp/vid_$b.npz | cut -c24-; done
