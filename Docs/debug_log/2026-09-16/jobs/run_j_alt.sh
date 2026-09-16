#!/bin/bash
# 범용 러너: $1 = 스크립트 파일명 (스크래치패드 기준), 나머지 = 인자
# 2026-09-10: 전송 전에 CRLF 를 제거한다. Windows 에서 만든 스크립트가 그대로 올라가면
#   원격 bash 가 $'\r' 을 명령으로 읽어 통째로 깨진다(job194 실제 사고).
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
F=$1; shift
T=$(mktemp)
tr -d '\r' < "$SPS/$F" > "$T" || exit 1
sshpass -p <PW> scp $OPT -q "$T" jetson@${JETSON_HOST:-172.30.1.8}:/tmp/$F || exit 1
rm -f "$T"
case "$F" in
  *.py) CMD="python3 /tmp/$F $*" ;;
  *)    CMD="export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; bash /tmp/$F $*" ;;
esac
timeout 300 sshpass -p <PW> ssh $OPT jetson@${JETSON_HOST:-172.30.1.8} "export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; $CMD 2>&1 | tail -60"
