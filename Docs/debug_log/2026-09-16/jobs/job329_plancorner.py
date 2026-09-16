#!/usr/bin/env python3
"""/plan 의 헤딩 프로파일: 지정 bag 시각의 최신 계획을 로버 최근접점부터 0.05 m 마다 (x, y, 진행방향°, 로버 yaw 대비 상대각) 출력"""
import sys, math, bisect
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import Path
BAG = sys.argv[1]; TS = [float(x) for x in sys.argv[2].split(',')]
def yaw_of(q): return math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
def wrap(a): return (a+math.pi)%(2*math.pi)-math.pi
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('',''))
mo, ob, plans = [], [], []
while r.has_next():
    topic, data, ts = r.read_next(); t = ts*1e-9
    if topic == '/tf':
        for tr in deserialize_message(data, TFMessage).transforms:
            tt = tr.header.stamp.sec + tr.header.stamp.nanosec*1e-9
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append((tt, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append((tt, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
    elif topic == '/plan': plans.append((t, deserialize_message(data, Path)))
mo.sort(); ob.sort(); T0 = ob[0][0]
def latest(seq, t):
    ts = [s[0] for s in seq]; i = bisect.bisect_right(ts, t)-1; return seq[i] if i >= 0 else None
for at in TS:
    t = T0+at; a = latest(mo, t); b = latest(ob, t); pl = latest(plans, t)
    X = a[1]+b[1]*math.cos(a[3])-b[2]*math.sin(a[3]); Y = a[2]+b[1]*math.sin(a[3])+b[2]*math.cos(a[3]); yaw = wrap(a[3]+b[3])
    pts = [(q.pose.position.x, q.pose.position.y) for q in pl[1].poses]
    d = [math.hypot(x-X, y-Y) for x, y in pts]; i0 = min(range(len(pts)), key=lambda k: d[k])
    print('=== t=%.1f 계획(%.1f s 전 발행, %d점, 점간격 %.3f m) 로버 (%.3f,%.3f) yaw %+.1f° 최근접 idx %d dist %.3f ===' % (at, t-pl[0], len(pts), math.hypot(pts[1][0]-pts[0][0], pts[1][1]-pts[0][1]) if len(pts) > 1 else 0, X, Y, math.degrees(yaw), i0, d[i0]))
    acc = 0.0; nxt = 0.0; out = []
    for k in range(i0, len(pts)-1):
        if acc >= nxt:
            j = min(k+3, len(pts)-1); h = math.atan2(pts[j][1]-pts[k][1], pts[j][0]-pts[k][0])
            out.append('  s=%.2f (%.3f,%.3f) 방향 %+5.1f° 상대 %+5.1f°' % (acc, pts[k][0], pts[k][1], math.degrees(h), math.degrees(wrap(h-yaw)))); nxt += 0.05
        acc += math.hypot(pts[k+1][0]-pts[k][0], pts[k+1][1]-pts[k][1])
        if acc > 0.85: break
    print('\n'.join(out))
