#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
timeout 60 sshpass -p <PW> scp $O -q jetson@$H:/tmp/j452.log /mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad/j452_sim_cc.txt && echo copied
