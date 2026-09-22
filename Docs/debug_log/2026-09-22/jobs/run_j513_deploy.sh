#!/bin/bash
# N6-0 배포·검증 러너(PC, 2026-09-22): rover_navigation 의 launch/·scripts/·config/nvblox_local.yaml·CMakeLists 를 Jetson 소스에 넣고 colcon 빌드 → 검증 시나리오 V1~V5
#   V1 camera_layer 기본(nvblox): Nav2 재기동 40 s 안에 nvblox_node 1 개·plugins nvblox·게이트 J 통과(/tmp/nvblox_node.log)
#   V2 launch 종료(job488 의 pkill) → 컨테이너 안 nvblox_node 0 개(래퍼 정리)
#   V3 camera_layer:=stvl → plugins stvl·nvblox_node 0
#   V4 docker stop 컨테이너 → nvblox 모드 재기동 → 래퍼가 docker start 로 복구·노드 기동(재부팅 상태 모사)
#   V5 job240(prep) 재기동 → nvblox_node PID 가 바뀜(EKF 재기동 뒤 자동 재시작)
H=${JETSON_HOST:-192.168.0.101}; REPO=/mnt/f/6_Indoor_Rover/Rover; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
PKG=$REPO/ros2_ws/src/rover_navigation; [ -d "$PKG" ] || PKG=$NSPS/rover_navigation_src
mkdir -p /tmp/x513/launch /tmp/x513/scripts /tmp/x513/config
for f in launch/navigation.launch.py launch/nvblox.launch.py scripts/nvblox_up.sh config/nvblox_local.yaml CMakeLists.txt; do tr -d '\r' < $PKG/$f > /tmp/x513/$f || exit 1; done
for f in job488_layer_ab.sh job505_modeN_gate.sh job513_verify.sh; do tr -d '\r' < $NSPS/$f > /tmp/$f; done
sshpass -p <PW> ssh $O jetson@$H "mkdir -p ~/ros2_ws/src/rover_navigation/scripts" || exit 1
sshpass -p <PW> scp $O -q /tmp/x513/launch/*.py jetson@$H:~/ros2_ws/src/rover_navigation/launch/ && sshpass -p <PW> scp $O -q /tmp/x513/scripts/nvblox_up.sh jetson@$H:~/ros2_ws/src/rover_navigation/scripts/ && sshpass -p <PW> scp $O -q /tmp/x513/config/nvblox_local.yaml jetson@$H:~/ros2_ws/src/rover_navigation/config/ && sshpass -p <PW> scp $O -q /tmp/x513/CMakeLists.txt jetson@$H:~/ros2_ws/src/rover_navigation/ && sshpass -p <PW> scp $O -q /tmp/job488_layer_ab.sh /tmp/job505_modeN_gate.sh /tmp/job513_verify.sh jetson@$H:/tmp/ || { echo "전송 실패"; exit 1; }
echo "전송 OK"
timeout 560 sshpass -p <PW> ssh $O jetson@$H "export TERM=xterm; bash /tmp/job513_verify.sh ${1:-all}"
