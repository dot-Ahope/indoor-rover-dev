#!/bin/bash
# N6-1 정지 검증 러너(PC): 현재(모드 N, prep 직후) → G1·G2 측정 → 모드 S 로 전환(job488 stvl, Nav2 만) → 같은 측정 → 모드 N 복귀. JSON 회수. 인자: BX BY
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
BX=${1:-1.145}; BY=${2:--0.068}
for f in job518_g1g2.sh job488_layer_ab.sh job489_gridcmp.py; do tr -d '\r' < $NSPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/ || exit 1; done
timeout 560 sshpass -p <PW> ssh $O jetson@$H "export TERM=xterm; bash /tmp/job518_g1g2.sh n61N $BX $BY; echo '######## 모드 S 전환'; QUICK=1 bash /tmp/job488_layer_ab.sh stvl $BX $BY 2>&1 | grep -aE '실행값|오류'; sleep 5; bash /tmp/job518_g1g2.sh n61S $BX $BY; echo '######## 모드 N 복귀'; QUICK=1 bash /tmp/job488_layer_ab.sh nvblox $BX $BY 2>&1 | grep -aE '실행값|오류'"
for f in grid_n61Ng_costmap.json grid_n61Nl_costmap.json grid_n61Sg_costmap.json grid_n61Sl_costmap.json; do sshpass -p <PW> scp $O -q jetson@$H:/tmp/$f $NSPS/$f && echo "회수 $f $(stat -c %s $NSPS/$f) B"; done
