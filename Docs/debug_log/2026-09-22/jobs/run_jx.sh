#!/bin/bash
# 범용 러너(09-22): 새 scratchpad 의 Jetson 측 파일 하나를 CRLF 제거 후 전송·실행. 인자: <job파일> [인자…]
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
F=$1; shift; tr -d '\r' < $NSPS/$F > /tmp/$F; sshpass -p <PW> scp $O -q /tmp/$F jetson@$H:/tmp/ || exit 1
case "$F" in *.py) RUN="python3 /tmp/$F";; *) RUN="bash /tmp/$F";; esac
timeout ${JX_TIMEOUT:-300} sshpass -p <PW> ssh $O jetson@$H "export TERM=xterm FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source /home/jetson/ros2_ws/install/setup.bash; $RUN $*"
