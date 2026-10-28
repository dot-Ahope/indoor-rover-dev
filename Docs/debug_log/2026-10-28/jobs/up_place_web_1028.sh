#!/bin/bash
# (PC·WSL) §16 place_web 올리기 + Jetson 확인 실행 + PC(ALOPS)에서 8080 접속 확인. 비밀번호는 run_jn.sh 에서 읽음(출력 안 함) · 키도 출력 안 함. 로버 안 움직임
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
J=jetson@192.168.0.110; T=/home/jetson/ros2_ws/src/rover_navigation
for f in place_server.py place_cmd.py path_end_yaw.py place_web.py; do sed 's/\r$//' $N/f25_$f > /tmp/$f; sshpass -p "$PW" scp $O /tmp/$f $J:$T/scripts/$f; done
sed 's/\r$//' $N/f25_places.yaml > /tmp/places.yaml; sshpass -p "$PW" scp $O /tmp/places.yaml $J:$T/config/places.yaml
sed 's/\r$//' $N/f25_CMakeLists.txt > /tmp/CMakeLists.txt; sshpass -p "$PW" scp $O /tmp/CMakeLists.txt $J:$T/CMakeLists.txt
JX_TIMEOUT=200 JX_WHY='F2.5 휴대폰 웹 창구 place_web 확인(10-28 §16, dry_run — 로버 안 움직임)' bash $N/run_jn.sh chk_place_web_1028.sh &
R=$!; sleep 35
K=$(sshpass -p "$PW" ssh $O $J "cat ~/.config/rover_web/key")
echo "== PC(WSL)→Jetson:8080 키 있음 → $(curl -s -m 5 -o /dev/null -w '%{http_code} %{time_total}s' "http://192.168.0.110:8080/?k=$K")"
echo "== PC→state → $(curl -s -m 5 -H "X-Rover-Key: $K" 'http://192.168.0.110:8080/api/state?after=999' | head -c 80)"
wait $R
