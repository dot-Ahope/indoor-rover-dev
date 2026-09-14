#!/bin/bash
# 주행 중 코스트맵 상자 군집의 시간 변화: bag 의 여러 시각에 job304 를 돌려 상자 행(전진 0.9~1.6, 횡 -0.4~+0.4 중심)만 뽑는다
NAME=${1:-sm1}
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
timeout 400 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; T0=\$(python3 - <<'PY'
import rosbag2_py, os
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
r=rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri='/tmp/bag_$NAME',storage_id='sqlite3'),rosbag2_py.ConverterOptions('',''))
while r.has_next():
    t,d,ts=r.read_next()
    if t=='/tf':
        for tr in deserialize_message(d,TFMessage).transforms:
            if tr.header.frame_id=='odom': print('%.2f'%(tr.header.stamp.sec+tr.header.stamp.nanosec*1e-9)); raise SystemExit
PY
); echo \"bag_$NAME T0=\$T0\"; echo '  bag시각  로버(전진,횡,yaw)  | 상자 군집: 셀수  횡범위  전진범위'; for DT in 2 8 12 15 18 22; do T=\$(python3 -c \"print(\$T0+\$DT)\"); python3 /tmp/job304_lethal_audit.py /tmp/bag_$NAME \$T 0.0 0.0 0.0 2>&1 | grep -av 'Opened database' | awk -v dt=\$DT 'BEGIN{p=\"\"} /^로버 odom 자세/ {p=\$0} /^ +[0-9]+ +[0-9]+ +\(/ {split(\$0,a,\"[(),]\"); fx=a[2]+0; fy=a[3]+0; if (fx>0.9 && fx<1.7 && fy>-0.4 && fy<0.4) print \"  +\" dt \"s  \" p \"  |  \" \$0}' | head -3; done"
