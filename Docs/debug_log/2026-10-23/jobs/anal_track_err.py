#!/usr/bin/env python3
"""anal_track_err — 컨트롤러 경로 추종 오차: 각 전역 경로(/plan_smoothed)가 쓰이는 동안(다음 경로가 올 때까지) 로버 중심이 그 경로 선에서 옆으로 얼마나 떨어졌나
  (2026-10-23 §14, PC, 로버 안 움직임).
  왜: 사용자 — "planner 가 만든 경로를 controller 가 제대로 추종하지 못하는 게 문제". 경로마다 그 경로 기준으로 재야 '다시 그리기' 가 오차를 지우는 효과에 속지 않음(§2 · §4 교훈).
  지표: 경로 받은 뒤 0.5 s ~ 다음 경로까지 로버 중심 ↔ 그 경로(전체) 수직 거리. 경로는 로버 자리에서 시작하므로 받은 순간 오차 ≈ 0 에서 출발해 그 경로 동안 쌓인 몫만 잼.
  ⚠ 첫 판 실수: 출발점 0.15 m 밖 구간만 쓰니 로버가 아직 출발점 근처일 때 '빠진 구간까지의 거리' 가 잡혀 모든 주행이 중앙 8.8 cm 로 똑같이 나옴(측정 인공물) → 전체 경로로 고침.
  출력: 주행 전체 · 상자 둘레(지도 x 0.8~1.8, y −0.3~0.5) · 굽은 구간(경로 0.5 m 안 방향 변화 > 30°)별 오차 중앙 · 95 % · 최대, 그리고 '한 경로 동안 쌓인 오차'(그 경로 끝 시각 오차).
  인자: bag들"""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
def seg_dist(P, q):
    a, b = P[:-1], P[1:]; ab = b - a; u = np.clip(np.einsum('ij,ij->i', q - a, ab) / np.maximum(np.einsum('ij,ij->i', ab, ab), 1e-9), 0, 1)
    return float(np.min(np.linalg.norm(a + u[:, None] * ab - q, axis=1)))
def bend(P, q):   # 로버 근처 경로 0.5 m 안 방향 변화(°)
    i = int(np.argmin(np.linalg.norm(P - q, axis=1))); s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P[i:], axis=0), axis=1))]; j = i + int(np.searchsorted(s, 0.5))
    if j >= len(P) - 1 or j - i < 3: return 0.0
    h = np.arctan2(np.diff(P[i:j + 1, 1]), np.diff(P[i:j + 1, 0])); return float(np.degrees(np.ptp(np.unwrap(h))))
f = lambda a: '중앙 %4.1f · 95 %% %4.1f · 최대 %4.1f cm (n %d)' % (100 * np.median(a), 100 * np.percentile(a, 95), 100 * a.max(), len(a)) if len(a) else '없음'
for bag in sys.argv[1:]:
    MO, OB, PL = [], [], []
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        T0 = rd.start_time * 1e-9
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/plan_smoothed')]):
            tt = t * 1e-9 - T0; m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/tf':
                for tr in m.transforms:
                    v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                    if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tt, v))
                    elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((tt, v))
            else:
                P = np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses]) if m.poses else np.zeros((0, 2))
                if len(P) > 5: PL.append((tt, P))
    for L in (MO, OB): L.sort(key=lambda q: q[0])
    MOt = [q[0] for q in MO]; at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]; OBt = [q[0] for q in OB]
    allv, boxv, bendv, endv = [], [], [], []
    for k, (tp, P) in enumerate(PL):
        tn = PL[k + 1][0] if k + 1 < len(PL) else tp + 2.1
        Q = P
        if len(Q) < 3: continue
        last_e = None
        for t in np.arange(tp + 0.5, tn, 0.2):
            p = comp(at(MO, MOt, t), at(OB, OBt, t)); q = np.array(p[:2]); e = seg_dist(Q, q); last_e = e; allv.append(e)
            if 0.8 <= q[0] <= 1.8 and -0.3 <= q[1] <= 0.5: boxv.append(e)
            if bend(P, q) > 30: bendv.append(e)
        if last_e is not None: endv.append(last_e)
    A = lambda v: np.array(v)
    print('%s · 경로 %d 개' % (Path(bag).name.replace('bag_', ''), len(PL)))
    print('   전체 %s' % f(A(allv))); print('   상자 둘레 %s' % f(A(boxv))); print('   굽은 구간 %s' % f(A(bendv))); print('   경로 끝 시각(한 경로 동안 쌓인 것) %s' % f(A(endv)))
