#!/usr/bin/env python3
"""anal_box_outside — 복귀 때 상자 칸 밖(테두리 밖)에 찍힌 nvblox 칸이 언제 · 어디서 본 것인지(2026-10-22 §11, PC).
  왜: 사용자 — 프리셋 3 그림에서 "복귀 시 상자 칸 밖에 노란색 칸이 찍힌 것" 이 아쉽다. 그 칸이 처음 생긴 순간의 로버 자세 · 거리 · 방위와,
      그 뒤 map→odom 보정이 얼마나 움직였는지(nvblox 는 odom 좌표로 기억 → 보정만큼 지도에서 밀림, 10-13 §12.2)를 본다.
  인자: 주행bag [창 시작 s=120] [영역 x0,x1,y0,y1=1.05,1.40,-0.35,0.20]"""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
TS = get_typestore(Stores.ROS2_HUMBLE)
TS.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
BOX = (1.151, 1.261, -0.20, -0.02); C = 0.05
bag = sys.argv[1]; TA = float(sys.argv[2]) if len(sys.argv) > 2 else 120
X0, X1, Y0, Y1 = (float(v) for v in (sys.argv[3] if len(sys.argv) > 3 else '1.05,1.40,-0.35,0.20').split(','))
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
MO, OB, SL = [], [], []
with AnyReader([Path(bag)], default_typestore=TS) as rd:
    T0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/nvblox_node/static_map_slice')]):
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9; v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((st, v))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((st, v))
        else:
            st = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
            # 처음 찍힌 시각을 주행 처음부터 찾음(창 앞 60 s 만 보면 기억된 칸이 로버 뒤에서 생긴 것처럼 보임 — 첫 실행 출력에서 방위 +160~176° 로 드러남)
            d = np.array(m.data, np.float32).reshape(m.height, m.width); iy, ix = np.nonzero((d <= 0) & (d != m.unknown_value)); r = m.resolution
            SL.append((st, np.c_[m.origin.x + (ix + .5) * r, m.origin.y + (iy + .5) * r]))
MO.sort(); OB.sort(); MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]
at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]
first = {}; seen = {}; nwin = 0
for st, P in SL:
    tt = st - T0; mo = at(MO, MOt, st); c, s = math.cos(mo[2]), math.sin(mo[2])
    gx = mo[0] + c * P[:, 0] - s * P[:, 1]; gy = mo[1] + s * P[:, 0] + c * P[:, 1]; k = (gx >= X0) & (gx <= X1) & (gy >= Y0) & (gy <= Y1)
    cells = set(zip(np.floor(gx[k] / C).astype(int), np.floor(gy[k] / C).astype(int)))
    if tt >= TA: nwin += 1
    for q in cells:
        if q not in first: first[q] = (tt, st, comp(mo, at(OB, OBt, st)), P[k][0] if k.any() else None)
        if tt >= TA: seen[q] = seen.get(q, 0) + 1
print('bag %s · 창 t ≥ %.0f s 조각 %d · 영역 x %.2f~%.2f y %.2f~%.2f · 상자 x %.3f~%.3f y %.3f~%.3f' % (Path(bag).name, TA, nwin, X0, X1, Y0, Y1, *BOX))
print(' 칸(왼아래 x,y) | 상자 안? | 창 안 비율 | 처음 찍힌 t | 그때 로버 map (x, y, yaw) · 칸까지 거리 · 방위 | 그 뒤 창 끝까지 map→odom 이동')
mo_end = MO[-1][1]
for q in sorted(seen, key=lambda q: (-q[1], q[0])):
    x, y = q[0] * C, q[1] * C; inside = (x + C > BOX[0]) and (x < BOX[1]) and (y + C > BOX[2]) and (y < BOX[3])
    tt, st, p, _ = first[q]; d = math.hypot(x + C / 2 - p[0], y + C / 2 - p[1]); b = math.degrees(math.atan2(math.sin(math.atan2(y + C / 2 - p[1], x + C / 2 - p[0]) - p[2]), math.cos(math.atan2(y + C / 2 - p[1], x + C / 2 - p[0]) - p[2])))
    m0 = at(MO, MOt, st); dm = math.hypot(mo_end[0] - m0[0], mo_end[1] - m0[1])
    print(' (%.2f, %5.2f) | %s | %3.0f %% | %6.1f s | (%5.2f, %5.2f, %5.0f°) · %.2f m · %+4.0f° | %.3f m · %+.1f°' % (x, y, '안' if inside else '밖', 100 * seen[q] / max(nwin, 1), tt, p[0], p[1], math.degrees(p[2]), d, b, dm, math.degrees(mo_end[2] - m0[2])))
