#!/bin/bash
# (PC·WSL) §7 S1 파일 전송 · Jetson 에서 독립 실행 시작 · 끝날 때까지 로그 따라보기 · 회수. 비밀번호는 run_jn.sh 에서 읽음(출력 안 함)
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
J=jetson@192.168.0.110; T=/home/jetson/ros2_ws/src/rover_navigation; NAME=${1:-f2pl1}; PLAN=${2:-full}   # §8 PLAN = full | fromC
for f in place_server.py place_cmd.py path_end_yaw.py; do sed 's/\r$//' $N/f25_$f > /tmp/$f; sshpass -p "$PW" scp $O /tmp/$f $J:$T/scripts/$f; done
sed 's/\r$//' $N/f25_places.yaml > /tmp/places.yaml; sshpass -p "$PW" scp $O /tmp/places.yaml $J:$T/config/places.yaml
sed 's/\r$//' $N/run_place_s1_1028.sh > /tmp/run_place_s1_1028.sh; sshpass -p "$PW" scp $O /tmp/run_place_s1_1028.sh $J:/tmp/
sshpass -p "$PW" ssh $O $J "cd $T && git hash-object scripts/place_server.py scripts/place_cmd.py config/places.yaml | cut -c1-10 | tr '\n' ' '; echo; setsid nohup bash /tmp/run_place_s1_1028.sh $NAME $PLAN > /tmp/place_s1.log 2>&1 < /dev/null & echo 시작됨"
L=0; for i in $(seq 1 600); do sleep 3
  OUT=$(sshpass -p "$PW" ssh $O $J "tail -n +$((L+1)) /tmp/place_s1.log" 2>/dev/null) || continue
  [ -n "$OUT" ] && { echo "$OUT"; L=$((L + $(echo "$OUT" | wc -l))); }
  echo "$OUT" | grep -aq "=== 끝\|주행하지 않음" && break; done
mkdir -p $N/s1_$NAME; for f in place_s1.log place_server_s1.log tegra_$NAME.log bag_$NAME.tgz; do sshpass -p "$PW" scp $O -q $J:/tmp/$f $N/s1_$NAME/ && echo "회수 $f"; done
for f in nav2 slam sensors; do sshpass -p "$PW" scp $O -q $J:/tmp/$f.log $N/s1_$NAME/ && echo "회수 $f.log"; done
