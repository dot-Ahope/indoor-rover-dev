#!/bin/bash
# 10-06 R3: 정식 ekf.launch.py(rf2o:=true shadow:=true use_sim_time:=true)를 도메인 42 에서 bag 재생으로 검증. 인자: BAG OUT
set +u; BAG=$1; OUT=$2; SRC=${3:-ekf}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; source ~/rf2o_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; export ROS_DOMAIN_ID=42
D=$(python3 -c "import yaml;print(int(yaml.safe_load(open('$BAG/metadata.yaml'))['rosbag2_bagfile_information']['duration']['nanoseconds']/1e9)+3)")
setsid ros2 launch rover_bringup ekf.launch.py rf2o:=true shadow:=true use_sim_time:=true gate_csv:=${OUT%.npz}_gate.csv gate_src:=$SRC > /tmp/r3_launch.log 2>&1 &
LPID=$!   # 10-06 §5: 정리는 이 launch 의 프로세스 그룹만 — 이름으로 pkill 하면 라이브(도메인 0) 스택까지 죽였다(내 실수)
sleep 6
python3 -u /tmp/r3_rec.py $OUT $((D+6)) & REC=$!; sleep 2
ros2 bag play $BAG --clock 100 --topics /scan /tf_static /imu/data /wheel_odom > /dev/null 2>&1
wait $REC
P=$(pgrep -g $LPID -f "rf2o_gate.py" | head -1); echo "  게이트($SRC) CPU 누적: $(ps -o times= -p $P 2>/dev/null) s / 재생 ${D} s"
grep -a "게이트 통과" /tmp/r3_launch.log | tail -1
kill -INT -- -$LPID 2>/dev/null; sleep 3; kill -9 -- -$LPID 2>/dev/null
grep -aiE "error|exception|failed" /tmp/r3_launch.log | grep -v "Message Filter" | head -5
