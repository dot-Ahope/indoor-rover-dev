#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
for f in r2_gate.py r2_rec.py; do tr -d "\r" < $SPS/$f > /tmp/$f; done
sshpass -p <PW> scp $OPT -q /tmp/r2_gate.py /tmp/r2_rec.py jetson@192.168.0.101:/tmp/ || exit 1
for b in ${BAGS:-rot3 rot2 f2b3 f2b4}; do
  JX_WHY="10-02 §14 R2 EKF A/B 재생 — bag_$b (로버 안 움직임)" JX_TIMEOUT=600 bash $SPS/run_jn.sh r2_run.sh /tmp/bag_$b /tmp/r2_$b.npz
  sshpass -p <PW> scp $OPT -q jetson@192.168.0.101:/tmp/r2_$b.npz $SPS/f2a6/
done
for b in rot3 rot2 f2b3 f2b4; do sshpass -p <PW> scp $OPT -q jetson@192.168.0.101:/tmp/r2_${b}_gate.csv $SPS/f2a6/; done; ls -la $SPS/f2a6/r2_*
