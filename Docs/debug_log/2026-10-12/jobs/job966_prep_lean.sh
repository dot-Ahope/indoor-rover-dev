#!/bin/bash
# 10-12 §6: 부하 여유 구성 prep — 그림자 EKF A 끔·MPPI 궤적 발행 끔, PreferForward 15. 로버 안 움직임
Y=/home/jetson/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml
sed -i "s/\(PreferForwardCritic: {enabled: true, cost_power: 1, cost_weight: \)[0-9.]*/\115.0/" $Y
echo "  설치본 PreferForward: $(grep -a 'PreferForwardCritic: {' $Y | grep -o 'cost_weight: [0-9.]*')"
export EXTRA_SENSORS="rf2o:=true shadow:=false gate_v:=on gate_vref:=wheel" EXTRA_NAV="global_camera:=nvblox replan_hz:=0.5"
bash /tmp/job780_prep_navmap.sh > /tmp/prep966.txt 2>&1
grep -aE "wheel_odom|map->odom|배터리|전역 plugins|EKF 위반" /tmp/prep966.txt | cut -c1-200
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
sleep 15
for n in controller_server planner_server bt_navigator nav_map_server; do for i in 1 2 3; do r=$(timeout 15 ros2 lifecycle get /$n 2>&1 | tail -1); echo "$r" | grep -q "\[" && break; done; echo "  $n: $r"; done
python3 /tmp/job956_gcmchk.py
for k in FollowPathMPPI.PreferForwardCritic.cost_weight FollowPathMPPI.visualize; do for i in 1 2 3; do r=$(timeout 15 ros2 param get /controller_server $k 2>&1 | tail -1); echo "$r" | grep -q value && break; done; echo "  $k: $r"; done
for i in 1 2 3; do r=$(timeout 15 ros2 param get /global_costmap/global_costmap nvblox_layer.nav2_costmap_global_frame 2>&1 | tail -1); echo "$r" | grep -q value && break; done
echo "  전역 nvblox 프레임: $r · BT $(grep -o 'RateController hz="[0-9.]*"' /tmp/nav_to_pose_active.xml) · ekf_node $(pgrep -fc ekf_node) 개(그림자 $(pgrep -fc '__node:=ekf_shadow_a')) · rf2o $(pgrep -fc rf2o_laser_odometry_node) · rf2o_gate $(pgrep -fc rf2o_gate.py)"
echo "  map→base: $(timeout 10 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -a -m1 Translation) · 잔류 러너 $(pgrep -fc 'job551_f0drive') · no map 경고 $(grep -ac 'no map received' /tmp/nav2.log)"
sleep 20; echo "  정지 부하(20 s 뒤): $(cut -d' ' -f1-3 /proc/loadavg) · 유휴 $(top -b -n2 -d3 | grep -a '%Cpu' | tail -1 | grep -o '[0-9.]* id')"
