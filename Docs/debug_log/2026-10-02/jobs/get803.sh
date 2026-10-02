#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
sshpass -p <PW> ssh $OPT jetson@192.168.0.101 'awk "/job803_locjump.sh office_v2:3.0/{f=1} f" /tmp/live/current.log | grep -av "^\["'
for f in office_v2_3.0 cand_1002_f2a12_c276_nolc_3.0 office_v2_1.0; do sshpass -p <PW> scp $OPT -q jetson@192.168.0.101:/tmp/locjump_$f.npz $SPS/f2a6/; done
