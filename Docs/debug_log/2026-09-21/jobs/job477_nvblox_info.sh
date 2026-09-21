#!/bin/bash
CN=isaac_ros_dev-aarch64-container
X() { docker exec -u admin --workdir /workspaces/isaac_ros-dev $CN bash -lc "$1"; }
echo "== 노드 발행 토픽:"; X 'export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; timeout 25 ros2 node info /nvblox_node 2>/dev/null | sed -n "/Publishers/,/Service Servers/p" | grep -E "nvblox|slice|esdf|mesh|map" | head -12'
echo "== 슬라이스 토픽 hz/타입:"; X 'export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; T=$(timeout 15 ros2 topic list 2>/dev/null | grep -E "map_slice" | head -1); echo "topic=$T"; [ -n "$T" ] && timeout 12 ros2 topic hz $T 2>&1 | grep -ao "average rate: [0-9.]*" | head -1; [ -n "$T" ] && timeout 8 ros2 topic echo $T --once --field resolution 2>/dev/null | head -1'
echo "== NVBlox Rates(마지막 블록):"; awk '/NVBlox Rates/{b=""; f=1} f{b=b"\n"$0} END{print b}' /tmp/nvblox_n0.log | head -14 | cut -c1-120
echo "== tegrastats 8 s (nvblox 실행 중):"; timeout 9 tegrastats --interval 1000 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i ~ /GR3D_FREQ/) g=$(i+1); if(match($0,/CPU \[[^]]*\]/)) c=substr($0,RSTART,RLENGTH); print g, c}' | tail -6
echo "== 컨테이너 nvblox CPU: $(top -b -n2 -d2 2>/dev/null | awk '/PID +USER/{f++} f==2' | awk '$12 ~ /nvblox/ {printf "%s%% ", $9}') | load $(cut -d' ' -f1-3 /proc/loadavg)"
