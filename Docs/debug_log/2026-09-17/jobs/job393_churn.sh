#!/bin/bash
# Fast DDS 2.6.12 확인: /tf·/map 구독자를 반복 생성·해체하면서 SLAM map->odom 생존 확인 (로버 정지)
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
P=$(pgrep -f async_slam_toolbox_node | head -1)
echo "slam lib: $(grep -a libfastrtps /proc/$P/maps | awk '{print $6}' | sort -u | tr '\n' ' ')"
echo "기준:"; python3 /tmp/job386_slamalive.py 2>&1 | grep -av "^\["
for r in 1 2 3; do
  timeout -s INT 6 ros2 bag record -o /tmp/churn_bag_$r /tf /tf_static /map /scan > /dev/null 2>&1; rm -rf /tmp/churn_bag_$r
  for i in $(seq 1 8); do timeout 3 ros2 topic echo /tf --once > /dev/null 2>&1; timeout 3 ros2 topic echo /map --once --no-arr > /dev/null 2>&1; done
  printf "라운드 %s (bag 해체 + 구독자 16 회): " $r; python3 /tmp/job386_slamalive.py 2>&1 | grep -av "^\[" | tr '\n' ' '; echo
done
echo "slam 그래프: $(timeout 8 ros2 node list 2>/dev/null | grep -c slam)  스레드 lock 대기: $(for t in /proc/$P/task/*; do cat $t/wchan 2>/dev/null; echo; done | grep -c futex)"
