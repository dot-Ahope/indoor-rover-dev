#!/bin/bash
# (PC·WSL) 10-27 f2st1 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음(값 출력 안 함)
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"; mkdir -p $N/logs_f2st1
for f in nav2 slam sensors; do sshpass -p "$PW" scp $O jetson@192.168.0.110:/tmp/$f.log $N/logs_f2st1/; done && ls -la $N/logs_f2st1
