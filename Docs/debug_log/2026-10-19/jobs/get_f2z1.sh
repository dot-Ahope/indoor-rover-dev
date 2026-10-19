#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $SPS/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
mkdir -p $SPS/f2z1_vis/bag_f2z1
for f in bag_f2z1_0.db3 metadata.yaml; do sshpass -p "$PW" scp $O jetson@192.168.0.110:/home/jetson/bags/bag_f2z1/$f $SPS/f2z1_vis/bag_f2z1/ || echo "실패 $f"; done
sshpass -p "$PW" ssh $O jetson@192.168.0.110 "grep -aE '결과:|누적 회전|stuck' /tmp/f0_f2z1.log" > $SPS/f2z1_run.txt
ls -la $SPS/f2z1_vis/bag_f2z1; cat $SPS/f2z1_run.txt
