#!/bin/bash
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
for i in $(seq 1 40); do
  n=$(timeout 15 sshpass -p <PW> ssh $O jetson@172.30.1.8 "grep -ac '끝 ' /tmp/rsim423.log" 2>/dev/null)
  [ "$n" = "1" ] && { echo done; break; }
  sleep 15
done
timeout 20 sshpass -p <PW> ssh $O jetson@172.30.1.8 "cat /tmp/rsim423.log"
