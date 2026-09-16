#!/bin/bash
# USB 가상 IP(192.168.55.1) 링크 진단 — 핑, TCP 22 배너, ssh 3회(stderr 포함), norc 진단 스크립트 실행
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
H=192.168.55.1
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=8 -o ServerAliveInterval=3 -o ServerAliveCountMax=3"
echo "=== 핑 5회 ==="; ping -c 5 -i 0.3 -W 2 $H | tail -2
echo "=== TCP 22 배너 ==="; timeout 6 bash -c "exec 3<>/dev/tcp/$H/22; head -c 40 <&3; echo" 2>&1 | head -2
for i in 1 2 3; do
  echo "=== ssh 시도 $i $(date +%T) ==="
  timeout 25 sshpass -p <PW> ssh $O -o LogLevel=INFO jetson@$H 'date; uptime; echo END' 2>&1 | tail -6
  echo "exit=${PIPESTATUS[0]}"
done
echo "=== norc 진단 스크립트 ==="
tr -d '\r' < $SPS/job324_diag.sh > /tmp/job324.sh
timeout 20 sshpass -p <PW> scp $O -o LogLevel=ERROR -q /tmp/job324.sh jetson@$H:/tmp/job324_diag.sh; echo "scp exit=$?"
timeout 90 sshpass -p <PW> ssh $O -o LogLevel=ERROR jetson@$H 'bash --noprofile --norc /tmp/job324_diag.sh' 2>&1; echo "diag exit=${PIPESTATUS[0]}"
