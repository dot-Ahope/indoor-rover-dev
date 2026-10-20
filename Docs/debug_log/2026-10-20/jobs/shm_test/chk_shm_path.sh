#!/bin/bash
# (10-20 §7.3c) SHM 경로 판별 — 모두 SHM 전용으로: V1 호스트 발행 → 호스트 구독, V2 호스트 발행 → 컨테이너 구독. 도메인 88, 로버 무관
set +u; CN=isaac_ros_dev-aarch64-container; D=/tmp/shmt; mkdir -p $D; chmod 777 $D
source /opt/ros/humble/setup.bash; export ROS_DOMAIN_ID=88
echo "컨테이너 /dev/shm 이 호스트와 같은가: 호스트 $(stat -c %i /dev/shm) · 컨테이너 $(docker exec $CN stat -c %i /dev/shm) · 컨테이너에서 보이는 fastrtps $(docker exec $CN bash -c 'ls /dev/shm | grep -c fastrtps') / 호스트 $(ls /dev/shm | grep -c fastrtps)"
echo "컨테이너 hostname $(docker exec $CN hostname) · 호스트 $(hostname)"
fastdds shm clean >/dev/null 2>&1
run() {   # $1 이름 $2 talker 프로파일 $3 host-listener 프로파일 $4 container-listener 프로파일
  rm -f $D/host $D/cont $D/*.pid
  FASTRTPS_DEFAULT_PROFILES_FILE=$2 python3 /tmp/shm_talker.py shmt_talker > $D/t.log 2>&1 & T=$!
  FASTRTPS_DEFAULT_PROFILES_FILE=$3 python3 /tmp/shm_listener.py shmt_host $D/host > $D/h.log 2>&1 & L=$!
  docker exec -d -u admin $CN bash -c "export ROS_DOMAIN_ID=88 FASTRTPS_DEFAULT_PROFILES_FILE=$4; source /opt/ros/humble/setup.bash; exec python3 /tmp/shm_listener.py shmt_cont $D/cont > $D/c.log 2>&1"
  sleep 12; echo "$1: 호스트 구독 [$(cat $D/host 2>/dev/null)] · 컨테이너 구독 [$(cat $D/cont 2>/dev/null)] (시각 n1 n2, 약 6~10 s 분량)"
  kill -INT $T $L; docker exec $CN kill -INT $(cat $D/cont.pid 2>/dev/null) 2>/dev/null; sleep 3; kill -9 $T $L 2>/dev/null; docker exec $CN kill -9 $(cat $D/cont.pid 2>/dev/null) 2>/dev/null
  grep -ahiE "error|warn" $D/t.log $D/h.log $D/c.log | head -3 | cut -c1-160; fastdds shm clean >/dev/null 2>&1
}
O=/tmp/fastdds_shm_only.xml; U=/tmp/fastdds_shm_udp.xml
run "V1 전부 SHM 전용" $O $O $O
run "V2 발행 SHM+UDP · 호스트 구독 SHM 전용 · 컨테이너 SHM 전용" $U $O $O
