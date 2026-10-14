#!/bin/bash
# (PC·WSL) 연결이 불안정할 때: 파일을 재시도하며 보내고, Jetson 에서 setsid nohup 으로 스크립트를 띄운 뒤(접속이 끊겨도 계속 돎) 결과 파일을 재시도하며 읽어 온다.
# 인자: 스크립트 [함께 보낼 파일 ...]   환경: JX_WAIT(끝날 때까지 기다릴 최대 초, 기본 120). 비밀번호는 run_jn.sh 에서 읽는다(여기에 적지 않음).
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad; H=${JETSON_HOST:-192.168.0.101}
PW=$(grep -o "sshpass -p *[^ ]*" $N/run_jn.sh | head -1 | sed "s/sshpass -p *//;s/^['\"]//;s/['\"]$//")
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=6 -o ServerAliveInterval=3 -o ServerAliveCountMax=2"
SC=$1; mkdir -p /tmp/rdet; for f in "$@"; do tr -d '\r' < $N/$f > /tmp/rdet/$f; done
try() { for i in 1 2 3 4 5 6 7 8; do "$@" && return 0; sleep 4; done; return 1; }
try sshpass -p "$PW" scp $O -q $(for f in "$@"; do echo /tmp/rdet/$f; done) jetson@$H:/tmp/ || { echo "전송 실패(8 회)"; exit 1; }
TAG=${SC%.*}; try sshpass -p "$PW" ssh $O jetson@$H "rm -f /tmp/$TAG.out /tmp/$TAG.done; setsid nohup bash -c 'bash /tmp/$SC > /tmp/$TAG.out 2>&1; touch /tmp/$TAG.done' > /dev/null 2>&1 < /dev/null & echo started" || { echo "기동 실패(8 회)"; exit 1; }
T0=$(date +%s); while [ $(( $(date +%s) - T0 )) -lt ${JX_WAIT:-120} ]; do sleep 5; sshpass -p "$PW" ssh $O jetson@$H "test -f /tmp/$TAG.done" 2>/dev/null && break; done
try sshpass -p "$PW" ssh $O jetson@$H "test -f /tmp/$TAG.done && echo '[끝남]' || echo '[아직 도는 중 또는 확인 실패]'; cat /tmp/$TAG.out" || echo "결과 읽기 실패(8 회)"
