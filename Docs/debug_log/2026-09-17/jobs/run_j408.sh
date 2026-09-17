#!/bin/bash
H=${JETSON_HOST:-172.30.1.8}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
DOC=/mnt/f/6_Indoor_Rover/Rover/Docs/debug_log
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10 -o ServerAliveInterval=10"
mkdir -p /mnt/f; mountpoint -q /mnt/f || mount -t drvfs F: /mnt/f
for f in job355_mppi_sim.py job408_wobblesim.sh; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/$f || exit 1; done
sshpass -p <PW> scp $O -q $DOC/2026-09-16/bags/bag_mp4.tgz jetson@$H:/tmp/bag_mp4.tgz && echo "mp4 업로드"
sshpass -p <PW> scp $O -q $DOC/2026-09-17/bags/bag_mp8.tgz jetson@$H:/tmp/bag_mp8.tgz && echo "mp8 업로드"
timeout 60 sshpass -p <PW> ssh $O jetson@$H "cd /tmp && for b in mp4 mp8; do [ -d bag_\$b ] || tar xzf bag_\$b.tgz; done; ls -d bag_mp4 bag_mp8 bag_mp11 | tr '\n' ' '; rm -f /tmp/wobblesim.log; setsid nohup bash /tmp/job408_wobblesim.sh > /tmp/wobblesim.log 2>&1 & echo; echo started \$(date +%T)"
