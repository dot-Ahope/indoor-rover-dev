#!/usr/bin/env python3
"""목표 도착 뒤 최종 heading 확인 (09-23): bag 끝(목표 도달 시점)의 map yaw·EKF(odom) yaw 와 출발 yaw 의 차, 그리고 라이다 스캔 상관으로 잰 출발→도착 실제 회전.
  목표 yaw = 출발 yaw(0°). 음수 = 오른쪽. 인자: BAG [BAG ...]"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def uw(a): return (a + math.pi) % (2 * math.pi) - math.pi
EP = {'n62a': (1790127332.547, 1790127364.308), 'n62b': (1790133846.347, 1790133879.538), 'n62c': (1790135085.346, 1790135117.662)}   # Begin navigating / Reached the goal (nav2 로그)
for BAG in sys.argv[1:]:
    r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
    types = {t.name: t.type for t in r.get_all_topics_and_types()}
    mo, ob, sc, cmd = [], [], [], []
    while r.has_next():
        tp, data, ts = r.read_next()
        if tp not in ('/tf', '/scan', '/cmd_vel'): continue
        m = deserialize_message(data, get_message(types[tp])); t = ts * 1e-9
        if tp == '/tf':
            for tr in m.transforms:
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append((t, yaw(tr.transform.rotation)))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append((t, yaw(tr.transform.rotation)))
        elif tp == '/cmd_vel': cmd.append((t, m.linear.x, m.angular.z))
        else:
            a = m.angle_min + np.arange(len(m.ranges)) * m.angle_increment; rr = np.asarray(m.ranges, dtype=float); ok = np.isfinite(rr) & (rr > 0.15) & (rr < 12)
            grid = np.arange(-math.pi, math.pi, math.radians(0.25)); sc.append((t, np.interp(grid, a[ok], rr[ok], period=2 * math.pi)))
    t0, t1 = EP[BAG.split('_')[-1]]
    def at(arr, t):
        k = bisect.bisect_left([x[0] for x in arr], t); return arr[min(max(k, 0), len(arr) - 1)][1]
    e0, e1 = at(ob, t0), at(ob, t1); m0, m1 = uw(at(mo, t0) + e0), uw(at(mo, t1) + e1)
    after = [(math.degrees(uw(uw(at(mo, t1 + d) + at(ob, t1 + d)) - m0))) for d in (0.5, 1.0, 2.0)]
    print('%s: "Reached the goal" 순간 heading 오차(목표 = 출발 map yaw, +왼쪽) — SLAM(map) %+.2f° | EKF(odom) %+.2f° | 도착 뒤 0.5/1/2 s map %s | 허용 ±8.6°' % (BAG.split('/')[-1], math.degrees(uw(m1 - m0)), math.degrees(uw(e1 - e0)), ' / '.join('%+.2f' % a for a in after)))
