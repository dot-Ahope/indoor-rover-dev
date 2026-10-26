#!/usr/bin/env python3
"""anal_bend_dev_odom — 복귀 상자 둘레(map x 0.5~2.4, y −0.8~0.8, 마지막 통과)에서 컨트롤러 자기 좌표(odom) 기준 경로 이탈, '굽은 곳 안쪽 +' 부호 (2026-10-26 §11, PC).
  §9 의 chk_dev_frame_f2sh2(상자 쪽 +)를 주행 공통으로: 로버(odom→base_link) ↔ /transformed_global_plan(odom) 옆 거리, 부호 = 경로가 휘는 쪽(±0.5 m 방향 변화 ≥ 15° 일 때만).
  출력: 굽은 곳 안쪽 이탈 최대 · 95 % · 그 시각 · 같은 창 map→odom 변화 범위. 인자: 이름=bag ..."""
import sys, math, bisect, time
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
def dev_inside(Q, q):
    a, b = Q[:-1], Q[1:]; ab = b - a; u = np.clip(np.einsum('ij,ij->i', q - a, ab) / np.maximum(np.einsum('ij,ij->i', ab, ab), 1e-12), 0, 1)
    F = a + u[:, None] * ab; k = int(np.argmin(np.linalg.norm(F - q, axis=1))); d = float(np.linalg.norm(F[k] - q))
    t = ab[k] / max(np.linalg.norm(ab[k]), 1e-9); side = np.sign(t[0] * (q[1] - F[k][1]) - t[1] * (q[0] - F[k][0]))
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(ab, axis=1))]); i0 = int(np.searchsorted(s, s[k] - 0.5)); i1 = min(int(np.searchsorted(s, s[k] + 0.5)), len(ab) - 1)
    h = np.unwrap(np.arctan2(ab[i0:i1 + 1, 1], ab[i0:i1 + 1, 0])); turn = h[-1] - h[0] if len(h) > 1 else 0.0
    return float('nan') if abs(turn) < math.radians(15) else d * side * np.sign(turn)
for arg in sys.argv[1:]:
    name, bag = arg.split('=', 1); MO, OB, TP = [], [], []
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/transformed_global_plan')]):
            m = rd.deserialize(raw, c.msgtype); ts = t * 1e-9
            if c.topic == '/tf':
                for tr in m.transforms:
                    v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                    if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((ts, v))
                    elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((ts, v))
            elif len(m.poses) > 3: TP.append((ts, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses])))
    for L in (MO, OB, TP): L.sort(key=lambda q: q[0])
    Lt = [[q[0] for q in L] for L in (MO, OB, TP)]
    at = lambda i, L, t: L[max(bisect.bisect_right(Lt[i], t) - 1, 0)][1]
    T = np.arange(OB[0][0], OB[-1][0], 0.2)
    Pm = np.array([comp(at(0, MO, t), at(1, OB, t)) for t in T])
    ins = (Pm[:, 0] > 0.5) & (Pm[:, 0] < 2.4) & (Pm[:, 1] > -0.8) & (Pm[:, 1] < 0.8); idx = np.nonzero(ins)[0]
    brk = np.nonzero(np.diff(idx) > 5)[0]; seg = idx[brk[-1] + 1:] if len(brk) else idx
    D = []; MOX = []
    for i in seg:
        t = T[i]; D.append(dev_inside(at(2, TP, t), np.array(at(1, OB, t)[:2]))); MOX.append(at(0, MO, t))
    D = np.array(D); ok = ~np.isnan(D); MOX = np.array(MOX)
    j = int(np.nanargmax(D)) if ok.any() else 0
    print('%s · 복귀 상자 둘레 %s~%s · 굽은 곳 안쪽 이탈(odom) 최대 %+.1f cm @ %s · 95 %% %+.1f · 중앙 %+.1f cm · 같은 창 map→odom 변화 x %.1f · y %.1f cm' % (
        name, time.strftime('%H:%M:%S', time.localtime(T[seg[0]])), time.strftime('%H:%M:%S', time.localtime(T[seg[-1]])), 100 * D[j], time.strftime('%H:%M:%S', time.localtime(T[seg[j]])),
        100 * np.nanpercentile(D, 95), 100 * np.nanmedian(D), 100 * np.ptp(MOX[:, 0]), 100 * np.ptp(MOX[:, 1])))
