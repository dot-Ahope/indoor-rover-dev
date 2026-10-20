#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $SPS/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
for c in on off; do mkdir -p $SPS/bt/bt_$c; for f in bt_${c}_0.db3 metadata.yaml; do sshpass -p "$PW" scp $O jetson@192.168.0.110:/home/jetson/bags/bt_$c/$f $SPS/bt/bt_$c/ || echo "실패 $c $f"; done; done; du -sh $SPS/bt/*
