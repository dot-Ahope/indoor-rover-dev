#!/bin/bash
# (PC·WSL) 10-22 §13 f2lp1 bag 회수(러너가 정지로 끝 처리를 못 함) — Jetson ~/bags 사본도 만듦. 비밀번호는 run_jn.sh 에서 읽음(출력 안 함)
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(sed -n 7p $N/run_jn.sh | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
sshpass -p "$PW" ssh $O jetson@192.168.0.110 "mkdir -p ~/bags; rm -rf ~/bags/bag_f2lp1; cp -r /tmp/bag_f2lp1 ~/bags/ && cp /tmp/nav2.log /tmp/slam.log /tmp/sensors.log ~/bags/bag_f2lp1/ 2>/dev/null; du -sh ~/bags/bag_f2lp1"
mkdir -p $N/bx/bag_f2lp1; sshpass -p "$PW" scp $O -r jetson@192.168.0.110:/home/jetson/bags/bag_f2lp1/* $N/bx/bag_f2lp1/ && ls -la $N/bx/bag_f2lp1
