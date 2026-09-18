#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
timeout 30 sshpass -p <PW> ssh $O jetson@$H "grep -ac '^S[12]_' /tmp/j452.log; grep -a '########\|Traceback\|Error' /tmp/j452.log | tail -3; pgrep -fc job452_run.sh"
