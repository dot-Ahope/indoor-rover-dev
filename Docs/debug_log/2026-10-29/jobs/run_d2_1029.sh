#!/bin/bash
# (PC·WSL) §4 d2: 주행(10-28 S1 러너 w3, 새 place_server 배포 포함) → 끝나자마자 d2s 정지 기록 40 분 시작. 로버는 주행 구간만 움직임
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
bash $N/up_place_s1_1028.sh d2 w3
bash $N/up_drift_rec_1029.sh d2s 2400
