#!/bin/bash
# (10-19 §7) 재생 nvblox 로그의 오류 · 마지막 줄 — 인자: 꼬리표. 로버 안 움직임
L=/tmp/nvblox_replay_$1.log; echo "줄 $(wc -l < $L)"; grep -anE "rror|xception|abort|terminate|Segment|CUDA|fail" $L | head -8 | cut -c1-220; echo "-- 끝 8 줄"; tail -8 $L | cut -c1-200
