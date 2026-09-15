#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
tr -d '\r' < $SPS/job321_drift.py > /tmp/job321.py; sshpass -p <PW> scp $OPT -q /tmp/job321.py $J:/tmp/job321_drift.py || exit 1
timeout 120 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; echo \"Jetson uptime: \$(uptime -p) | 에이전트 컨테이너: \$(docker ps --format '{{.Names}} {{.Status}}' | grep microros)\"; echo \"EKF 위반 \$(grep -ac 'violat' /tmp/sensors.log) | slam 폐기 \$(grep -ac 'dropping' /tmp/slam.log) | nav2 오류 \$(grep -ac 'ERROR' /tmp/nav2.log) | 에이전트 세션 \$(docker logs microros_agent 2>&1 | grep -ac 'session established')\"; python3 -u /tmp/job321_drift.py 2>&1 | grep -av '^\[INFO\]'; echo \"load: \$(uptime | grep -oE 'load average.*')\"; grep -a '프레임:' /tmp/sensors.log | tail -1 | grep -aoE '[0-9.]+ ms/프레임'"
