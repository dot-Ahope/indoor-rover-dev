#!/bin/bash
# (PC·WSL) 10-29 정지 기록 스크립트 전송 + 시작. 인자: 이름 길이s. 비밀번호는 run_jn.sh 에서 읽음(출력 안 함)
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
tr -d '\r' < $N/chk_drift_rec_1029.sh > /tmp/chk_drift_rec_1029.sh; sshpass -p "$PW" scp $O /tmp/chk_drift_rec_1029.sh jetson@192.168.0.110:/tmp/
printf '#!/bin/bash\nbash /tmp/chk_drift_rec_1029.sh %s %s\n' "$1" "$2" > $N/_d_call.sh
JX_WHY="$1 정지 기록 $2 s(로버 안 움직임)" bash $N/run_jn.sh _d_call.sh
