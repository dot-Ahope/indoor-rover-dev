#!/bin/bash
# (EKF 노드 이름은 ekf.yaml 키와 같게 ekf_filter_node 유지 — 도메인 42 라 라이브와 안 섞임)
# B2·B3 오프라인 A/B 래퍼(Jetson, 2026-09-28 §27): 도메인 42 에서 C++ 컨디셔너(설정 V) + EKF(ekf.yaml, use_sim_time) 를 띄우고 job627 로 재생.
#   V: off = 기본(B2·B3 꺼짐) / b2 = icr_enable / b23 = icr_enable + rot_cov_enable.  인자: BAG V
set +u
BAG=$1; V=$2
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
export ROS_DOMAIN_ID=42
pkill -9 -f "b2ab_cond" 2>/dev/null; pkill -9 -f "ekf_node.*use_sim_time:=true" 2>/dev/null; sleep 1
P="-p use_sim_time:=true"; [ "$V" = b2 ] && P="$P -p icr_enable:=true"; [ "$V" = b23 ] && P="$P -p icr_enable:=true -p rot_cov_enable:=true"
Y=$(ros2 pkg prefix rover_bringup)/share/rover_bringup/config/ekf.yaml
setsid ros2 run rover_bringup sensor_conditioner_node --ros-args -r __node:=b2ab_cond $P > /tmp/b2ab_cond_$V.log 2>&1 &
setsid ros2 run robot_localization ekf_node --ros-args --params-file $Y -p use_sim_time:=true -r odometry/filtered:=/odometry/filtered > /tmp/b2ab_ekf_$V.log 2>&1 &
sleep 5
echo "== $BAG / 설정 $V | 컨디셔너 icr=$(ros2 param get /b2ab_cond icr_enable 2>/dev/null | grep -o 'True\|False') rot_cov=$(ros2 param get /b2ab_cond rot_cov_enable 2>/dev/null | grep -o 'True\|False')"
python3 /tmp/job627_ekfreplay.py $BAG 2>&1 | grep -av "^\["
pkill -INT -f "b2ab_cond" 2>/dev/null; pkill -INT -f "ekf_node.*use_sim_time:=true" 2>/dev/null; sleep 1; pkill -9 -f "b2ab_cond" 2>/dev/null; pkill -9 -f "ekf_node.*use_sim_time:=true" 2>/dev/null
echo "  남은 노드: $(pgrep -fc 'b2ab_cond|ekf_node.*use_sim_time')"
