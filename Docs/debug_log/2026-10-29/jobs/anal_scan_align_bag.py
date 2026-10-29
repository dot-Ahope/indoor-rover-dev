#!/usr/bin/env python3
"""anal_scan_align_bag — bag 의 라이다 판마다 정적 /map 과 맞춤 점수(10-29 §2, PC).
  점수 = 라이다 점(≤ 6 m) 중 정적 점유 칸(≥ 65, 1 칸 팽창) 안에 드는 비율 — chk_scan_align.py 와 같은 정의.
  판마다(STEP s 간격): 지금 TF 점수 s0 · ±30° 0.5° 훑어 최고 점수 sb 와 그 각 db · 로버 map 자세 · 속도(정지/주행).
  목적: 위치 추정이 맞던 주행에서 s0 · db 분포 → place_server 출발 전 검사 문턱값 근거.
  인자: 이름 bag폴더 [STEP=2.0]  → 표 줄(이름 t x y yaw v s0 sb db) 를 stdout 으로"""
import sys, math
import numpy as np
from pathlib import Path
from scipy.ndimage import binary_dilation
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore

name, bag = sys.argv[1], Path(sys.argv[2]); STEP = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
yaw = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def T3(tr):
    a = yaw(tr.rotation); c, s = math.cos(a), math.sin(a); return np.array([[c, -s, tr.translation.x], [s, c, tr.translation.y], [0, 0, 1]])
mo, ob, static, scans, MAP = [], [], {}, [], None
with AnyReader([bag], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/scan', '/map')]):
        m = rd.deserialize(raw, c.msgtype); ts = t * 1e-9
        if c.topic == '/map': MAP = m if MAP is None else MAP   # 정적 지도(위치 추정 모드라 바뀌지 않음) — 첫 판
        elif c.topic == '/tf_static':
            for tr in m.transforms: static[tr.child_frame_id] = (tr.header.frame_id, T3(tr.transform))
        elif c.topic == '/tf':
            for tr in m.transforms:
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append((ts, T3(tr.transform)))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append((ts, T3(tr.transform)))
        elif c.topic == '/scan' and (not scans or ts - scans[-1][0] >= STEP):
            r = np.array(m.ranges, np.float32); a = m.angle_min + m.angle_increment * np.arange(len(r))
            ok = np.isfinite(r) & (r > m.range_min) & (r < min(m.range_max, 6.0))
            scans.append((ts, m.header.frame_id, r[ok], a[ok]))
i = MAP.info; G = binary_dilation(np.array(MAP.data, np.int16).reshape(i.height, i.width) >= 65, iterations=1)
tsm, tso = np.array([x[0] for x in mo]), np.array([x[0] for x in ob])
last = lambda L, T, t: L[max(np.searchsorted(T, t, side='right') - 1, 0)][1]
def chain(f):
    M = np.eye(3)
    while f != 'base_link': p, mm = static[f]; M = mm @ M; f = p
    return M
D = np.radians(np.arange(-30, 30.25, 0.5))
for ts, fr, r, a in scans:
    if ts < tsm[0] or ts < tso[0] or len(r) < 50: continue
    B = last(mo, tsm, ts) @ last(ob, tso, ts); L = B @ chain(fr)            # map ← 라이다
    P = np.c_[r * np.cos(a), r * np.sin(a)]
    lx, ly, la = L[0, 2], L[1, 2], math.atan2(L[1, 0], L[0, 0])
    ang = la + np.arctan2(P[:, 1], P[:, 0]); rr = np.hypot(P[:, 0], P[:, 1])
    def score(d):
        x = lx + rr * np.cos(ang + d); y = ly + rr * np.sin(ang + d)
        J = ((y - i.origin.position.y) / i.resolution).astype(int); I = ((x - i.origin.position.x) / i.resolution).astype(int)
        v = (J >= 0) & (J < G.shape[0]) & (I >= 0) & (I < G.shape[1]); return float(G[J[v], I[v]].mean()) if v.any() else 0.0
    S = np.array([score(d) for d in D]); k = int(np.argmax(S))
    p0 = last(ob, tso, ts - 1.0); v = math.hypot(B[0, 2] - (last(mo, tsm, ts) @ p0)[0, 2], B[1, 2] - (last(mo, tsm, ts) @ p0)[1, 2])
    print('%s %.1f %+.2f %+.2f %+6.1f %.3f %.3f %.3f %+5.1f' % (name, ts, B[0, 2], B[1, 2], math.degrees(math.atan2(B[1, 0], B[0, 0])), v,
                                                       S[len(D) // 2], S[k], math.degrees(D[k])))
