#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
tr -d "\r" < $SPS/job805_evid.py > /tmp/job805_evid.py
sshpass -p <PW> ssh $OPT jetson@192.168.0.101 "mkdir -p /tmp/f2bags" || exit 1
for i in 1 2 3 4 5 6 7 8 9 10 11; do sshpass -p <PW> scp $OPT -q $SPS/f0_f2a$i/bag_f2a$i.tgz jetson@192.168.0.101:/tmp/f2bags/ || exit 1; done
sshpass -p <PW> ssh $OPT jetson@192.168.0.101 "ln -sfn /home/jetson/bags/bag_f2a12 /home/jetson/bags/f2/bag_f2a12 2>/dev/null; mkdir -p /home/jetson/bags/f2; ln -sfn /home/jetson/bags/bag_f2a12 /home/jetson/bags/f2/bag_f2a12"
sshpass -p <PW> scp $OPT -q /tmp/job805_evid.py jetson@192.168.0.101:/tmp/
JX_WHY='10-02 §5 F2 bag 12 개에서 지우기 증거(라이다·nvblox) 추출, 약 10 분' JX_TIMEOUT=1500 bash $SPS/run_jn.sh job805_evid.sh
mkdir -p $SPS/evid; sshpass -p <PW> scp $OPT -q "jetson@192.168.0.101:/tmp/evid/*.npz" $SPS/evid/; ls -la $SPS/evid
