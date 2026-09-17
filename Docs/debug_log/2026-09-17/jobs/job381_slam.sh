#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
P=$(pgrep -f async_slam_toolbox_node | head -1)
echo "slam pid $P: $(ps -o stat=,pcpu=,etime=,rss= -p $P)  threads $(ls /proc/$P/task | wc -l)"
echo "slam.log 줄 수 $(wc -l < /tmp/slam.log), 'queue is full' $(grep -ac 'queue is full' /tmp/slam.log), 마지막 3 줄:"; tail -3 /tmp/slam.log | cut -c1-200
printf "/map hz(12 s): "; timeout 12 ros2 topic hz /map 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1; echo
printf "map->odom (10 s): "; timeout 10 ros2 run tf2_ros tf2_echo map odom 2>&1 | grep -aE "At time|Translation|Invalid|does not exist" | head -2 | tr '\n' ' '; echo
printf "/tf 안 map->odom 발행: "; timeout 6 ros2 topic echo /tf 2>/dev/null | grep -a -B3 'child_frame_id: odom' | grep -aE 'sec:' | head -2 | tr '\n' ' '; echo
echo "epoch now $(date +%s)"
echo "slam 파라미터: $(grep -aE 'minimum_time_interval|transform_publish_period|map_update_interval|scan_queue_size|throttle_scans|resolution:' ~/ros2_ws/install/rover_bringup/share/rover_bringup/config/*slam*.yaml 2>/dev/null | tr -s ' ' | tr '\n' ';' | cut -c1-300)"
