#!/bin/bash
# 주행 러너 v2 (09-15 교훈): 원격에서 nohup 으로 게이트+주행을 띄우고 로그 파일을 폴링한다 — ssh 가 끊겨도 주행은 기록되고, 재접속 후 이어 읽는다.
# 인자: NAME D BX BY TOL GL   (게이트는 run_inf1.sh 와 동일: 상자 ±TOL, 통로 띠 근거 없는 셀 ≤1, 창 ≥0.20)
NAME=${1:-drv}; D=${2:-1.8}; BX=${3:-1.15}; BY=${4:-0.0}; TOL=${5:-0.06}; GL=${6:-0}
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
H=${JETSON_HOST:-192.168.0.101}
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8 -o ServerAliveInterval=3 -o ServerAliveCountMax=3"
J=jetson@$H
for f in job254_s4run.sh job231_drive.sh job125_avoid3.py job248_audit.py job315_boxcells.py; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f $J:/tmp/$f || { echo "전송 실패 $f"; exit 1; }; done
# --- 사전 게이트 (run_inf1.sh 와 같은 판정, 한 번의 ssh) ---
A=$(timeout 150 sshpass -p <PW> ssh $O $J "source /opt/ros/humble/setup.bash; BOX_HINT='$BX $BY' python3 /tmp/job248_audit.py 2>&1")
echo "$A" | grep -aE '^상자:|최소폭'
NB=$(echo "$A" | grep -aE '^  로컬\[' -A1 | grep -aoE '\(\+?[-0-9.]+,[-+0-9.]+\)' | tr -d '()+' | awk -F, '$1>0.3 && $1<1.6 && $2>-0.10 && $2<0.50' | wc -l)
LB=$(echo "$A" | grep -aE '^   1\.[0-3]0 ' | awk '{print $2}' | tr -d '[]' | cut -d'~' -f2 | sort -n | head -1)
BM=$(timeout 60 sshpass -p <PW> ssh $O $J "source /opt/ros/humble/setup.bash; python3 /tmp/job315_boxcells.py $BX $BY 2>&1 | grep -av '^\[' | tail -1")
W2=$(awk -v lb="$LB" -v bm="$BM" 'BEGIN{ if (bm=="nan"||bm=="") print "nan"; else printf "%.3f", lb - (bm + 0.195) }')
echo "통로 띠 근거 없는 셀 $NB (≤1) | 창 $W2 m (≥0.20; 좌측 $LB, 상자 셀 최대 y $BM)"
[ -n "$NB" ] && [ "$NB" -le 1 ] || { echo "★ 근거 없는 셀 $NB — 주행하지 않음"; exit 1; }
awk -v w="$W2" 'BEGIN{exit !(w+0 >= 0.20)}' || { echo "★ 창 < 0.20 — 주행하지 않음"; exit 1; }
# --- 주행: 원격 nohup + 로그 ---
LOG=/tmp/drive_$NAME.log
timeout 20 sshpass -p <PW> ssh $O $J "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; rm -f $LOG; GOAL_LAT=$GL nohup bash /tmp/job254_s4run.sh $NAME $D $BX $BY $TOL > $LOG 2>&1 & echo started_pid \$!"
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
