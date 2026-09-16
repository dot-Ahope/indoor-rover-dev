#!/bin/bash
# Jetson LAN(172.30.1.8) 연결 확인 + 스크립트 실행 러너: $1 = 실행할 원격 스크립트(스크래치패드 파일명)
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
H=${JETSON_HOST:-172.30.1.8}
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8 -o ServerAliveInterval=3 -o ServerAliveCountMax=3"
ping -c 2 -W 2 $H | tail -1
timeout 20 sshpass -p <PW> ssh $O jetson@$H 'echo SSH_OK; uptime' 2>&1; echo "ssh exit=${PIPESTATUS[0]}"
if [ -n "$1" ]; then
  tr -d '\r' < $SPS/$1 > /tmp/$1
  timeout 20 sshpass -p <PW> scp $O -q /tmp/$1 jetson@$H:/tmp/$1; echo "scp exit=$?"
  timeout 120 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/$1" 2>&1; echo "run exit=${PIPESTATUS[0]}"
fi
