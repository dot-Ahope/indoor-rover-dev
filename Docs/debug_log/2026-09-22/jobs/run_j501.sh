#!/bin/bash
# 09-22 §1 절단 A/B 러너(PC): job501 전송·실행 → JSON·감사 출력 회수. 인자: BX BY
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
BX=${1:-1.153}; BY=${2:--0.079}; PHASE=${3:-a}
for f in job501_trunc_ab.sh job488_layer_ab.sh job489_gridcmp.py; do tr -d '\r' < $NSPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/ || exit 1; done
timeout 560 sshpass -p <PW> ssh $O jetson@$H "export TERM=xterm; bash /tmp/job501_trunc_ab.sh $BX $BY $PHASE"
if [ "$PHASE" = a ]; then FL="grid_stvl3_costmap.json grid_t4_costmap.json grid_t4_slice.json j501_ab_t4.txt nvblox_t4.log"; else FL="grid_t2_costmap.json grid_t2_slice.json j501_ab_t2.txt nvblox_t2.log"; fi
for f in $FL; do sshpass -p <PW> scp $O -q jetson@$H:/tmp/$f $NSPS/$f && echo "회수 $f $(stat -c %s $NSPS/$f) B"; done
