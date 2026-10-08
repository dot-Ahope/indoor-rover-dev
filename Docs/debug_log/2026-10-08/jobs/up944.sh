#!/bin/bash
# 10-08 §6 시뮬 파일 전송(비밀번호는 run_jn.sh 에서 읽음)
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad; H=${JETSON_HOST:-192.168.0.101}
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
sshpass -p $PW scp $O -q $N/bag_f2a10.tgz $N/job776_mppi_sim_ack.py jetson@$H:/tmp/ && echo 전송 완료
