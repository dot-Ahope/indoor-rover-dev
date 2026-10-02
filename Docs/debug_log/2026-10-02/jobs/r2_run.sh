#!/bin/bash
# 10-02 §14 R2: 도메인 42·sim time — rf2o + 게이트 + EKF A/B + 기록기, bag 재생(/scan /tf /tf_static /wheel_odom /imu/data). 인자: BAG OUT
set +u; BAG=$1; OUT=$2
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; source ~/rf2o_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; export ROS_DOMAIN_ID=42
Y=$(ros2 pkg prefix rover_bringup)/share/rover_bringup/config/ekf.yaml
NOIMU=$(grep -c "/imu/data" $BAG/metadata.yaml); NOIMU=$([ "$NOIMU" = 0 ] && echo 1 || echo 0)
python3 - "$Y" "$NOIMU" <<'PY'
import sys, yaml
NOIMU = sys.argv[2] == '1'
src = yaml.safe_load(open(sys.argv[1]))['ekf_filter_node']['ros__parameters']
for k, extra in (('A', {}), ('B', {'odom1': '/r2/rf2o_gated', 'odom1_config': [False]*6 + [True, True, False] + [False]*6,
                                  'odom1_queue_size': 10, 'odom1_nodelay': True, 'odom1_differential': False, 'odom1_relative': False})):
    p = dict(src); p.update({'use_sim_time': True, 'publish_tf': False, 'odom0': '/r2/wheel_' + k}); p.update(extra)
    if NOIMU:   # 10-02 §14.1: /imu/data 없는 bag(rot2·rot3) → 라이브 EKF 회전 속도를 자이로 대신(odom2 vyaw 만, 분산 0.02^2)
        p.update({'odom2': '/r2/live_w', 'odom2_config': [False]*11 + [True] + [False]*3, 'odom2_queue_size': 10, 'odom2_nodelay': True, 'odom2_differential': False, 'odom2_relative': False})
    yaml.safe_dump({'ekf' + k: {'ros__parameters': p}}, open('/tmp/r2_ekf%s.yaml' % k, 'w'))
open('/tmp/r2_rf2o.yaml', 'w').write('rf2o_laser_odometry:\n  ros__parameters:\n    use_sim_time: true\n    publish_tf: false\n    laser_scan_topic: /scan\n    odom_topic: /odom_rf2o\n    base_frame_id: base_link\n    odom_frame_id: odom\n    init_pose_from_topic: ""\n    freq: 10.0\n')
PY
D=$(python3 -c "import yaml;print(int(yaml.safe_load(open('$BAG/metadata.yaml'))['rosbag2_bagfile_information']['duration']['nanoseconds']/1e9)+3)")
setsid ros2 run rf2o_laser_odometry rf2o_laser_odometry_node --ros-args -r __node:=rf2o_laser_odometry --params-file /tmp/r2_rf2o.yaml > /tmp/r2_rf2o.log 2>&1 &
setsid python3 /tmp/r2_gate.py --ros-args -p use_sim_time:=true -p csv:=${OUT%.npz}_gate.csv > /tmp/r2_gate.log 2>&1 &
for k in A B; do setsid ros2 run robot_localization ekf_node --ros-args -r __node:=ekf$k --params-file /tmp/r2_ekf$k.yaml -r odometry/filtered:=/r2/ekf$k > /tmp/r2_ekf$k.log 2>&1 & done
sleep 4
python3 -u /tmp/r2_rec.py $OUT $((D+6)) & REC=$!; sleep 2
ros2 bag play $BAG --clock 100 --topics /scan /tf /tf_static /wheel_odom /imu/data /odometry/filtered > /dev/null 2>&1
wait $REC
grep -a "게이트" /tmp/r2_gate.log | tail -1; echo "  imu 없음=$NOIMU"; head -c 400 /tmp/r2_ekfA.log
pkill -f rf2o_laser_odometry_node; pkill -f r2_gate.py; pkill -f "__node:=ekfA"; pkill -f "__node:=ekfB"; sleep 1
grep -aiE "error|exception" /tmp/r2_ekfA.log /tmp/r2_ekfB.log /tmp/r2_gate.log | head -5
