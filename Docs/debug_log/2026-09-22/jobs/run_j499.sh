#!/bin/bash
# 09-22: 09-21 세트 + 절단 A/B 파일 재전송 → 컨테이너 복구
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
FILES="job472_container.sh job473_nvblox_run.sh job474_n0_measure.py job478_boxphys.py job488_layer_ab.sh job489_gridcmp.py job248_audit.py job315_boxcells.py job440_startclear.py job499_container_up.sh job482_nvblox_state.sh nvblox_n0.yaml nvblox_n0_t2.yaml"
mkdir -p /tmp/x499; for f in $FILES; do tr -d '\r' < $NSPS/$f > /tmp/x499/$f || exit 1; done
sshpass -p <PW> scp $O -q /tmp/x499/* jetson@$H:/tmp/ || { echo "전송 실패"; exit 1; }
echo "전송 $(echo $FILES | wc -w) 개"
timeout 600 sshpass -p <PW> ssh $O jetson@$H "chmod +x /tmp/job*.sh; for f in /tmp/job474_n0_measure.py /tmp/job478_boxphys.py /tmp/job488_layer_ab.sh; do :; done; bash /tmp/job499_container_up.sh"
