#!/bin/bash
# 10-29 정지 방향 드리프트 기록(Jetson, 로버 안 움직임 · 명령 없음). 인자: 이름 길이s(기본 1800)
# 기록 = TF · EKF · 휠(원 · 조건) · 카메라 IMU(원 · 조건) · cuVSLAM · 라이다 · 지도 → /tmp/bag_<이름>. 끝나면 sensors · slam 로그 사본.
# setsid nohup 으로 독립 실행 — PC 연결이 끊겨도 길이만큼 기록하고 스스로 멈춘다.
NAME=${1:?이름}; DUR=${2:-1800}; BAG=/tmp/bag_$NAME
if [ "${3:-}" != inner ]; then
  setsid nohup bash /tmp/chk_drift_rec_1029.sh $NAME $DUR inner > /tmp/drift_$NAME.log 2>&1 &
  echo "시작 $(date +%T) · $DUR s · 기록 $BAG · 진행 /tmp/drift_$NAME.log"; exit 0; fi
printf '/tf:\n  reliability: best_effort\n  history: keep_last\n  depth: 100\n  durability: volatile\n' > /tmp/bag_qos_$NAME.yaml
rm -rf $BAG
echo "== $NAME 시작 $(date '+%F %T') · 길이 $DUR s"
grep -a "gyro bias calibrated" /tmp/sensors.log | tail -1 | sed 's/^.*gyro bias/gyro bias/'
ros2 bag record -o $BAG --qos-profile-overrides-path /tmp/bag_qos_$NAME.yaml /tf /tf_static /map /scan /odometry/filtered \
  /wheel_odom /wheel_odom/conditioned /imu/data /camera/camera/imu /vslam/odom /cmd_vel > /tmp/bag_$NAME.log 2>&1 &
BP=$!; sleep $DUR; kill -INT $BP; wait $BP
cp /tmp/sensors.log /tmp/sensors_$NAME.log; cp /tmp/slam.log /tmp/slam_$NAME.log
echo "== 끝 $(date +%T) · bag $(du -sh $BAG | cut -f1) · ZUPT 줄 $(grep -ac ZUPT /tmp/sensors_$NAME.log)"
