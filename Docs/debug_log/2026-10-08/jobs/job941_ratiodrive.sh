#!/bin/bash
# 트랙 비율 통제 시험 래퍼(Jetson, 10-08 §5): 게이트 A(프로세스)·B(보드)·C(SLAM) → 30 s(DDS 규칙) → bag → job940 → 메타(job453).
#   인자: NAME PLAN [REPS] [ANG]  (setsid nohup 으로 띄워 ssh 가 끊겨도 계속). 09-28 job565 기반.
set +u
NAME=$1; PLAN=$2; REPS=${3:-4}; ANG=${4:-90}
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "########## 비율 시험 게이트 $(date +%T) ##########"
DUP=0; for p in microros_agent robot_state_publisher realsense2_camera rplidar sensor_conditioner ekf_node slam_toolbox stuck_monitor; do c=$(pgrep -fc "$p" 2>/dev/null | head -1); e=1; [ $p = ekf_node ] && e=$((1 + $(pgrep -fc "__node:=ekf_shadow_a" 2>/dev/null | head -1))); [ "${c:-0}" != $e ] && { DUP=1; echo "  ★ $p = $c개"; }; done
[ $DUP = 1 ] && { echo "  A 불합격 — 주행하지 않음"; exit 1; }
for i in 1 2 3; do SH=$(timeout 15 ros2 param get /stuck_monitor shadow_mode 2>&1 | tail -1); echo "$SH" | grep -q Boolean && break; done;   # 10-08 §5.6: 첫 조회가 빈 값으로 오는 일이 있어 3 회
echo "  stuck_monitor shadow: $SH (관찰 모드여야 반피벗 병진을 정체로 오판해 지령을 끊지 않음)"
echo "$SH" | grep -q True || { echo "  S 불합격(stuck_monitor 작동 모드) — 주행하지 않음"; exit 1; }
BR=$(timeout 6 ros2 topic hz /wheel_odom 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1); [ -z "$BR" ] && { echo "  B 불합격(보드 무발행) — 주행하지 않음"; exit 1; }
SA=$(python3 /tmp/job386_slamalive.py 2>&1 | grep -av "^\["); [ "$(echo "$SA" | tail -1)" = OK ] || { echo "  C 불합격(SLAM) — 주행하지 않음"; echo "$SA" | tail -2; exit 1; }
echo "  A·B·C·S 통과 ($BR) | 배터리 $(timeout 5 ros2 topic echo /battery --once --field voltage 2>/dev/null | head -1) V"
sleep 30   # DDS 참여자 생성 뒤 30 s (09-21 규칙)
BAG=/tmp/bag_$NAME; rm -rf $BAG
TOPICS="/tf /tf_static /map /scan /odometry/filtered /wheel_odom /cmd_vel /rover/status /battery /rover/stuck /imu/data"
setsid nohup ros2 bag record -o $BAG $TOPICS > /tmp/bag_$NAME.log 2>&1 &
(for i in $(seq 1 600); do top -b -n1 | head -30; sleep 2; done) > /tmp/top_$NAME.log 2>&1 &
TOPPID=$!; sleep 8
echo "########## 비율 시험 $(date +%T) — $PLAN, 블록당 $REPS 회 × $ANG° ##########"
python3 -u /tmp/job940_ratio.py $NAME "$PLAN" $REPS $ANG 2>&1 | grep -av "^\["
sleep 2; pkill -INT -f "ros2 bag record" 2>/dev/null; kill $TOPPID 2>/dev/null
for i in $(seq 1 10); do [ "$(pgrep -fc 'ros2 bag record')" = 0 ] && break; sleep 1; done
TOPICS="$TOPICS" bash /tmp/job453_runmeta.sh $NAME "ratio plan=$PLAN reps=$REPS ang=$ANG" 0 >/dev/null 2>&1; cp /tmp/meta_$NAME/run_meta.txt /tmp/meta_$NAME/params.txt $BAG/ 2>/dev/null
tar czf /tmp/bag_$NAME.tgz -C /tmp bag_$NAME 2>/dev/null; echo "=== 끝 $(date +%T) bag $(stat -c %s /tmp/bag_$NAME.tgz 2>/dev/null) B ==="
