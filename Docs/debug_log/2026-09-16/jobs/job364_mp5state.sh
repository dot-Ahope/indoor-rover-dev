#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
echo "=== 로버 상태 ==="; printf "cmd_vel: "; timeout 4 ros2 topic hz /cmd_vel 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo "없음(정지)"
timeout 8 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' '; echo
echo "=== nav2.log: goal 이후 이벤트 ==="; grep -aE "Begin navigating|Failed to make progress|STUCK|Aborting handle|missed its desired|Goal succeeded|Received request to clear|Client requested" /tmp/nav2.log | awk -F'[][]' '{split($4,a,"."); if (a[1]+0>=1789547850) print}' | cut -c1-150 | head -14
echo "루프 미달: $(grep -a 'missed its desired' /tmp/nav2.log | awk -F'[][]' '{split($4,a,"."); if (a[1]+0>=1789547850) print}' | wc -l)  STUCK(shadow): $(grep -a 'STUCK' /tmp/nav2.log | awk -F'[][]' '{split($4,a,"."); if (a[1]+0>=1789547850) print}' | wc -l)"
echo "=== drive 로그 후반 ==="; grep -aE "^ +(2[0-9]|[3-8][0-9])\.[0-9] " /tmp/drive_mp5.log | awk 'NR%5==1' | cut -c1-110
[ -d /tmp/bag_mp5 ] && [ ! -f /tmp/bag_mp5.tgz ] && tar czf /tmp/bag_mp5.tgz -C /tmp bag_mp5 && echo "bag tgz $(stat -c %s /tmp/bag_mp5.tgz)"
