#!/bin/bash
# 사용: run_step.sh init | +90 | -90
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
if [ "$1" = init ]; then for f in step_rot.py job853_step_init.sh job854_step.sh; do tr -d "\r" < $SPS/$f > /tmp/$f; done
  sshpass -p <PW> scp $OPT -q /tmp/step_rot.py jetson@192.168.0.101:/tmp/ || exit 1
  JX_WHY='10-06 §4 단계별 회전 실측 — bag 기록 시작·시작 자세(정지)' JX_TIMEOUT=60 bash $SPS/run_jn.sh job853_step_init.sh
else JX_WHY="10-06 §4 단계별 회전 실측 — 제자리 $1° 한 단계(로버 회전)" JX_TIMEOUT=60 bash $SPS/run_jn.sh job854_step.sh "$1"; fi
