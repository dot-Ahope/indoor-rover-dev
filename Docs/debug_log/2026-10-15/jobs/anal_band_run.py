#!/usr/bin/env python3
"""anal_band_run — 주행 전체에서 차체(패딩 포함) ↔ 로컬 치명 칸 정확 여유와 Nav2 식 풋프린트 판정. (2026-10-15 §29.2, 오늘만)
  왜: §29.1 판정 ② — ClearanceBandCritic 뒤 상자 옆 최소 여유 ≥ 5 cm 인지, 칸 판정 경계 띠(2.7~4.4 cm) 안에 얼마나 있었는지.
  출력: 프레임 수, 최소 여유와 그때 시각 · 자세 · 칸 몸체 위치, 여유 구간별 프레임 수(< 2.7 · 2.7~4.4 · 4.4~6 · ≥ 6 cm), fp 100(서 있는 자세 '닿음') 프레임,
        여유 < 6 cm 였던 구간 목록(연속 프레임 묶음: 시작 · 끝 · 최소 · 칸 몸체 위치).
  anal_stall_entry.py 의 fp_cost · exact 와 같은 식. 인자: 이름=bag ..."""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore

# anal_stall_entry.py 는 인자 루프가 모듈 끝에 있어 import 하면 실행되므로 같은 함수를 여기에 둔다
XF, XR, HW = 0.272, -0.258, 0.175
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
hms = lambda ts: time.strftime('%H:%M:%S', time.localtime(ts)) + '.%d' % (int(ts * 10) % 10)


def bresenham(x0, y0, x1, y1):
    dx, dy = abs(x1 - x0), abs(y1 - y0); sx = 1 if x1 >= x0 else -1; sy = 1 if y1 >= y0 else -1; err = dx - dy; out = []
    while True:
        out.append((x0, y0))
        if x0 == x1 and y0 == y1: return out
        e2 = 2 * err
        if e2 > -dy: err -= dy; x0 += sx
        if e2 < dx: err += dx; y0 += sy


def fp_cost(a, info, P):
    cx, cy, cth = P; c, s = math.cos(cth), math.sin(cth); best = 0; cells = []
    for vx, vy in [(XF, HW), (XF, -HW), (XR, -HW), (XR, HW)]:
        wx = cx + c * vx - s * vy; wy = cy + s * vx + c * vy
        cells.append((int(math.floor((wx - info[0]) / info[2])), int(math.floor((wy - info[1]) / info[2]))))
    for i in range(4):
        for mx, my in bresenham(*cells[i], *cells[(i + 1) % 4]):
            if not (0 <= mx < a.shape[1] and 0 <= my < a.shape[0]): return 100
            v = int(a[my, mx]); best = max(best, v)
            if v >= 100: return 100
    return best


def exact(a, info, P):
    iy, ix = np.nonzero(a >= 100)
    if len(ix) == 0: return 9.0, (0, 0)
    wx = info[0] + (ix + 0.5) * info[2]; wy = info[1] + (iy + 0.5) * info[2]
    c, s = math.cos(P[2]), math.sin(P[2]); dx, dy = wx - P[0], wy - P[1]; bx = c * dx + s * dy; by = -s * dx + c * dy
    d = np.hypot(np.maximum(np.maximum(XR - bx, bx - XF), 0), np.maximum(np.abs(by) - HW, 0)); k = int(np.argmin(d))
    return float(d[k]), (float(bx[k]), float(by[k]))


for arg in sys.argv[1:]:
    nm, bag = arg.split('=')
    poses = []; rows = []
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        G = []
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/local_costmap/costmap')]):
            m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/tf':
                for tr in m.transforms:
                    if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                        poses.append((tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9, tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation)))
            else:
                G.append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, np.array(m.data, np.int16).reshape(m.info.height, m.info.width), (m.info.origin.position.x, m.info.origin.position.y, m.info.resolution)))
    poses.sort(); PT = np.array([p[0] for p in poses])
    for st, a, info in G:
        i = int(np.searchsorted(PT, st)); i = min(max(i, 1), len(poses) - 1); p = poses[i - 1] if abs(poses[i - 1][0] - st) < abs(poses[i][0] - st) else poses[i]
        P = p[1:]; d, cell = exact(a, info, P); rows.append((st, P, d, cell, fp_cost(a, info, P)))
    D = np.array([r[2] for r in rows]); k = int(np.argmin(D)); r = rows[k]
    bins = [(0, 0.027), (0.027, 0.044), (0.044, 0.06), (0.06, 99)]
    print('\n== %s · 로컬 코스트맵 %d 프레임(%s ~ %s)' % (nm, len(rows), hms(rows[0][0]), hms(rows[-1][0])))
    print('  최소 정확 여유 %.1f cm · %s · 자세 odom (%+.3f, %+.3f, %+.1f°) · 칸 몸체 (%+.3f, %+.3f) · 그때 fp %d' % (100 * r[2], hms(r[0]), r[1][0], r[1][1], math.degrees(r[1][2]), r[3][0], r[3][1], r[4]))
    print('  여유 구간 프레임: ' + ' · '.join('%s %d' % (lab, int(((D >= lo) & (D < hi)).sum())) for lab, (lo, hi) in zip(['< 2.7 cm', '2.7~4.4', '4.4~6', '≥ 6'], bins)))
    print('  fp 100(서 있는 자세 닿음) 프레임 %d' % sum(1 for r in rows if r[4] >= 100))
    # 여유 < 6 cm 연속 묶음
    seg = None
    for r in rows + [None]:
        if r is not None and r[2] < 0.06:
            if seg is None: seg = [r]
            else: seg.append(r)
        elif seg is not None:
            j = min(range(len(seg)), key=lambda q: seg[q][2]); s = seg[j]
            print('    < 6 cm 구간 %s ~ %s (%d 프레임) 최소 %.1f cm @ %s 칸 몸체 (%+.3f, %+.3f) 자세 (%+.2f, %+.2f, %+.0f°) fp 최대 %d'
                  % (hms(seg[0][0]), hms(seg[-1][0]), len(seg), 100 * s[2], hms(s[0]), s[3][0], s[3][1], s[1][0], s[1][1], math.degrees(s[1][2]), max(q[4] for q in seg)))
            seg = None
