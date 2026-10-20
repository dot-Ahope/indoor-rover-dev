#!/usr/bin/env python3
"""anal_vslam_rpe — 짧은 창(Δ s) 상대 오차: cuVSLAM · EKF 가 Δ 초 동안 움직인 양이 SLAM 이 본 움직임과 얼마나 다른가. (2026-10-20 §4, PC)
  왜: 상자 기억 밀림은 절대 오차가 아니라 '상자를 본 뒤 지나가는 동안(≈10 s)' 쌓인 오도메트리 오차가 만든다(10-19 §14).
  EKF 에 cuVSLAM 을 yaw 속도만 넣으면 yaw 쪽, 속도(vx·vy)까지 넣으면 위치 쪽 상대 오차가 cuVSLAM 쪽으로 간다 — 그 상한 추정.
  오차 = 로버 몸 기준 상대 변환 차(위치 cm · yaw °), 창은 1 s 간격으로 밀며 전 구간 · 복귀 회전(t160~210) · 상자 옆(출발 t18~36, 복귀 t180~200).
  인자: 주행bag csv폴더 [Δ=10]"""
import sys, math, bisect, csv, os
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, cdir = sys.argv[1:3]; D = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0
SEG = {'전 구간': (20, 1e9), '복귀 회전 t160~210': (160, 210), '상자 옆 출발 t18~36': (18, 36), '상자 옆 복귀 t180~200': (180, 200)}


def qm(x, y, z, w):
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def T(tr):
    M = np.eye(4); q = tr.rotation; M[:3, :3] = qm(q.x, q.y, q.z, q.w); M[:3, 3] = [tr.translation.x, tr.translation.y, tr.translation.z]; return M


static = {}; MO, OB = [], []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static')]):
        for tr in rd.deserialize(raw, c.msgtype).transforms:
            st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9
            if c.topic == '/tf_static': static[tr.child_frame_id] = (tr.header.frame_id, T(tr.transform))
            elif tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((st, T(tr.transform)))
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((st, T(tr.transform)))
MO.sort(key=lambda q: q[0]); OB.sort(key=lambda q: q[0]); MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]; t0 = MOt[0]
at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]
B2C = np.eye(4); f = 'camera_link'
while f != 'base_link':
    p, A = static[f]; B2C = A @ B2C; f = p
slam = lambda t: at(MO, MOt, t) @ at(OB, OBt, t) @ B2C
ekf = lambda t: at(OB, OBt, t) @ B2C
src = {'EKF': ekf}
for v in ('false_vs_off',):
    R = np.array([[float(x) for x in r] for r in list(csv.reader(open(os.path.join(cdir, 'vslam_%s.csv' % v))))[1:]]); Rt = R[:, 0]
    def vs(t, R=R, Rt=Rt):
        r = R[max(bisect.bisect_right(Rt, t) - 1, 0)]; M = np.eye(4); M[:3, :3] = qm(*r[4:8]); M[:3, 3] = r[1:4]; return M
    src['cuVSLAM(IMU 끔)'] = vs
ts = np.arange(t0 + 20, min(OBt[-1], Rt[-1]) - D, 1.0)
for nm, fn in src.items():
    out = []
    for a in ts:
        G = np.linalg.inv(slam(a)) @ slam(a + D); E = np.linalg.inv(fn(a)) @ fn(a + D); X = np.linalg.inv(G) @ E
        out.append((a - t0, 100 * math.hypot(X[0, 3], X[1, 3]), abs(math.degrees(math.atan2(X[1, 0], X[0, 0]))), 100 * abs(X[1, 3])))
    O = np.array(out); line = []
    for sn, (s0, s1) in SEG.items():
        k = (O[:, 0] + D > s0) & (O[:, 0] < s1)   # 창이 구간과 겹치면
        if k.sum() == 0: continue
        line.append('%s: 위치 95%% %.1f · 최대 %.1f cm · 옆 최대 %.1f cm · yaw 95%% %.2f · 최대 %.2f°' % (sn, np.percentile(O[k, 1], 95), O[k, 1].max(), O[k, 3].max(), np.percentile(O[k, 2], 95), O[k, 2].max()))
    print('  %-16s Δ%.0f s\n    ' % (nm, D) + '\n    '.join(line))
