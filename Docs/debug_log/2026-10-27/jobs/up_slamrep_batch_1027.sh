#!/bin/bash
# (PC·WSL) §26 재생 A/B 묶음 전송 · 실행 · 결과 회수 — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함)
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
for f in run_slam_replay.sh slam_replay_feed.py; do sed 's/\r$//' $N/$f > /tmp/$f; sshpass -p "$PW" scp $O /tmp/$f jetson@192.168.0.110:/tmp/$f; done
JX_TIMEOUT=2400 JX_WHY='SLAM 재생 A/B 6 변형(10-27 §26, 로버 안 움직임, 도메인 42)' bash $N/run_jn.sh run_slamrep_batch_1027.sh
mkdir -p $N/slamrep; sshpass -p "$PW" scp $O "jetson@192.168.0.110:/tmp/slamrep/*" $N/slamrep/ && echo 회수
