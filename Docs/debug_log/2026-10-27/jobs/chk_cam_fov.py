#!/usr/bin/env python3
"""chk_cam_fov — §21 복귀 때 카메라(nvblox)가 상자만 못 봤나, 아무것도 못 봤나 (2026-10-27, PC).
  1 s 마다 카메라 시야 부채꼴(camera_link 기준 ±반각, 거리 ≤ R) 안의 nvblox 슬라이스 칸(odom → map):
    아는 칸 수 · 장애(≤0) 칸 수 · 1 s 전 슬라이스 대비 새로 알게 된 칸(미지 → 앎) · 값이 바뀐 칸(|Δ| > 0.02 m) 수,
    시야 안 장애 칸 중 1 s 전에는 장애가 아니던 칸(새 장애) 수, 그리고 시야 안 라이다 점 수(비교용).
  깊이 원본은 bag 에 없음 → 통합 결과(슬라이스)로만 판단. 인자: bag폴더 시작 끝 [반각=43] [R=2.0]"""
import sys, time, math
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
ts_ = get_typestore(Stores.ROS2_HUMBLE)
ts_.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
day = '2026-10-27 '; t0 = time.mktime(time.strptime(day + sys.argv[2], '%Y-%m-%d %H:%M:%S')); t1 = time.mktime(time.strptime(day + sys.argv[3], '%Y-%m-%d %H:%M:%S'))
HA = math.radians(float(sys.argv[4]) if len(sys.argv) > 4 else 43.0); RR = float(sys.argv[5]) if len(sys.argv) > 5 else 2.0
hs = lambda t: time.strftime('%H:%M:%S', time.localtime(t))
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def T3(tr):
    a = yaw(tr.rotation); c, s = math.cos(a), math.sin(a); return np.array([[c, -s, tr.translation.x], [s, c, tr.translation.y], [0, 0, 1]])
SL, mo, ob, sc, static = [], [], [], [], {}
with AnyReader([Path(sys.argv[1])], default_typestore=ts_) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/nvblox_node/static_map_slice', '/tf', '/tf_static', '/scan')]):
        ts = t * 1e-9
        if c.topic == '/tf_static':
            for tr in rd.deserialize(raw, c.msgtype).transforms: static[tr.child_frame_id] = (tr.header.frame_id, T3(tr.transform))
            continue
        if ts < t0 - 2 or ts > t1 + 1: continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append((ts, T3(tr.transform)))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append((ts, T3(tr.transform)))
        elif c.topic == '/scan':
            a = m.angle_min + m.angle_increment * np.arange(len(m.ranges)); r = np.array(m.ranges, np.float32); ok = np.isfinite(r) & (r > m.range_min) & (r < m.range_max)
            sc.append((ts, m.header.frame_id, np.c_[r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok]), np.ones(ok.sum())]))
        else:
            SL.append((ts, m.origin.x, m.origin.y, m.resolution, np.array(m.data, np.float32).reshape(m.height, m.width), m.unknown_value))
def last(L, t): return L[max(np.searchsorted([x[0] for x in L], t, side='right') - 1, 0)]
def chain(f):
    M = np.eye(3)
    while f != 'base_link': p, mm = static[f]; M = mm @ M; f = p
    return M
CAMF = next(f for f in ('camera_link', 'camera_depth_frame') if f in static)
def grid(S):   # 슬라이스 → 칸 사전 {(i,j) odom 칸: 값}
    _, ox, oy, r, d, unk = S; J, I = np.nonzero(d != unk)
    return {(int(round(ox / r)) + i, int(round(oy / r)) + j): float(d[j, i]) for i, j in zip(I, J)}, r
print('시각 | 로버 map · 방향 | 시야 안(±%.0f°, ≤ %.1f m): 아는 칸 · 장애 칸 · 1 s 새로 앎 · 값 바뀜 · 새 장애 | 시야 안 라이다 점' % (math.degrees(HA), RR))
prevG = None
for w in np.arange(t0, t1 + 0.01, 1.0):
    S = last(SL, w); G, r = grid(S); Mmo = last(mo, w)[1]; Mmb = Mmo @ last(ob, w)[1]; Mc = Mmb @ chain(CAMF)
    Minv = np.linalg.inv(Mc)   # map → 카메라
    K = np.array(list(G.keys())); P = np.c_[(K + .5) * r, np.ones(len(K))]           # odom 칸 중심
    C = (Minv @ Mmo @ P.T).T                                                          # 카메라 좌표
    rng = np.hypot(C[:, 0], C[:, 1]); ang = np.arctan2(C[:, 1], C[:, 0]); inside = (C[:, 0] > 0) & (np.abs(ang) <= HA) & (rng <= RR)
    keys = [tuple(k) for k in K[inside]]; vals = np.array([G[k] for k in keys]) if keys else np.zeros(0)
    nobs = int((vals <= 0).sum()); new = chg = newobs = 0
    if prevG is not None:
        for k, v in zip(keys, vals):
            pv = prevG.get(k)
            if pv is None: new += 1
            elif abs(pv - v) > 0.02: chg += 1
            if v <= 0 and (pv is None or pv > 0): newobs += 1
    Z = last(sc, w); Lc = (Minv @ Mmb @ chain(Z[1]) @ Z[2].T).T; la = np.arctan2(Lc[:, 1], Lc[:, 0]); lr = np.hypot(Lc[:, 0], Lc[:, 1])
    nl = int(((Lc[:, 0] > 0) & (np.abs(la) <= HA) & (lr <= RR)).sum())
    print('%s | (%.2f, %.2f) %+.0f° | 아는 %d · 장애 %d · 새로 앎 %d · 바뀜 %d · 새 장애 %d | 라이다 %d' % (
        hs(w), Mmb[0, 2], Mmb[1, 2], math.degrees(math.atan2(Mmb[1, 0], Mmb[0, 0])), len(keys), nobs, new, chg, newobs, nl))
    prevG = G
