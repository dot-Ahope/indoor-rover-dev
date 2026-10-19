#!/bin/bash
# 주행 로그 원격 감시(읽기만, DDS 없음): 인자 NAME
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $SPS/run_jn.sh | head -1 | awk '{print $3}')
sshpass -p "$PW" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR jetson@192.168.0.110 "timeout 1500 tail -n +1 -F /tmp/f0_$1.log" 2>/dev/null
