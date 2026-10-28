#!/bin/bash
# (PC·WSL) 10-28 f2tt2 산출물 · 로그 회수(PC 쪽 러너 폴링이 끊겨 자동 회수 안 됨) — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함)
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
mkdir -p $N/f0_f2tt2 $N/logs_f2tt2
for f in f0_f2tt2.log f2tt2.csv tegra_f2tt2.log rss_f2tt2.txt proc_f2tt2.log bag_f2tt2.tgz net_f2tt2.log; do sshpass -p "$PW" scp $O -q jetson@192.168.0.110:/tmp/$f $N/f0_f2tt2/ 2>/dev/null && echo "회수 $f"; done
for f in nav2 slam sensors; do sshpass -p "$PW" scp $O -q jetson@192.168.0.110:/tmp/$f.log $N/logs_f2tt2/ && echo "회수 $f.log"; done
