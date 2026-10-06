#!/bin/bash
S=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
tr -d "\r" < $S/step_rot.py > /tmp/step_rot.py; sshpass -p <PW> scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -q /tmp/step_rot.py jetson@192.168.0.101:/tmp/ && bash $S/run_step.sh "$1"
