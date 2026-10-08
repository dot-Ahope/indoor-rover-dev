#!/bin/bash
# 비율 시험 PC 러너(10-08 §5, 09-28 run_spin.sh 기반): 전송(재시도 3) → job941 을 setsid nohup 으로 기동 → 로그 폴링 → 산출물 회수
#   인자: NAME PLAN [REPS]   환경: STAGE NOTE GIT_HEAD JETSON_HOST JX_WHY
#   비밀번호는 이 파일에 쓰지 않고 run_jn.sh 에서 읽는다(커밋 사본에 남지 않게).
NAME=$1; PLAN=$2; REPS=${3:-4}; H=${JETSON_HOST:-192.168.0.101}
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad; OLD=$N/rescued_jetson_tmp
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}')
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8 -o ServerAliveInterval=3 -o ServerAliveCountMax=3"
rm -rf /tmp/xr0; mkdir -p /tmp/xr0; for f in job940_ratio.py job941_ratiodrive.sh; do tr -d '\r' < $N/$f > /tmp/xr0/$f; done
for f in job386_slamalive.py job451_paramsnap.py job453_runmeta.sh; do tr -d '\r' < $OLD/$f > /tmp/xr0/$f; done
for t in 1 2 3; do sshpass -p $PW scp $O -q /tmp/xr0/* jetson@$H:/tmp/ && break; echo "전송 재시도 $t"; sleep 5; done || { echo 전송 실패; exit 1; }
sshpass -p $PW ssh $O jetson@$H "cd /tmp; mkdir -p /tmp/live; echo \"===== \$(date '+%F %T') 시작 | job941 $NAME | ${JX_WHY:-(목적 미기재)}\" >> /tmp/live/current.log; STAGE='$STAGE' NOTE='$NOTE' GIT_HEAD='$GIT_HEAD' setsid nohup bash -c \"bash /tmp/job941_ratiodrive.sh $NAME '$PLAN' $REPS 2>&1 | tee -a /tmp/live/current.log > /tmp/ratio_$NAME.log\" < /dev/null > /dev/null 2>&1 & echo started" || { echo 기동 실패; exit 1; }
L=0; for i in $(seq 1 900); do sleep 2
  OUT=$(sshpass -p $PW ssh $O jetson@$H "tail -n +$((L+1)) /tmp/ratio_$NAME.log" 2>/dev/null) || continue
  [ -n "$OUT" ] && { echo "$OUT"; L=$((L + $(echo "$OUT" | wc -l))); }
  echo "$OUT" | grep -aqE "=== 끝|주행하지 않음" && break
done
mkdir -p $N/ratio_$NAME; for f in ratio_$NAME.log $NAME.csv top_$NAME.log bag_$NAME.tgz; do sshpass -p $PW scp $O -q jetson@$H:/tmp/$f $N/ratio_$NAME/ 2>/dev/null && echo "회수 $f"; done
