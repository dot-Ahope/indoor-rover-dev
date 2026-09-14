#!/bin/bash
# 주행 bag 에피소드 분석: NAME LOGT(이 시각 이후의 nav2.log 충돌만) [START x y yaw_deg]
NAME=${1:-inf2}; LOGT=${2:-0}; SX=${3:-0.0}; SY=${4:-0.0}; SYAW=${5:-0.0}
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
for f in job303_bagstall.py job304_lethal_audit.py job305_ghost_stats.py; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $OPT -q /tmp/$f $J:/tmp/$f || exit 1; done
cat > /tmp/epi_remote.sh <<'REMOTE_END'
NAME=$1; LOGT=$2; SX=$3; SY=$4; SYAW=$5
source /opt/ros/humble/setup.bash
T0=$(python3 - <<'PY'
import sys, rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
import os
r=rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri='/tmp/bag_'+os.environ['NAME'],storage_id='sqlite3'),rosbag2_py.ConverterOptions('',''))
while r.has_next():
    topic,data,ts=r.read_next()
    if topic=='/tf':
        for tr in deserialize_message(data,TFMessage).transforms:
            if tr.header.frame_id=='odom': print('%.2f'%(tr.header.stamp.sec+tr.header.stamp.nanosec*1e-9)); raise SystemExit
PY
)
echo "bag 첫 odom T0=$T0"
COLL=$(grep -a 'detected collision' /tmp/nav2.log | grep -aoE '\[[0-9]{10}\.[0-9]+\]' | tr -d '[]' | awk -v lt=$LOGT '$1>lt' | awk 'BEGIN{last=-99} {if ($1-last>3.0) print $1; last=$1}')
echo "충돌 에피소드: $COLL"
for T in $COLL; do
  echo "=== 에피소드 T=$T (bag +$(python3 -c "print('%.1f'%($T-$T0))") s) ==="
  python3 /tmp/job303_bagstall.py /tmp/bag_$NAME $T $SX $SY $SYAW 2>&1 | grep -av 'Opened database' | grep -avE '^bag |^첫 충돌'
done
FIRST=$(echo $COLL | awk '{print $1}')
echo "=== 첫 에피소드 LETHAL 군집 (로컬, 로버 1.0 m 이내만) ==="
python3 /tmp/job304_lethal_audit.py /tmp/bag_$NAME $FIRST $SX $SY $SYAW 2>&1 | grep -av 'Opened database' | grep -avE '^bag 토픽' | sed -n '/^LETHAL/,/^시작프레임 지도/p' | awk '$0 ~ /^ +[0-9]+ / {if ($(NF-3)+0 <= 1.0) print; next} {print}' | head -24
echo "=== 신규 LETHAL 통계 (job305) — 카메라 거리 0.3~0.4 m 대역이 근거리 아티팩트 ==="
python3 /tmp/job305_ghost_stats.py /tmp/bag_$NAME 2>&1 | grep -av 'Opened database' | sed -n '/^신규 LETHAL/,/전방 시야/p'
python3 /tmp/job305_ghost_stats.py /tmp/bag_$NAME 2>&1 | grep -aE '카메라 0\.3[0-9] m' | head -20
REMOTE_END
sshpass -p <PW> scp $OPT -q /tmp/epi_remote.sh $J:/tmp/epi_remote.sh
timeout 500 sshpass -p <PW> ssh $OPT $J "NAME=$NAME bash /tmp/epi_remote.sh $NAME $LOGT $SX $SY $SYAW"
