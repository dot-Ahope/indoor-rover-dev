#!/bin/bash
# (PC·WSL) 스크래치패드의 파일을 Jetson /tmp 로 전송(CR 제거). 인자: 파일명 ... 비밀번호는 run_jn.sh 에서 읽는다(여기에 적지 않음).
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p *[^ ]*" $N/run_jn.sh | head -1 | sed "s/sshpass -p *//;s/^['\"]//;s/['\"]$//")
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
mkdir -p /tmp/put1; for f in "$@"; do tr -d '\r' < $N/$f > /tmp/put1/$f; sshpass -p "$PW" scp $O -q /tmp/put1/$f jetson@${JETSON_HOST:-192.168.0.101}:/tmp/ && echo "전송 $f"; done
