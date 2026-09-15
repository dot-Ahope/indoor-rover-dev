#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=6"
J=jetson@192.168.0.101
for i in $(seq 1 ${1:-12}); do
  if ping -c 1 -W 2 192.168.0.101 >/dev/null 2>&1; then
    echo "핑 복구 $(date +%T) (시도 $i)"
    tr -d '\r' < $SPS/job323_state.sh > /tmp/job323.sh
    sshpass -p <PW> scp $OPT -q /tmp/job323.sh $J:/tmp/job323_state.sh && sshpass -p <PW> ssh $OPT $J "bash /tmp/job323_state.sh"
    exit 0
  fi
  sleep 5
done
echo "핑 실패 ($(( ${1:-12} * 5 )) s)"
