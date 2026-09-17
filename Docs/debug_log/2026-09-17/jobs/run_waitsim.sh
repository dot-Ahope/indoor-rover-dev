#!/bin/bash
# 원격 시뮬 로그에 끝 표시가 나올 때까지 대기(최대 N 초) 후 출력
H=${JETSON_HOST:-172.30.1.8}; LOG=${1:-/tmp/wobblesim.log}; MAX=${2:-1500}
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
T0=$(date +%s)
while [ $(( $(date +%s) - T0 )) -lt $MAX ]; do
  N=$(timeout 15 sshpass -p <PW> ssh $O jetson@$H "grep -ac '흔들림' $LOG; grep -ac '######## 끝' $LOG" 2>/dev/null | tr '\n' ' ')
  set -- $N; [ "${2:-0}" = "1" ] && break
  sleep 30
done
echo "경과 $(( $(date +%s) - T0 )) s, 완료 $N"
timeout 30 sshpass -p <PW> ssh $O jetson@$H "cat $LOG"
