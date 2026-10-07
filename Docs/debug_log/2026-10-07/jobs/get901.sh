#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad; OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
for c in clean A_walk08 C_sway D_inout E_fast; do for f in g4_$c.npz g4_${c}_gate.csv; do sshpass -p <PW> scp $OPT -q jetson@192.168.0.101:/tmp/$f $SPS/g4/ || echo "실패 $f"; done; done
for d in 81 82 83 84 85; do sshpass -p <PW> scp $OPT -q jetson@192.168.0.101:/tmp/g4_run_$d.txt $SPS/g4/; done; ls $SPS/g4
