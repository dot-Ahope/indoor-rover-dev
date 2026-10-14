#!/usr/bin/env python3
"""anal_hesitation — '멈칫거리며 움직임'(사용자 영상)을 수치로: 구간별 명령 속도가 순항(≥0.06)에서 0.03 아래로 떨어졌다 돌아오는 횟수,
  각속도 부호 바뀜 횟수, 지도 보정(map→odom) 각의 변화 — 두 주행의 같은 구간을 나란히. (2026-10-14, 오늘만)
  인자: 이름=bag@HH:MM:SS~HH:MM:SS ..."""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
print('구간                         길이   평균 명령 v   순항→멈칫 횟수(분당)   ω 부호 바뀜(분당)   지도 보정 각 변화   EKF 각속도 대 휠 각속도 비')
for a in sys.argv[1:]:
    nm, rest = a.split('='); bag, rng = rest.split('@'); h0, h1 = rng.split('~'); cm = []; mo = []; wo = []; od = []
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        day = None
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/cmd_vel', '/tf', '/wheel_odom', '/odometry/filtered')]):
            ts = t / 1e9
            if day is None: day = time.strftime('%Y-%m-%d ', time.localtime(ts)); A = time.mktime(time.strptime(day + h0, '%Y-%m-%d %H:%M:%S')); B = time.mktime(time.strptime(day + h1, '%Y-%m-%d %H:%M:%S'))
            if ts < A or ts > B: continue
            m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/cmd_vel': cm.append((ts, m.linear.x, m.angular.z))
            elif c.topic == '/wheel_odom': wo.append((ts, m.twist.twist.angular.z))
            elif c.topic == '/odometry/filtered': od.append((ts, m.twist.twist.angular.z))
            else:
                for tr in m.transforms:
                    if tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo.append((ts, yq(tr.transform.rotation)))
    C = np.array(cm); T = (B - A) / 60; v = C[:, 1]; w = C[:, 2]
    cruise = False; dips = 0
    for x in v:
        if x >= 0.06: cruise = True
        elif x < 0.03 and cruise: dips += 1; cruise = False
    ws = np.sign(np.where(np.abs(w) > 0.05, w, 0)); ws = ws[ws != 0]; flips = int((ws[1:] != ws[:-1]).sum())
    M = np.array(mo); dyaw = math.degrees(((M[-1, 1] - M[0, 1] + math.pi) % (2 * math.pi)) - math.pi) if len(M) > 1 else float('nan')
    W = np.array(wo); O = np.array(od); rat = float(np.sum(np.abs(O[:, 1])) * np.median(np.diff(O[:, 0])) / max(np.sum(np.abs(W[:, 1])) * np.median(np.diff(W[:, 0])), 1e-6))
    print('%-28s %4.0f s   %.3f m/s     %3d (%4.1f)            %3d (%4.1f)           %+5.1f°             %.2f' % (nm, B - A, v.mean(), dips, dips / T, flips, flips / T, dyaw, rat))
