#!/bin/bash
# N0 (i)(ii): 컨테이너 안 job474 로 ESDF 슬라이스 측정. 인자: NAME SEC BX BY [TOPIC]
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
N=$1; SEC=$2; BX=$3; BY=$4; T=${5:-/nvblox_node/static_map_slice}
tr -d '\r' < $NSPS/job474_n0_measure.py > /tmp/job474_n0_measure.py; sshpass -p <PW> scp $O -q /tmp/job474_n0_measure.py jetson@$H:/tmp/ || exit 1
timeout 300 sshpass -p <PW> ssh $O jetson@$H "docker exec -u admin --workdir /workspaces/isaac_ros-dev isaac_ros_dev-aarch64-container bash -lc 'export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; python3 /tmp/job474_n0_measure.py $N $SEC $BX $BY $T 2>&1 | grep -av \"^\[\"'"
