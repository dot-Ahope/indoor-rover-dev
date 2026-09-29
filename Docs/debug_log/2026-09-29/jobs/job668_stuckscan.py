#!/usr/bin/env python3
"""09-29 §13 G3: bag 에 남은 stuck_monitor 판정(/rover/stuck, 판정 때만 발행) 전수 조사.
   판정마다: 시각(첫 지령 기준), 메시지(지령 vs 관측), map 위치·방향, 직전 2 s 지령 평균 v·ω,
   그리고 **실제로 움직였나** = 같은 2 s 동안 map 이동(cm)·회전(°) — SLAM 포즈(= 스캔 정합 기반) 기준.
   stuck_monitor 코드는 09-18 이후 그대로라 09-23~29 bag 의 판정 = 현재 코드의 판정.
   인자: BAG [BAG ...]"""
import sys, math, bisect
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def load(bag):
    r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
    types = {t.name: t.type for t in r.get_all_topics_and_types()}
    st, cmd, mo, ob = [], [], [], []
    while r.has_next():
        tp, data, ts = r.read_next(); t = ts * 1e-9
        if tp not in ('/rover/stuck', '/cmd_vel', '/tf'): continue
        m = deserialize_message(data, get_message(types[tp]))
        if tp == '/rover/stuck':
            for s in m.status: st.append((t, s.level[0] if isinstance(s.level, (bytes, bytearray)) else int(s.level), s.message))
        elif tp == '/cmd_vel': cmd.append((t, m.linear.x, m.angular.z))
        else:
            for tr in m.transforms:
                p, q = tr.transform.translation, tr.transform.rotation; v = (t, p.x, p.y, yaw(q))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append(v)
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append(v)
    mo.sort(); ob.sort()
    return '/rover/stuck' in types, st, cmd, mo, ob


def at(lst, t):
    k = bisect.bisect_left([x[0] for x in lst], t); return lst[min(max(k, 0), len(lst) - 1)]


def mpose(mo, ob, t):
    if not mo: B = at(ob, t); return B[1], B[2], B[3]
    A = at(mo, t); B = at(ob, t); c, s = math.cos(A[3]), math.sin(A[3])
    return A[1] + c * B[1] - s * B[2], A[2] + s * B[1] + c * B[2], A[3] + B[3]


tot = 0
for bag in sys.argv[1:]:
    has, st, cmd, mo, ob = load(bag)
    act = [c for c in cmd if abs(c[1]) > 0.005 or abs(c[2]) > 0.01]
    dur = (act[-1][0] - act[0][0]) if act else 0
    name = bag.rstrip('/').split('/')[-1]
    if not has: print('%-14s /rover/stuck 토픽 없음(기록 안 됨)' % name); continue
    print('%-14s 지령 구간 %4.0f s | 판정 %d 건' % (name, dur, len(st))); tot += len(st)
    t0 = act[0][0] if act else (st[0][0] if st else 0)
    for t, lv, msg in st:
        w = [c for c in cmd if t - 2 <= c[0] <= t]
        v = sum(abs(c[1]) for c in w) / len(w) if w else 0; om = sum(abs(c[2]) for c in w) / len(w) if w else 0
        a, b = mpose(mo, ob, t - 2), mpose(mo, ob, t)
        d = 100 * math.hypot(b[0] - a[0], b[1] - a[1]); dth = math.degrees((b[2] - a[2] + math.pi) % (2 * math.pi) - math.pi)
        print('   t %6.1f s  level %d  map (%5.2f, %5.2f, %6.1f°) | 직전 2 s 지령 |v| %.3f |ω| %.2f → 실제 %.1f cm·%+.1f° | %s'
              % (t - t0, lv, b[0], b[1], math.degrees(b[2]), v, om, d, dth, msg))
print('합계 판정 %d 건' % tot)
