#!/bin/bash
# (PC·WSL) 정지 기록 회수: Jetson /tmp/bag_<이름> 를 묶어 scratchpad/drift_<이름>/ 로 + 로그. 인자: 이름
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
D=$N/drift_$1; mkdir -p $D
sshpass -p "$PW" ssh $O jetson@192.168.0.110 "cd /tmp && tar czf bag_$1.tgz bag_$1 && ls -la bag_$1.tgz"
for f in bag_$1.tgz sensors_$1.log slam_$1.log drift_$1.log; do sshpass -p "$PW" scp $O jetson@192.168.0.110:/tmp/$f $D/; done
cd $D && tar xzf bag_$1.tgz && ls -la $D
