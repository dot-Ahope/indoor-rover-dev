#!/usr/bin/env python3
"""anal_motion_probe — 한 순간의 로컬 코스트맵 위에 차체(패딩 포함 직사각형)를 기본 움직임대로 옮겨 놓고, 치명 칸(100)에 닿는지 · 가장 가까운 치명 칸까지 거리. (2026-10-15 §5, 오늘만)
  왜: f2v1 목표 4(남쪽)는 같은 자리에서 '후보 전부 충돌', 복귀(북쪽)는 바로 움직였다(§4). 두 순간에 어떤 움직임이 막혔는지 비교.
  규칙: MPPI CostCritic(consider_footprint) 은 차체 모양이 치명 칸에 닿으면 충돌(humble 소스, 10-14 §20). 여기서는 차체 넓이 전체로 검사(가장자리만 보는 Nav2 보다 약간 엄격).
  움직임: 전진 0.10 · 0.20 · 0.26 m, 후진 0.05 · 0.10 m, 제자리 회전 ±15 · ±30 · ±60 · ±90 · ±150°, 전진 0.15 m + 좌/우 20°.
  인자: 이름=bag@HH:MM:SS.f ..."""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
XF, XR, HW = 0.272, -0.258, 0.175
MOVES = [('정지', 0, 0)] + [('전진 %.2f' % d, d, 0) for d in (0.10, 0.20, 0.26)] + [('후진 %.2f' % d, -d, 0) for d in (0.05, 0.10)] + \
        [('회전 %+d°' % a, 0, a) for a in (15, -15, 30, -30, 60, -60, 90, -90, 150, -150)] + [('전진 0.15 + 좌 20°', 0.15, 20), ('전진 0.15 + 우 20°', 0.15, -20)]
for spec in sys.argv[1:]:
    nm, rest = spec.split('='); bag, hh = rest.split('@'); hms, _, fr = hh.partition('.'); ob = None; lc = None
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        T = None
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/local_costmap/costmap')]):
            ts = t / 1e9
            if T is None: T = time.mktime(time.strptime(time.strftime('%Y-%m-%d ', time.localtime(ts)) + hms, '%Y-%m-%d %H:%M:%S')) + (float('0.' + fr) if fr else 0)
            if ts > T: break
            m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/tf':
                for tr in m.transforms:
                    if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
            else: lc = m
    a = np.array(lc.data, np.int16).reshape(lc.info.height, lc.info.width); iy, ix = np.nonzero(a >= 100)
    wx = lc.info.origin.position.x + (ix + 0.5) * lc.info.resolution; wy = lc.info.origin.position.y + (iy + 0.5) * lc.info.resolution
    print('\n== %s %s  로버 odom (%.2f, %.2f, %+.0f°) · 코스트맵 %.1f s 전' % (nm, hh, ob[0], ob[1], math.degrees(ob[2]), 0.0))
    res = []
    for lab, d, da in MOVES:
        # 전진·후진은 지금 방향으로, 회전은 제자리, 조합은 전진 뒤 회전
        x = ob[0] + d * math.cos(ob[2]); y = ob[1] + d * math.sin(ob[2]); th = ob[2] + math.radians(da)
        c_, s_ = math.cos(th), math.sin(th); bx = c_ * (wx - x) + s_ * (wy - y); by = -s_ * (wx - x) + c_ * (wy - y)
        inside = (bx >= XR) & (bx <= XF) & (np.abs(by) <= HW)
        dx = np.maximum(np.maximum(XR - bx, bx - XF), 0); dy = np.maximum(np.abs(by) - HW, 0); dist = np.where(inside, 0, np.hypot(dx, dy))
        k = int(np.argmin(dist)); side = ('앞' if bx[k] > 0 else '뒤') + ('왼' if by[k] > 0 else '오')
        res.append('%-18s %s  최근접 %4.1f cm(%s)' % (lab, '충돌' if inside.any() else '  ok', 100 * dist[k], side))
    for i in range(0, len(res), 2): print('   ' + '   |   '.join(res[i:i + 2]))
