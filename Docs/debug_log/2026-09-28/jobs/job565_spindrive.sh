#!/bin/bash
# 제자리 회전 시험 래퍼(Jetson, 2026-09-28): 게이트 A(프로세스)·B(보드)·C(SLAM) → bag → job562 → 메타(job453).
#   인자: NAME W DIR REPS  (setsid nohup 으로 띄워 ssh 가 끊겨도 계속)
set +u
NAME=$1; W=$2; DIR=$3; REPS=$4
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "########## 회전 시험 게이트 $(date +%T) ##########"
DUP=0; for p in robot_state_publisher realsense2_camera rplidar sensor_conditioner ekf_node slam_toolbox; do c=$(pgrep -fc "$p" 2>/dev/null | head -1); [ "${c:-0}" != 1 ] && { DUP=1; echo "  ★ $p = $c개"; }; done
[ $DUP = 1 ] && { echo "  A 불합격 — 주행하지 않음"; exit 1; }
BR=$(timeout 6 ros2 topic hz /wheel_odom 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1); [ -z "$BR" ] && { echo "  B 불합격(보드 무발행) — 주행하지 않음"; exit 1; }
# C: 09-28 회전 시험은 SLAM 값을 쓰지 않으므로(측정 = 스캔 직접 정합) 간헐 지연 튐에 대비해 최대 3 회 검사, 결과 모두 기록
CO=0; for i in 1 2 3; do SA=$(python3 /tmp/job386_slamalive.py 2>&1 | grep -av "^\["); echo "  C 검사 $i: $(echo "$SA" | tr '
' ' ')"; [ "$(echo "$SA" | tail -1)" = OK ] && { CO=1; break; }; done
[ $CO = 1 ] || { echo "  C 불합격(SLAM 3 회) — 주행하지 않음"; exit 1; }
echo "  A·B·C 통과 ($BR) | 배터리 $(timeout 5 ros2 topic echo /battery --once --field voltage 2>/dev/null | head -1)"
BAG=/tmp/bag_$NAME; rm -rf $BAG
TOPICS="/tf /tf_static /map /scan /odometry/filtered /wheel_odom /wheel_odom/conditioned /imu/data /cmd_vel /rover/status /battery /rover/stuck"
setsid nohup ros2 bag record -o $BAG $TOPICS > /tmp/bag_$NAME.log 2>&1 &
(for i in $(seq 1 200); do top -b -n1 | head -30; sleep 2; done) > /tmp/top_$NAME.log 2>&1 &
TOPPID=$!; sleep 10
echo "########## 회전 $(date +%T) — ω $W, 방향 $DIR, $REPS 회 ##########"
python3 /tmp/job562_spin.py $NAME $W $DIR $REPS 2>&1 | grep -av "^\["
pkill -INT -f "ros2 bag record" 2>/dev/null; kill $TOPPID 2>/dev/null
for i in $(seq 1 10); do [ "$(pgrep -fc 'ros2 bag record')" = 0 ] && break; sleep 1; done
TOPICS="$TOPICS" bash /tmp/job453_runmeta.sh $NAME "spin w=$W dir=$DIR reps=$REPS" $W >/dev/null 2>&1; cp /tmp/meta_$NAME/run_meta.txt /tmp/meta_$NAME/params.txt $BAG/ 2>/dev/null
tar czf /tmp/bag_$NAME.tgz -C /tmp bag_$NAME 2>/dev/null; echo "=== 끝 $(date +%T) bag $(stat -c %s /tmp/bag_$NAME.tgz 2>/dev/null) B ==="
