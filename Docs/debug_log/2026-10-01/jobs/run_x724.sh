#!/bin/bash
# 10-01 §4: 남쪽 통로 구간(+590 s 이후) 스캔을 빼고(=+590 s 에서 자름) 루프 클로저 끔으로 재생 → 격자
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
CUT719=590 V719=nolc bash $SPS/run_x719.sh
N722=cand_0930_cut590_nolc bash $SPS/run_x722.sh
