#!/bin/bash
# (10-19 §16 S2) 정지 상태에서 지금 스택의 부하 · 흐름 측정 30 s — 번갈이 구성 판정용. 로버 안 움직임
#   인자: <꼬리표> [REC=0|1 — 1 이면 측정 동안 러너 BAG_IR 과 같은 IR 토픽 · QoS 로 기록(/home/jetson/bags/s2_<꼬리표>)]
set +u
TAG=${1:?tag}; REC=${2:-0}
EK0=$(grep -ac 'Failed to meet update rate' /tmp/sensors.log); SL0=$(grep -ac 'Message Filter dropping' /tmp/slam.log)
if [ "$REC" = 1 ]; then
  Q=/tmp/s2_qos.yaml; : > $Q
  for t in /camera/raw/infra1/image_rect_raw /camera/raw/infra2/image_rect_raw /camera/camera/imu /camera/camera/depth/image_rect_raw; do printf "$t:\n  reliability: best_effort\n  history: keep_last\n  depth: 20\n  durability: volatile\n" >> $Q; done
  B=/home/jetson/bags/s2_$TAG; rm -rf $B
  setsid nohup ros2 bag record -o $B --qos-profile-overrides-path $Q /tf /tf_static /camera/raw/infra1/image_rect_raw /camera/raw/infra2/image_rect_raw \
    /camera/camera/infra1/metadata /camera/camera/infra2/metadata /camera/camera/depth/metadata /camera/camera/infra1/camera_info /camera/camera/infra2/camera_info \
    /camera/camera/imu /camera/camera/depth/image_rect_raw /camera/camera/depth/camera_info > /tmp/s2_rec.log 2>&1 < /dev/null &
  sleep 4
fi
# 부하는 측정 도구(ros2 topic hz)를 띄우기 전 30 s 만으로 — 측정 도구 자체 CPU 가 섞이지 않게
L0=$(head -1 /proc/stat)
for i in 1 2 3 4 5 6; do top -b -n1 -w 250 | awk 'NR>7 {print $NF, $9}'; sleep 4; done > /tmp/s2_top.txt   # 프로세스별(코어 1 = 100), 6 회 평균
sleep 3; L1=$(head -1 /proc/stat)
LU=$(python3 -c "import sys;a=list(map(int,sys.argv[1].split()[1:]));b=list(map(int,sys.argv[2].split()[1:]));d=[y-x for x,y in zip(a,b)];print(round((1-(d[3]+d[4])/sum(d))*100,1))" "$L0" "$L1")
# 흐름(각 6 s) — 주행 전이 아니므로 DDS 참여자 생성 무관
for t in /odometry/filtered /tf /scan /camera/camera/depth/image_rect_raw /camera/depth/points_filtered /nvblox_node/static_map_slice /camera/camera/infra1/image_rect_raw; do
  printf "  %-38s %s
" $t "$(timeout 7 ros2 topic hz $t 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1)"
done > /tmp/s2_hz.txt
EK1=$(grep -ac 'Failed to meet update rate' /tmp/sensors.log); SL1=$(grep -ac 'Message Filter dropping' /tmp/slam.log)
echo "== S2 $TAG (기록 $REC) $(date +%T)"
echo "  전체 CPU 사용률 $LU % (P 게이트 ≤ 60) · load $(cut -d' ' -f1-3 /proc/loadavg) · EKF 위반 +$((EK1-EK0)) · slam 폐기 +$((SL1-SL0)) (약 80 s)"
echo "  프로세스 CPU(평균, 코어 1 = 100):"
awk '{s[$1]+=$2; n[$1]++} END {for (k in s) if (s[k]/6 >= 3) printf "    %-18s %6.1f\n", k, s[k]/6}' /tmp/s2_top.txt | sort -k2 -nr | head -16
awk '{s+=$2} END {printf "    (합 %.0f %%)\n", s/6}' /tmp/s2_top.txt
echo "  흐름:"; cat /tmp/s2_hz.txt
grep -a "10 s:" /tmp/sensors.log | tail -1 | sed 's/.*10 s: /  분리 노드: /' | cut -c1-400
if [ "$REC" = 1 ]; then
  pkill -INT -f "ros2 bag record -o $B"; sleep 4
  ros2 bag info $B 2>/dev/null | grep -aE "Duration|Bag size|infra[12]/image|metadata|imu|depth/image" | sed 's/^/  /' | cut -c1-160
fi
