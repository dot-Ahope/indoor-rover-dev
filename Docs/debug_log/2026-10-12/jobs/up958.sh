#!/bin/bash
# 10-12 §3.2: navigation.launch(지도 서버 관리 노드 3 s 지연) 배포·빌드 + 확인 스크립트 전송
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad; J=jetson@192.168.0.101
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
tr -d '\r' < $N/job956_gcmchk.py > /tmp/job956_gcmchk.py
sshpass -p $PW scp $O -q $N/up958_nav.py $J:/home/jetson/ros2_ws/src/rover_navigation/launch/navigation.launch.py && sshpass -p $PW scp $O -q /tmp/job956_gcmchk.py $J:/tmp/ || exit 1
sshpass -p $PW ssh $O $J "cd ~/ros2_ws && source /opt/ros/humble/setup.bash && colcon build --packages-select rover_navigation 2>&1 | tail -1; grep -c navmap_ensure install/rover_navigation/share/rover_navigation/launch/navigation.launch.py"
