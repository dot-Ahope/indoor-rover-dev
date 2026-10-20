#!/bin/bash
# (10-20 §7.3) SHM 재기동 시험 — 팔 A(정리 없음) NA 주기 → 팔 B(매 기동 전 fastdds shm clean) NB 주기. 도메인 88, 로버 · 실행 중 스택과 무관.
#   준비물(/tmp): fastdds_shm_udp.xml shm_talker.py shm_listener.py shm_idle.py. 인자: [NA=15] [NB=30]
set +u
NA=${1:-15}; NB=${2:-30}; CN=isaac_ros_dev-aarch64-container; D=/tmp/shmt; mkdir -p $D; chmod 777 $D
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=88 FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_shm_udp.xml
udp() { awk '/^Udp:/{n++} n==2 && /^Udp:/{print $2; exit}' /proc/net/snmp; }
nshm() { ls /dev/shm | grep -c fastrtps; }
cnt() { [ -f $1 ] && cat $1 || echo "0 0 0"; }
echo "컨테이너 FastDDS: $(docker exec $CN bash -c 'ls /opt/ros/humble/lib/libfastrtps.so.* 2>/dev/null | head -1') · 호스트: $(ls /opt/ros/humble/lib/libfastrtps.so.* | head -1)"
echo "시작 전 /dev/shm fastrtps $(nshm) 개 · 컨테이너 구독 프로파일 ${CPROF:-/tmp/fastdds_shm_udp.xml}"
H=()   # 호스트 쪽 pid: talker hostlistener idle1 idle2
start_all() {
  rm -f $D/*.pid $D/cont $D/host
  python3 /tmp/shm_talker.py shmt_talker > $D/talker.log 2>&1 & T=$!
  python3 /tmp/shm_listener.py shmt_host $D/host > $D/host.log 2>&1 & L=$!
  python3 /tmp/shm_idle.py shmt_idle1 > $D/idle1.log 2>&1 & I1=$!
  python3 /tmp/shm_idle.py shmt_idle2 > $D/idle2.log 2>&1 & I2=$!
  docker exec -d -u admin $CN bash -c "export ROS_DOMAIN_ID=88 FASTRTPS_DEFAULT_PROFILES_FILE=${CPROF:-/tmp/fastdds_shm_udp.xml}; source /opt/ros/humble/setup.bash; exec python3 /tmp/shm_listener.py shmt_cont $D/cont > $D/cont.log 2>&1"
}
ckill() { local p; p=$(cat $D/cont.pid 2>/dev/null); [ -n "$p" ] && docker exec $CN kill -$1 $p 2>/dev/null; }
calive() { local p; p=$(cat $D/cont.pid 2>/dev/null); [ -n "$p" ] && docker exec $CN kill -0 $p 2>/dev/null; }
stop_all() {   # $1 = INT|TERM|KILL
  kill -$1 $T $L $I1 $I2 2>/dev/null; ckill $1
  for i in $(seq 1 10); do alive=0; for p in $T $L $I1 $I2; do kill -0 $p 2>/dev/null && alive=1; done; calive && alive=1; [ $alive = 0 ] && break; sleep 1; done
  [ $alive = 1 ] && { echo -n " [남음→-9]"; kill -9 $T $L $I1 $I2 2>/dev/null; ckill 9; sleep 1; }
}
rate() {   # 6 s 동안 컨테이너 · 호스트 구독 Hz 와 UDP 증가 — 출력 "c1 c2 h1 h2 udp/s"
  local a b ha hb u0 u1; a=($(cnt $D/cont)); ha=($(cnt $D/host)); u0=$(udp); sleep 6; b=($(cnt $D/cont)); hb=($(cnt $D/host)); u1=$(udp)
  awk -v a1=${a[1]} -v a2=${a[2]} -v b1=${b[1]} -v b2=${b[2]} -v h1=${ha[1]} -v h2=${ha[2]} -v g1=${hb[1]} -v g2=${hb[2]} -v u=$((u1-u0)) 'BEGIN{printf "%.1f %.1f %.1f %.1f %.0f", (b1-a1)/6, (b2-a2)/6, (g1-h1)/6, (g2-h2)/6, u/6}'
}
errs() { cat $D/*.log 2>/dev/null | grep -acE "open_and_lock_file|RTPS_TRANSPORT_SHM|init_port|Failed to create|SHM Error"; }
cycle() {   # $1 팔 $2 번호
  local mode=$(( ($2 - 1) % 4 )) MN=(INT TERM KILL "발행-9재기동")
  [ $1 = B ] && CL=$(fastdds shm clean 2>&1 | tail -1 | cut -c1-60) || CL="-"
  local u0 u1; u0=$(udp); sleep 6; u1=$(udp); local base=$(( (u1 - u0) / 6 ))
  start_all; sleep 6; local r=$(rate)
  local extra=""
  if [ $mode = 3 ]; then
    kill -9 $T; sleep 2; python3 /tmp/shm_talker.py shmt_talker > $D/talker2.log 2>&1 & T=$!; sleep 6; extra=" | 발행 재기동 뒤 $(rate | awk '{print $1, $2}')"; stop_all INT
  else stop_all ${MN[$mode]}; fi
  sleep 1
  printf "%s%02d %-12s 정리[%s] 기준 UDP %d/s | 구독 컨테이너·호스트 Hz·UDP/s: %s%s | SHM오류 %d | 끝 /dev/shm %d\n" $1 $2 "${MN[$mode]}" "$CL" $base "$r" "$extra" $(errs) $(nshm)
  cat $D/*.log 2>/dev/null | grep -aE "open_and_lock_file|RTPS_TRANSPORT_SHM|init_port|SHM Error" | head -2 | cut -c1-160
  rm -f $D/*.log
}
echo "########## 팔 A: 정리 없음 ##########"; for i in $(seq 1 $NA); do cycle A $i; done
echo "########## 팔 B: 매 기동 전 fastdds shm clean ##########"; for i in $(seq 1 $NB); do cycle B $i; done
echo "마지막 정리: $(fastdds shm clean 2>&1 | tail -1) · /dev/shm fastrtps $(nshm)"
