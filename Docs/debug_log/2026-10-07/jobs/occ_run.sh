#!/bin/bash
# 10-06 §10: 합성 가림 1 조건 — 인자 DOMAIN COVERAGE OUT [CENTER_DEG RHO]
set +u; DOM=$1; COV=$2; OUT=$3; CD=${4:-20.0}; RHO=${5:-0.6}; EXTRA=${6:-}; BAG=/tmp/bag_step1   # EXTRA = '-p amp:=… -p period:=… -p move_deg:=… -p legs:=true'
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; source ~/rf2o_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; export ROS_DOMAIN_ID=$DOM
D=$(python3 -c "import yaml;print(int(yaml.safe_load(open('$BAG/metadata.yaml'))['rosbag2_bagfile_information']['duration']['nanoseconds']/1e9)+3)")
setsid ros2 launch rover_bringup ekf.launch.py rf2o:=true use_sim_time:=true gate_q:=${GQ:-off} gate_v:=${GV:-off} gate_vref:=${GVREF:-abs} gate_csv:=${OUT%.npz}_gate.csv > /tmp/occ_launch_$DOM.log 2>&1 & LP=$!
setsid python3 /tmp/occ_scan.py --ros-args -p use_sim_time:=true -p coverage:=$COV -p center_deg:=$CD -p rho:=$RHO $EXTRA > /tmp/occ_scan_$DOM.log 2>&1 & OP=$!
sleep 6; python3 -u /tmp/occ_rec.py $OUT $((D+6)) & REC=$!; sleep 2
ros2 bag play $BAG --clock 100 --topics /scan /tf_static /imu/data /wheel_odom /odometry/filtered /cmd_vel --remap /scan:=/scan_in /odometry/filtered:=/truth_odom > /dev/null 2>&1
wait $REC
echo "도메인 $DOM 가림 $COV: $(grep -a '게이트 통과' /tmp/occ_launch_$DOM.log | tail -1 | grep -oE '통과.*') | $(grep -a '가린 빔' /tmp/occ_scan_$DOM.log | tail -1 | grep -oE '가린.*')"
kill -INT -- -$LP -$OP 2>/dev/null; sleep 3; kill -9 -- -$LP -$OP 2>/dev/null
