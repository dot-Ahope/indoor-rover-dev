#!/usr/bin/env python3
"""chk_gcm_odd — §15 앞뒤와 크게 다른 전역 코스트맵 프레임이 무엇과 겹치나 (2026-10-27, PC).
  · /map(SLAM) 수신 시각 · 크기 · 원점, map→odom TF 변화(같은 창)
  · 이상 프레임 vs 직전 프레임: 치명 칸 집합을 (dx, dy) 칸만큼 옮겨 겹침이 최대인 이동량, 바뀐 칸이 static(벽) 쪽인지 상자 쪽인지
  인자: bag폴더 시작HH:MM:SS 끝HH:MM:SS"""
import sys, time, math
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag = Path(sys.argv[1])
t0 = time.mktime(time.strptime('2026-10-27 ' + sys.argv[2], '%Y-%m-%d %H:%M:%S')); t1 = time.mktime(time.strptime('2026-10-27 ' + sys.argv[3], '%Y-%m-%d %H:%M:%S'))
hs = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + '.%02d' % int((t % 1) * 100)
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
G = []; mo = []
with AnyReader([bag], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/map', '/global_costmap/costmap', '/tf')]):
        ts = t * 1e-9
        if ts < t0 - 15 or ts > t1: continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                    mo.append((ts, tr.transform.translation.x, tr.transform.translation.y, math.degrees(yaw(tr.transform.rotation))))
            continue
        i = m.info; g = np.array(m.data, np.int8).reshape(i.height, i.width)
        if c.topic == '/map':
            print('/map 수신 %s stamp %s 원점 (%.2f, %.2f) %dx%d 점유 %d' % (hs(ts), hs(m.header.stamp.sec + m.header.stamp.nanosec * 1e-9), i.origin.position.x, i.origin.position.y, i.width, i.height, int((g == 100).sum())))
        elif ts >= t0: G.append((ts, g, i.origin.position.x, i.origin.position.y, i.resolution))
# map→odom 변화(0.5 s 간격 마지막 값)
print('map→odom (x, y, yaw°):')
last = -1
for ts, x, y, a in mo:
    if ts >= t0 and ts - last >= 1.0: print('  %s (%.3f, %.3f, %.2f)' % (hs(ts), x, y, a)); last = ts
for k in range(1, len(G) - 1):
    ts, g, ox, oy, r = G[k]; p = G[k - 1][1]; n = G[k + 1][1]
    d = int((g != p).sum())
    if d < 2500: continue
    L = g == 100; Lp = p == 100
    best = max(((int((np.roll(np.roll(Lp, dy, 0), dx, 1) & L).sum()), dx, dy) for dx in range(-6, 7) for dy in range(-6, 7)))
    print('\n이상 프레임 %s: 직전과 다른 칸 %d · 다음과 다른 칸 %d · 직전↔다음 다른 칸 %d' % (hs(ts), d, int((g != n).sum()), int((p != n).sum())))
    print('  치명 칸 수 %d (직전 %d) · 겹침 최대 이동 dx %+d dy %+d 칸 = (%+.2f, %+.2f) m, 겹침 %d (이동 0 이면 %d)' % (
        L.sum(), Lp.sum(), best[1], best[2], best[1] * r, best[2] * r, best[0], int((L & Lp).sum())))
    ch = np.argwhere(g != p); W = np.c_[ox + (ch[:, 1] + .5) * r, oy + (ch[:, 0] + .5) * r]
    print('  바뀐 칸 범위 x %.2f~%.2f y %.2f~%.2f · 값 변화 예:' % (W[:, 0].min(), W[:, 0].max(), W[:, 1].min(), W[:, 1].max()),
          [(round(float(a), 2), round(float(b), 2), int(p[j, i]), int(g[j, i])) for (j, i), (a, b) in list(zip(ch, W))[::max(1, len(ch) // 6)]][:6])
