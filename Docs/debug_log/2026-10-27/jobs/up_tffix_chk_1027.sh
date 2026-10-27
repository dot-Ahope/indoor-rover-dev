#!/bin/bash
# (PC·WSL) §17 확인 스크립트 전송 후 실행 — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함)
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
for f in chk_nvlayer_tffix_1027.py prep_smac_1027.sh; do sed 's/\r$//' $N/$f > /tmp/$f; sshpass -p "$PW" scp $O /tmp/$f jetson@192.168.0.110:/tmp/$f; done
JX_TIMEOUT=600 JX_WHY='수정 nvblox 층 prep + 정지 120 s 확인(10-27 §17, 로버 안 움직임)' bash $N/run_jn.sh run_tffix_chk_1027.sh
