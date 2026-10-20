#!/bin/bash
# (10-20 §7.5) UDP 전용으로 크기만 바꿔 호스트 발행 → 컨테이너 구독(best effort, nvblox · cuVSLAM 과 같음). 조건마다 5 s 대기 + 20 s 측정, 두 번씩 번갈아.
#   측정: 컨테이너 수신 Hz, 같은 창 RcvbufErrors/s 증가(실행 중 스택 몫 포함 — 조건 사이 '발행 없음' 창도 잼). 도메인 88, 로버 무관
set +u; CN=isaac_ros_dev-aarch64-container; D=/tmp/shmt; mkdir -p $D; chmod 777 $D
source /opt/ros/humble/setup.bash; export ROS_DOMAIN_ID=88
U=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; cp -f $U /tmp/fastdds_udp_only.xml
rb() { awk '/^Udp:/{n++} n==2 && /^Udp:/{print $6; exit}' /proc/net/snmp; }
one() {   # $1 라벨 $2.. talker 인자(폭 높이 바이트 줄수) 또는 none
  rm -f $D/cont $D/cont.pid
  docker exec -d -u admin $CN bash -c "export ROS_DOMAIN_ID=88 FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; exec python3 /tmp/shm_listener.py shmt_cont $D/cont > $D/c.log 2>&1"
  T=""; [ "$2" != none ] && { FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml python3 /tmp/size_talker.py shmt_size $2 $3 $4 $5 > $D/t.log 2>&1 & T=$!; }
  sleep 5; a=($(cat $D/cont 2>/dev/null || echo "0 0 0")); e0=$(rb); sleep 20; b=($(cat $D/cont 2>/dev/null || echo "0 0 0")); e1=$(rb)
  printf "  %-34s 수신 %5.1f / %5.1f Hz · 수신버퍼 버림 %4d/s\n" "$1" $(echo "(${b[1]}-${a[1]})/20" | bc -l) $(echo "(${b[2]}-${a[2]})/20" | bc -l) $(( (e1-e0)/20 ))
  [ -n "$T" ] && kill -INT $T; docker exec $CN kill -INT $(cat $D/cont.pid 2>/dev/null) 2>/dev/null; sleep 3
  [ -n "$T" ] && kill -9 $T 2>/dev/null; docker exec $CN kill -9 $(cat $D/cont.pid 2>/dev/null) 2>/dev/null
}
for r in 1 2; do
  echo "##### 반복 $r"
  one "발행 없음(기준)" none
  one "C1 160×120×2B ×1 (38 kB, 지금 깊이)" 160 120 2 1
  one "C4 640×480×1B ×1 (307 kB, IR 한 줄)" 640 480 1 1
  one "C2 640×480×1B ×2 (307 kB ×2, IR 좌우)" 640 480 1 2
  one "C3 640×480×2B ×1 (614 kB, 깊이 원본)" 640 480 2 1
done
