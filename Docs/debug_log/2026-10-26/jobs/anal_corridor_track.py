#!/usr/bin/env python3
"""anal_corridor_track — 서쪽 통로(map x −2.3~−0.9, y −5.7~−3.4)에서 로버가 컨트롤러 경로(/transformed_global_plan, odom)를 얼마나 바짝 따랐나 · 그 경로가 지나는 전역 코스트 (2026-10-26 §15, PC).
  왜: f2sa3(MPPI 28 · 5)에서 통로 최소 여유 0.8 cm · 최적화 실패 · 7 s 정지 — 가설: 통로에선 Smac 실패 → NavFn 경로(벽에 붙음)를 PathAlign 28 이 더 바짝 따라감.
  출력: 통로 안 틱의 |경로 이탈| 중앙 · 95 %, 로버 자리 로컬 코스트맵 값(0~100) 중앙 · 95 %. 인자: 이름=bag ..."""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
def dist(Q, q):
    a, b = Q[:-1], Q[1:]; ab = b - a; u = np.clip(np.einsum('ij,ij->i', q - a, ab) / np.maximum(np.einsum('ij,ij->i', ab, ab), 1e-12), 0, 1)
    return float(np.min(np.linalg.norm(a + u[:, None] * ab - q, axis=1)))
for arg in sys.argv[1:]:
    name, bag = arg.split('=', 1); MO, OB, TP, LC = [], [], [], []
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/transformed_global_plan', '/local_costmap/costmap')]):
            m = rd.deserialize(raw, c.msgtype); ts = t * 1e-9
            if c.topic == '/tf':
                for tr in m.transforms:
                    v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                    if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((ts, v))
                    elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((ts, v))
            elif c.topic == '/transformed_global_plan':
                if len(m.poses) > 3: TP.append((ts, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses])))
            else: LC.append((ts, (m.info.origin.position.x, m.info.origin.position.y, m.info.resolution, np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width))))
    for L in (MO, OB, TP, LC): L.sort(key=lambda q: q[0])
    Lt = [[q[0] for q in L] for L in (MO, OB, TP, LC)]
    at = lambda i, L, t: L[max(bisect.bisect_right(Lt[i], t) - 1, 0)][1]
    E, C = [], []
    for t in np.arange(OB[0][0], OB[-1][0], 0.2):
        ob = at(1, OB, t); pm = comp(at(0, MO, t), ob)
        if not (-2.3 < pm[0] < -0.9 and -5.7 < pm[1] < -3.4): continue
        E.append(dist(at(2, TP, t), np.array(ob[:2])))
        ox, oy, r, G = at(3, LC, t); i, j = int((ob[1] - oy) / r), int((ob[0] - ox) / r)
        if 0 <= i < G.shape[0] and 0 <= j < G.shape[1]: C.append(int(G[i, j]))
    E, C = np.array(E), np.array(C)
    print('%s · 통로 안 %d 틱 · |경로 이탈| 중앙 %.1f · 95 %% %.1f cm · 로버 중심 로컬 비용 중앙 %d · 95 %% %d · ≥ 99 비율 %.0f %%' % (name, len(E), 100 * np.median(E), 100 * np.percentile(E, 95), np.median(C), np.percentile(C, 95), 100 * (C >= 99).mean()))
