#!/bin/bash
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad; PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}')
mkdir -p /tmp/u972; for f in job971_prepchk.py job972_prep_fast.sh; do tr -d '\r' < $N/$f > /tmp/u972/$f; done
sshpass -p $PW scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -q /tmp/u972/* jetson@192.168.0.101:/tmp/ && echo up
