#!/bin/bash
# 10-02 §13 R1: 도메인 42·sim time — rf2o(publish_tf false) + bag 재생(--clock) + 기록기. 인자: BAG OUT
set +u; BAG=$1; OUT=$2
source /opt/ros/humble/setup.bash; source ~/rf2o_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; export ROS_DOMAIN_ID=42
D=$(python3 -c "import yaml;print(int(yaml.safe_load(open('$BAG/metadata.yaml'))['rosbag2_bagfile_information']['duration']['nanoseconds']/1e9)+3)")
cat > /tmp/rf2o_params.yaml <<'Y'
rf2o_laser_odometry:
  ros__parameters:
    use_sim_time: true
    publish_tf: false
    laser_scan_topic: /scan
    odom_topic: /odom_rf2o
    base_frame_id: base_link
    odom_frame_id: odom
    init_pose_from_topic: ""
    freq: 10.0
Y
setsid ros2 run rf2o_laser_odometry rf2o_laser_odometry_node --ros-args -r __node:=rf2o_laser_odometry --params-file /tmp/rf2o_params.yaml > /tmp/rf2o_replay.log 2>&1 &
sleep 3
python3 -u /tmp/job835_rf2o_rec.py $OUT $((D+6)) &
REC=$!; sleep 2
ros2 bag play $BAG --clock 100 --topics /scan /tf /tf_static > /dev/null 2>&1
wait $REC
P=$(pgrep -f rf2o_laser_odometry_node); echo "  rf2o CPU(누적 s): $(ps -o times= -p $P 2>/dev/null)"; pkill -f rf2o_laser_odometry_node
grep -aiE "error|warn" /tmp/rf2o_replay.log | head -5
