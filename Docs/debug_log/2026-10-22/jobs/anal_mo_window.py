#!/usr/bin/env python3
"""anal_mo_window — map→odom 이 W 초 창 안에서 얼마나 바뀌는지(= 그 창 동안 기억된 물체가 로버 기준으로 틀어지는 양)를 주행 앞 · 뒤 절반으로 나눠 (2026-10-22 §11.4, PC).
  왜: 사용자 — "주행이 장기화될수록 비슷한 문제가 더 많이 발생하는가?" 기억 오차는 주행 전체 누적이 아니라 '관측 뒤 기억이 쓰이는 동안' 의 EKF 오차.
  기억된 점 = 상자 중심 (1.206, −0.110) 으로 두고 창 시작 → 끝 사이 지도 이동량. 창은 1 s 간격으로 밀며, 앞 절반 · 뒤 절반의 중앙 · 95 % · 최대.
  인자: W(s) bag들"""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
W = float(sys.argv[1]); P = (1.206, -0.110)
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
for bag in sys.argv[2:]:
    MO = []
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        T0 = rd.start_time * 1e-9
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/tf']):
            for tr in rd.deserialize(raw, c.msgtype).transforms:
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                    MO.append((tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9 - T0, (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))))
    MO.sort(); Mt = [q[0] for q in MO]; at = lambda t: MO[max(bisect.bisect_right(Mt, t) - 1, 0)][1]
    def mv(a, b):
        A, B = at(a), at(b); dx, dy = P[0] - A[0], P[1] - A[1]; c, s = math.cos(-A[2]), math.sin(-A[2]); o = (c * dx - s * dy, s * dx + c * dy)
        c, s = math.cos(B[2]), math.sin(B[2]); return math.hypot(B[0] + c * o[0] - s * o[1] - P[0], B[1] + s * o[0] + c * o[1] - P[1])
    T1 = MO[-1][0]; ts = np.arange(MO[0][0], T1 - W, 1.0); v = np.array([mv(t, t + W) for t in ts]); h = ts < (MO[0][0] + T1 - W) / 2
    end = mv(MO[0][0], T1)
    f = lambda a: '중앙 %4.1f · 95 %% %4.1f · 최대 %4.1f cm' % (100 * np.median(a), 100 * np.percentile(a, 95), 100 * a.max())
    print('%s · 길이 %.0f s · 주행 전체 누적(처음→끝) %.1f cm | 창 %.0f s 이동: 앞 절반 %s | 뒤 절반 %s' % (Path(bag).name, T1, 100 * end, W, f(v[h]), f(v[~h])))
