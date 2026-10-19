#!/bin/bash
# (PC·WSL, 10-19 §6) 재생 출력 tgz 회수 — 인자: 꼬리표 ...
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
for t in "$@"; do bash $N/fetch_one.sh replay_$t.tgz $N/rp >/dev/null && echo "회수 $t"; done
