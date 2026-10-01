#!/bin/bash
# ── 깨끗한 기동 절차 (2026-09-11 제정) ───────────────────────────────────────
# 왜: 매 주행 전 상태를 보장하지 못해 오늘 여러 번 혼선이 났다.
#   · 재부팅 후 base(micro-ROS 에이전트)를 빠뜨려 보드 토픽이 전멸했는데
#     "Nav2 활성화가 느리다" 로 오인했다 (09-10, 09-11 두 번).
#   · 코스트맵 클리어 직후 6초 만에 측정해 **갱신 전 옛 데이터**를 읽고
#     "상자를 옮겼는데 통과 폭이 그대로" 라는 잘못된 판단을 했다 (job234).
#   · 주행을 반복하며 코스트맵이 오염돼(통과 폭 0.30 → 0.15 m) 원인 분석이 흐려졌다.
# 그래서 **기동 → 검증 → 클리어 → 충분한 재마킹 대기 → 통과 폭 측정**을 한 절차로 묶는다.
# 순서는 base → sensors → slam → nav2 (뒤 단계가 앞 단계 TF/토픽에 의존한다).
#
# 사용: bash job240_clean.sh [클리어후대기초=15]
set +u      # ⚠ set -u 금지 — ROS setup.bash 가 미정의 변수를 참조해 즉시 죽는다
WAIT=${1:-15}
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

# ★ 2026-09-11 (2차): base 계층(에이전트·robot_state_publisher)은 **정리하지 않는다.**
#   에이전트를 죽였다 띄우면 보드는 옛 세션을 믿고 계속 송신하고 새 에이전트는 그것을 버린다
#   (XRCE-DDS 세션은 클라이언트가 CREATE_SESSION 을 보내야 맺어진다). 보드 리셋 없이는 복구 불가.
#   → 에이전트가 살아 있으면 그대로 두고 센서·SLAM·Nav2 만 재기동한다. 고아 프로세스도 생기지 않는다.
#   에이전트가 없을 때만(재부팅 직후) 띄우고, 그 경우 보드 리셋을 요청한다.
PATS="localization.launch amcl map_server joy_linux_node teleop_node nvblox_up.sh depth_relay.py navigation.launch slam.launch sensors.launch navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense2_camera foxglove_bridge"

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
echo "  정리 후: $(cnt) | /dev/shm fastrtps 잔재: $(ls /dev/shm 2>/dev/null | grep -c fastrtps)"
: > /tmp/sensors.log; : > /tmp/slam.log; : > /tmp/nav2.log

# 2026-09-11: launch 를 죽여도 자식(robot_state_publisher)이 고아로 남아 그래프에 노드 이름이
#   중복됐다(PID 3054/5769). 정리 목록에 이름으로 넣고, 기동 후 반드시 1개인지 센다.
echo "  base 계층 유지: 에이전트 $(docker ps --format '{{.Names}}' 2>/dev/null | grep -c microros_agent)개, robot_state_publisher $(pgrep -fc robot_state_publisher | head -1)개 (각 1 이어야)"
echo "########## 2. base (micro-ROS 에이전트) ##########"
echo "  /dev/rover -> $(readlink -f /dev/rover 2>&1)"
if [ "$(docker ps --format '{{.Names}}' 2>/dev/null | grep -c microros_agent)" = "1" ] && \
   { [ -n "$(timeout 6 ros2 topic hz /wheel_odom 2>&1 | grep -aoE 'average rate: [0-9.]+')" ] || [ "$(docker logs microros_agent 2>&1 | grep -ac 'session established')" -ge 1 ]; }; then
  # 09-16: 세션이 이미 맺어진 에이전트는 hz 검사가 실패해도 재기동하지 않는다(재기동 = 보드 리셋 재요구). 원인은 뒤 게이트가 보고.
  echo "  에이전트 살아 있고 보드 송수신 정상 → base 재기동 생략 (세션 유지)"
else
  echo "  에이전트 없음/보드 무발행 → base 기동 (기동 후 보드 리셋이 필요할 수 있다)"
  if systemctl --user is-enabled rover-base >/dev/null 2>&1; then
    # 09-29: 부팅 자동 기동 서비스가 있으면 그것을 재시작(수동 launch 와 겹치면 Restart 가 되살려 컨테이너 이름이 충돌한다)
    : > /tmp/base.log; systemctl --user restart rover-base; echo "  rover-base 서비스 재시작"
  else
    pkill -TERM -f "base.launch" 2>/dev/null; docker rm -f microros_agent >/dev/null 2>&1; sleep 2
    : > /tmp/base.log
    setsid nohup ros2 launch rover_bringup base.launch.py > /tmp/base.log 2>&1 &
  fi
  sleep 12
fi
echo "  컨테이너: $(docker ps --format '{{.Names}} {{.Status}}' 2>/dev/null | grep -a micro || echo '없음!')"
# ⚠ 보드 연결 검증은 **게이트**로 건다. 빈 값으로 조용히 지나가면 뒤 단계가 전부 헛돈다.
#   2026-09-11 실제 사고: 사용자가 보드 리셋 → 그 뒤 에이전트를 재시작 → 세션 0건.
#   XRCE-DDS 세션은 **클라이언트(보드)가 CREATE_SESSION 을 보내야** 맺어지는데, 보드는
#   리셋 직후 이미 맺었다고 믿고 데이터만 계속 보낸다(시리얼에 3초 69kB 가 흐르고 있었다).
#   새로 뜬 에이전트는 그 세션을 몰라 전부 무시한다. → **에이전트를 띄운 뒤 보드를 리셋**해야 한다.
BOARD_OK=1
for t in /wheel_odom /rover/status; do
  R=$(timeout 8 ros2 topic hz $t 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1)
  if [ -z "$R" ]; then
    BOARD_OK=0; echo "  $t  무발행"
  else
    echo "  $t  $R"
  fi
done
if [ "$BOARD_OK" = "0" ]; then
  echo "  세션 수립: $(grep -ac 'session established' /tmp/base.log)건"
  echo "  시리얼 수신 확인 중..."
  timeout 3 cat /dev/rover > /tmp/ser.bin 2>/dev/null
  SB=$(stat -c %s /tmp/ser.bin 2>/dev/null || echo 0)
  echo "  시리얼 3초 수신: $SB 바이트"
  echo ""
  if [ "$SB" -gt 1000 ]; then
    echo "  ★ 보드는 송신 중인데 세션이 없다 = 에이전트보다 보드 리셋이 먼저였다."
    echo "    → **보드 리셋 버튼을 한 번 더 눌러 주십시오.** (에이전트는 이미 떠 있다)"
  else
    echo "  ★ 시리얼에 데이터가 없다 = 보드가 멈췄거나 배선/전원 문제."
    echo "    → 보드 전원·USB 연결을 확인하고 리셋한다."
  fi
  echo "  보드 없이는 /cmd_vel 이 전달되지 않아 주행이 불가하므로 여기서 중단한다."
  exit 1
fi

echo "########## 3. sensors (자이로 캘리브 ~10s, 로버 정지 필수) ##########"
echo "  sensors 인자: ${SENSORS_ARGS:-(없음)}"   # 09-29: B2·B3 라이브 시험용(예: SENSORS_ARGS="icr:=true rot_cov:=true")
setsid nohup ros2 launch rover_bringup sensors.launch.py $SENSORS_ARGS > /tmp/sensors.log 2>&1 &
sleep 28
grep -a "gyro bias" /tmp/sensors.log | tail -1 | sed 's/^/  /'
printf "  %-16s " "/odometry/filtered"
timeout 7 ros2 topic hz /odometry/filtered 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo "무발행"

echo "########## 4. slam ##########"
echo "  slam 인자: ${SLAM_ARGS:-(없음 = 새 지도)}"   # 09-30 F1 이어 그리기: SLAM_ARGS="map_file:=/home/jetson/maps/office/<이름>"
# 10-01 F1-4: LOCALIZER=slam(기본, SLAM_ARGS 에 slam_mode:=localization 가능) | amcl(AMCL_MAP=<yaml>, slam 대신 map_server+amcl)
if [ "${LOCALIZER:-slam}" = "amcl" ]; then
  echo "  위치 추정: AMCL, 지도 ${AMCL_MAP:?AMCL_MAP 필요}"
  setsid nohup ros2 launch rover_navigation localization.launch.py map:=$AMCL_MAP > /tmp/slam.log 2>&1 &
else
setsid nohup ros2 launch rover_bringup slam.launch.py $SLAM_ARGS > /tmp/slam.log 2>&1 &
fi
sleep 15
echo -n "  map->odom: "; timeout 8 ros2 run tf2_ros tf2_echo map odom 2>&1 | grep -a Translation | head -1 || echo "없음"

echo "########## 5. nav2 ##########"
# 09-16: MPPI 튜닝 주행 동안 stuck_monitor 는 관찰만(mp4 에서 떨림 명령을 STUCK 으로 오판해 18 s 에 취소). 진행 감시는 progress checker 25 s + 러너 90 s.
# 09-29 §13.2: 자이로 우선 수정 뒤 오판 0(20 bag 재생)·받침대 검출 0.8~0.9 s → 기본 작동(false). 관찰만 하려면 STUCK_SHADOW=true.
# 09-30 §11: 매핑 전용 모드(MAPPING=1) — 패드 매핑 때 Nav2·nvblox 를 띄우지 않는다. 목표 없이 대기하는 Nav2 노드들이
#   ≈ 130 %, nvblox 35 % 를 써 부하 평균 10.9 → EKF 주기 미달(24 s 에 25 회)·SLAM 스캔 버림 → Foxglove 에서 로버가 멈췄다 점프.
#   안전: stuck_monitor 는 단독으로 띄우고(작동 모드), 펌웨어 워치독·스톨 보호는 그대로.
if [ "${MAPPING:-0}" = "1" ]; then
  echo "  매핑 전용 모드: Nav2·nvblox 생략, stuck_monitor 단독 기동"
  # 09-30 §14: 매핑(사람 조종)에서는 관찰만 — 패드 회전 중 3 회 발동해 조종에 0 지령이 끼어들었다(§13). 사람이 보고 있으므로.
  setsid nohup ros2 run rover_bringup stuck_monitor.py --ros-args -p shadow_mode:=${STUCK_SHADOW:-true} > /tmp/nav2.log 2>&1 &
  # 09-30 §14: 점프를 사후 분석할 수 있게 경량 bag(§13 은 기록이 없어 순간을 못 봄). 지도(/map)는 빼고 재생으로 SLAM 을 다시 돌릴 입력만.
  MB=/tmp/bags/map_$(date +%m%d_%H%M); mkdir -p /tmp/bags
  setsid nohup ros2 bag record -o $MB /scan /tf /tf_static /odometry/filtered /wheel_odom /imu/data /cmd_vel /joy > /tmp/mapbag.log 2>&1 &
  sleep 5
  echo "  stuck_monitor: $(pgrep -fc 'stuck_monitor.py') (shadow ${STUCK_SHADOW:-true}) | bag $MB: $(pgrep -fc 'ros2 bag record')"
else
setsid nohup ros2 launch rover_navigation navigation.launch.py stuck_shadow:=${STUCK_SHADOW:-false} > /tmp/nav2.log 2>&1 &
sleep 30
for nd in /controller_server /planner_server /bt_navigator /behavior_server; do
  printf "  %-20s " "$nd"; timeout 6 ros2 lifecycle get "$nd" 2>/dev/null || echo "?"
done
fi

echo "########## 6. 설정 검증 ##########"
for cm in local_costmap global_costmap; do
  printf "  %-15s " $cm
  for p in stvl_layer.voxel_decay stvl_layer.decay_model; do
    V=$(timeout 6 ros2 param get /$cm/$cm $p 2>/dev/null | sed 's/^.*is: //')
    printf "%s=%s " "${p##*.}" "${V:-?}"
  done; echo
done
BT=~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav_to_pose_no_spin.xml
echo "  BT ExceptRegion $(grep -c ClearCostmapExceptRegion $BT)곳 / EntireCostmap $(grep -c '<ClearEntireCostmap' $BT)곳"
grep -ao 'reset_distance="[0-9.]*"' $BT | sort | uniq -c | sed 's/^/    /'
echo "  ZUPT: $(grep -c ZUPT ~/ros2_ws/install/rover_bringup/lib/rover_bringup/sensor_conditioner.py)곳, 로그 $(grep -ac ZUPT /tmp/sensors.log)건"

echo "########## 7. 코스트맵 클리어 + 재마킹 대기 ${WAIT}초 ##########"
timeout 10 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1 && echo "  local 클리어"
timeout 10 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1 && echo "  global 클리어"
sleep $WAIT

echo "########## 8. 상태 ##########"
echo -n "  로버 자세: "; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' '; echo
echo "  EKF 위반 $(grep -ac 'Failed to meet update rate' /tmp/sensors.log)회 | slam 폐기 $(grep -ac 'Message Filter dropping' /tmp/slam.log)회 | load $(cut -d' ' -f1-3 /proc/loadavg)"
echo
echo "########## 9. 통과 가능성 (물리 틈 / 코스트맵 감사 / RPP 기준) ##########"
# 2026-09-11: job233 은 footprint 투영에 99 를 써서 반경을 두 번 셌다(과장된 "통과 불가").
#   job248 은 센서 원시 점 기준 물리 틈, LETHAL 셀의 센서 근거, RPP 실제 기준(둘레<100)을 병기한다.
python3 /tmp/job248_audit.py 2>&1 | sed -n '5,40p'
