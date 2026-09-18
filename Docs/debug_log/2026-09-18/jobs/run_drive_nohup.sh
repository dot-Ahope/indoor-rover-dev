#!/bin/bash
# 주행 러너 v2 (09-15 교훈): 원격에서 nohup 으로 게이트+주행을 띄우고 로그 파일을 폴링한다 — ssh 가 끊겨도 주행은 기록되고, 재접속 후 이어 읽는다.
# 인자: NAME D BX BY TOL GL   (게이트는 run_inf1.sh 와 동일: 상자 ±TOL, 통로 띠 근거 없는 셀 ≤1, 창 ≥0.20)
NAME=${1:-drv}; D=${2:-1.8}; BX=${3:-1.15}; BY=${4:-0.0}; TOL=${5:-0.06}; GL=${6:-0}
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
H=${JETSON_HOST:-192.168.0.101}
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8 -o ServerAliveInterval=3 -o ServerAliveCountMax=3"
J=jetson@$H
for f in job254_s4run.sh job231_drive.sh job125_avoid3.py job248_audit.py job315_boxcells.py job386_slamalive.py; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f $J:/tmp/$f || { echo "전송 실패 $f"; exit 1; }; done
# --- 사전 게이트 (run_inf1.sh 와 같은 판정, 한 번의 ssh) ---
A=$(timeout 150 sshpass -p <PW> ssh $O $J "export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; BOX_HINT='$BX $BY' python3 /tmp/job248_audit.py 2>&1")
# 09-16: 감사 출력이 간혹 표 없이 잘린다(run_gate 1회) → 최소폭 줄이 없으면 한 번 재시도
echo "$A" | grep -aq '최소폭' || { echo "  (감사 출력 불완전 — 재시도)"; A=$(timeout 150 sshpass -p <PW> ssh $O $J "export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; BOX_HINT='$BX $BY' python3 /tmp/job248_audit.py 2>&1"); }
echo "$A" | grep -aE '^상자:|최소폭'
NB=$(echo "$A" | grep -aE '^  로컬\[' -A1 | grep -aoE '\(\+?[-0-9.]+,[-+0-9.]+\)' | tr -d '()+' | awk -F, '$1>0.3 && $1<1.6 && $2>-0.10 && $2<0.50' | wc -l)
# 상자 셀 최대 y: 1 회 표본은 한 셀(5 cm) 튀는 순간을 잡는다(09-16 mp3 게이트: 0.219 한 번, 이후 6/6 이 0.169) → 3 회 표본의 중앙값
BMS=$(timeout 90 sshpass -p <PW> ssh $O $J "export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; for i in 1 2 3; do python3 /tmp/job315_boxcells.py $BX $BY 2>&1 | grep -av '^\[' | tail -1; sleep 3; done" | tr '
' ' ')
BM=$(echo $BMS | tr ' ' '
' | grep -aE '^-?[0-9.]+$' | sort -n | sed -n 2p)
echo "상자 셀 최대 y 표본 3회: $BMS → 중앙값 $BM"
# 좌측 경계: x 1.10~1.30 행의 기준1 구간 중 **하한이 상자 셀 최대 y 보다 큰 것**(왼쪽 통로)만 — 09-16 mp3 게이트에서 1.00 행의 우측 구간 [-0.35~+0.00] 이 섞여 창이 -0.365 로 오판
LB=$(echo "$A" | grep -aE '^   1\.[1-3]0 ' | awk '{print $2}' | tr -d '[]' | awk -F'~' -v bm="$BM" '$1+0 > bm+0 {print $2+0}' | sort -n | head -1)
W2=$(awk -v lb="$LB" -v bm="$BM" 'BEGIN{ if (bm=="nan"||bm=="") print "nan"; else printf "%.3f", lb - (bm + 0.195) }')
echo "통로 띠 근거 없는 셀 $NB (≤1) | 창 $W2 m (≥0.20; 좌측 $LB, 상자 셀 최대 y $BM)"
[ -n "$NB" ] && [ "$NB" -le 1 ] || { echo "★ 근거 없는 셀 $NB — 주행하지 않음"; exit 1; }
awk -v w="$W2" 'BEGIN{exit !(w+0 >= 0.20)}' || { echo "★ 창 < 0.20 — 주행하지 않음"; exit 1; }
# 09-17 mp6 교훈: 목표를 벽 0.37 m 앞에 둬서 풋프린트 여유 ~10 cm → 목표 0.24 m 앞에서 정체. 목표 풋프린트 ↔ LETHAL ≥ 0.20 m 요구
tr -d '\r' < $SPS/job377_goalclear.py > /tmp/job377_goalclear.py; sshpass -p <PW> scp $O -q /tmp/job377_goalclear.py $J:/tmp/job377_goalclear.py
GC=$(timeout 60 sshpass -p <PW> ssh $O $J "export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; python3 /tmp/job377_goalclear.py $D $GL 2>&1 | grep -av '^\['")
echo "$GC" | head -1
awk -v c="$(echo "$GC" | tail -1)" 'BEGIN{exit !(c+0 >= 0.20)}' || { echo "★ 목표 풋프린트 여유 < 0.20 m — 목표를 옮길 것, 주행하지 않음"; exit 1; }
# 09-18 dy3 교훈: 출발 자세가 내접 셀 안(로버 뒤 ≈5 cm 물체 — 관찰자 발 추정)이면 스무더 충돌·Optimizer fail. 차체 외곽 ≥ 0.10 m 요구
tr -d '\r' < $SPS/job440_startclear.py > /tmp/job440_startclear.py; sshpass -p <PW> scp $O -q /tmp/job440_startclear.py $J:/tmp/job440_startclear.py
SC=$(timeout 60 sshpass -p <PW> ssh $O $J "export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; python3 /tmp/job440_startclear.py 2>&1 | grep -av '^\['")
# 09-18 dy4: 새 노드가 DDS 탐색 지연으로 데이터를 못 받으면 nan → 한 번 더
echo "$SC" | tail -1 | grep -qE '^[0-9.]+$' || { echo "  (출발 자세 결과 없음/비정상: $(echo "$SC" | tail -1 | cut -c1-80) — 재시도)"; SC=$(timeout 60 sshpass -p <PW> ssh $O $J "export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; python3 /tmp/job440_startclear.py 2>&1 | grep -av '^\['"); }
echo "$SC" | grep -a "출발 자세"
echo "$SC" | tail -1 | grep -qE '^[0-9.]+$' || { echo "★ 출발 자세 검사 실패(2 회): $(echo "$SC" | tail -2 | tr '
' ' ' | cut -c1-160) — 주행하지 않음"; exit 1; }
awk -v c="$(echo "$SC" | tail -1)" 'BEGIN{exit !(c+0 >= 0.10)}' || { echo "★ 출발 자세 여유 < 0.10 m — 로버 주변(특히 뒤) 물체·사람을 치울 것, 주행하지 않음"; exit 1; }
# --- 주행: 원격 nohup + 로그 ---
LOG=/tmp/drive_$NAME.log
timeout 20 sshpass -p <PW> ssh $O $J "export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; rm -f $LOG; GOAL_LAT=$GL nohup bash /tmp/job254_s4run.sh $NAME $D $BX $BY $TOL > $LOG 2>&1 & echo started_pid \$!"
echo "주행 시작 $(date +%T) — 로그 $LOG (링크가 끊겨도 원격에서 계속됨; 정지는 job156_stop.sh)"
# --- 로그 폴링 (최대 8분; ssh 실패는 재시도) ---
T0=$(date +%s); LAST=0
while [ $(( $(date +%s) - T0 )) -lt 480 ]; do
  sleep 5
  OUT=$(timeout 15 sshpass -p <PW> ssh $O $J "cat $LOG 2>/dev/null" 2>/dev/null) || { echo "  (ssh 재시도 $(date +%T))"; continue; }
  N=$(echo "$OUT" | wc -l)
  if [ "$N" -gt "$LAST" ]; then echo "$OUT" | sed -n "$((LAST+1)),${N}p" | grep -avE '^ +[0-9]+\.[0-9] \+|^   (0\.9|1\.[0-4])0 '; LAST=$N; fi
  echo "$OUT" | grep -aqE '^결과 |게이트 실패|주행하지 않음' && break
done
echo "=== 끝 $(date +%T) ==="
