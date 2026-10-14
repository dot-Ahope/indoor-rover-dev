#!/usr/bin/env python3
"""anal_sw_turn — 남서 통로(f2t1 목표 4·5)에서 로버가 왜 상자 쪽으로 머리를 돌렸는지. (2026-10-14 §20, 오늘만)
  0.5 s 마다(odom 좌표 — 컨트롤러가 보는 좌표 그대로):
    로버 방향, 컨트롤러가 받은 경로(/transformed_global_plan)의 '가장 가까운 점에서 0.3 m 앞' 방향과 그 차(경로 오차),
    로버가 경로에서 옆으로 떨어진 거리(+ = 경로 왼쪽), 명령 v·ω, MPPI 최적 궤적(/trajectories 의 Optimal) 끝 방향,
    로컬 코스트맵 치명 칸(값 100 = 장애물 칸; 99 는 내접 띠라 차체 반폭만큼 부풀어 있어 옆 여유가 음수로 나옴 — 인자 5 로 고를 수 있음)까지 차체 왼쪽·오른쪽 옆 여유(차체 길이 범위 x −0.25~+0.26 안에서, 차체 옆면 0.165 에서 잰 거리).
  '상자 쪽으로 틀기' = ω 가 옆 여유가 더 작은 쪽으로 도는 0.5 s 칸. 그때 경로 오차·최적 궤적이 어느 쪽을 가리켰는지로 원인을 가른다.
  인자: bag 시작HH:MM:SS 끝HH:MM:SS [간격 s=0.5] [치명 문턱=100]"""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, h0, h1 = sys.argv[1:4]; DT = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5; LETH = int(sys.argv[5]) if len(sys.argv) > 5 else 100   # 100 = 치명(장애물 칸), 99 = 내접(차체 반폭 안)
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
wrap = lambda a: (a + math.pi) % (2 * math.pi) - math.pi
ob = []; cm = []; tg = []; lc = []; op = []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    day = None
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/cmd_vel', '/transformed_global_plan', '/local_costmap/costmap', '/trajectories')]):
        ts = t / 1e9
        if day is None: day = time.strftime('%Y-%m-%d ', time.localtime(ts)); A = time.mktime(time.strptime(day + h0, '%Y-%m-%d %H:%M:%S')); B = time.mktime(time.strptime(day + h1, '%Y-%m-%d %H:%M:%S'))
        if ts < A - 3 or ts > B + 1: continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob.append((ts, tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation)))
        elif c.topic == '/cmd_vel': cm.append((ts, m.linear.x, m.angular.z))
        elif c.topic == '/transformed_global_plan': tg.append((ts, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses])))
        elif c.topic == '/local_costmap/costmap':
            g = np.array(m.data, np.int16).reshape(m.info.height, m.info.width); lc.append((ts, m.info.origin.position.x, m.info.origin.position.y, m.info.resolution, g))
        else:
            pts = [(k.points[0].x, k.points[0].y) if k.points else (k.pose.position.x, k.pose.position.y) for k in m.markers if 'ptimal' in k.ns]
            if pts: op.append((ts, np.array(pts)))
ob = np.array(ob); cm = np.array(cm)
last = lambda L, t: next((x for x in reversed(L) if x[0] <= t), None)
print('optimal 궤적 메시지 %d 개, 경로 %d, 로컬 코스트맵 %d' % (len(op), len(tg), len(lc)))
print('시각      로버°  경로°  경로오차°  옆거리cm  v      ω      최적끝°  왼여유cm 오른여유cm  판정')
rows = []
for t in np.arange(A, B, DT):
    i = np.searchsorted(ob[:, 0], t);
    if i >= len(ob): break
    _, x, y, yw = ob[i]; c, s = math.cos(yw), math.sin(yw)
    k = (cm[:, 0] >= t) & (cm[:, 0] < t + DT); v = cm[k, 1].mean() if k.any() else 0.0; w = cm[k, 2].mean() if k.any() else 0.0
    P = last(tg, t); pe = lat = pdir = float('nan')
    if P is not None and len(P[1]) > 1:
        Q = P[1]; d = np.hypot(Q[:, 0] - x, Q[:, 1] - y); j = int(np.argmin(d)); acc = np.r_[0, np.cumsum(np.hypot(*np.diff(Q, axis=0).T))]
        j2 = int(np.searchsorted(acc, acc[j] + 0.3)); j2 = min(j2, len(Q) - 1)
        if j2 > j: pdir = math.atan2(Q[j2, 1] - Q[j, 1], Q[j2, 0] - Q[j, 0]); pe = math.degrees(wrap(pdir - yw))
        jn = min(j + 1, len(Q) - 1); jp = max(j - 1, 0); tdir = math.atan2(Q[jn, 1] - Q[jp, 1], Q[jn, 0] - Q[jp, 0])
        lat = 100 * (-(x - Q[j, 0]) * math.sin(tdir) + (y - Q[j, 1]) * math.cos(tdir))   # 경로 왼쪽 +
    O = last(op, t); oe = float('nan')
    if O is not None and len(O[1]) > 1: e = O[1][-1]; oe = math.degrees(wrap(math.atan2(e[1] - y, e[0] - x) - yw))
    L = last(lc, t); lm = rm = float('nan')
    if L is not None:
        _, ox, oy, r, g = L; iy, ix = np.nonzero(g >= LETH); wx = ox + (ix + 0.5) * r; wy = oy + (iy + 0.5) * r
        bx = c * (wx - x) + s * (wy - y); by = -s * (wx - x) + c * (wy - y); band = (bx > -0.25) & (bx < 0.26)
        lft = by[band & (by > 0)]; rgt = -by[band & (by < 0)]
        lm = 100 * (lft.min() - 0.165) if len(lft) else float('nan'); rm = 100 * (rgt.min() - 0.165) if len(rgt) else float('nan')
    tag = ''
    if abs(w) > 0.08 and not (math.isnan(lm) and math.isnan(rm)):
        near = 'L' if (np.nan_to_num(lm, nan=99) < np.nan_to_num(rm, nan=99)) else 'R'; turn = 'L' if w > 0 else 'R'
        tag = '상자쪽' if near == turn else '반대쪽'
        tag += '·경로도' if (not math.isnan(pe) and abs(pe) > 5 and (pe > 0) == (w > 0)) else '·경로와 반대' if not math.isnan(pe) and abs(pe) > 5 else '·경로 평행'
    rows.append((t, yw, pdir, pe, lat, v, w, oe, lm, rm, tag))
    print('%s  %+5.0f  %+5.0f  %+6.1f   %+6.1f   %+.3f %+.2f  %+6.0f   %6.1f   %6.1f    %s' % (time.strftime('%H:%M:%S', time.localtime(t)) + '.%d' % (int(round(t % 1 * 10)) % 10),
          math.degrees(yw), math.degrees(pdir), pe, lat, v, w, oe, lm, rm, tag))
# 요약
from collections import Counter
C = Counter(r[10] for r in rows if r[10]); print('\n회전 칸(|ω|>0.08) 분류:', dict(C))
