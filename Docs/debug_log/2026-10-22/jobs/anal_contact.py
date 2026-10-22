#!/usr/bin/env python3
"""anal_contact — 차체 외곽(footprint)과 출발점 낮은 상자(기록 위치) 사이 최소 거리를 시간순으로, 가까울 때 그 순간 지도들이 상자를 갖고 있었는지(2026-10-22 §13, PC).
  왜: 사용자 — f2lp1 2 바퀴째 로버가 상자를 쳤다. 언제 · 어디서 닿았고, 그때 로컬 코스트맵(MPPI) · 전역 코스트맵(계획기) · nvblox 조각에 상자 칸이 있었는지.
  거리는 map 기준(SLAM) 차체 사각형 ↔ 상자 사각형. 0 이하 = 겹침(접촉 추정, SLAM 오차 수 cm 포함). 상자가 밀린 뒤 값은 의미 없음.
  출력: 거리 ≤ D 인 구간마다 시작 · 끝 · 최소 거리 시각 · 로버 자세 · 속도 지령, 최소 순간의 상자 영역 칸 수(로컬 LETHAL · 전역 LETHAL · 조각).
  인자: bag [D=0.10]"""
import sys, math, bisect, datetime
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
TS = get_typestore(Stores.ROS2_HUMBLE)
TS.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
bag = sys.argv[1]; DMAX = float(sys.argv[2]) if len(sys.argv) > 2 else 0.10
BOX = (1.151, 1.261, -0.20, -0.02); REG = (BOX[0] - 0.10, BOX[1] + 0.10, BOX[2] - 0.10, BOX[3] + 0.10)
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]])
KST = datetime.timezone(datetime.timedelta(hours=9))
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
def seg_rect(p, q):   # 선분 p→q 와 상자 사각형의 거리(표본)
    t = np.linspace(0, 1, 30)[:, None]; P = p + (q - p) * t
    dx = np.maximum(np.maximum(BOX[0] - P[:, 0], P[:, 0] - BOX[1]), 0); dy = np.maximum(np.maximum(BOX[2] - P[:, 1], P[:, 1] - BOX[3]), 0)
    return float(np.min(np.hypot(dx, dy)))
def inside_any(poly):
    xs, ys = np.meshgrid(np.linspace(BOX[0], BOX[1], 6), np.linspace(BOX[2], BOX[3], 8)); pts = np.c_[xs.ravel(), ys.ravel()]
    from matplotlib.path import Path as MP
    return MP(poly).contains_points(pts).any()
MO, OB, LC, GC, SL, CMD = [], [], [], [], [], []
with AnyReader([Path(bag)], default_typestore=TS) as rd:
    T0 = rd.start_time * 1e-9
    want = ('/tf', '/local_costmap/costmap', '/global_costmap/costmap', '/nvblox_node/static_map_slice', '/cmd_vel')
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in want]):
        tt = t * 1e-9 - T0; m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tt, v))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((tt, v))
        elif c.topic == '/cmd_vel': CMD.append((tt, m.linear.x, m.angular.z))
        elif c.topic.endswith('costmap'):
            g = m.info; (LC if c.topic.startswith('/local') else GC).append((tt, m.header.frame_id, g.origin.position.x, g.origin.position.y, g.resolution, np.array(m.data, np.int16).reshape(g.height, g.width)))
        else:
            d = np.array(m.data, np.float32).reshape(m.height, m.width); iy, ix = np.nonzero((d <= 0) & (d != m.unknown_value)); r = m.resolution
            SL.append((tt, m.header.frame_id, np.c_[m.origin.x + (ix + .5) * r, m.origin.y + (iy + .5) * r]))
for L in (MO, OB): L.sort(key=lambda q: q[0])
MOt = [q[0] for q in MO]; at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)]
LCt = [q[0] for q in LC]; GCt = [q[0] for q in GC]; SLt = [q[0] for q in SL]; CMt = [q[0] for q in CMD]
clock = lambda t: datetime.datetime.fromtimestamp(T0 + t, KST).strftime('%H:%M:%S.%f')[:11]
def cells(entry, t, lethal=100):
    tt, fr, ox, oy, r, A = entry; ys, xs = np.nonzero(A >= lethal); px, py = ox + (xs + .5) * r, oy + (ys + .5) * r
    if fr == 'odom':
        mo = at(MO, MOt, tt)[1]; c, s = math.cos(mo[2]), math.sin(mo[2]); px, py = mo[0] + c * px - s * py, mo[1] + s * px + c * py
    return int(np.sum((px >= REG[0]) & (px <= REG[1]) & (py >= REG[2]) & (py <= REG[3])))
def slcells(entry):
    tt, fr, P = entry; px, py = P[:, 0], P[:, 1]
    if fr != 'map':
        mo = at(MO, MOt, tt)[1]; c, s = math.cos(mo[2]), math.sin(mo[2]); px, py = mo[0] + c * P[:, 0] - s * P[:, 1], mo[1] + s * P[:, 0] + c * P[:, 1]
    return int(np.sum((px >= REG[0]) & (px <= REG[1]) & (py >= REG[2]) & (py <= REG[3])))
rows = []
for tt, ob in OB[::2]:
    if tt < MOt[0]: continue
    p = comp(at(MO, MOt, tt)[1], ob); c, s = math.cos(p[2]), math.sin(p[2]); poly = np.c_[p[0] + c * FP[:, 0] - s * FP[:, 1], p[1] + s * FP[:, 0] + c * FP[:, 1]]
    d = min(seg_rect(poly[i], poly[(i + 1) % 4]) for i in range(4))
    if d < 1e-6 and inside_any(poly): d = -0.01
    rows.append((tt, d, p))
print('bag %s · 차체 ↔ 상자(기록 위치) 최소 거리 ≤ %.2f m 구간 · 상자 영역 = 상자 ±0.10 m' % (Path(bag).name, DMAX))
seg = None
for i, (tt, d, p) in enumerate(rows + [(1e9, 9, None)]):
    if d <= DMAX and seg is None: seg = [i, i]
    elif d <= DMAX: seg[1] = i
    elif seg is not None:
        a, b = seg; k = min(range(a, b + 1), key=lambda j: rows[j][1]); tm, dm, pm = rows[k]
        cm = at(CMD, CMt, tm) if CMD else (0, 0, 0)
        print(' %s~%s (t %.1f~%.1f s) 최소 %+.3f m @ %s t %.1f · 로버 (%.2f, %.2f, %.0f°) · 지령 v %.3f ω %.2f | 상자 영역 칸: 로컬 LETHAL %d · 전역 LETHAL %d · 조각 %d'
              % (clock(rows[a][0]), clock(rows[b][0]), rows[a][0], rows[b][0], dm, clock(tm), tm, pm[0], pm[1], math.degrees(pm[2]), cm[1], cm[2],
                 cells(at(LC, LCt, tm), tm), cells(at(GC, GCt, tm), tm), slcells(at(SL, SLt, tm))))
        seg = None
