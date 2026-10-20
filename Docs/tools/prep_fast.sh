#!/bin/bash
# prep_fast — 순회용 빠른 기동(정리 → 센서 → SLAM 위치 추정 → Nav2 → 준비 확인). 로버 안 움직임. 옛 이름 job972_prep_fast.sh(10-12 §13)
#   ① ros2 조회 약 25 회 → 확인 노드 1 개(job971_prepchk.py)  ② 고정 대기(28·15·30 s 등) → '준비될 때까지' 폴링.
#   기동 순서·정리 방식·인자는 그대로(base 유지 → sensors → slam(위치 추정) → nav2). 빠진 것: 통과 폭 감사(job248)·지도 복원 확인(job697) — 순회에는 안 씀.
#   환경: MAP(기본 office_v3) EXTRA_SENSORS EXTRA_NAV STUCK_SHADOW(기본 true) FWD(설치본 PreferForward 값, 기본 15.0) WAIT(재마킹 대기, 기본 15)
#   단계마다 시각을 찍는다(다음 단축 근거).
set +u
T0=$(date +%s); st() { echo "  ⏱ +$(( $(date +%s) - T0 )) s $1"; }
MAP=${MAP:-office_v3}; D=/home/jetson/maps/office; WAIT=${WAIT:-15}
[ -e $D/$MAP.posegraph ] || { echo "지도 없음: $MAP"; exit 1; }
Y=/home/jetson/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml
sed -i "s/\(PreferForwardCritic: {enabled: true, cost_power: 1, cost_weight: \)[0-9.]*/\1${FWD:-15.0}/" $Y
set +u      # ⚠ set -u 금지 — ROS setup.bash 가 미정의 변수를 참조해 즉시 죽는다
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
[ -f ~/rf2o_ws/install/setup.bash ] && source ~/rf2o_ws/install/setup.bash   # 10-06 R3: ekf.launch rf2o:=true 용
PATS="cuvslam_up.sh vslam_twist nav_guard rf2o_laser_odometry rf2o_gate.py ekf_shadow_a localization.launch amcl map_server joy_linux_node teleop_node nvblox_up.sh depth_relay.py navigation.launch slam.launch sensors.launch navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense2_camera foxglove_bridge"

cnt() { local n=0 c; for p in $PATS; do c=$(pgrep -fc "$p" 2>/dev/null | head -1); n=$((n+${c:-0})); done; echo $n; }

echo "########## 1. 정리 ##########"
# 09-30 §14: 매핑 bag 은 SIGINT 로 먼저 닫는다(메타데이터 기록) — PATS 의 SIGTERM 보다 앞에
pkill -INT -f "ros2 bag record" 2>/dev/null && sleep 3
echo "  정리 전 프로세스: $(cnt)"
for p in $PATS; do pkill -TERM -f "$p" 2>/dev/null; done
for i in $(seq 1 15); do [ "$(cnt)" = "0" ] && break; sleep 1; done
if [ "$(cnt)" != "0" ]; then
  for p in $PATS; do pkill -9 -f "$p" 2>/dev/null; done; sleep 3
fi
# 10-20 §6: 래퍼가 -9 로 죽으면 컨테이너 안 cuVSLAM 이 고아로 남는다 → 직접 정리
CV=$(docker exec isaac_ros_dev-aarch64-container bash -c "pgrep -f 'cuvslam_[a]ctive.launch.py|__node:=cuvslam_[c]ontainer' || true" 2>/dev/null)
[ -n "$CV" ] && { docker exec isaac_ros_dev-aarch64-container bash -c "pkill -INT -f 'cuvslam_[a]ctive.launch.py|__node:=cuvslam_[c]ontainer'; sleep 3; pkill -9 -f 'cuvslam_[a]ctive.launch.py|__node:=cuvslam_[c]ontainer'" 2>/dev/null; echo "  컨테이너 cuVSLAM 고아 정리: $(echo $CV | wc -w) 개"; }
echo "  정리 후: $(cnt) | /dev/shm fastrtps 잔재: $(ls /dev/shm 2>/dev/null | grep -c fastrtps)"
# 10-14 §24: 비우기 전에 직전 기록을 보관 — 재기동이 앞 주행의 Nav2 기록(계획기·코스트맵 경고)을 지워 이상 경로 원인을 못 봤다.
#   /tmp/logkeep/<보관시각>_{nav2,slam,sensors}.log, 최근 8 벌만 남김(nav2.log 가 주행당 수 MB 라 /tmp 를 채우지 않게). /tmp 라 재부팅하면 사라진다.
K=/tmp/logkeep; mkdir -p $K; TS=$(date +%m%d_%H%M%S)
for f in nav2 slam sensors; do [ -s /tmp/$f.log ] && cp /tmp/$f.log $K/${TS}_$f.log; done
ls -1t $K/*_nav2.log 2>/dev/null | tail -n +9 | sed 's/_nav2\.log$//' | while read p; do rm -f ${p}_*.log; done
echo "  직전 기록 보관: $K/${TS}_*.log ($(ls $K/${TS}_*.log 2>/dev/null | wc -l) 개) · 보관 벌 수 $(ls $K/*_nav2.log 2>/dev/null | wc -l)"
: > /tmp/sensors.log; : > /tmp/slam.log; : > /tmp/nav2.log
st "정리 끝"
echo "########## 2. base ##########"
AG=$(docker ps --format '{{.Names}}' 2>/dev/null | grep -c microros_agent); SE=$(docker logs microros_agent 2>&1 | grep -ac 'session established')
echo "  에이전트 컨테이너 $AG 개 · 세션 수립 기록 $SE 건 · robot_state_publisher $(pgrep -fc robot_state_publisher | head -1) 개"
[ "$AG" = 1 ] || { echo "  ★ 에이전트 없음 — 빠른 prep 은 base 를 띄우지 않는다. job240(전체 절차)으로 기동할 것"; exit 1; }
echo "########## 3. sensors (자이로 캘리브, 로버 정지) ##########"
setsid nohup ros2 launch rover_bringup sensors.launch.py viz:=map ${EXTRA_SENSORS:-} > /tmp/sensors.log 2>&1 &
for i in $(seq 1 80); do grep -aq "gyro bias calibrated" /tmp/sensors.log && break; sleep 0.5; done
grep -a "gyro bias" /tmp/sensors.log | tail -1 | sed 's/^.*gyro bias/  gyro bias/' | cut -c1-110; st "자이로 캘리브 끝"
echo "########## 4. slam(위치 추정) + 5. nav2 ##########"
setsid nohup ros2 launch rover_bringup slam.launch.py map_file:=$D/$MAP slam_mode:=localization > /tmp/slam.log 2>&1 &
for i in $(seq 1 60); do grep -aqE "Registering sensor|Load From File|위치 추정" /tmp/slam.log && break; sleep 0.5; done; st "slam 기동 로그 확인"
setsid nohup ros2 launch rover_navigation navigation.launch.py stuck_shadow:=${STUCK_SHADOW:-true} nav_map:=$D/$MAP.yaml ${EXTRA_NAV:-} > /tmp/nav2.log 2>&1 &
st "nav2 기동"
echo "########## 6. 준비 확인(노드 1 개) ##########"
python3 -u /tmp/chk_prep.py $WAIT 150 2>&1 | grep -av "^\[INFO\]\|^\[WARN\]" | tee /tmp/prepchk.txt
st "확인 끝"
echo "########## 7. 로그·프로세스(DDS 조회 없음) ##########"
echo "  설치본 PreferForward $(grep -a 'PreferForwardCritic: {' $Y | grep -o 'cost_weight: [0-9.]*') · BT $(grep -o 'RateController hz="[0-9.]*"' /tmp/nav_to_pose_active.xml 2>/dev/null) · $(head -1 /tmp/nav2_params_active.yaml | cut -c1-90)"
echo "  navmap_ensure: $(grep -a 'navmap_ensure\]' /tmp/nav2.log | tail -1 | sed 's/^.*\[navmap_ensure\] //' | cut -c1-40) · no map 경고 $(grep -ac 'no map received' /tmp/nav2.log) · SHM 오류 $(cat /tmp/nav2.log /tmp/sensors.log /tmp/slam.log | grep -ac 'RTPS_TRANSPORT_SHM\|init_port')"
echo "  EKF 위반 $(grep -ac 'Failed to meet update rate' /tmp/sensors.log)회 · slam 폐기 $(grep -ac 'Message Filter dropping' /tmp/slam.log)회 · load $(cut -d' ' -f1-3 /proc/loadavg)"
printf "  프로세스:"; for p in rplidar_node realsense2_camera_node sensor_conditioner_node ekf_node rf2o_laser_odometry_node rf2o_gate.py localization_slam controller_server planner_server bt_navigator nav_map_server stuck_monitor.py nav_guard.py foxglove_bridge job551_f0drive; do printf " %s=%s" "${p%%_node}" "$(pgrep -fc "$p")"; done; echo
echo "  nvblox(컨테이너): $(docker exec isaac_ros_dev-aarch64-container bash -c "pgrep -fc '^/opt/ros/humble/lib/nvblox_ros/nvblox_node' || true" 2>/dev/null) 개 · cuVSLAM(컨테이너): $(docker exec isaac_ros_dev-aarch64-container bash -c "pgrep -fc '__node:=cuvslam_[c]ontainer' || true" 2>/dev/null) 개 · vslam_twist $(pgrep -fc vslam_twist.py) · ekf_vslam $(pgrep -fc '__node:=ekf_[v]slam')"
st "prep 끝 — $(tail -1 /tmp/prepchk.txt)"
