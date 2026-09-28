#!/bin/bash
# 범용 러너(09-28, 현재 스크래치패드 기준 — 옛 82ce61d4 폴더 소실 대체): $1 = 스크립트 파일명, 나머지 = 인자. 환경 JETSON_HOST, JX_TIMEOUT
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
H=${JETSON_HOST:-192.168.0.101}; OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
F=$1; shift; T=$(mktemp); tr -d '\r' < "$SPS/$F" > "$T" || exit 1
sshpass -p <PW> scp $OPT -q "$T" jetson@$H:/tmp/$F || exit 1; rm -f "$T"
case "$F" in *.py) CMD="python3 /tmp/$F $*" ;; *) CMD="bash /tmp/$F $*" ;; esac
timeout ${JX_TIMEOUT:-300} sshpass -p <PW> ssh $OPT jetson@$H "export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash 2>/dev/null; $CMD"
