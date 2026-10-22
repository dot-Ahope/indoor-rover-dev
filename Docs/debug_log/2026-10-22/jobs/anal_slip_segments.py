#!/usr/bin/env python3
"""anal_slip_segments — 주행을 시간 묶음으로 나눠 휠 · EKF · SLAM 의 회전 · 이동을 나란히(2026-10-22 §4, PC).
  왜: 사용자 — "W3 에서 전선을 밟았는데, 잘 작동했는지 확인". 전선을 밟아 트랙이 헛돌거나 들리면 휠(지령에 가까움)과 SLAM(라이다로 본 실제)이 어긋난다.
  휠 = /wheel_odom twist 적분(ω · v), EKF = /odometry/filtered 자세 차, SLAM = map→odom ∘ odom→base_link 자세 차.
  인자: bag 묶음s [시각들 'HH:MM:SS.cc,…'(그 시각 로버 map 자세 출력)]"""
import sys, math, bisect, datetime
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore

bag = sys.argv[1]; W = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
QT = [s for s in sys.argv[3].split(',')] if len(sys.argv) > 3 else []
KST = datetime.timezone(datetime.timedelta(hours=9))
yaw = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
wrap = lambda a: math.atan2(math.sin(a), math.cos(a))


def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])


MO, OB, WO, EK, ST, CMD = [], [], [], [], [], []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    t0 = rd.start_time * 1e-9
    want = ('/tf', '/wheel_odom', '/odometry/filtered', '/rover/stuck', '/cmd_vel')
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in want]):
        tt = t * 1e-9 - t0; m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                a = (tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tt, a))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((tt, a))
        elif c.topic == '/wheel_odom': WO.append((tt, m.twist.twist.linear.x, m.twist.twist.angular.z))
        elif c.topic == '/odometry/filtered': EK.append((tt, m.pose.pose.position.x, m.pose.pose.position.y, yaw(m.pose.pose.orientation)))
        elif c.topic == '/cmd_vel': CMD.append((tt, m.linear.x, m.angular.z))
        else: ST.append((tt, str(getattr(m, 'data', m))[:90]))
for L in (MO, OB): L.sort(key=lambda q: q[0])
MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]; EKt = [q[0] for q in EK]
at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]
slam = lambda t: comp(at(MO, MOt, t), at(OB, OBt, t))
ek = lambda t: EK[max(bisect.bisect_right(EKt, t) - 1, 0)][1:]
clock = lambda t: datetime.datetime.fromtimestamp(t0 + t, KST).strftime('%H:%M:%S')
ts = max(MOt[0], OBt[0]); te = min(MO[-1][0], OB[-1][0])
print('bag %s · %.1f~%.1f s (%s~%s) · 묶음 %.0f s' % (Path(bag).name, ts, te, clock(ts), clock(te), W))
print(' 묶음(시계)   | 로버 map 시작→끝            | 회전° 휠 / EKF / SLAM   | 이동 m 휠 / SLAM | 명령 |v|평균 · |ω|평균')
k = ts; tot = np.zeros(3)
while k < te - 1e-6:
    e = min(k + W, te)
    w = [(t, v, o) for t, v, o in WO if k <= t < e]
    if len(w) > 1:
        dt = np.diff([q[0] for q in w]); wv = np.array([q[1] for q in w[:-1]]); wo = np.array([q[2] for q in w[:-1]])
        rw = math.degrees(np.sum(wo * dt)); dw = float(np.sum(np.abs(wv) * dt))
    else: rw = dw = 0.0
    a, b = slam(k), slam(e); ea, eb = ek(k), ek(e)
    rs = math.degrees(wrap(b[2] - a[2])); re_ = math.degrees(wrap(eb[2] - ea[2])); ds = math.hypot(b[0] - a[0], b[1] - a[1])
    cm = [(abs(v), abs(o)) for t, v, o in CMD if k <= t < e]
    cv, co = (np.mean([q[0] for q in cm]), np.mean([q[1] for q in cm])) if cm else (0, 0)
    tot += (rw, re_, rs)
    print(' %s | (%5.2f,%5.2f)→(%5.2f,%5.2f) | %6.1f / %6.1f / %6.1f | %.2f / %.2f | %.3f · %.2f' % (clock(k), a[0], a[1], b[0], b[1], rw, re_, rs, dw, ds, cv, co))
    k = e
print(' 합 회전° 휠 %.1f · EKF %.1f · SLAM %.1f' % tuple(tot))
for s in ST: print(' /rover/stuck %s %s' % (clock(s[0]), s[1]))
for q in QT:
    hh, mm, ss = q.split(':'); sec = int(hh) * 3600 + int(mm) * 60 + float(ss)
    base = datetime.datetime.fromtimestamp(t0, KST); t = sec - (base.hour * 3600 + base.minute * 60 + base.second + base.microsecond * 1e-6)
    p = slam(t); print(' %s (t %.1f) 로버 map (%.2f, %.2f, %.0f°)' % (q, t, p[0], p[1], math.degrees(p[2])))
