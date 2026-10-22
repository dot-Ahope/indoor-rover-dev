#!/bin/bash
# (PC·WSL) 10-22 §9 재생 출력 회수 — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함)
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(sed -n 7p $N/run_jn.sh | awk '{print $3}'); mkdir -p $N/rp
for t in "$@"; do sshpass -p "$PW" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR jetson@192.168.0.110:/tmp/replay_$t.tgz $N/rp/ && tar xzf $N/rp/replay_$t.tgz -C $N/rp && echo "회수 $t"; done
