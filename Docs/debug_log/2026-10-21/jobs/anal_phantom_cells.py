#!/usr/bin/env python3
"""anal_phantom_cells — 전역 코스트맵의 LETHAL(값 100) 칸을 근거별로 나눈다: 저장 지도(/map 점유)에 있음 · 지금 라이다 점 근처 · 둘 다 아님(= 카메라 층만, '유령' 후보). (2026-10-21 §13, PC)
  사용자 관찰: 출발점에서 상자 뒤에 장애물 칸이 많이 찍히고, 문 가운데에도 뭔가 있다고 찍혔는데 실제로는 없었다.
  인자: bag 시각t(s, bag 시작 기준; 음수면 끝에서) 그림.png [창 x0,x1,y0,y1=-1.5,3.5,-2.5,1.5]
  ⚠ 코스트맵 메시지 값은 0~100(100 = LETHAL, 99 = INSCRIBED). 라이다 '근처' = 0.10 m 안(최근 1 s 스캔 10 장 합침), 지도 '있음' = 0.10 m 안 점유(≥ 65) 칸."""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
TS = get_typestore(Stores.ROS2_HUMBLE)
TS.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))   # 10-19 anal_slice_box.py 와 같은 정의
bag, tq, fig = sys.argv[1], float(sys.argv[2]), sys.argv[3]
W = [float(v) for v in sys.argv[4].split(',')] if len(sys.argv) > 4 else [-1.5, 3.5, -2.5, 1.5]
NEAR = 0.10


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])


GC, MP, SC, MO, OB, ST, SL = [], None, [], [], [], {}, []
with AnyReader([Path(bag)], default_typestore=TS) as rd:
    t0 = rd.start_time * 1e-9; tend = rd.end_time * 1e-9 - t0; T = tq if tq >= 0 else tend + tq
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/global_costmap/costmap', '/map', '/scan', '/tf', '/tf_static', '/nvblox_node/static_map_slice')]):
        tt = t * 1e-9 - t0
        if c.topic in ('/global_costmap/costmap', '/scan', '/nvblox_node/static_map_slice') and not (T - 3 <= tt <= T + 1.5): continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/nvblox_node/static_map_slice':
            d = np.array(m.data, np.float32).reshape(m.height, m.width); iy, ix = np.nonzero((d <= m.resolution) & (d != m.unknown_value))
            SL.append((tt, m.header.frame_id, np.c_[m.origin.x + (ix + 0.5) * m.resolution, m.origin.y + (iy + 0.5) * m.resolution])); continue
        if c.topic in ('/tf', '/tf_static'):
            for tr in m.transforms:
                a = (tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))
                if c.topic == '/tf_static': ST[tr.child_frame_id] = (tr.header.frame_id, a)
                elif tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tt, a))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((tt, a))
        elif c.topic == '/scan': SC.append((tt, m.angle_min, m.angle_increment, np.array(m.ranges)))
        else:
            g = m.info; A = np.array(m.data, dtype=np.int16).reshape(g.height, g.width)
            if c.topic == '/map': MP = (g.origin.position.x, g.origin.position.y, g.resolution, A)
            else: GC.append((tt, g.origin.position.x, g.origin.position.y, g.resolution, A))
at = lambda L, t: L[max(bisect.bisect_right([x[0] for x in L], t) - 1, 0)][1]
B2L = (0.0, 0.0, 0.0); f = 'lidar_link'; ch = []
while f in ST and f != 'base_link':
    p, a = ST[f]; ch.append(a); f = p
for a in reversed(ch): B2L = comp(B2L, a)
k = max(bisect.bisect_right([g[0] for g in GC], T) - 1, 0); tg, ox, oy, r, A = GC[k]
ys, xs = np.nonzero(A >= 100); cx, cy = ox + (xs + 0.5) * r, oy + (ys + 0.5) * r
inw = (cx >= W[0]) & (cx <= W[1]) & (cy >= W[2]) & (cy <= W[3]); cx, cy = cx[inw], cy[inw]
LP = []
for ts, a0, da, rg in SC:
    if not (tg - 1.0 <= ts <= tg + 0.1): continue
    P = comp(comp(at(MO, ts), at(OB, ts)), B2L); ok = np.isfinite(rg) & (rg > 0.05); an = a0 + da * np.arange(len(rg))
    LP.append(np.c_[P[0] + rg[ok] * np.cos(P[2] + an[ok]), P[1] + rg[ok] * np.sin(P[2] + an[ok])])
LP = np.vstack(LP); pose = comp(at(MO, tg), at(OB, tg))
mx, my, mr, MA = MP; mys, mxs = np.nonzero(MA >= 65); MPt = np.c_[mx + (mxs + 0.5) * mr, my + (mys + 0.5) * mr]


def near(px, py, Q):
    out = np.zeros(len(px), bool)
    for i in range(len(px)):
        d = np.hypot(Q[:, 0] - px[i], Q[:, 1] - py[i]); out[i] = d.min() <= NEAR
    return out


inmap = near(cx, cy, MPt); inlid = near(cx, cy, LP); ghost = ~inmap & ~inlid
# nvblox 자체 판단(슬라이스 거리 ≤ 1 칸 = 점유): 슬라이스 좌표계(odom) → map
ks = max(bisect.bisect_right([q[0] for q in SL], tg) - 1, 0) if SL else None
if SL:
    ts_, fr_, Q = SL[ks]; A_ = at(MO, ts_) if fr_ == 'odom' else (0.0, 0.0, 0.0); c_, s_ = math.cos(A_[2]), math.sin(A_[2])
    NV = np.c_[A_[0] + c_ * Q[:, 0] - s_ * Q[:, 1], A_[1] + s_ * Q[:, 0] + c_ * Q[:, 1]]
    innv = near(cx, cy, NV)
    print('nvblox 슬라이스 t=%.1f s (%s, 점유 %d 칸) — 유령 후보 %d 중 nvblox 가 점유로 봄 %d · nvblox 도 아님(라이다 층 기억 추정) %d' % (ts_, fr_, len(Q), ghost.sum(), (ghost & innv).sum(), (ghost & ~innv).sum()))
else:
    print('nvblox 슬라이스 없음')
print('bag %s · 코스트맵 t=%.1f s · 로버 (%.2f, %.2f, %.0f°) · 창 %s' % (Path(bag).name, tg, pose[0], pose[1], math.degrees(pose[2]), W))
print('창 안 LETHAL %d 칸: 지도에 있음 %d · 지도엔 없고 라이다 근처 %d · 둘 다 아님(카메라 층만) %d' % (len(cx), inmap.sum(), (~inmap & inlid).sum(), ghost.sum()))
# 카메라 층만 칸을 0.15 m 로 묶어 덩어리 위치 보고
gp = np.c_[cx[ghost], cy[ghost]]; lab = -np.ones(len(gp), int); n = 0
for i in range(len(gp)):
    if lab[i] >= 0: continue
    st = [i]; lab[i] = n
    while st:
        j = st.pop(); d = np.hypot(gp[:, 0] - gp[j, 0], gp[:, 1] - gp[j, 1])
        for q in np.nonzero((d <= 0.15) & (lab < 0))[0]: lab[q] = n; st.append(q)
    n += 1
for c in sorted(range(n), key=lambda c: -(lab == c).sum())[:10]:
    q = gp[lab == c]; print('  덩어리 %3d 칸 · 중심 (%.2f, %.2f) · 범위 x %.2f~%.2f y %.2f~%.2f · 로버에서 %.2f m' % (len(q), q[:, 0].mean(), q[:, 1].mean(), q[:, 0].min(), q[:, 0].max(), q[:, 1].min(), q[:, 1].max(), math.hypot(q[:, 0].mean() - pose[0], q[:, 1].mean() - pose[1])))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
fg, ax = plt.subplots(figsize=(10, 8.2))
mk = (MPt[:, 0] >= W[0]) & (MPt[:, 0] <= W[1]) & (MPt[:, 1] >= W[2]) & (MPt[:, 1] <= W[3])
ax.scatter(MPt[mk, 0], MPt[mk, 1], s=6, marker='s', c='#9aa0a6', label='저장 지도 벽(점유)')
for sel, col, lb in ((inmap, '#5b6770', 'LETHAL · 지도에 있음'), (~inmap & inlid, '#2e7d32', 'LETHAL · 지금 라이다가 봄'), (ghost, '#d81b60', 'LETHAL · 카메라 층만(유령 후보)')):
    ax.scatter(cx[sel], cy[sel], s=14, marker='s', c=col, label='%s %d' % (lb, sel.sum()))
lk = (LP[:, 0] >= W[0]) & (LP[:, 0] <= W[1]) & (LP[:, 1] >= W[2]) & (LP[:, 1] <= W[3])
ax.scatter(LP[lk, 0], LP[lk, 1], s=2, c='#1e88e5', label='라이다 점(최근 1 s)')
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165], [0.262, 0.165]]); c_, s_ = math.cos(pose[2]), math.sin(pose[2])
ax.plot(pose[0] + FP[:, 0] * c_ - FP[:, 1] * s_, pose[1] + FP[:, 0] * s_ + FP[:, 1] * c_, color='#f9a825', lw=2, label='로버')
ax.set_xlim(W[0], W[1]); ax.set_ylim(W[2], W[3]); ax.set_aspect('equal'); ax.grid(alpha=0.3); ax.legend(fontsize=8, loc='lower left')
ax.set_title('%s t=%.0f s 전역 LETHAL 칸의 근거' % (Path(bag).name, tg)); ax.set_xlabel('map x (m)'); ax.set_ylabel('map y (m)')
fg.tight_layout(); fg.savefig(fig, dpi=110); print('그림', fig)
