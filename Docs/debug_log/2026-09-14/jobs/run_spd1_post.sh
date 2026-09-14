#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
bash $SPS/run_post.sh spd1 2>&1 | grep -avE '^\(|^    |^\[INFO\]'
bash $SPS/run_epi.sh spd1 1789355610 0.0 0.0 2.0 2>&1 | grep -avE '^\[INFO\]' | sed -n '1,/^=== 신규 LETHAL/p' | grep -avE '^    (idx|없음|\(대조\))'
echo "=== 주행 시작 시점(bag +11 s) 로컬 LETHAL 군집 — 통로(횡 +0.15~+0.65, 전진 0.6~1.5) 안의 것 ==="
timeout 200 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; T0=\$(python3 -c \"
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
r=rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri='/tmp/bag_spd1',storage_id='sqlite3'),rosbag2_py.ConverterOptions('',''))
while r.has_next():
    t,d,ts=r.read_next()
    if t=='/tf':
        for tr in deserialize_message(d,TFMessage).transforms:
            if tr.header.frame_id=='odom': print('%.2f'%(tr.header.stamp.sec+tr.header.stamp.nanosec*1e-9)); raise SystemExit
\"); for DT in 11 20; do echo \"--- bag +\$DT s ---\"; python3 /tmp/job304_lethal_audit.py /tmp/bag_spd1 \$(python3 -c \"print(\$T0+\$DT)\") 0.0 0.0 2.0 2>&1 | grep -av 'Opened database' | sed -n '/^   #/,/^시작프레임 지도/p' | awk '\$0 ~ /^ +[0-9]+ / {split(\$0,a,\"[(),]\"); fx=a[2]+0; fy=a[3]+0; if (fx>=0.6 && fx<=1.5 && fy>=0.15 && fy<=0.65) print \"  통로 안:\" \$0; next}'; done"
echo "=== spd1.csv 속도 프로파일 ==="
PYTHONUTF8=1 python - "$SPS/spd1.csv" <<'PY'
import csv, sys
R = [r for r in csv.DictReader(open(sys.argv[1], encoding='utf-8'))]
last = -1
for r in R:
    t = float(r['t'])
    if int(t) != last:
        last = int(t)
        print('  %5.1f  전진 %+.3f 횡 %+.3f  계획횡 %s  v %+.3f w %+.3f  lc %3s gc %3s' % (t, float(r['fwd']), float(r['lat']), r['plan_lat_at_box'][:6], float(r['v']), float(r['w']), r['lc_box'], r['gc_box']))
v = [float(r['v']) for r in R if 0.6 <= float(r['fwd']) <= 0.85 and float(r['v']) > 0.005]
if v: print('  전진 0.6~0.85 구간 움직일 때 v 중앙 %.3f, ≥0.07 비율 %.0f%%' % (sorted(v)[len(v)//2], 100*sum(1 for x in v if x>=0.07)/len(v)))
PY
