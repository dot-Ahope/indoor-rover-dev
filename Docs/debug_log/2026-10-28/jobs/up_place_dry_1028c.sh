#!/bin/bash
# (PC·WSL) §8 수정한 place_server(거절에 방향 기록)를 Jetson src 에 올리고 dry_run 정지 시험 — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함). 로버 안 움직임
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
J=jetson@192.168.0.110; T=/home/jetson/ros2_ws/src/rover_navigation
for f in place_server.py place_cmd.py path_end_yaw.py; do sed 's/\r$//' $N/f25_$f > /tmp/$f; sshpass -p "$PW" scp $O /tmp/$f $J:$T/scripts/$f; done
sed 's/\r$//' $N/f25_places.yaml > /tmp/places.yaml; sshpass -p "$PW" scp $O /tmp/places.yaml $J:$T/config/places.yaml
sed 's/\r$//' $N/f25_CMakeLists.txt > /tmp/CMakeLists.txt; sshpass -p "$PW" scp $O /tmp/CMakeLists.txt $J:$T/CMakeLists.txt
sshpass -p "$PW" ssh $O $J "chmod +x $T/scripts/place_*.py $T/scripts/path_end_yaw.py; cd $T && git hash-object scripts/place_server.py scripts/place_cmd.py scripts/path_end_yaw.py config/places.yaml CMakeLists.txt | cut -c1-10 | tr '\n' ' '"; echo
JX_TIMEOUT=600 JX_WHY='F2.5 place_server 통로 북쪽 거절 재현 dry_run(10-28 §8, 로버 안 움직임)' bash $N/run_jn.sh chk_place_dry_1028c.sh
