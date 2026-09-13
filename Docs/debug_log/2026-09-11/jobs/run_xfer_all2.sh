#!/bin/bash
# 재부팅 후 /tmp 작업 스크립트 일괄 재전송 (2026-09-14: job* 전체)
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
cd $SPS || exit 1
FILES=$(ls job*.sh job*.py 2>/dev/null | tr '\n' ' ')
for t in 1 2 3; do
  if sshpass -p <PW> scp $OPT -q $FILES jetson@192.168.0.101:/tmp/ 2>&1; then
    sshpass -p <PW> ssh $OPT jetson@192.168.0.101 \
      'sed -i "s/\r$//" /tmp/job*.sh /tmp/job*.py 2>/dev/null; chmod +x /tmp/job*.sh
       echo "/tmp 스크립트: $(ls /tmp/job* | wc -l)개"
       for f in /tmp/job*.py; do python3 -m py_compile $f 2>/dev/null || echo "COMPILE FAIL $f"; done
       echo "py 컴파일 검사 끝"'
    exit 0
  fi; sleep 3
done; echo "전송 실패"; exit 1
