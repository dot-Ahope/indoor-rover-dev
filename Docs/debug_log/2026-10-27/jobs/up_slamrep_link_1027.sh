#!/bin/bash
# (PC·WSL) §29.2 link_scan_maximum_distance A/B(계측판) 한 변형 — 인자: 변형이름(L10|L075). 비밀번호는 run_jn.sh 에서 읽음(출력 안 함)
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
JX_TIMEOUT=600 JX_WHY="SLAM link 거리 A/B $1(10-27 §29, 도메인 42, 로버 안 움직임)" bash $N/run_jn.sh _rep_$1.sh
sshpass -p "$PW" scp $O "jetson@192.168.0.110:/tmp/slamrep/$1.*" $N/slamrep/ && echo 회수
