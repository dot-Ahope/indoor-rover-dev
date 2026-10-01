#!/bin/bash
# F0 PC 러너: Jetson 에 파일 전송(재시도 3) → job551 을 setsid nohup 으로 기동 → 로그 폴링(끊겨도 주행은 계속) → 끝나면 산출물 회수
# 인자: NAME "GOALS" [SPEED] [PAUSE]   환경: STAGE NOTE GIT_HEAD BAG_PROFILE JETSON_HOST
NAME=$1; GOALS=$2; SPEED=${3:-0.07}; PAUSE=${4:-0}; H=${JETSON_HOST:-192.168.0.101}
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad; OLD=$N/rescued_jetson_tmp   # 09-28: 옛 82ce61d4 폴더 소실 → Jetson 에서 회수한 사본
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8 -o ServerAliveInterval=3 -o ServerAliveCountMax=3"
mkdir -p /tmp/xf0; for f in job550_f0run.py job551_f0drive.sh job613_pathyaw.py; do tr -d '\r' < $N/$f > /tmp/xf0/$f; done
for f in job386_slamalive.py job440_startclear.py job451_paramsnap.py job453_runmeta.sh; do tr -d '\r' < $OLD/$f > /tmp/xf0/$f; done
for t in 1 2 3; do sshpass -p <PW> scp $O -q /tmp/xf0/* jetson@$H:/tmp/ && break; echo "전송 재시도 $t"; sleep 5; done || { echo 전송 실패; exit 1; }
sshpass -p <PW> ssh $O jetson@$H "cd /tmp; STAGE='$STAGE' NOTE='$NOTE' GIT_HEAD='$GIT_HEAD' BAG_PROFILE='$BAG_PROFILE' setsid nohup bash /tmp/job551_f0drive.sh $NAME '$GOALS' $SPEED $PAUSE > /tmp/f0_$NAME.log 2>&1 < /dev/null & mkdir -p /tmp/live; { echo; echo \"===== \$(date '+%F %T') 시작 | F0 주행 $NAME 목표 $GOALS 속도 $SPEED 정지 $PAUSE (job551→job550) — 원문 /tmp/f0_$NAME.log\"; } >> /tmp/live/current.log; setsid nohup timeout 1200 tail -n +1 -F /tmp/f0_$NAME.log >> /tmp/live/current.log 2>/dev/null < /dev/null & echo started" || { echo 기동 실패; exit 1; }
L=0; for i in $(seq 1 900); do sleep 2
  OUT=$(sshpass -p <PW> ssh $O jetson@$H "tail -n +$((L+1)) /tmp/f0_$NAME.log" 2>/dev/null) || continue
  [ -n "$OUT" ] && { echo "$OUT"; L=$((L + $(echo "$OUT" | wc -l))); }
  echo "$OUT" | grep -aqE "=== 끝|주행하지 않음" && break
done
mkdir -p $N/f0_$NAME; for f in f0_$NAME.log $NAME.csv tegra_$NAME.log top_$NAME.log rss_$NAME.txt proc_$NAME.log bag_$NAME.tgz; do sshpass -p <PW> scp $O -q jetson@$H:/tmp/$f $N/f0_$NAME/ 2>/dev/null && echo "회수 $f"; done
