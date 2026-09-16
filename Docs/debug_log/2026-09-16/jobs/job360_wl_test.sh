#!/bin/bash
# 화이트리스트별 /wheel_odom 가시성 (에이전트가 어떤 주소를 광고하는지 간접 확인)
source /opt/ros/humble/setup.bash
X=~/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
for ip in 172.17.0.1 172.30.1.8; do
  sed "/<interfaceWhiteList>/,/<\/interfaceWhiteList>/c\        <interfaceWhiteList><address>$ip</address></interfaceWhiteList>" $X > /tmp/wl_$ip.xml
  ros2 daemon stop >/dev/null 2>&1
  printf "  whitelist %-12s hz: " $ip; FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/wl_$ip.xml timeout 8 ros2 topic hz /wheel_odom 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1; echo
done
ros2 daemon stop >/dev/null 2>&1
