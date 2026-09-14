#!/bin/bash
# Nav2 복귀(bag) → 출발 heading 정렬 → 자세·상자 재검출.  인자: NAME X Y YAW_deg FACE_deg
NAME=${1:-inf2_ret}; X=${2:-0.0}; Y=${3:-0.0}; YAW=${4:-175.6}; FACE=${5:--4.4}
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
for f in job288_return_bag.sh job207_return.py job225_face.py; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $OPT -q /tmp/$f $J:/tmp/$f || exit 1; done
echo "=== Nav2 복귀 $NAME → ($X, $Y, $YAW°) ==="
timeout 400 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; bash /tmp/job288_return_bag.sh $NAME $X $Y $YAW 2>&1 | tail -25"
echo "=== heading 정렬 $FACE° ==="
timeout 120 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; python3 /tmp/job225_face.py $FACE 1.5 2>&1 | tail -3; sleep 3; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE 'Translation|RPY' | head -2; BOX_HINT='1.13 -0.04' python3 /tmp/job248_audit.py 2>&1 | grep -aE '^상자:'"
