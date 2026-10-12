#!/bin/bash
# 10-12 §3.3: Nav2·센서 로그 통째 회수(재부팅 전에)
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad; PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
mkdir -p $N/f0_${RUN:-f2f3}; sshpass -p $PW ssh $O jetson@192.168.0.101 "cd /tmp && gzip -c nav2.log > nav2_${RUN:-f2f3}.log.gz && gzip -c sensors.log > sensors_${RUN:-f2f3}.log.gz && ls -la nav2_${RUN:-f2f3}.log.gz sensors_${RUN:-f2f3}.log.gz | awk '{print \$5, \$9}'"
sshpass -p $PW scp $O -q jetson@192.168.0.101:/tmp/nav2_${RUN:-f2f3}.log.gz jetson@192.168.0.101:/tmp/sensors_${RUN:-f2f3}.log.gz $N/f0_${RUN:-f2f3}/ && echo 회수
