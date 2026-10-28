#!/bin/bash
# (PC·WSL) 10-28 재부팅 뒤 prep 재전송 + prep. 인자: 회차번호. 비밀번호는 run_jn.sh 에서 읽음(출력 안 함). 로버 안 움직임
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
for f in prep_fast.sh prep_patrol.sh chk_prep.py chk_drive_gate.py; do sed 's/\r$//' $N/tools_$f > /tmp/$f; sshpass -p "$PW" scp $O /tmp/$f jetson@192.168.0.110:/tmp/$f; done
printf '#!/bin/bash\nbash /tmp/prep_smac_1028.sh %s\n' "${1:-1}" > $N/_prep_call.sh; sed 's/\r$//' $N/prep_smac_1028.sh > /tmp/prep_smac_1028.sh; sshpass -p "$PW" scp $O /tmp/prep_smac_1028.sh jetson@192.168.0.110:/tmp/
JX_TIMEOUT=400 JX_WHY="prep 10-28 #${1:-1}(로버 안 움직임)" bash $N/run_jn.sh _prep_call.sh
