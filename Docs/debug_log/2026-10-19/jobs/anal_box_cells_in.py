#!/usr/bin/env python3
"""anal_box_cells_in — nvblox 조각에서 '실제 상자 안' 칸 수와 상자 주변 칸 무리의 위치를 시간에 따라. (2026-10-19 §22)
  왜: 사용자 — 복귀 때 상자 범위 안에 칸이 없어 보인다(§21 그림). 상자가 지워졌나, 옆으로 밀려 찍혔나.
  칸 = 조각 거리 ≤ 0(표면 안), 그 조각 시각의 map→odom 으로 지도에. 상자 안 = 칸 중심이 실제 상자(x 1.151~1.261, y −0.20~−0.02) 안.
  주변 무리 = x 0.9~1.5, y −0.35~+0.15 의 칸(남쪽 창문틀 띠 y < −0.35 제외) — 중심 · 개수.
  같이: 출발 길 통과 순간 대비 map→odom 변화(odom 에 기억된 칸이 지도에서 밀리는 양, §11).
  출력: 상자 옆 구간(로버가 x 0.9~1.7, |y| < 0.6) 조각마다 요약 + 구간별 중앙값. 인자: 이름=주행bag ..."""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
TS = get_typestore(Stores.ROS2_HUMBLE)
TS.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
BOX = (1.151, 1.261, -0.20, -0.02); NB = (0.9, 1.5, -0.35, 0.15)
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
comp = lambda A, B: (A[0] + math.cos(A[2]) * B[0] - math.sin(A[2]) * B[1], A[1] + math.sin(A[2]) * B[0] + math.cos(A[2]) * B[1], A[2] + B[2])
for arg in sys.argv[1:]:
    nm, bag = arg.split('='); MO, OB, SL = [], [], []
    with AnyReader([Path(bag)], default_typestore=TS) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/nvblox_node/static_map_slice')]):
            m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/tf':
                for tr in m.transforms:
                    st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9; v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                    if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((st, v))
                    elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((st, v))
            else:
                d = np.array(m.data, np.float32).reshape(m.height, m.width); iy, ix = np.nonzero((d <= 0) & (d != m.unknown_value))
                SL.append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, m.origin.x + (ix + 0.5) * m.resolution, m.origin.y + (iy + 0.5) * m.resolution))
    MO.sort(); OB.sort(); MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]; t0 = MOt[0]
    at = lambda L, T, t: L[max(bisect.bisect_right(T, t) - 1, 0)][1]
    rows = []
    for st, lx, ly in SL:
        mo = at(MO, MOt, st); P = comp(mo, at(OB, OBt, st))
        if not (0.9 <= P[0] <= 1.7 and abs(P[1]) < 0.6): continue
        gx = mo[0] + math.cos(mo[2]) * lx - math.sin(mo[2]) * ly; gy = mo[1] + math.sin(mo[2]) * lx + math.cos(mo[2]) * ly
        inb = (gx > BOX[0]) & (gx < BOX[1]) & (gy > BOX[2]) & (gy < BOX[3]); nb = (gx > NB[0]) & (gx < NB[1]) & (gy > NB[2]) & (gy < NB[3])
        rows.append((st, int(inb.sum()), int(nb.sum()), gx[nb].mean() if nb.any() else np.nan, gy[nb].mean() if nb.any() else np.nan, mo))
    T = [r[0] for r in rows]; cuts = [0] + [i for i in range(1, len(T)) if T[i] - T[i - 1] > 5] + [len(T)]
    segs = list(zip(cuts, cuts[1:])); mo_out = rows[segs[0][0]][5]
    print('== %s (상자 중심 (1.206, −0.110), 실제 상자 안에 칸 중심이 들 수 있는 최대 ≈ 2×4 = 8 칸)' % nm)
    for si, (a, b) in enumerate(segs):
        R = rows[a:b]; inn = np.array([r[1] for r in R]); nbn = np.array([r[2] for r in R])
        cxm = np.nanmedian([r[3] for r in R]); cym = np.nanmedian([r[4] for r in R]); mo = R[len(R) // 2][5]
        dmo = (100 * (mo[0] - mo_out[0]), 100 * (mo[1] - mo_out[1]), math.degrees(mo[2] - mo_out[2]))
        print('  %s t %.1f~%.1f s · 조각 %d · 상자 안 칸 중앙 %.0f (범위 %d~%d, 0 칸인 조각 %d) · 주변 칸 중앙 %.0f · 주변 무리 중심 (%.3f, %.3f) = 상자 중심 대비 (%+.1f, %+.1f) cm · map→odom 출발 길 대비 (%+.1f, %+.1f cm, %+.2f°)'
              % (['출발 길', '복귀 길'][min(si, 1)], R[0][0] - t0, R[-1][0] - t0, len(R), np.median(inn), inn.min(), inn.max(), int((inn == 0).sum()), np.median(nbn), cxm, cym,
                 100 * (cxm - 1.206), 100 * (cym + 0.110), *dmo))
