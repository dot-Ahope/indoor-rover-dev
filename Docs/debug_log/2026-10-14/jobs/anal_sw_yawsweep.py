#!/usr/bin/env python3
"""anal_sw_yawsweep — 그 시각 그 자리에서 로버 방향만 바꿔 놓았다면 차체(패딩 포함 직사각형)가 로컬 코스트맵에서 얼마나 여유·비용을 갖는지. (2026-10-14 §20, 오늘만)
  왜: 남서 통로에서 로버가 서서 경로 방향 대신 장애물이 가까운 쪽으로 머리를 돌렸다(anal_sw_turn). MPPI CostCritic 은 차체 칸 비용을 본다 —
      경로 방향으로 돌면 차체 어느 모서리가 더 비싼 칸에 들어가는지 확인한다.
  출력: 방향(odom °)별 — 차체 안 최대 비용(0~100, 99 = 내접·100 = 치명), 차체 둘레 15 cm 띠 안 비용 합, 가장 가까운 치명 칸까지 거리(차체 밖이면 +) 와 그 칸이 차체의 어느 쪽(앞왼·앞오·뒤왼·뒤오).
  인자: bag HH:MM:SS[.f] [HH:MM:SS ...]"""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag = sys.argv[1]; whens = sys.argv[2:]
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
XF, XR, HW = 0.262 + 0.01, -0.248 - 0.01, 0.165 + 0.01   # 발행 풋프린트 + 패딩 0.01
ob = []; lc = []; tg = []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/local_costmap/costmap', '/transformed_global_plan')]):
        m = rd.deserialize(raw, c.msgtype); ts = t / 1e9
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob.append((ts, tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation)))
        elif c.topic == '/local_costmap/costmap':
            lc.append((ts, m.info.origin.position.x, m.info.origin.position.y, m.info.resolution, np.array(m.data, np.int16).reshape(m.info.height, m.info.width)))
        else: tg.append((ts, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses])))
ob = np.array(ob); day = time.strftime('%Y-%m-%d ', time.localtime(ob[0, 0]))
for w in whens:
    hms, _, fr = w.partition('.'); t = time.mktime(time.strptime(day + hms, '%Y-%m-%d %H:%M:%S')) + (float('0.' + fr) if fr else 0)
    i = min(np.searchsorted(ob[:, 0], t), len(ob) - 1); _, x, y, yw = ob[i]
    L = next(v for v in reversed(lc) if v[0] <= t); _, ox, oy, r, g = L
    P = next(v for v in reversed(tg) if v[0] <= t)[1]; d = np.hypot(P[:, 0] - x, P[:, 1] - y); j = int(np.argmin(d)); j2 = min(j + 8, len(P) - 1)
    pdir = math.degrees(math.atan2(P[j2, 1] - P[j, 1], P[j2, 0] - P[j, 0]))
    iy, ix = np.indices(g.shape); wx = ox + (ix + 0.5) * r; wy = oy + (iy + 0.5) * r
    print('\n== %s  로버 (%.2f, %.2f) 방향 %+.0f° · 경로 방향 %+.0f°(가까운 점에서 8 점 앞) · 코스트맵 %.1f s 전' % (w, x, y, math.degrees(yw), pdir, t - L[0]))
    print('   방향°   차체안 최대   둘레15cm 비용합   가장 가까운 치명 칸 (cm, 어느 쪽)')
    cand = sorted(set([round(math.degrees(yw))] + [round(pdir)] + list(range(int(round(math.degrees(yw))) - 30, int(round(math.degrees(yw))) + 31, 5))))
    for deg in cand:
        a = math.radians(deg); c, s = math.cos(a), math.sin(a)
        bx = c * (wx - x) + s * (wy - y); by = -s * (wx - x) + c * (wy - y)
        inside = (bx >= XR) & (bx <= XF) & (np.abs(by) <= HW)
        dx = np.maximum(np.maximum(XR - bx, bx - XF), 0); dy = np.maximum(np.abs(by) - HW, 0); dist = np.hypot(dx, dy)
        ring = (~inside) & (dist <= 0.15)
        leth = g >= 100; mx = int(g[inside].max()) if inside.any() else -1
        if leth.any():
            dd = np.where(leth, np.where(inside, -1.0, dist), 9.0); k = np.unravel_index(np.argmin(dd), dd.shape)
            side = ('앞' if bx[k] > 0 else '뒤') + ('왼' if by[k] > 0 else '오')
            nl = '%5.1f %s' % (100 * dd[k], side)
        else: nl = '-'
        tag = ' ← 지금' if deg == round(math.degrees(yw)) else (' ← 경로' if deg == round(pdir) else '')
        print('   %+5d    %5d        %7d          %s%s' % (deg, mx, int(np.clip(g[ring], 0, 100).sum()), nl, tag))
