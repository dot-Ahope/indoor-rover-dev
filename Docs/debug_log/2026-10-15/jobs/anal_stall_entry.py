#!/usr/bin/env python3
"""anal_stall_entry — 멈춤 직전 몇 초, 로버가 어떻게 'Nav2 칸 검사로 서 있는 자세부터 닿음' 상태에 들어갔는지. (2026-10-15 §28, 오늘만)
  왜: 사용자 "MPPI 가 스스로 빠져나올 수 있다면 갑자기 멈춰서 움직이지 못하는 문제는 왜 발생하는가?" — 들어가는 경로 후보
      (가) 지도가 로버 밑에서 바뀜(칸이 새로 생기거나 두꺼워짐 · 기억 밀림) (나) 실제 움직임이 예측과 어긋남(미끄러짐) (다) MPPI 가 낸 최적 궤적 자체가 이미 칸 검사로 닿음.
  방법(로컬 코스트맵 프레임마다, odom 좌표):
    fp_now  = 그 순간 실제 자세의 Nav2 식 풋프린트 비용(꼭짓점 → 칸 내림, 변을 Bresenham 으로 따라 최대; 100 = 치명) — nav2_costmap_2d FootprintCollisionChecker 와 같은 식
    fp_prev = 같은 자세를 바로 앞 프레임 지도에 놓았을 때 → fp_now 치명 · fp_prev 아님 = 지도가 바뀌어 막힘(가)
    fp_was  = 앞 프레임 자세를 이 프레임 지도에 → 앞 자세도 이 지도에선 이미 막힘 = 지도 변화, 아니면 움직임으로 들어감
    new8    = 이 프레임에서 새로 치명이 된 칸 중 차체 8 cm 안 개수
    opt     = 직전 최적 궤적(32 점)을 이 지도에 놓았을 때 최대 풋프린트 비용 · 처음 치명 점 번호(다)
    dev     = 0.5 s 전 최적 궤적이 지금 시각에 예측한 자세와 실제 자세 차이(몸체 옆 방향 cm, 앞 방향 cm, yaw °)(나)
    exact   = 차체(패딩 포함 직사각형) ↔ 치명 칸 중심 정확 최소 거리
  인자: 이름=bag@HH:MM:SS.f@앞초 ..."""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore

XF, XR, HW = 0.272, -0.258, 0.175   # 로컬 코스트맵 풋프린트(패딩 0.01 포함) — nav2_params.yaml
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def hms(ts):
    return time.strftime('%H:%M:%S', time.localtime(ts)) + '.%d' % (int(ts * 10) % 10)


def bresenham(x0, y0, x1, y1):
    # nav2_util LineIterator 와 같은 정수 직선
    dx, dy = abs(x1 - x0), abs(y1 - y0); sx = 1 if x1 >= x0 else -1; sy = 1 if y1 >= y0 else -1; err = dx - dy; out = []
    while True:
        out.append((x0, y0))
        if x0 == x1 and y0 == y1: return out
        e2 = 2 * err
        if e2 > -dy: err -= dy; x0 += sx
        if e2 < dx: err += dx; y0 += sy


def fp_cost(G, P):
    """Nav2 FootprintCollisionChecker::footprintCostAtPose 와 같은 식. 지도 밖이면 치명으로."""
    a, info = G
    cx, cy, cth = P; c, s = math.cos(cth), math.sin(cth); best = 0
    vs = [(XF, HW), (XF, -HW), (XR, -HW), (XR, HW)]
    cells = []
    for vx, vy in vs:
        wx = cx + c * vx - s * vy; wy = cy + s * vx + c * vy
        mx = int(math.floor((wx - info[0]) / info[2])); my = int(math.floor((wy - info[1]) / info[2])); cells.append((mx, my))
    for i in range(4):
        for mx, my in bresenham(*cells[i], *cells[(i + 1) % 4]):
            if not (0 <= mx < a.shape[1] and 0 <= my < a.shape[0]): return 100
            v = int(a[my, mx]); best = max(best, v)
            if v >= 100: return 100
    return best


def exact(G, P):
    a, info = G; iy, ix = np.nonzero(a >= 100)
    if len(ix) == 0: return 9.0, (0, 0)
    wx = info[0] + (ix + 0.5) * info[2]; wy = info[1] + (iy + 0.5) * info[2]
    c, s = math.cos(P[2]), math.sin(P[2]); dx, dy = wx - P[0], wy - P[1]; bx = c * dx + s * dy; by = -s * dx + c * dy
    d = np.hypot(np.maximum(np.maximum(XR - bx, bx - XF), 0), np.maximum(np.abs(by) - HW, 0)); k = int(np.argmin(d))
    return float(d[k]), (float(bx[k]), float(by[k]))


for spec in sys.argv[1:]:
    nm, rest = spec.split('='); bag, hh, back = rest.split('@'); back = float(back); hm, _, fr = hh.partition('.')
    poses = []; grids = []; opts = []; T = None
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        cons = [c for c in rd.connections if c.topic in ('/tf', '/local_costmap/costmap', '/trajectories')]
        for c, t, raw in rd.messages(connections=cons):
            ts = t / 1e9
            if T is None: T = time.mktime(time.strptime(time.strftime('%Y-%m-%d ', time.localtime(ts)) + hm, '%Y-%m-%d %H:%M:%S')) + (float('0.' + fr) if fr else 0)
            if ts < T - back - 3: continue
            if ts > T + 2: break
            m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/tf':
                for tr in m.transforms:
                    if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                        st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9
                        poses.append((st, tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation)))
            elif c.topic == '/local_costmap/costmap':
                st = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
                a = np.array(m.data, np.int16).reshape(m.info.height, m.info.width)
                grids.append((st, ts, (a, (m.info.origin.position.x, m.info.origin.position.y, m.info.resolution))))
            else:
                pts = [mk for mk in m.markers if mk.ns == 'Optimal Trajectory']
                if pts:
                    pts.sort(key=lambda mk: mk.id)
                    opts.append((ts, [(mk.pose.position.x, mk.pose.position.y) for mk in pts]))
    poses.sort(); PT = np.array([p[0] for p in poses])

    def pose_at(st):
        i = int(np.searchsorted(PT, st)); i = min(max(i, 1), len(poses) - 1); p0, p1 = poses[i - 1], poses[i]
        if p1[0] == p0[0]: return p1[1:]
        f = min(max((st - p0[0]) / (p1[0] - p0[0]), 0), 1); dyaw = math.atan2(math.sin(p1[3] - p0[3]), math.cos(p1[3] - p0[3]))
        return (p0[1] + f * (p1[1] - p0[1]), p0[2] + f * (p1[2] - p0[2]), p0[3] + f * dyaw)

    def opt_pose(o, k):
        # 최적 궤적 점 k 의 자세 — 위치는 점, 방향은 이웃 점 차(정지에 가까우면 이전 값)
        xs = o[1]; k = min(max(k, 0), len(xs) - 1); j0, j1 = max(k - 1, 0), min(k + 1, len(xs) - 1)
        th = math.atan2(xs[j1][1] - xs[j0][1], xs[j1][0] - xs[j0][0]) if math.hypot(xs[j1][0] - xs[j0][0], xs[j1][1] - xs[j0][1]) > 0.004 else None
        return xs[k][0], xs[k][1], th

    print('\n== %s 기준 %s(첫 실패) · 앞 %.0f s · 로컬 코스트맵 %d 프레임 · 최적 궤적 %d' % (nm, hh, back, sum(1 for g in grids if T - back <= g[0] <= T + 1.5), len(opts)))
    print('  시각        | 자세 odom (x, y, yaw)        | exact cm (칸 몸체)        | fp_now fp_prev fp_was | new8 | opt 최대(첫 치명 점) | dev 옆 · 앞 cm · yaw°(0.5 s 전 예측)')
    prev = None
    for st, rt, G in grids:
        if st < T - back - 1.5: prev = (st, G, pose_at(st)); continue
        if st > T + 1.5: break
        P = pose_at(st); ex, cell = exact(G, P); fn = fp_cost(G, P); fpv = fp_cost(prev[1], P) if prev else -1; fw = fp_cost(G, prev[2]) if prev else -1
        new8 = 0
        if prev is not None and prev[1][0].shape == G[0].shape and prev[1][1] == G[1]:
            nw = (G[0] >= 100) & (prev[1][0] < 100); iy, ix = np.nonzero(nw)
            if len(ix):
                wx = G[1][0] + (ix + 0.5) * G[1][2]; wy = G[1][1] + (iy + 0.5) * G[1][2]; c, s = math.cos(P[2]), math.sin(P[2]); dx, dy = wx - P[0], wy - P[1]
                bx = c * dx + s * dy; by = -s * dx + c * dy; d = np.hypot(np.maximum(np.maximum(XR - bx, bx - XF), 0), np.maximum(np.abs(by) - HW, 0)); new8 = int((d < 0.08).sum())
        elif prev is not None:
            new8 = -1   # 격자 원점이 움직임(롤링) — 칸 비교 생략
        # (다) 직전 최적 궤적을 이 지도에
        oc = '-'
        ob = [o for o in opts if o[0] <= rt]
        if ob:
            o = ob[-1]; mx = 0; first = None; th_last = P[2]
            for k in range(len(o[1])):
                x, y, th = opt_pose(o, k); th_last = th if th is not None else th_last
                v = fp_cost(G, (x, y, th_last)); mx = max(mx, v)
                if v >= 100 and first is None: first = k
            oc = '%3d(%s)' % (mx, '-' if first is None else first)
        # (나) 0.5 s 전 최적 궤적의 예측 vs 실제
        dv = '-'
        ob5 = [o for o in opts if o[0] <= rt - 0.5]
        if ob5:
            o = ob5[-1]; k = int(round((rt - o[0]) / 0.1)); x, y, th = opt_pose(o, k)
            c, s = math.cos(P[2]), math.sin(P[2]); dx, dy = P[0] - x, P[1] - y
            dv = '%+5.1f · %+5.1f · %s' % (100 * (-s * dx + c * dy), 100 * (c * dx + s * dy), '-' if th is None else '%+.1f' % math.degrees(math.atan2(math.sin(P[2] - th), math.cos(P[2] - th))))
        mark = ' ◀ 기준' if abs(st - T) < 0.35 else ''
        print('  %s | (%+.3f, %+.3f, %+6.1f°) | %5.1f (%+.3f, %+.3f) | %4d %6d %6d | %4d | %-12s | %s%s'
              % (hms(st), P[0], P[1], math.degrees(P[2]), 100 * ex, cell[0], cell[1], fn, fpv, fw, new8, oc, dv, mark))
        prev = (st, G, P)
