#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
bash $SPS/run_x810.sh >/dev/null 2>&1; tr -d "\r" < $SPS/job726_prep_map.sh > /tmp/job726_prep_map.sh; tr -d "\r" < $SPS/job240_clean.sh > /tmp/job240_clean.sh; sshpass -p <PW> scp $OPT -q /tmp/job726_prep_map.sh /tmp/job240_clean.sh jetson@192.168.0.101:/tmp/ || exit 1
JX_WHY='10-06 R3 prep: rf2o·그림자 EKF 켬(로버 출발 테이프, 정지, 약 4 분)' JX_TIMEOUT=700 bash $SPS/run_jn.sh job852_prep_rf2o.sh
JX_WHY='10-06 R3 정지 기동 확인' JX_TIMEOUT=200 bash $SPS/run_jn.sh job851_r3chk.sh
