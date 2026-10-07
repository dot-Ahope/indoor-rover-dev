#!/bin/bash
# 10-07 §4: 주행 bag 재생(가림 합성 없음) — 인자 DOMAIN BAG OUT. 환경 GV(gate_v) GVREF(gate_vref). 라이브 EKF B 는 /truth_odom 으로 기록
set +u; DOM=$1; BAG=$2; OUT=$3
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; source ~/rf2o_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; export ROS_DOMAIN_ID=$DOM
D=$(python3 -c "import yaml;print(int(yaml.safe_load(open('$BAG/metadata.yaml'))['rosbag2_bagfile_information']['duration']['nanoseconds']/1e9)+3)")
setsid ros2 launch rover_bringup ekf.launch.py rf2o:=true use_sim_time:=true gate_v:=${GV:-on} gate_vref:=${GVREF:-wheel} gate_csv:=${OUT%.npz}_gate.csv > /tmp/rp_launch_$DOM.log 2>&1 & LP=$!
sleep 6; python3 -u /tmp/occ_rec.py $OUT $((D+6)) & REC=$!; sleep 2
ros2 bag play $BAG --clock 100 --topics /scan /tf_static /imu/data /wheel_odom /odometry/filtered /cmd_vel --remap /odometry/filtered:=/truth_odom > /dev/null 2>&1
wait $REC
echo "도메인 $DOM $(basename $BAG) GVREF=${GVREF:-wheel}: $(grep -a '게이트 통과' /tmp/rp_launch_$DOM.log | tail -1 | grep -oE '통과.*')"
kill -INT -- -$LP 2>/dev/null; sleep 3; kill -9 -- -$LP 2>/dev/null
