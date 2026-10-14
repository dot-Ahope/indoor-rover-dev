#!/usr/bin/env python3
"""anal_box_edge_growth — 사용자 지적 2 가지를 bag 과 계산으로 본다. (2026-10-14, 오늘만)
  ① 비스듬히 볼 때 번지는가: 상자 끝 둘레의 nvblox 칸을 **odom 좌표에 고정**해(지도 보정의 영향을 없앰) 처음 본 때부터 시야 밖으로 나갈 때까지
     어느 칸이 언제 장애물이 됐는지와, 그때 로버가 상자를 본 방향(상자의 북쪽 면에 대한 입사각)을 나란히 낸다. 비스듬해질수록 칸이 늘면 번짐.
  ② 격자와 나란하지 않아 계단이 되는가: 실제 상자(18 × 11 cm, 코스 문서)를 5 cm 격자에 여러 각도·여러 격자 어긋남으로 찍어, 면에서 바깥으로 얼마나 나가는지(칸 가장자리 기준) 계산.
  인자: bag 정지HH:MM:SS 시작HH:MM:SS"""
import sys, time, math
from pathlib import Path
import numpy as np
from scipy import ndimage
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
bag, hstop, hstart = sys.argv[1:4]
ts_ = get_typestore(Stores.ROS2_HUMBLE)
ts_.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
def T2(tr):
    q = tr.rotation; yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z)); c, s = math.cos(yaw), math.sin(yaw); return np.array([[c, -s, tr.translation.x], [s, c, tr.translation.y], [0, 0, 1]])
ob = []; mo = []; sl = []
with AnyReader([Path(bag)], default_typestore=ts_) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/nvblox_node/static_map_slice')]):
        ts = t / 1e9; m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob.append((ts, T2(tr.transform)))
                elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo.append((ts, T2(tr.transform)))
        else: sl.append((ts, m.origin.x, m.origin.y, m.resolution, m.unknown_value, np.asarray(m.data, np.float32).reshape(m.height, m.width)))
last = lambda L, t: L[max(np.searchsorted([x[0] for x in L], t, side='right') - 1, 0)]
day = time.strftime('%Y-%m-%d ', time.localtime(ob[0][0])); ep = lambda s: time.mktime(time.strptime(day + s, '%Y-%m-%d %H:%M:%S')); tA, tB = ep(hstart), ep(hstop)
# 정지 때 슬라이스에서 차체에 가장 가까운 장애물 칸 → 그 칸을 가운데로 odom 격자 7 × 7 칸 창을 고정
s = last(sl, tB); Mob = last(ob, tB)[1]; res = s[3]; L = np.argwhere(s[5] <= 0); P = np.c_[s[1] + (L[:, 1] + 0.5) * res, s[2] + (L[:, 0] + 0.5) * res]
pb = (np.linalg.inv(Mob) @ np.c_[P, np.ones(len(P))].T).T; d = np.hypot(np.maximum.reduce([-0.248 - pb[:, 0], np.zeros(len(pb)), pb[:, 0] - 0.262]), np.maximum.reduce([-0.165 - pb[:, 1], np.zeros(len(pb)), pb[:, 1] - 0.165]))
c0 = P[int(np.argmin(d))]; Mmo = last(mo, tB)[1]; cm = (Mmo @ np.r_[c0, 1])[:2]
print('%s: 차체에 가장 가까운 nvblox 장애물 칸 odom (%.3f, %.3f) = 지도 (%.2f, %.2f), 차체 여유 %.1f cm(칸 중심)' % (Path(bag).name, c0[0], c0[1], cm[0], cm[1], d.min() * 100))
N = 3; offs = [(i, j) for i in range(N, -N - 1, -1) for j in range(-N, N + 1)]
def window(t):
    s = last(sl, t); out = {}
    for i, j in offs:
        x, y = c0[0] + j * res, c0[1] + i * res; a = int(math.floor((y - s[2]) / res)); b = int(math.floor((x - s[1]) / res))
        out[(i, j)] = None if not (0 <= a < s[5].shape[0] and 0 <= b < s[5].shape[1]) else s[5][a, b]
    return out, s[4]
print('\n① odom 고정 창(7 × 7 칸, 가운데 = 위 칸, 위쪽 = odom +y)에서 장애물(거리 ≤ 0) 칸 수와 로버가 본 방향')
print('시각       로버→칸 거리  방위(로버 앞 기준)  창 안 장애물 칸  새로 생긴 칸  사라진 칸  | 가운데 줄 위로 1·2 줄(로버 쪽)의 장애물 칸 수')
prev = None; rows = []
for t in np.arange(tA, tB + 0.01, 1.0):
    w, unk = window(t); occ = {k for k, v in w.items() if v is not None and v != unk and v <= 0}; M = last(ob, t)[1]; rb = (np.linalg.inv(M) @ np.r_[c0, 1])[:2]
    # 로버 쪽이 어느 방향인지: 정지 때 로버 중심이 칸에서 본 방향의 부호(odom y)
    side = 1 if (Mob[1, 2] - c0[1]) > 0 else -1; up1 = sum(1 for (i, j) in occ if i == side); up2 = sum(1 for (i, j) in occ if i == 2 * side)
    new = len(occ - prev) if prev is not None else 0; gone = len(prev - occ) if prev is not None else 0; prev = occ
    rows.append((t, np.hypot(*rb), math.degrees(math.atan2(rb[1], rb[0])), len(occ), new, gone, up1, up2, occ))
    print('%s   %.2f m        %+4.0f°              %2d             %2d          %2d       | %d · %d' % (time.strftime('%H:%M:%S', time.localtime(t)), rows[-1][1], rows[-1][2], len(occ), new, gone, up1, up2))
def draw(occ): return '\n'.join('   ' + ' '.join(('#' if (i, j) in occ else '.') for j in range(-N, N + 1)) for i in range(N, -N - 1, -1))
first = next((r for r in rows if r[3] > 0), rows[0]); print('\n처음 장애물이 보인 때(%s, %.2f m, 방위 %+.0f°):\n%s' % (time.strftime('%H:%M:%S', time.localtime(first[0])), first[1], first[2], draw(first[8])))
print('정지 때(%s):\n%s' % (time.strftime('%H:%M:%S', time.localtime(rows[-1][0])), draw(rows[-1][8])))

print('\n② 실제 상자 18(y) × 11(x) cm 를 5 cm 격자에 찍었을 때, 한 면에서 바깥으로 나간 거리(칸 가장자리까지, cm): 평균 / 최대 — 격자 어긋남 400 가지')
rng = np.random.default_rng(0); W, Dp, R = 0.18, 0.11, 0.05
for ang in (0, 5, 10, 20, 30, 45):
    a = math.radians(ang); c, s_ = math.cos(a), math.sin(a); over = []
    for _ in range(400):
        ox, oy = rng.uniform(0, R, 2); g = np.arange(-8, 9); X, Y = np.meshgrid(ox + g * R, oy + g * R)   # 칸의 왼아래 모서리
        # 칸(정사각형)이 상자(회전 사각형)와 겹치는가: 칸의 네 모서리·중심을 상자 좌표로 옮겨 하나라도 안이면, 또는 상자 모서리가 칸 안이면
        hit = np.zeros(X.shape, bool)
        for dx, dy in ((0, 0), (R, 0), (0, R), (R, R), (R / 2, R / 2), (R / 2, 0), (0, R / 2), (R, R / 2), (R / 2, R)):
            px, py = X + dx, Y + dy; bx = c * px + s_ * py; by = -s_ * px + c * py; hit |= (np.abs(bx) <= Dp / 2) & (np.abs(by) <= W / 2)
        # 북쪽 면(상자 좌표 +y = W/2) 바깥으로 나간 최대 거리: 겹친 칸들의 모서리 중 by 최댓값 − W/2
        m_ = 0.0
        for dx, dy in ((0, 0), (R, 0), (0, R), (R, R)):
            px, py = X[hit] + dx, Y[hit] + dy; m_ = max(m_, float((-s_ * px + c * py).max()) - W / 2)
        over.append(m_)
    print('   격자와 %2d° 어긋남: %.1f / %.1f' % (ang, np.mean(over) * 100, np.max(over) * 100))
