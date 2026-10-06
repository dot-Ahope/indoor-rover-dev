#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
for f in occ_scan.py occ_run.sh; do tr -d "\r" < $SPS/$f > /tmp/$f; done
sshpass -p <PW> scp $OPT -q /tmp/occ_scan.py /tmp/occ_run.sh jetson@192.168.0.101:/tmp/ || exit 1
JX_WHY='10-06 §11 움직이는 몸 합성 가림 5 조건 동시 재생(약 35 분, 로버 안 움직임)' JX_TIMEOUT=3000 bash $SPS/run_jn.sh job870_occmove.sh
for c in A_walk08 B_walk05 C_arc50_sway D_arc30_inout E_arc50_fast; do sshpass -p <PW> scp $OPT -q jetson@192.168.0.101:/tmp/occm_$c.npz $SPS/occ/; done; ls $SPS/occ
