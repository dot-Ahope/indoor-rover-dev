#!/bin/bash
# (PC·WSL) §24 게이트 비교 — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함)
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
sed 's/\r$//' $N/chk_drive_gate.py > /tmp/chk_drive_gate.py; sshpass -p "$PW" scp $O /tmp/chk_drive_gate.py jetson@192.168.0.110:/tmp/chk_drive_gate.py
JX_WHY='게이트 비교(10-27 §24, 로버 안 움직임)' bash $N/run_jn.sh cmp_gate_1027.sh
