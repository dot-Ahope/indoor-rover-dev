#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
for f in depth_relay.py camera.launch.py; do tr -d '\r' < $SPS/$f > /tmp/$f; done
sshpass -p <PW> scp $OPT -q /tmp/depth_relay.py $J:~/ros2_ws/src/rover_bringup/scripts/depth_relay.py || exit 1
sshpass -p <PW> scp $OPT -q /tmp/camera.launch.py $J:~/ros2_ws/src/rover_bringup/launch/camera.launch.py || exit 1
sshpass -p <PW> ssh $OPT $J "python3 -m py_compile ~/ros2_ws/src/rover_bringup/scripts/depth_relay.py && echo '원격 컴파일 OK'"
echo "=== 1. 재기동 (릴레이 새 버전, launch 파라미터) ==="; bash $SPS/run_j.sh job240_clean.sh 15 2>&1 | grep -aE '에이전트|세션|중복|자세:|상자:|근거 없는 셀 위치|최소폭'
echo "=== 2. 릴레이 정리 + 로그 ==="; bash $SPS/run_j.sh job314_relay_orphan.sh 2>&1 | grep -aE '남은 릴레이|발행자'
sshpass -p <PW> ssh $OPT $J "sleep 12; grep -a '프레임:' /tmp/sensors.log | tail -1 | cut -c1-200"
echo "=== 3. 상자 앞 점 (필터 후 60 s) ==="
BXF=$(awk "BEGIN{print $1-0.30}")
timeout 200 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; python3 -u /tmp/job320_boxfront.py $1 $2 60 2>&1 | grep -av '^\[INFO\]'; echo '--- 로컬 코스트맵 상자 앞(x-0.30) 셀 최대 y ---'; python3 /tmp/job315_boxcells.py $BXF $2 2>&1 | tail -1; echo '--- 상자 본체 (job312 12 s) ---'; TOPIC=/camera/depth/points_filtered ZTH=0.08 python3 /tmp/job312_box_edge.py $1 $2 12 2>&1 | grep -aE '^  (핵심|좌측|앞쪽)|코스트맵'"
