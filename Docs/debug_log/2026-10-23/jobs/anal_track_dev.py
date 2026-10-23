#!/usr/bin/env python3
"""anal_track_dev — 상자 옆을 지날 때 '계획 경로의 여유' 와 '실제로 지나간 여유' 의 차이: 로버가 경로에서 상자 쪽으로 얼마나 벗어났나(2026-10-23 §2, PC).
  왜: §1 에서 기록된 전역 경로는 실제 상자에서 여유 4~14 cm 인데 f2pi1 실제 여유는 1.1 cm — 차이가 경로(계획기) 쪽인지 따라가기(MPPI) 쪽인지.
  시각마다: 실제 여유(차체 사각형 ↔ 실제 상자), 그 시각 최신 /plan_smoothed 가 상자 옆에서 갖는 여유(경로점 ↔ 상자 − 반폭),
           로버 중심의 경로 수직 거리(+ = 상자 쪽으로 벗어남), /transformed_global_plan(컨트롤러가 받은 것)도 같은 계산.
  ⚠ 경로는 0.5 Hz 로 로버 자리에서 다시 그려지므로 '최신 경로' 기준 벗어남은 로버를 따라가 0 에 가깝다(첫 실행에서 확인) →
     FREEZE=시각 을 주면 그 시각의 경로(상자 앞에서 그린 것)를 고정해 그 경로 대비 벗어남을 본다.
  인자: bag 시작s 끝s [간격 s=0.5]   환경 FREEZE=s"""
import sys, math, bisect, os
from pathlib import Path
import numpy as np
from matplotlib.path import Path as MP
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, TA, TB = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); DT = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
BOX = (1.151, 1.261, -0.20, -0.02); BC = np.array([(BOX[0] + BOX[1]) / 2, (BOX[2] + BOX[3]) / 2])
BOXP = np.array([[x, y] for x in np.linspace(BOX[0], BOX[1], 12) for y in np.linspace(BOX[2], BOX[3], 19)])
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]])
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
MO, OB, PS, TP = [], [], [], []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    T0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/plan_smoothed', '/transformed_global_plan')]):
        tt = t * 1e-9 - T0; m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tt, v))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((tt, v))
        else:
            fr = m.header.frame_id; P = np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses]) if m.poses else np.zeros((0, 2))
            (PS if c.topic == '/plan_smoothed' else TP).append((tt, fr, P))
for L in (MO, OB): L.sort(key=lambda q: q[0])
MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]; at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]
def to_map(P, fr, t):
    if fr == 'map' or len(P) == 0: return P
    a = at(MO, MOt, t); c, s = math.cos(a[2]), math.sin(a[2]); return np.c_[a[0] + c * P[:, 0] - s * P[:, 1], a[1] + s * P[:, 0] + c * P[:, 1]]
def poly_clear(Q):
    if MP(Q).contains_points(BOXP).any(): return 0.0
    d = np.inf
    for i in range(4):
        a, b = Q[i], Q[(i + 1) % 4]; ab = b - a; u = np.clip(((BOXP - a) @ ab) / (ab @ ab), 0, 1); d = min(d, float(np.min(np.linalg.norm(BOXP - (a + u[:, None] * ab), axis=1))))
    return d
def path_stats(P, p):
    if len(P) < 2: return (np.nan, np.nan)
    dP = np.min(np.hypot(P[:, None, 0] - BOXP[None, :, 0], P[:, None, 1] - BOXP[None, :, 1]), axis=1); clear = float(dP.min()) - 0.165
    q = np.array(p[:2]); seg = P[1:] - P[:-1]; u = np.clip(np.einsum('ij,ij->i', q - P[:-1], seg) / np.maximum(np.einsum('ij,ij->i', seg, seg), 1e-9), 0, 1)
    foot = P[:-1] + u[:, None] * seg; k = int(np.argmin(np.linalg.norm(foot - q, axis=1))); off = float(np.linalg.norm(foot[k] - q))
    toward = np.linalg.norm(q - BC) < np.linalg.norm(foot[k] - BC)
    return clear, off if toward else -off
print('bag %s · t %.0f~%.0f s · 여유 = 실제 상자까지(− 반폭) · 벗어남 + = 로버 중심이 경로보다 상자 쪽' % (Path(bag).name, TA, TB))
print('   t   | 로버 (x, y, yaw)        | 실제 여유 | 다듬은 전역 경로 여유 · 벗어남 | 컨트롤러 경로 여유 · 벗어남')
t = TA
while t <= TB + 1e-9:
    p = comp(at(MO, MOt, t), at(OB, OBt, t)); c, s = math.cos(p[2]), math.sin(p[2]); Q = np.c_[p[0] + c * FP[:, 0] - s * FP[:, 1], p[1] + s * FP[:, 0] + c * FP[:, 1]]
    out = []
    for L in (PS, TP):
        tf_ = float(os.environ['FREEZE']) if os.environ.get('FREEZE') else t
        cand = [q for q in L if q[0] <= tf_]
        if cand: tt, fr, P = cand[-1]; out.append(path_stats(to_map(P, fr, tt), p))
        else: out.append((np.nan, np.nan))
    print(' %6.1f | (%5.2f, %5.2f, %5.0f°) | %5.1f cm | %5.1f cm · %+5.1f cm | %5.1f cm · %+5.1f cm' % (t, p[0], p[1], math.degrees(p[2]), 100 * poly_clear(Q), 100 * out[0][0], 100 * out[0][1], 100 * out[1][0], 100 * out[1][1]))
    t += DT
