#!/bin/bash
# 10-07 §4: 재생 결과 회수(인자 = 파일 이름들)
P=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad/rp
for f in "$@"; do sshpass -p <PW> scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -q jetson@${JETSON_HOST:-172.30.1.8}:/tmp/$f $P/ || echo "실패 $f"; done
