#!/bin/bash
# 새 릴레이 코드(array.array)의 CPU: 두 번째 인스턴스를 20 s 띄우고 top 으로 %CPU 표본 (원 릴레이는 그대로)
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
R=~/ros2_ws/install/rover_bringup/lib/rover_bringup/depth_relay.py
python3 $R --ros-args -r __node:=depth_relay_new -p out_topic:=/relay_new -p min_range:=0.45 -p max_range:=4.0 -p voxel:=0.05 -p min_points_per_voxel:=3 -p persist_frames:=5 -p persist_min:=3 -p process_every:=1 >/tmp/relay_new.log 2>&1 &
P=$!; sleep 8
for i in 1 2 3 4; do printf "새 릴레이 %%CPU: %s | 기존 릴레이(8443) %%CPU: %s\n" "$(top -bn1 -p $P | tail -1 | awk '{print $9}')" "$(top -bn1 -p 8443 | tail -1 | awk '{print $9}')"; sleep 3; done
printf "새 릴레이 출력 hz: "; timeout 6 ros2 topic hz /relay_new 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
kill $P 2>/dev/null; sleep 1
grep -a "프레임" /tmp/relay_new.log | tail -1 | cut -c1-160
