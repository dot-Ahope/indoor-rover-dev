#!/bin/bash
# 범용 러너(10-07 재작성 — 스크래치패드 사본 소실, 09-28 판 + JX_WHY 실시간 로그): $1 = 스크립트, 나머지 = 인자. 환경 JETSON_HOST, JX_TIMEOUT, JX_WHY
# 출력은 PC 로도 오고 Jetson /tmp/live/current.log 에도 쌓임(사용자가 tail -F 로 봄, 09-29)
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
H=${JETSON_HOST:-192.168.0.101}; OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
F=$1; shift; T=$(mktemp); tr -d '\r' < "$SPS/$F" > "$T" || exit 1
sshpass -p <PW> scp $OPT -q "$T" jetson@$H:/tmp/$F || exit 1; rm -f "$T"
case "$F" in *.py) CMD="python3 -u /tmp/$F $*" ;; *) CMD="bash /tmp/$F $*" ;; esac
timeout ${JX_TIMEOUT:-300} sshpass -p <PW> ssh $OPT jetson@$H "export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash 2>/dev/null; mkdir -p /tmp/live; { echo; echo \"===== \2026-10-07 08:49:55 시작 | $F | ${JX_WHY:-(목적 미기재)}\"; } >> /tmp/live/current.log; $CMD 2>&1 | tee -a /tmp/live/current.log; echo \"===== \08:49:55 끝 | $F\" >> /tmp/live/current.log"
