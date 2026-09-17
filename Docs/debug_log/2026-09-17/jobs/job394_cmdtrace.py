#!/usr/bin/env python3
"""mp8 목표 앞 정지 구간: /cmd_vel 발행 간격·값 분포, /wheel_odom 속도, /rover/status, /odometry/filtered 속도 (goal 기준 초)"""
import sys, collections, rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
BAG = sys.argv[1]; G = float(sys.argv[2])
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
want = ['/cmd_vel', '/wheel_odom', '/odometry/filtered', '/rover/status']
D = collections.defaultdict(list)
while r.has_next():
    topic, data, ts = r.read_next()
    if topic in want:
        D[topic].append((ts * 1e-9 - G, deserialize_message(data, get_message(types[topic]))))
for tpc in want:
    print('%s: %d 메시지 (%s)' % (tpc, len(D[tpc]), types.get(tpc)))
def win(lst, a, b): return [(t, m) for t, m in lst if a <= t < b]
for a, b in ((25, 35), (35, 40), (40, 50), (60, 62), (80, 90)):
    c = win(D['/cmd_vel'], a, b)
    if c:
        dts = [c[i][0] - c[i-1][0] for i in range(1, len(c))]
        vals = collections.Counter((round(m.linear.x, 4), round(m.angular.z, 4)) for _, m in c)
        print('  cmd %d~%d s: %d 개, 간격 최대 %.2f s, 값 상위 %s' % (a, b, len(c), max(dts) if dts else 0, vals.most_common(4)))
    w = win(D['/wheel_odom'], a, b)
    if w:
        vs = [m.twist.twist.linear.x for _, m in w]; ws = [m.twist.twist.angular.z for _, m in w]
        print('  wheel_odom %d~%d s: v 평균 %+.4f 최대 %+.4f, w 평균 %+.4f' % (a, b, sum(vs)/len(vs), max(vs, key=abs), sum(ws)/len(ws)))
    s = win(D['/rover/status'], a, b)
    if s:
        m = s[-1][1]
        print('  status %d~%d s 마지막: %s' % (a, b, str(m)[:260]))
