#!/bin/bash
# (10-19 §6) 재생 로그의 복셀 크기 줄 — 인자: 꼬리표 ... 로버 안 움직임
for t in "$@"; do echo "== $t: $(grep -aiE 'voxel_size|voxel size' /tmp/nvblox_replay_$t.log | head -2 | cut -c1-120 | tr '\n' ' ')"; done
