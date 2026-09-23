#!/bin/bash
# F0 주행 래퍼(Jetson, 2026-09-23): 일반 게이트(A 프로세스·B 보드·J nvblox·C SLAM·G2 출발 자세) → bag·tegrastats·top·RSS → job550 → 메타(job453).
#   상자 코스 게이트(D·E·F·L·M·N)는 쓰지 않는다. 목표 여유(G1)는 Nav2 가 목표 셀을 거부하면 러너가 중단하는 것으로 대신한다.
#   인자: NAME "GOALS" [SPEED] [PAUSE s]  (setsid nohup 으로 띄워 ssh 가 끊겨도 계속)
set +u
NAME=$1; GOALS=$2; SPEED=${3:-0.07}; PAUSE=${4:-0}
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "########## F0 게이트 $(date +%T) ##########"
DUP=0; for p in microros_agent robot_state_publisher realsense2_camera rplidar sensor_conditioner ekf_node slam_toolbox controller_server planner_server bt_navigator behavior_server lifecycle_manager stuck_monitor; do c=$(pgrep -fc "$p" 2>/dev/null | head -1); [ "${c:-0}" != 1 ] && { DUP=1; echo "  ★ $p = $c개"; }; done
[ $DUP = 1 ] && { echo "  A 불합격 — 주행하지 않음"; exit 1; }
BR=$(timeout 6 ros2 topic hz /wheel_odom 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1); [ -z "$BR" ] && { echo "  B 불합격(보드 무발행) — 주행하지 않음"; exit 1; }
echo "  A·B 통과 ($BR)"
if grep -q nvblox_layer /tmp/nav2_params_active.yaml 2>/dev/null; then
  NP=$(docker exec isaac_ros_dev-aarch64-container bash -c "pgrep -fc '^/opt/ros/humble/lib/nvblox_ros/nvblox_node' || true" 2>/dev/null)
  RD=$(grep -aA7 "NVBlox Rates" /tmp/nvblox_node.log | grep -aE "ros/depth_image_callback" | awk '{print $NF}' | tail -1)
  [ "$NP" = 1 ] && awk -v d="$RD" 'BEGIN{exit !(d+0>=10)}' || { echo "  J 불합격(nvblox $NP 개, 깊이 $RD Hz) — 주행하지 않음"; exit 1; }; echo "  J 통과 (깊이 $RD Hz)"
fi
SA=$(python3 /tmp/job386_slamalive.py 2>&1 | grep -av "^\["); [ "$(echo "$SA" | tail -1)" = OK ] || { echo "  C 불합격(SLAM) — 주행하지 않음"; echo "$SA" | tail -2; exit 1; }; echo "  C 통과"
SC=$(timeout 60 python3 /tmp/job440_startclear.py 2>&1 | grep -av "^\["); echo "$SC" | tail -2 | sed 's/^/  /'
G2=$(echo "$SC" | tail -1); awk -v d="$G2" 'BEGIN{exit !(d+0>=0.10)}' || { echo "  G2 불합격(출발 자세 여유 $G2 m < 0.10) — 주행하지 않음"; exit 1; }; echo "  G2 통과 ($G2 m)"
sleep 30   # DDS 참여자 생성 뒤 30 s (09-21 cc1 규칙)
BAG=/tmp/bag_$NAME; rm -rf $BAG
TOPICS="/tf /tf_static /map /scan /plan /plan_smoothed /local_costmap/costmap /global_costmap/costmap /odometry/filtered /wheel_odom /cmd_vel /rover/status /battery /rover/stuck /imu/data"
[ "${BAG_PROFILE:-}" = nvblox ] && TOPICS="$TOPICS /nvblox_node/static_map_slice"
setsid nohup ros2 bag record -o $BAG $TOPICS > /tmp/bag_$NAME.log 2>&1 &
setsid nohup tegrastats --interval 1000 > /tmp/tegra_$NAME.log 2>&1 &
(for i in $(seq 1 400); do top -b -n1 | head -30; sleep 2; done) > /tmp/top_$NAME.log 2>&1 &
TOPPID=$!; ps -eo pid,rss,pcpu,comm,args --sort=-rss | head -25 > /tmp/rss_$NAME.txt; sleep 2
echo "########## F0 주행 $(date +%T) — 목표 $GOALS ##########"
python3 /tmp/job550_f0run.py $NAME "$GOALS" $SPEED $PAUSE 2>&1 | grep -av "^\["
pkill -INT -f "ros2 bag record" 2>/dev/null; pkill -f "tegrastats --interval 1000" 2>/dev/null; kill $TOPPID 2>/dev/null
for i in $(seq 1 10); do [ "$(pgrep -fc 'ros2 bag record')" = 0 ] && break; sleep 1; done
TOPICS="$TOPICS" bash /tmp/job453_runmeta.sh $NAME "$GOALS" $SPEED >/dev/null 2>&1; cp /tmp/meta_$NAME/run_meta.txt /tmp/meta_$NAME/params.txt $BAG/ 2>/dev/null
tar czf /tmp/bag_$NAME.tgz -C /tmp bag_$NAME 2>/dev/null; echo "=== 끝 $(date +%T) bag $(stat -c %s /tmp/bag_$NAME.tgz 2>/dev/null) B ==="
