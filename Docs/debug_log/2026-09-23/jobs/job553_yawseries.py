#!/usr/bin/env python3
"""목표 도달 전후 yaw 시계열 (09-23): map yaw·EKF yaw·지령 ω 를 'Reached the goal' 전 6 s ~ 후 3 s, 0.5 s 간격으로."""
import sys, math, bisect
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def uw(a): return (a + math.pi) % (2 * math.pi) - math.pi
EP = {'n62a': 1790127364.308, 'n62b': 1790133879.538, 'n62c': 1790135117.662}
for BAG in sys.argv[1:]:
    r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
    types = {t.name: t.type for t in r.get_all_topics_and_types()}
    mo, ob, cmd = [], [], []
    while r.has_next():
        tp, data, ts = r.read_next()
        if tp not in ('/tf', '/cmd_vel'): continue
        m = deserialize_message(data, get_message(types[tp])); t = ts * 1e-9
        if tp == '/tf':
            for tr in m.transforms:
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append((t, yaw(tr.transform.rotation)))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append((t, yaw(tr.transform.rotation), tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9))
        else: cmd.append((t, m.linear.x, m.angular.z))
    def at(arr, t, i=1):
        k = bisect.bisect_left([x[0] for x in arr], t); return arr[min(max(k, 0), len(arr) - 1)][i]
    t1 = EP[BAG.split('_')[-1]]
    print('%s  (bag 수신시각 − odom stamp 지연 at t1 = %.3f s)' % (BAG, t1 - at(ob, t1, 2)))
    for d in [x * 0.5 for x in range(-12, 7)]:
        t = t1 + d
        print('  %+5.1f s  map %+7.2f°  EKF %+7.2f°  map→odom %+6.2f°  지령 v %+.3f ω %+.3f' % (d, math.degrees(uw(at(mo, t) + at(ob, t))), math.degrees(at(ob, t)), math.degrees(at(mo, t)), at(cmd, t), at(cmd, t, 2)))
