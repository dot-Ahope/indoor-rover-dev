#!/bin/bash
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad; PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}')
mkdir -p /tmp/u963; for f in job551_f0drive.sh job956_gcmchk.py; do tr -d '\r' < $N/$f > /tmp/u963/$f; done
sshpass -p $PW scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -q /tmp/u963/* jetson@192.168.0.101:/tmp/ && echo up
