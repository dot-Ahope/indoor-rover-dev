#!/bin/bash
# (PC·WSL) Jetson /tmp 의 파일 하나를 PC 로 회수. 인자: 원격 파일명, 받을 폴더(/mnt/...). 비밀번호는 run_jn.sh 에서 읽는다(여기에 적지 않음).
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p *[^ ]*" $N/run_jn.sh | head -1 | sed "s/sshpass -p *//;s/^['\"]//;s/['\"]$//")
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
sshpass -p "$PW" scp $O -q jetson@${JETSON_HOST:-192.168.0.101}:/tmp/$1 "$2/" && ls -la "$2/$1"
