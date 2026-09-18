#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
LIST=$(sed -n '/^FILES="/,/"$/p' $SPS/run_xfer_all.sh | tr -d '"' | sed 's/^FILES=//')
EX=""; MISS=""; for f in $LIST; do [ -f "$SPS/$f" ] && EX="$EX $f" || MISS="$MISS $f"; done
echo "있음 $(echo $EX | wc -w) / 없음 $(echo $MISS | wc -w):$MISS"
T=$(mktemp -d); for f in $EX; do tr -d '\r' < $SPS/$f > $T/$f; done
cd $T && sshpass -p <PW> scp $OPT -q $EX jetson@192.168.0.101:/tmp/ && sshpass -p <PW> ssh $OPT jetson@192.168.0.101 'chmod +x /tmp/job*.sh; echo "/tmp 스크립트 $(ls /tmp/job* | wc -l) 개"'
rm -rf $T
