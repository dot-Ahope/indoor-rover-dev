#!/bin/bash
# F0 주행 래퍼(Jetson, 2026-09-23): 일반 게이트(A 프로세스·B 보드·J nvblox·C SLAM·G2 출발 자세) → bag·tegrastats·top·RSS → job550 → 메타(job453).
#   상자 코스 게이트(D·E·F·L·M·N)는 쓰지 않는다. 목표 여유(G1)는 Nav2 가 목표 셀을 거부하면 러너가 중단하는 것으로 대신한다.
#   인자: NAME "GOALS" [SPEED] [PAUSE s]  (setsid nohup 으로 띄워 ssh 가 끊겨도 계속)
set +u
NAME=$1; GOALS=$2; SPEED=${3:-0.07}; PAUSE=${4:-0}
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "########## F0 게이트 $(date +%T) ##########"
# 10-07: 그림자 EKF A(ekf_shadow_a, TF 안 냄)가 떠 있으면 ekf_node 2 개가 정상. 10-20 §6.3: cuVSLAM 그림자 EKF(ekf_vslam)도 같은 취급
DUP=0; for p in microros_agent robot_state_publisher realsense2_camera rplidar sensor_conditioner ekf_node slam_toolbox controller_server planner_server bt_navigator behavior_server lifecycle_manager_navigation stuck_monitor; do c=$(pgrep -fc "$p" 2>/dev/null | head -1); e=1; [ $p = ekf_node ] && e=$((1 + $(pgrep -fc "__node:=ekf_shadow_a" 2>/dev/null | head -1) + $(pgrep -fc "__node:=ekf_[v]slam" 2>/dev/null | head -1))); [ "${c:-0}" != $e ] && { DUP=1; echo "  ★ $p = $c개"; }; done
[ $DUP = 1 ] && { echo "  A 불합격 — 주행하지 않음"; exit 1; }
# 10-27 §24: B(ros2 topic hz 12 s) · C(job386 5 s) · G2(job440 ≤ 60 s)를 한 노드 chk_drive_gate.py 로(참여자 3 → 1, 약 24 → 7 s). 기준은 그대로.
GT=$(timeout 40 python3 /tmp/chk_drive_gate.py 2>&1 | grep -av "^\["); echo "$GT" | grep -av "^GATE"; GL=$(echo "$GT" | grep -a "^GATE" | tail -1)
echo "$GL" | grep -q "B=OK" || { echo "  B 불합격(보드 무발행) — 주행하지 않음"; exit 1; }
echo "  A·B 통과"
if grep -q nvblox_layer /tmp/nav2_params_active.yaml 2>/dev/null; then
  NP=$(docker exec isaac_ros_dev-aarch64-container bash -c "pgrep -fc '^/opt/ros/humble/lib/nvblox_ros/nvblox_node' || true" 2>/dev/null)
  RD=$(grep -aA7 "NVBlox Rates" /tmp/nvblox_node.log | grep -aE "ros/depth_image_callback" | awk '{print $NF}' | tail -1)
  [ "$NP" = 1 ] && awk -v d="$RD" 'BEGIN{exit !(d+0>=10)}' || { echo "  J 불합격(nvblox $NP 개, 깊이 $RD Hz) — 주행하지 않음"; exit 1; }; echo "  J 통과 (깊이 $RD Hz)"
fi
echo "$GL" | grep -q "C=OK" || { echo "  C 불합격(SLAM) — 주행하지 않음"; exit 1; }; echo "  C 통과"
# 10-02 §6.3: G2_SKIP=1 = 사용자가 현장을 보고 "앞에 아무것도 없다, 출발 가능" 이라 한 경우만(로컬 카메라 표시 1 칸이 범퍼 6.7 cm 앞). 값은 기록하고 진행.
G2=$(echo "$GL" | grep -o "G2=[^ ]*" | cut -d= -f2)
if [ "${G2_SKIP:-0}" = 1 ]; then echo "  G2 무시(사용자 지시) — 여유 $G2 m"; else
awk -v d="$G2" 'BEGIN{exit !(d+0>=0.10)}' || { echo "  G2 불합격(출발 자세 여유 $G2 m < 0.10) — 주행하지 않음"; exit 1; }; echo "  G2 통과 ($G2 m)"; fi
# 10-27 §24: 부하 게이트 P 를 30 s 대기의 마지막 10 s 로 잼(예전: 30 s 뒤 따로 10 s)
sleep 20   # DDS 참여자 생성 뒤 30 s (09-21 cc1 규칙) = 20 s + 아래 P 측정 10 s
# 10-01 §8.9: 출발 전 부하 게이트 — 정지 10 s 코어 평균 사용률(/proc/stat). f2a3 은 주행 중 88 %·sy 31 % 로 서버 응답 시간 초과(원인 미확정),
#   정지 기준선은 36 %(job745). 출발 직전 이미 무거우면(> LOAD_MAX, 기본 60 %) 주행하지 않는다.
L0=$(head -1 /proc/stat); sleep 10; L1=$(head -1 /proc/stat)
LU=$(python3 -c "import sys;a=list(map(int,sys.argv[1].split()[1:]));b=list(map(int,sys.argv[2].split()[1:]));d=[y-x for x,y in zip(a,b)];print(round((1-(d[3]+d[4])/sum(d))*100))" "$L0" "$L1")
awk -v u=$LU -v m=${LOAD_MAX:-60} 'BEGIN{exit !(u<=m)}' || { echo "  P 불합격(정지 부하 $LU % > ${LOAD_MAX:-60} %) — 주행하지 않음"; exit 1; }; echo "  P 통과 (정지 부하 $LU %)"
BAG=/tmp/bag_$NAME; rm -rf $BAG
TOPICS="/tf /tf_static /map /scan /plan /plan_smoothed /local_costmap/costmap /global_costmap/costmap /odometry/filtered /wheel_odom /cmd_vel /rover/status /battery /rover/stuck /imu/data"
[ "${BAG_PROFILE:-}" = nvblox ] && TOPICS="$TOPICS /nvblox_node/static_map_slice"
TOPICS="$TOPICS ${EXTRA_TOPICS:-}"
# 10-19 §3: BAG_DEPTH=1 이면 nvblox 입력(깊이 160×120 · camera_info, 약 0.6 MB/s)도 기록 — 오프라인 nvblox 재생 A/B 용(run_nvblox_replay.sh)
[ "${BAG_IR:-0}" = 1 ] && BAG_DEPTH=1   # 10-19 §16: IR 기록은 깊이 기록을 포함
[ "${BAG_DEPTH:-0}" = 1 ] && TOPICS="$TOPICS /camera/camera/depth/image_rect_raw /camera/camera/depth/camera_info"
# 10-19 §16 · §17: BAG_IR=1(BAG_DEPTH 포함) — prep 에 SENSORS_ADD="emitter_flash:=true" 필요. 원시 IR 좌우(켬 · 끔 모두) · IR 메타데이터 · IR camera_info ·
#   카메라 IMU 는 ros2 bag record 가 아니라 카메라와 같은 프로세스의 분리 노드가 직접 쓴다(/home/jetson/bags/bag_<NAME>_ir) — §16 S2: 별도 기록기는
#   CPU 77 % · IR 8 Hz 로 불합격. 시작 · 끝 = 분리 노드 record_path 파라미터.
[ "${LONG_REC:-0}" = 1 ] && TOPICS="$TOPICS /trajectories /transformed_global_plan"   # 10-07 §11: 장기 주행만 — MPPI 후보·최적 궤적(prep 에 mppi_viz:=true 필요)   # 10-07 §2: rf2o 비교 주행 — /odometry/ekf_a /odom_rf2o /odom_rf2o/gated
# 10-12 §11: 기록기가 /trajectories(206 kB × 10 Hz)만 '손실 허용(best effort)' 으로 구독 — 조각을 잃어도 재전송을 요구하지 않게.
#   왜: §9.2 평상시 수신 버퍼 손실이 나는 소켓은 기록기뿐이었고, 신뢰성 재전송이 통신 폭주(10 배)의 씨앗으로 추정됨. BAG_BE_TRAJ=0 이면 예전처럼.
QOSOPT=""; if [ "${BAG_BE_TRAJ:-1}" = 1 ]; then printf '/trajectories:
  reliability: best_effort
  history: keep_last
  depth: 5
  durability: volatile
' > /tmp/bag_qos_$NAME.yaml
# 10-13 §2: 기록기가 /tf 도 best effort 로 구독(/tf_static 은 그대로). 기본 켬(10-13 §4, 사용자 결정) — reliable 이면 느린 기록기가 /tf 쓰는 쪽을
#   붙잡아 HEARTBEAT 폭주(포화)를 일으킨다(§1.2·§2.1: f2n1 포화 없음·bag /tf 100 %). BAG_BE_TF=0 이면 예전처럼.
[ "${BAG_BE_TF:-1}" = 1 ] && printf '/tf:
  reliability: best_effort
  history: keep_last
  depth: 100
  durability: volatile
' >> /tmp/bag_qos_$NAME.yaml
# 10-19 §3: 깊이도 best effort 로 구독 — 발행자(realsense)는 reliable · transient_local 이라 느린 reliable 기록기가 카메라 발행을 붙잡지 않게
[ "${BAG_DEPTH:-0}" = 1 ] && printf '/camera/camera/depth/image_rect_raw:
  reliability: best_effort
  history: keep_last
  depth: 10
  durability: volatile
' >> /tmp/bag_qos_$NAME.yaml
QOSOPT="--qos-profile-overrides-path /tmp/bag_qos_$NAME.yaml"; fi
echo "  bag 기록 QoS 재정의: ${QOSOPT:-없음}"
IRB=/home/jetson/bags/bag_${NAME}_ir
[ "${BAG_IR:-0}" = 1 ] && { rm -rf $IRB; echo "  IR 기록 시작: $(timeout 10 ros2 param set /emitter_splitter record_path $IRB 2>&1 | tail -1)"; }
setsid nohup ros2 bag record -o $BAG $QOSOPT $TOPICS > /tmp/bag_$NAME.log 2>&1 &
setsid nohup tegrastats --interval 1000 > /tmp/tegra_$NAME.log 2>&1 &
# 10-27 §24: top 2 s 루프 제거 — /proc 프로세스별 틱 기록(proc_) 과 겹치고 top 실행 자체가 CPU 를 씀. 명령줄은 rss_ 스냅숏(args)으로.
TOPPID=""
# 10-01 §8.9: 전체 프로세스 CPU 틱 기록(top 상위 30 줄은 작은 것을 놓침) — 2 s 마다 "시각 pid 틱 명령" → 사후 분석
(for i in $(seq 1 400); do T=$(date +%s); for p in /proc/[0-9]*; do read -r a < $p/stat 2>/dev/null || continue; set -- $a; echo "$T ${p#/proc/} $((${14}+${15})) $2"; done; echo "$T ALL $(head -1 /proc/stat)"; sleep 2; done) > /tmp/proc_$NAME.log 2>&1 &
PROCPID=$!
# 10-12 §8: UDP 수신 버퍼 손실을 시간순으로(DDS 를 건드리지 않는 파일 읽기만). 2 s 마다 커널 누적값(Udp InDatagrams·RcvbufErrors)과 소켓별 drops,
#   15 s 뒤·끝에 소켓 inode → 프로세스 이름 표. 왜: rmem_max 208 kB 인데 /trajectories 메시지 1 개가 206 kB — 포화 시작 때 어느 소켓이 넘치는지 확인.
netmap() { for p in $(pgrep -u jetson); do c=$(cat /proc/$p/comm 2>/dev/null); for i in $(ls -l /proc/$p/fd 2>/dev/null | grep -o 'socket:\[[0-9]*\]' | tr -d 'socket:[]'); do echo "MAP $i $p $c"; done; done; }
[ "${NET_LOG:-0}" = 1 ] && (sleep 15; netmap; for i in $(seq 1 400); do T=$(date +%s); echo "$T SNMP $(awk '/^Udp:/{l=$0} END{print l}' /proc/net/snmp)"; awk -v t=$T 'NR>1 && $NF>0{print t, "SOCK", $2, $NF, $(NF-3)}' /proc/net/udp; sleep 2; done) > /tmp/net_$NAME.log 2>&1 &
NETPID=$!   # 10-27 §24: NET_LOG=1 일 때만(10-12 통신 폭증 조사용, 10-13 해결) — 꺼져 있으면 $! 는 앞 프로세스라 아래 kill 대상에서 뺌
[ "${NET_LOG:-0}" = 1 ] || NETPID=""
# 10-13 §1: 루프백 패킷 캡처(CAP_PCAP=1) — 포화 때 늘어나는 패킷의 종류·송신자 확인용. tcpdump 에 캡처 권한(setcap)이 있으면 자동,
#   없으면 사용자가 따로 sudo tcpdump 를 돌린다(안내만 출력). -s 512: 앞 512 B 만(종류·끝점·탐색 정보의 토픽 이름까지).
CAPPID=""
if [ "${CAP_PCAP:-0}" = 1 ]; then
  if getcap "$(which tcpdump)" 2>/dev/null | grep -q cap_net_raw; then
    setsid nohup tcpdump -i lo -s 512 -w /tmp/cap_$NAME.pcap udp > /tmp/cap_$NAME.log 2>&1 & CAPPID=$!; echo "  패킷 캡처 시작(자동): /tmp/cap_$NAME.pcap"
  else echo "  패킷 캡처: tcpdump 권한 없음 — 사용자가 실행한 sudo tcpdump(/tmp/lo_cap.pcap)에 맡김"; fi
fi
ps -eo pid,rss,pcpu,comm,args --sort=-rss | head -25 > /tmp/rss_$NAME.txt; sleep 2
echo "########## F0 주행 $(date +%T) — 목표 $GOALS ##########"
python3 /tmp/job550_f0run.py $NAME "$GOALS" $SPEED $PAUSE 2>&1 | grep -av "^\["
[ "${BAG_IR:-0}" = 1 ] && echo "  IR 기록 끝: $(timeout 10 ros2 param set /emitter_splitter record_path '' 2>&1 | tail -1)"
pkill -INT -f "ros2 bag record" 2>/dev/null; pkill -f "tegrastats --interval 1000" 2>/dev/null; kill $TOPPID $PROCPID $NETPID 2>/dev/null; [ -n "$CAPPID" ] && { kill -INT $CAPPID 2>/dev/null; sleep 1; ls -la /tmp/cap_$NAME.pcap 2>/dev/null | awk '{print "  캡처 파일", $5, "B"}'; }; netmap >> /tmp/net_$NAME.log 2>/dev/null
for i in $(seq 1 10); do [ "$(pgrep -fc 'ros2 bag record')" = 0 ] && break; sleep 1; done
TOPICS="$TOPICS" bash /tmp/job453_runmeta.sh $NAME "$GOALS" $SPEED >/dev/null 2>&1; cp /tmp/meta_$NAME/run_meta.txt /tmp/meta_$NAME/params.txt $BAG/ 2>/dev/null
[ "${BAG_DEPTH:-0}" = 1 ] && { mkdir -p /home/jetson/bags; rm -rf /home/jetson/bags/bag_$NAME; cp -r /tmp/bag_$NAME /home/jetson/bags/ && echo "  깊이 bag 사본 /home/jetson/bags/bag_$NAME (재부팅에도 남음)"; }
# 10-19 §16: IR bag 은 수 GB — PC 로 옮길 tgz 는 만들지 않는다(분석은 Jetson 또는 따로 가져옴)
[ "${BAG_IR:-0}" = 1 ] && { du -sh $IRB | sed 's/^/  IR bag 크기 /'; ros2 bag info $IRB 2>/dev/null | grep -aE "Duration|Count" | sed 's/^/  /' | cut -c1-150; du -sh /home/jetson/bags/bag_$NAME | sed 's/^/  IR bag 크기 /'; echo "=== 끝 $(date +%T) (IR bag, tgz 생략) ==="; exit 0; }
tar czf /tmp/bag_$NAME.tgz -C /tmp bag_$NAME 2>/dev/null; echo "=== 끝 $(date +%T) bag $(stat -c %s /tmp/bag_$NAME.tgz 2>/dev/null) B ==="
