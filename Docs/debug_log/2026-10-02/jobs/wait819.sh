#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
for i in $(seq 1 120); do
  sshpass -p <PW> ssh $O jetson@192.168.0.101 "grep -aqE '=== 끝|주행하지 않음' /tmp/f0_f2b4.log" && break; sleep 10; done
mkdir -p $SPS/f0_f2b4; for f in f0_f2b4.log f2b4.csv bag_f2b4.tgz; do sshpass -p <PW> scp $O -q jetson@192.168.0.101:/tmp/$f $SPS/f0_f2b4/; done
cat $SPS/f0_f2b4/f0_f2b4.log | tail -14
