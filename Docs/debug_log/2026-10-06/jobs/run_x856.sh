#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
JX_WHY='10-06 §4 단계별 실측 끝 — bag 정지·회수' JX_TIMEOUT=120 bash $SPS/run_jn.sh job856_end.sh
mkdir -p $SPS/step1; sshpass -p <PW> scp $OPT -q jetson@192.168.0.101:/tmp/bag_step1.tgz jetson@192.168.0.101:/tmp/step_state_1.json $SPS/step1/; ls -la $SPS/step1
