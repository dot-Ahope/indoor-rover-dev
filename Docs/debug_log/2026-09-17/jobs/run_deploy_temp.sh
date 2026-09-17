#!/bin/bash
# nav2_params.yaml 배포(src+install), nav2 재기동 없음 — 기존 설치본과 diff 로 temperature 만 바뀌는지 확인
H=${JETSON_HOST:-172.30.1.8}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
rm -f /tmp/nav2_params.yaml; tr -d '\r' < $SPS/nav2_params_0917T.yaml > /tmp/nav2_params.yaml && [ -s /tmp/nav2_params.yaml ] || exit 1
sshpass -p <PW> scp $O -q /tmp/nav2_params.yaml jetson@$H:/tmp/nav2_params.yaml || exit 1
timeout 60 sshpass -p <PW> ssh $O jetson@$H 'I=~/ros2_ws/install/rover_navigation/share/rover_navigation/config; S=~/ros2_ws/src/rover_navigation/config
python3 -c "import yaml;d=yaml.safe_load(open(\"/tmp/nav2_params.yaml\"));print(\"yaml ok, temperature =\", d[\"controller_server\"][\"ros__parameters\"][\"FollowPathMPPI\"][\"temperature\"])" || exit 1
echo "== 설치본 대비 diff (주석 제외) =="; diff <(grep -v "^\s*#" $I/nav2_params.yaml | sed "s/\s*#.*//") <(grep -v "^\s*#" /tmp/nav2_params.yaml | sed "s/\s*#.*//")
cp $I/nav2_params.yaml /tmp/nav2_params_before_0917T.yaml; for d in $S $I; do cp /tmp/nav2_params.yaml $d/; done; md5sum $S/nav2_params.yaml $I/nav2_params.yaml /tmp/nav2_params.yaml | cut -c1-12
echo -n "실행 중 controller temperature: "; export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; timeout 15 ros2 param get /controller_server FollowPathMPPI.temperature 2>&1 | tail -1'
