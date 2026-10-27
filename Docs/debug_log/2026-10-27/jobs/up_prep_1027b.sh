#!/bin/bash
# (PC·WSL) §24 chk_prep(파라미터 조회 확장) · prep_smac_1027b 전송 후 prep — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함). 로버 안 움직임
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
for f in chk_prep.py prep_smac_1027b.sh; do sed 's/\r$//' $N/$f > /tmp/$f; sshpass -p "$PW" scp $O /tmp/$f jetson@192.168.0.110:/tmp/$f; done
JX_TIMEOUT=400 JX_WHY='prep(10-27 §24, 검사 정리판, 로버 안 움직임)' bash $N/run_jn.sh prep_smac_1027b.sh
