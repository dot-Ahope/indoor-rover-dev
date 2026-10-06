#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
mkdir -p /tmp/r3up; for f in scripts/rf2o_gate.py config/rf2o.yaml launch/ekf.launch.py CMakeLists.txt; do tr -d "\r" < $SPS/r3src/$(basename $f) > /tmp/r3up/$(basename $f); done
for f in r3_rec.py r3_replay.sh job240_clean.sh; do tr -d "\r" < $SPS/$f > /tmp/r3up/$f; done
cp $SPS/f0_f2b3/bag_f2b3.tgz $SPS/f0_f2b4/bag_f2b4.tgz /tmp/r3up/
sshpass -p <PW> ssh $OPT jetson@192.168.0.101 "mkdir -p /tmp/r3" && sshpass -p <PW> scp $OPT -q /tmp/r3up/* jetson@192.168.0.101:/tmp/r3/ || exit 1
sshpass -p <PW> ssh $OPT jetson@192.168.0.101 "cp /tmp/r3/r3_rec.py /tmp/r3/r3_replay.sh /tmp/r3/job240_clean.sh /tmp/"
JX_WHY='10-06 R3 rf2o 게이트 정식 배포·빌드(로버 안 움직임)' JX_TIMEOUT=400 bash $SPS/run_jn.sh job850_deploy.sh
for b in f2b4 f2b3; do JX_WHY="10-06 R3 정식 ekf.launch 재생 검증 — bag_$b(도메인 42)" JX_TIMEOUT=600 bash $SPS/run_jn.sh r3_replay.sh /tmp/bag_$b /tmp/r3_$b.npz; sshpass -p <PW> scp $OPT -q jetson@192.168.0.101:/tmp/r3_$b.npz jetson@192.168.0.101:/tmp/r3_${b}_gate.csv $SPS/f2a6/; done
ls -la $SPS/f2a6/r3_*
