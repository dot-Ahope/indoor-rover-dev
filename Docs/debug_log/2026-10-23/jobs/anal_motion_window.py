#!/usr/bin/env python3
"""anal_motion_window — 지정 시각 앞 W 초 동안 이동량을 소스별로: 명령(/cmd_vel 적분) · 휠(/wheel_odom 적분) · 주 EKF(/odometry/filtered 자세 차) ·
  cuVSLAM 속도(/vslam/odom 적분) · SLAM(map→odom∘odom→base 자세 차) (2026-10-23 §10, PC).
  왜: f2von1(vslam:=on) 에서 stuck_monitor(그림자)가 '지령 15.7 cm 인데 관측 0~2.8 cm' 를 4 번 냄 — 실제로 안 움직였나, EKF 가 못 봤나.
  인자: bag 시각들(s, 쉼표) [W=2.0]"""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag = sys.argv[1]; TQ = [float(v) for v in sys.argv[2].split(',')]; W = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
D = {k: [] for k in ('cmd', 'wheel', 'vs', 'ekf', 'MO', 'OB')}
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    T0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/cmd_vel', '/wheel_odom', '/vslam/odom', '/odometry/filtered', '/tf')]):
        tt = t * 1e-9 - T0; m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/cmd_vel': D['cmd'].append((tt, m.linear.x, m.angular.z))
        elif c.topic == '/wheel_odom': D['wheel'].append((tt, m.twist.twist.linear.x, m.twist.twist.angular.z))
        elif c.topic == '/vslam/odom': D['vs'].append((tt, math.hypot(m.twist.twist.linear.x, m.twist.twist.linear.y), m.twist.twist.angular.z))
        elif c.topic == '/odometry/filtered': D['ekf'].append((tt, m.pose.pose.position.x, m.pose.pose.position.y, yq(m.pose.pose.orientation)))
        else:
            for tr in m.transforms:
                v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': D['MO'].append((tt, v))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': D['OB'].append((tt, v))
for k in D: D[k].sort(key=lambda q: q[0])
at = lambda L, t: L[max(bisect.bisect_right([q[0] for q in L], t) - 1, 0)]
def integ(L, a, b):
    s = [q for q in L if a <= q[0] <= b]
    if len(s) < 2: return 0.0, 0.0
    tt = np.array([q[0] for q in s]); v = np.array([abs(q[1]) for q in s]); w = np.array([q[2] for q in s]); dt = np.diff(tt)
    return float(np.sum(v[:-1] * dt)), math.degrees(float(np.sum(w[:-1] * dt)))
print('bag %s · 창 %.1f s(시각 앞) · 이동 cm / 회전 °' % (Path(bag).name, W))
print('  t     | 명령          | 휠            | cuVSLAM 속도 적분 | 주 EKF        | SLAM')
for t in TQ:
    a = t - W
    ce, cw = integ(D['cmd'], a, t); we, ww = integ(D['wheel'], a, t); ve, vw = integ(D['vs'], a, t)
    e0, e1 = at(D['ekf'], a)[1:], at(D['ekf'], t)[1:]; ee = math.hypot(e1[0] - e0[0], e1[1] - e0[1]); ew = math.degrees(math.atan2(math.sin(e1[2] - e0[2]), math.cos(e1[2] - e0[2])))
    s0 = comp(at(D['MO'], a)[1], at(D['OB'], a)[1]); s1 = comp(at(D['MO'], t)[1], at(D['OB'], t)[1]); se = math.hypot(s1[0] - s0[0], s1[1] - s0[1]); sw = math.degrees(math.atan2(math.sin(s1[2] - s0[2]), math.cos(s1[2] - s0[2])))
    print('  %5.1f | %5.1f / %+5.1f | %5.1f / %+5.1f | %5.1f / %+5.1f     | %5.1f / %+5.1f | %5.1f / %+5.1f' % (t, 100 * ce, cw, 100 * we, ww, 100 * ve, vw, 100 * ee, ew, 100 * se, sw))
