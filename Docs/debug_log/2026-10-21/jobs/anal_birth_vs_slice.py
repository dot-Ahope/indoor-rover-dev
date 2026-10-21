#!/usr/bin/env python3
"""anal_birth_vs_slice — 전역 LETHAL 칸(저장 지도 밖)이 처음 생긴 그 순간, nvblox 슬라이스(바로 그때 받은 판)도 그 자리를 점유로 갖고 있었나. (2026-10-21 §13, PC)
  왜: 로버에서 4~6 m 떨어진 곳(통합 거리 1.4 m · nvblox 지도 지우기 반경 3 m 밖)에서도 칸이 새로 생겼다 → 출처가 nvblox 관측인지, 코스트맵 층이 옮겨 적는 단계인지 가른다.
  인자: bag [창 x0,x1,y0,y1]   출력: 탄생 칸을 로버 거리별(< 1.5 · 1.5~3 · > 3 m)로 나눠, 슬라이스에 있었음(0.10 m 안) 비율 · 슬라이스 범위 밖 비율."""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
TS = get_typestore(Stores.ROS2_HUMBLE)
TS.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
bag = sys.argv[1]; W = [float(v) for v in sys.argv[2].split(',')] if len(sys.argv) > 2 else [-1.5, 3.5, -2.5, 1.5]
yaw = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
GC, MP, MO, OB, SL, SC, ST = [], None, [], [], [], [], {}
with AnyReader([Path(bag)], default_typestore=TS) as rd:
    t0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/global_costmap/costmap', '/map', '/tf', '/tf_static', '/scan', '/nvblox_node/static_map_slice')]):
        m = rd.deserialize(raw, c.msgtype); tt = t * 1e-9 - t0
        if c.topic == '/scan':
            SC.append((tt, m.angle_min, m.angle_increment, np.array(m.ranges))); continue
        if c.topic in ('/tf', '/tf_static'):
            for tr in m.transforms:
                a = (tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))
                if c.topic == '/tf_static': ST[tr.child_frame_id] = (tr.header.frame_id, a); continue
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tt, a))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((tt, a))
        elif c.topic == '/nvblox_node/static_map_slice':
            d = np.array(m.data, np.float32).reshape(m.height, m.width); iy, ix = np.nonzero((d <= m.resolution) & (d != m.unknown_value))
            SL.append((tt, np.c_[m.origin.x + (ix + 0.5) * m.resolution, m.origin.y + (iy + 0.5) * m.resolution],
                       (m.origin.x, m.origin.x + m.width * m.resolution, m.origin.y, m.origin.y + m.height * m.resolution)))
        else:
            g = m.info; A = np.array(m.data, dtype=np.int16).reshape(g.height, g.width)
            if c.topic == '/map': MP = (g.origin.position.x, g.origin.position.y, g.resolution, A)
            else: GC.append((tt, g.origin.position.x, g.origin.position.y, g.resolution, A))
for L in (MO, OB): L.sort(key=lambda q: q[0])
MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]; SLt = [q[0] for q in SL]
at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]
def o2m(t, Q):
    a = at(MO, MOt, t); c, s = math.cos(a[2]), math.sin(a[2]); return np.c_[a[0] + c * Q[:, 0] - s * Q[:, 1], a[1] + s * Q[:, 0] + c * Q[:, 1]]
mx, my, mr, MA = MP; mys, mxs = np.nonzero(MA >= 65); MPt = np.c_[mx + (mxs + 0.5) * mr, my + (mys + 0.5) * mr]
seen, stat = set(), {}
SCt = [q[0] for q in SC]
def comp(a, b):
    c, s_ = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s_ * b[1], a[1] + s_ * b[0] + c * b[1], a[2] + b[2])
B2L = (0.0, 0.0, 0.0); f = 'lidar_link'; ch = []
while f in ST and f != 'base_link':
    pp, aa = ST[f]; ch.append(aa); f = pp
for aa in reversed(ch): B2L = comp(B2L, aa)
def lidar_pts(t):   # 직전 2 s 스캔(map 좌표)
    out = []
    for i in range(max(bisect.bisect_left(SCt, t - 2.0), 0), bisect.bisect_right(SCt, t)):
        ts_, a0, da, rg = SC[i]; P_ = comp(comp(at(MO, MOt, ts_), at(OB, OBt, ts_)), B2L); ok = np.isfinite(rg) & (rg > 0.05); an = a0 + da * np.arange(len(rg))
        out.append(np.c_[P_[0] + rg[ok] * np.cos(P_[2] + an[ok]), P_[1] + rg[ok] * np.sin(P_[2] + an[ok])])
    return np.vstack(out) if out else np.zeros((0, 2))
print('bag %s · 전역 코스트맵 %d 장 · nvblox 슬라이스 %d 장' % (Path(bag).name, len(GC), len(SL)))
for gi, (tt, ox, oy, r, A) in enumerate(GC):
    ys, xs = np.nonzero(A >= 100); P = np.c_[ox + (xs + 0.5) * r, oy + (ys + 0.5) * r]
    P = P[(P[:, 0] >= W[0]) & (P[:, 0] <= W[1]) & (P[:, 1] >= W[2]) & (P[:, 1] <= W[3])]
    new = [p for p in P if (round(p[0], 2), round(p[1], 2)) not in seen]
    for p in P: seen.add((round(p[0], 2), round(p[1], 2)))
    if gi == 0 or not new: continue   # 첫 장은 녹화 전부터 있던 것
    new = np.array(new); new = new[np.array([np.hypot(MPt[:, 0] - p[0], MPt[:, 1] - p[1]).min() > 0.10 for p in new])]
    if not len(new): continue
    k = max(bisect.bisect_right(SLt, tt) - 1, 0); ts, Q, bb = SL[k]; QM = o2m(ts, Q); LPb = lidar_pts(tt)
    a = at(MO, MOt, tt); b = at(OB, OBt, tt); c, s = math.cos(a[2]), math.sin(a[2]); rx, ry = a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1]
    for p in new:
        d = math.hypot(p[0] - rx, p[1] - ry); band = '< 1.5 m' if d < 1.5 else ('1.5~3 m' if d < 3 else '> 3 m')
        insl = len(QM) and np.hypot(QM[:, 0] - p[0], QM[:, 1] - p[1]).min() <= 0.10
        # 슬라이스 범위(odom) 안인가
        po = p - np.array([a[0], a[1]]); po = np.array([c * po[0] + s * po[1], -s * po[0] + c * po[1]])
        inbb = bb[0] <= po[0] <= bb[1] and bb[2] <= po[1] <= bb[3]
        inl = len(LPb) and np.hypot(LPb[:, 0] - p[0], LPb[:, 1] - p[1]).min() <= 0.10
        st = stat.setdefault(band, [0, 0, 0, 0]); st[0] += 1; st[1] += bool(insl); st[2] += (not inbb); st[3] += bool(inl)
for band in ('< 1.5 m', '1.5~3 m', '> 3 m'):
    if band in stat:
        n, a1, a2, a3 = stat[band]; print('  로버에서 %-7s: 새 칸 %4d · 그 순간 슬라이스에도 점유 %4d (%.0f %%) · 슬라이스 범위 밖 %d · 직전 2 s 라이다 점 0.10 m 안 %d (%.0f %%)' % (band, n, a1, 100 * a1 / n, a2, a3, 100 * a3 / n))
