#!/bin/bash
# (PC·WSL) 스크래치패드의 이진 파일을 그대로 Jetson /tmp 로 전송(put_one.sh 는 CR 을 지우므로 이진 파일엔 쓰면 안 됨). 비밀번호는 run_jn.sh 에서 읽는다.
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p *[^ ]*" $N/run_jn.sh | head -1 | sed "s/sshpass -p *//;s/^['\"]//;s/['\"]$//")
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
for f in "$@"; do sshpass -p "$PW" scp $O -q $N/$f jetson@${JETSON_HOST:-192.168.0.101}:/tmp/ && echo "전송 $f $(stat -c %s $N/$f) B"; done
