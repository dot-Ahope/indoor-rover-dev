#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
ros2 daemon stop >/dev/null 2>&1
echo "노드에 slam: $(timeout 10 ros2 node list 2>/dev/null | grep -ac slam)"
echo "/map 발행자: $(timeout 8 ros2 topic info /map 2>/dev/null | grep -a 'Publisher count')"
echo "/scan 구독자 노드: $(timeout 8 ros2 topic info -v /scan 2>/dev/null | grep -a 'Node name' | tr -s ' ' | tr '\n' ';' | cut -c1-300)"
P=$(pgrep -f async_slam_toolbox_node | head -1)
echo "slam 스레드 상태: $(for t in /proc/$P/task/*; do cat $t/stat 2>/dev/null | awk '{print $3}'; done | sort | uniq -c | tr '\n' ' ')"
echo "slam wchan: $(for t in /proc/$P/task/*; do cat $t/wchan 2>/dev/null; echo; done | sort | uniq -c | tr '\n' ' ' | cut -c1-300)"
echo "slam 환경 FASTRTPS: $(tr '\0' '\n' < /proc/$P/environ | grep -a FASTRTPS)"
echo "slam 소켓 수: $(ls -l /proc/$P/fd 2>/dev/null | grep -c socket)"
sleep 3; echo "CPU 3 s: $(ps -o pcpu= -p $P)  utime $(awk '{print $14}' /proc/$P/stat)"; sleep 5; echo "5 s 뒤 utime $(awk '{print $14}' /proc/$P/stat)"
