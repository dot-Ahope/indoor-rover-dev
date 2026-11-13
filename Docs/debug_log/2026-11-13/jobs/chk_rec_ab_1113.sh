#!/bin/bash
# chk_rec_ab_1113 — 11-13 §0 정지 기록 시험 A/B. 로버 안 움직임(/cmd_vel 안 냄 · 목표 안 보냄). 스택은 prep 으로 떠 있어야 함.
#   왜: README 시각화용 bag 에 컬러(5 fps) · 깊이 · 추가 토픽을 넣으면, 지금 기록(f2rr1 과 같은 목록 · UDP 기록기)보다
#       /tf 수신율 · CPU · 카메라 주기가 나빠지는지 주행 전에 본다. 컬러 원본은 기록기를 SHM+UDP 프로파일로 띄워 카메라 프로세스와 SHM 으로 받는다.
#   A = 지금 목록(job551 기본 + nvblox 슬라이스 + run_f2c 의 /trajectories · /transformed_global_plan), UDP 전용 기록기 — f2rr1 과 같음
#   B = A + 추가 토픽 + 컬러 · 깊이(+ camera_info), SHM+UDP 기록기
#   인자: $1 = 각 구간 초(기본 60) · $2 = 돌릴 구간(기본 AB, 11-13 §1 에서 A 만 다시 = "A2"). 출력: 표준 출력(PC 가 outputs/ 로), bag 은 /tmp/bag_rab_A · /tmp/bag_rab_B.
SEC=${1:-60}; ONLY=${2:-AB}
SH=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config
BASE="/tf /tf_static /map /scan /plan /plan_smoothed /local_costmap/costmap /global_costmap/costmap /odometry/filtered /wheel_odom /cmd_vel /rover/status /battery /rover/stuck /imu/data /nvblox_node/static_map_slice /trajectories /transformed_global_plan"
ADD="/wheel_odom/conditioned /vslam/odom /visual_slam/tracking/odometry /visual_slam/status /pose /behavior_tree_log /local_costmap/published_footprint /rover/guard"
CAM="/camera/camera/color/image_raw /camera/camera/color/camera_info /camera/camera/depth/image_rect_raw /camera/camera/depth/camera_info"
echo "== 스택: realsense $(pgrep -fc realsense2_camera) · slam $(pgrep -fc slam_toolbox) · controller $(pgrep -fc controller_server) · bt $(pgrep -fc bt_navigator) · nvblox $(pgrep -fc '^/opt/ros/humble/lib/nvblox_ros/nvblox_node')"
echo "== 카메라 컬러 프로파일 파라미터: $(timeout 10 ros2 param get /camera/camera rgb_camera.color_profile 2>&1 | tail -1)"
# QoS 재정의: job551 과 같은 /trajectories · /tf best effort, B 는 카메라 영상 두 줄도 best effort(느린 기록기가 카메라 발행을 붙잡지 않게 — job551 의 깊이와 같은 이유)
qos() { : > $2; for t in $1; do case $t in /trajectories) D=5;; /tf) D=100;; *) D=10;; esac
  printf '%s:\n  reliability: best_effort\n  history: keep_last\n  depth: %s\n  durability: volatile\n' $t $D >> $2; done; }
qos "/trajectories /tf" /tmp/bag_qos_rab_A.yaml
qos "/trajectories /tf /camera/camera/color/image_raw /camera/camera/depth/image_rect_raw" /tmp/bag_qos_rab_B.yaml
# 프로세스별 CPU(utime+stime 틱): 이름 패턴 → 합
ticks() { local s=0; for p in $(pgrep -f "$1"); do read -r a < /proc/$p/stat 2>/dev/null || continue; set -- $a; s=$((s + ${14} + ${15})); done; echo $s; }
PATS="realsense2_camera ros2.bag.record slam_toolbox controller_server nvblox_node ekf_node"
run() {  # $1 이름 $2 프로파일 xml $3 토픽
  local N=$1; rm -rf /tmp/bag_rab_$N
  echo; echo "########## $N $(date +%T) — 프로파일 $(basename $2) · 토픽 $(echo $3 | wc -w) 개 · ${SEC} s ##########"
  FASTRTPS_DEFAULT_PROFILES_FILE=$2 setsid nohup ros2 bag record -o /tmp/bag_rab_$N --qos-profile-overrides-path /tmp/bag_qos_rab_$N.yaml $3 > /tmp/bag_rab_$N.log 2>&1 &
  sleep 8   # 기록기 구독 맺기
  declare -A T0; for p in $PATS; do T0[$p]=$(ticks $p); done; S0=$(head -1 /proc/stat)
  sleep $SEC
  # 틱은 100 Hz(CLK_TCK) → 초당 틱 = 코어 1 개 기준 %
  S1=$(head -1 /proc/stat); for p in $PATS; do echo "  CPU $p $(( ($(ticks $p) - ${T0[$p]}) / SEC )) %(코어 1 = 100)"; done
  # /proc/stat 첫 줄: cpu user nice system idle iowait irq softirq steal guest guest_nice(11 칸) — 두 줄을 이어 붙였으니 둘째 줄은 +11
  echo "$S0 $S1" | awk '{b0=$2+$3+$4+$7+$8+$9; i0=$5+$6; b1=$13+$14+$15+$18+$19+$20; i1=$16+$17; printf "  CPU 전체 %.1f %%(6 코어 평균)\n", 100*(b1-b0)/((b1+i1)-(b0+i0))}'
  pkill -INT -f "ros2 bag record -o /tmp/bag_rab_$N"; for i in $(seq 1 15); do pgrep -f "bag_rab_$N " >/dev/null || break; sleep 1; done
  echo "  크기 $(du -sh /tmp/bag_rab_$N | cut -f1)"
  python3 - /tmp/bag_rab_$N/metadata.yaml <<'PY'
import sys, yaml
m = yaml.safe_load(open(sys.argv[1]))['rosbag2_bagfile_information']; d = m['duration']['nanoseconds'] / 1e9
print(f"  기록 길이 {d:.1f} s")
for t in sorted(m['topics_with_message_count'], key=lambda t: t['topic_metadata']['name']):
    print(f"  {t['topic_metadata']['name']:40s} {t['message_count']:6d} {t['message_count'] / d:7.2f} Hz")
PY
  grep -aiE "warn|error|lost|dropp" /tmp/bag_rab_$N.log | head -5 | sed 's/^/  기록기 로그: /'
}
case $ONLY in
  AB) run A $SH/fastdds_udp_only.xml "$BASE"; sleep 10; run B $SH/fastdds_shm_udp.xml "$BASE $ADD $CAM";;
  A2) cp /tmp/bag_qos_rab_A.yaml /tmp/bag_qos_rab_A2.yaml; run A2 $SH/fastdds_udp_only.xml "$BASE";;   # 11-13 §1: B 뒤 A 다시(순서 영향 확인)
esac
echo; echo "== /dev/shm fastrtps $(ls /dev/shm | grep -c fastrtps) · 끝 $(date +%T)"
