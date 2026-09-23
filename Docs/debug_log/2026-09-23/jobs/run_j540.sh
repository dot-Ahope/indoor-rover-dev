#!/bin/bash
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=4"
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
for i in $(seq 1 90); do
  for H in 192.168.0.101 172.30.1.8; do
    if ping -c1 -W1 $H >/dev/null 2>&1; then
      sshpass -p <PW> scp $O -q $N/job539_unix.sh jetson@$H:/tmp/job539.sh && sshpass -p <PW> scp $O -q $N/job540_unix.sh jetson@$H:/tmp/job540.sh && \
      sshpass -p <PW> ssh $O jetson@$H 'setsid nohup bash /tmp/job540.sh >/dev/null 2>&1 < /dev/null & echo started' && { echo "$(date +%T) 원격 기록 시작 ($H)"; exit 0; }
    fi
  done; sleep 2
done; echo "$(date +%T) 3 분 동안 기동 실패"
