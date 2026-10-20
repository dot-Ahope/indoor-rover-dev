#!/bin/bash
# (10-20 §5) EKF 오프라인 재실행 — WSL(ROS Humble) 에서 입력 bag 재생 + EKF 변형 4 개 동시, 출력 bag 기록. Jetson · 로버 안 씀.
#   인자: 입력bag 출력bag params.yaml. 다른 컴퓨터와 섞이지 않게 localhost 전용 · 별도 도메인.
set +u
IN=$1; OUT=$2; PAR=$3
source /opt/ros/humble/setup.bash
export ROS_LOCALHOST_ONLY=1 ROS_DOMAIN_ID=87
rm -rf "$OUT"
printf '/tf_static:\n  reliability: reliable\n  history: keep_all\n  durability: transient_local\n' > /tmp/ekfre_qos.yaml
P=()
for v in ${VARS:-v0 v1 v2 v3}; do
  ros2 run robot_localization ekf_node --ros-args -r __node:=ekf_$v --params-file "$PAR" -r odometry/filtered:=/ekf/$v > /tmp/ekfre_$v.log 2>&1 &
  P+=($!)
done
ros2 bag record -o "$OUT" $(for v in ${VARS:-v0 v1 v2 v3}; do echo -n "/ekf/$v "; done) > /tmp/ekfre_rec.log 2>&1 &
R=$!
sleep 4
ros2 bag play "$IN" --clock 100 --qos-profile-overrides-path /tmp/ekfre_qos.yaml > /tmp/ekfre_play.log 2>&1
sleep 2
kill -INT $R; sleep 2; kill -INT "${P[@]}" 2>/dev/null; sleep 1; pkill -INT -f "__node:=ekf_v" 2>/dev/null; sleep 1; pkill -9 -f "__node:=ekf_v" 2>/dev/null   # ros2 run 래퍼만 죽고 ekf_node 가 남아 다음 재생에 섞였음(§5.3)
tail -3 /tmp/ekfre_play.log; grep -ih "warn\|error" /tmp/ekfre_v*.log | sort | uniq -c | head -8
ros2 bag info "$OUT" | grep -E "Duration|/ekf/"
