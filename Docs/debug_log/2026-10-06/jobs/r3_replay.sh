#!/bin/bash
# 10-06 R3: 정식 ekf.launch.py(rf2o:=true shadow:=true use_sim_time:=true)를 도메인 42 에서 bag 재생으로 검증. 인자: BAG OUT
set +u; BAG=$1; OUT=$2
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; source ~/rf2o_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; export ROS_DOMAIN_ID=42
D=$(python3 -c "import yaml;print(int(yaml.safe_load(open('$BAG/metadata.yaml'))['rosbag2_bagfile_information']['duration']['nanoseconds']/1e9)+3)")
setsid ros2 launch rover_bringup ekf.launch.py rf2o:=true shadow:=true use_sim_time:=true gate_csv:=${OUT%.npz}_gate.csv > /tmp/r3_launch.log 2>&1 &
sleep 6
python3 -u /tmp/r3_rec.py $OUT $((D+6)) & REC=$!; sleep 2
ros2 bag play $BAG --clock 100 --topics /scan /tf_static /imu/data /wheel_odom > /dev/null 2>&1
wait $REC
P=$(pgrep -f "rf2o_gate.py" | head -1); echo "  게이트 CPU 누적: $(ps -o times= -p $P 2>/dev/null) s"
grep -a "게이트 통과" /tmp/r3_launch.log | tail -1
pkill -f "ekf.launch.py"; sleep 2; pkill -f rf2o_laser_odometry_node; pkill -f rf2o_gate.py; pkill -f ekf_node; pkill -f sensor_conditioner
grep -aiE "error|exception|failed" /tmp/r3_launch.log | grep -v "Message Filter" | head -5
