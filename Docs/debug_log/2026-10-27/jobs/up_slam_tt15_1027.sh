#!/bin/bash
# (PC·WSL) §21 slam.launch.py 전송 · 적용 — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함)
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
sed 's/\r$//' $N/up_slam.launch.py > /tmp/up_slam.launch.py; sshpass -p "$PW" scp $O /tmp/up_slam.launch.py jetson@192.168.0.110:/tmp/up_slam.launch.py
JX_WHY='slam.launch transform_timeout 1.5 배포(10-27 §21, 로버 안 움직임)' bash $N/run_jn.sh apply_slam_tt15_1027.sh
