#!/bin/bash
# (PC·WSL) 10-22 §16 f2sh2 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(sed -n 7p $N/run_jn.sh | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"; mkdir -p $N/logs_f2sh2
for f in nav2 slam sensors; do sshpass -p "$PW" scp $O jetson@192.168.0.110:/tmp/$f.log $N/logs_f2sh2/; done && ls -la $N/logs_f2sh2
