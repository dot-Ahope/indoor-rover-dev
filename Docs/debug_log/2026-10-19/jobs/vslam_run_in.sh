#!/bin/bash
# (10-19 §23) 컨테이너 안에서 실행: 오프라인 cuVSLAM 한 판 — 런치(끔 · 켬 두 개) → 출력 기록 → 입력 bag 재생(1 배속, --clock) → 정리 → csv 로 내보내기.
#   인자: <imu true|false> [입력 이름=f2y1_split(§25 부터 f2z1_split 등)]. 도메인 42(실시간 스택과 분리), 컨테이너 안 기본 DDS(같은 컨테이너 프로세스끼리).
set +u   # ROS setup.bash 가 미정의 변수를 써서 set -u 면 중단(10-19 첫 실행)
IMU=$1; SPL=${2:-f2y1_split}; W=/workspaces/isaac_ros-dev/vslam; IN=$W/$SPL; OUT=$W/out_${SPL%_split}_imu_$IMU; rm -rf $OUT
export ROS_DOMAIN_ID=42; unset FASTRTPS_DEFAULT_PROFILES_FILE; source /opt/ros/humble/setup.bash
ros2 launch $W/vslam_offline.launch.py imu:=$IMU > $W/launch_$IMU.log 2>&1 &
LP=$!; sleep 15
grep -aiE "error|version|tracker|imu" $W/launch_$IMU.log | head -6 | cut -c1-160
ros2 bag record -o $OUT /vs_off/visual_slam/tracking/odometry /vs_off/visual_slam/status /vs_on/visual_slam/tracking/odometry /vs_on/visual_slam/status > $W/rec_$IMU.log 2>&1 &
RP=$!; sleep 4
T0=$(date +%s); ros2 bag play $IN --clock 100 > $W/play_$IMU.log 2>&1; echo "재생 $(( $(date +%s) - T0 )) s"
sleep 4; kill -INT $RP; sleep 3; kill -INT $LP; sleep 5; pkill -9 -f vs_off_container; pkill -9 -f vs_on_container
echo "경고(프레임 간격 · 추적 잃음) 수: $(grep -ac 'jitter\|Delta between' $W/launch_$IMU.log) · $(grep -aic 'lost\|fail' $W/launch_$IMU.log)"
python3 $W/export_vslam.py $OUT $W/vslam_${SPL%_split}_$IMU
