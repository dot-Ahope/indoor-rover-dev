#!/bin/bash
# N0 (i)(ii) 측정: 호스트 상자 감사(카메라 점군 → 물리 전면 x·중심 y) → 컨테이너 안 job474 로 ESDF 슬라이스 SEC 초. 인자: NAME [SEC=30]
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
N=${1:-n0}; SEC=${2:-30}
for f in job474_n0_measure.py; do tr -d '\r' < $NSPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/ || exit 1; done
tr -d '\r' < $SPS/job248_audit.py > /tmp/job248_audit.py; sshpass -p <PW> scp $O -q /tmp/job248_audit.py jetson@$H:/tmp/ || exit 1
timeout 300 sshpass -p <PW> ssh $O jetson@$H "export TERM=xterm FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
A=\$(BOX_HINT='1.15 -0.10' timeout 120 python3 /tmp/job248_audit.py 2>&1 | grep -a '^상자:' | head -1); echo \"\$A\"
BX=\$(echo \"\$A\" | grep -oE 'x=[-0-9.]+' | head -1 | cut -d= -f2); BY=\$(echo \"\$A\" | grep -oE 'y=[-0-9.]+' | head -1 | cut -d= -f2); echo \"물리(카메라 점군) 전면 x=\$BX 중심 y=\$BY\"
docker exec -u admin --workdir /workspaces/isaac_ros-dev isaac_ros_dev-aarch64-container bash -lc \"export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; python3 /tmp/job474_n0_measure.py $N $SEC \$BX \$BY /nvblox_node/static_map_slice 2>&1 | grep -av '^\['\"
echo '--- 같은 창, pessimistic 슬라이스'; docker exec -u admin --workdir /workspaces/isaac_ros-dev isaac_ros_dev-aarch64-container bash -lc \"export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; python3 /tmp/job474_n0_measure.py ${N}_pess 10 \$BX \$BY /nvblox_node/pessimistic_static_map_slice 2>&1 | grep -av '^\['\""
