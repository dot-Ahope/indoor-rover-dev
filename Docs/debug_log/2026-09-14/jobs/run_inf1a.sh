#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
for f in job303_bagstall.py job304_lethal_audit.py job310_bodyfixed.py; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $OPT -q /tmp/$f $J:/tmp/$f || exit 1; done
cat > /tmp/inf1a_remote.sh <<'REMOTE_END'
source /opt/ros/humble/setup.bash
echo "=== nav2.log inf1 구간: 충돌·복구 시각 ==="
grep -aE 'detected collision|Running backup|Running wait|backup failed|Goal succeeded|Received request to clear' /tmp/nav2.log | grep -aoE '\[[0-9]{10}\.[0-9]+\] \[[a-z_.]+\]: .{0,70}' | awk -F'[][]' '$2>1789346110' | sed 's/\.[0-9]\{6\}\]/]/' | uniq -c | head -40
T0=$(python3 - <<'PY'
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
r=rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri='/tmp/bag_inf1',storage_id='sqlite3'),rosbag2_py.ConverterOptions('',''))
while r.has_next():
    topic,data,ts=r.read_next()
    if topic=='/tf':
        for tr in deserialize_message(data,TFMessage).transforms:
            if tr.header.frame_id=='odom': print('%.2f'%(tr.header.stamp.sec+tr.header.stamp.nanosec*1e-9)); raise SystemExit
PY
)
echo "bag 첫 odom 시각 T0=$T0"
COLL=$(grep -a 'detected collision' /tmp/nav2.log | grep -aoE '\[[0-9]{10}\.[0-9]+\]' | tr -d '[]' | awk '$1>1789346110' | awk -v t0=$T0 'BEGIN{last=-99} {if ($1-last>3.0) print $1; last=$1}')
echo "충돌 에피소드 시각: $COLL"
for T in $COLL; do
  echo "=== 에피소드 T=$T (bag +$(python3 -c "print('%.1f'%($T-$T0))") s) ==="
  python3 /tmp/job303_bagstall.py /tmp/bag_inf1 $T 0.0 0.0 0.5 2>&1 | grep -av 'Opened database' | grep -avE '^bag |^첫 충돌'
done
FIRST=$(echo $COLL | awk '{print $1}')
echo "=== 첫 에피소드 LETHAL 군집 (로컬) ==="
python3 /tmp/job304_lethal_audit.py /tmp/bag_inf1 $FIRST 0.0 0.0 0.5 2>&1 | grep -av 'Opened database' | grep -avE '^bag 토픽' | sed -n '1,/^시작프레임 지도/p' | head -30
echo "=== 차체 고정 LETHAL 마킹 (job310 2부) ==="
python3 /tmp/job310_bodyfixed.py /tmp/bag_inf1 2>&1 | grep -av 'Opened database' | sed -n '/^(1)/,$p' | grep -avE '^    (idx|없음)'
REMOTE_END
sshpass -p <PW> scp $OPT -q /tmp/inf1a_remote.sh $J:/tmp/inf1a_remote.sh
timeout 500 sshpass -p <PW> ssh $OPT $J "bash /tmp/inf1a_remote.sh"
