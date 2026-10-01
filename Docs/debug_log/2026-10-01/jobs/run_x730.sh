#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
rm -rf /tmp/f14; mkdir -p /tmp/f14
for f in slam.launch.py localization.launch.py navigation.launch.py amcl.yaml; do tr -d '\r' < $SPS/f14src/$f > /tmp/f14/$f; done
for f in job240_clean.sh job726_prep_map.sh job697_restore_chk.py; do tr -d '\r' < $SPS/$f > /tmp/$f; done
sshpass -p <PW> ssh $OPT jetson@192.168.0.101 "rm -rf /tmp/f14; mkdir -p /tmp/f14" && sshpass -p <PW> scp $OPT -q /tmp/f14/* jetson@192.168.0.101:/tmp/f14/ && sshpass -p <PW> scp $OPT -q /tmp/job240_clean.sh /tmp/job726_prep_map.sh /tmp/job697_restore_chk.py jetson@192.168.0.101:/tmp/ || exit 1
JX_WHY='10-01 §7 F1-4 준비: 위치 추정 후보(slam_toolbox 위치 추정·AMCL) 배포·정지 기동 확인(로버 안 움직임, ~9 분)' JX_TIMEOUT=900 bash $SPS/run_jn.sh job730_f14_deploy.sh
