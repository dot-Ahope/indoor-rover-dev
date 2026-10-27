#!/usr/bin/env python3
"""anal_block_cell — f2st1 복귀 길 막힘 판정 칸 (1.13, 0.14) 을 원자료와 대조 (2026-10-27 §14, PC, 로버 안 움직임).
  왜: §13 영상에서 그 칸이 기록 상자(x 1.151~1.261, y −0.20~−0.02) 북쪽 약 16 cm 의 '작은 둥근 덩어리' 로 보였음 →
      상자의 기억 밀림인지 · 바닥 유령인지 · 상자 자체의 내접 띠인지 가린다.
  PathBlockedAhead 는 **전역 코스트맵(map)** 의 OccupancyGrid 값 ≥ 99(내접 253)를 본다(path_blocked_ahead_condition.cpp).
  시각마다(0.5 s 간격) 칸 P 기준:
    · 전역 · 로컬 코스트맵: P 의 값, P 에서 가장 가까운 치명(100) 칸 위치 · 거리, P 0.4 m 안 치명 칸 수(그중 상자 사각형 ±5 cm 밖 수)
    · nvblox 슬라이스(odom, 카메라 기원): P 의 거리값, P 0.4 m 안 거리 ≤ 0 칸 중 가장 가까운 위치 · 거리
    · 라이다 /scan(map 으로 옮김): P 0.4 m 안 점 수 · 가장 가까운 점
    · 로버 위치 · P 까지 거리 · 로버 기준 방위(카메라 시야 ±43° 안인지)
  인자: bag폴더 시작HH:MM:SS 끝HH:MM:SS [간격 s=0.5]"""
import sys, math, time
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
P = np.array([1.13, 0.14]); BOX = (1.151, 1.261, -0.20, -0.02); R = 0.40
ts_ = get_typestore(Stores.ROS2_HUMBLE)
ts_.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
bag = Path(sys.argv[1]); day = '2026-10-27 '
t0s = time.mktime(time.strptime(day + sys.argv[2], '%Y-%m-%d %H:%M:%S')); t1s = time.mktime(time.strptime(day + sys.argv[3], '%Y-%m-%d %H:%M:%S'))
STEP = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def T3(tr):
    a = yaw(tr.rotation); c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, tr.translation.x], [s, c, tr.translation.y], [0, 0, 1]])
def last(L, t):
    i = np.searchsorted([x[0] for x in L], t, side='right') - 1
    return L[max(i, 0)][1] if L else None
def inbox(x, y, m=0.05): return (BOX[0] - m <= x <= BOX[1] + m) and (BOX[2] - m <= y <= BOX[3] + m)


mo, ob, static, gcm, lcm, sl, sc = [], [], {}, [], [], [], []
with AnyReader([bag], default_typestore=ts_) as rd:
    con = [c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/global_costmap/costmap', '/local_costmap/costmap', '/nvblox_node/static_map_slice', '/scan')]
    for c, t, raw in rd.messages(connections=con):
        ts = t * 1e-9
        if c.topic == '/tf_static':
            for tr in rd.deserialize(raw, c.msgtype).transforms: static[tr.child_frame_id] = (tr.header.frame_id, T3(tr.transform))
            continue
        if ts < t0s - 5 or ts > t1s + 1: continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append((ts, T3(tr.transform)))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append((ts, T3(tr.transform)))
        elif c.topic in ('/global_costmap/costmap', '/local_costmap/costmap'):
            i = m.info; g = np.array(m.data, np.int16).reshape(i.height, i.width)
            (gcm if c.topic[1] == 'g' else lcm).append((ts, (m.header.frame_id, i.origin.position.x, i.origin.position.y, i.resolution, g)))
        elif c.topic == '/nvblox_node/static_map_slice':
            d = np.array(m.data, np.float32).reshape(m.height, m.width)
            sl.append((ts, (m.origin.x, m.origin.y, m.resolution, d, m.unknown_value)))
        elif c.topic == '/scan':
            a = m.angle_min + m.angle_increment * np.arange(len(m.ranges)); r = np.array(m.ranges, np.float32)
            ok = np.isfinite(r) & (r >= m.range_min) & (r <= m.range_max)
            sc.append((ts, (m.header.frame_id, np.c_[r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok]), np.ones(ok.sum())])))
mo.sort(key=lambda x: x[0]); ob.sort(key=lambda x: x[0])
for L in (gcm, lcm, sl, sc): L.sort(key=lambda x: x[0])


def chain(frame):   # frame → base_link (정적)
    M = np.eye(3)
    while frame != 'base_link': par, mm = static[frame]; M = mm @ M; frame = par
    return M


def grid_probe(G, Pf):
    """격자에서 P 값, 가까운 치명 칸, 0.4 m 안 치명 칸 수(상자 밖 수). Pf = 격자 좌표계의 P, 역변환 Minv = 격자→map."""
    fr, ox, oy, res, g = G
    ii, jj = int((Pf[0] - ox) / res), int((Pf[1] - oy) / res)
    v = int(g[jj, ii]) if 0 <= ii < g.shape[1] and 0 <= jj < g.shape[0] else None
    J, I = np.nonzero(g == 100)
    X, Y = ox + (I + .5) * res, oy + (J + .5) * res
    return v, X, Y


print('P = map (%.2f, %.2f) · 상자 기록 x %.3f~%.3f y %.2f~%.2f · 반경 %.2f m' % (P[0], P[1], *BOX, R))
print('시각 | 로버 map(x,y,yaw) · P 거리 · 방위 | 전역: P 값 · 최근접 치명(위치, cm) · 0.4 m 안 치명 수(상자 밖) | 로컬: 같은 꼴 | nvblox: P 거리값 · 최근접 ≤0 칸(위치, cm) · 수(상자 밖) | 라이다: 점 수 · 최근접(cm)')
t = t0s
while t <= t1s:
    Mmo = last(mo, t); Mob = last(ob, t)
    if Mmo is None or Mob is None: t += STEP; continue
    Mmb = Mmo @ Mob; rx, ry = Mmb[0, 2], Mmb[1, 2]; ryaw = math.atan2(Mmb[1, 0], Mmb[0, 0])
    dP = math.hypot(P[0] - rx, P[1] - ry); brg = (math.degrees(math.atan2(P[1] - ry, P[0] - rx) - ryaw) + 180) % 360 - 180
    row = ['%s.%d' % (time.strftime('%H:%M:%S', time.localtime(t)), int((t % 1) * 10)), '로버 (%.2f, %.2f, %+.0f°) · P %.2f m · %+.0f°' % (rx, ry, math.degrees(ryaw), dP, brg)]
    Podom = np.linalg.inv(Mmo) @ np.r_[P, 1]
    for L in (gcm, lcm):
        G = last(L, t)
        if G is None: row.append('-'); continue
        Mg = Mmo if G[0] == 'odom' else np.eye(3)   # 격자 프레임 → map
        Pf = Podom if G[0] == 'odom' else np.r_[P, 1]
        v, X, Y = grid_probe(G, Pf)
        W = (Mg @ np.c_[X, Y, np.ones(len(X))].T).T; d = np.hypot(W[:, 0] - P[0], W[:, 1] - P[1]); k = d < R
        if k.any():
            j = int(np.argmin(d)); nout = sum(1 for x, y in W[k, :2] if not inbox(x, y))
            row.append('%s 값 %s · 치명 (%.2f, %.2f) %.0f cm · %d(밖 %d)' % (G[0], v, W[j, 0], W[j, 1], 100 * d[j], k.sum(), nout))
        else: row.append('%s 값 %s · 치명 없음' % (G[0], v))
    S = last(sl, t)
    if S is not None:
        ox, oy, res, dd, unk = S
        ii, jj = int((Podom[0] - ox) / res), int((Podom[1] - oy) / res)
        vp = dd[jj, ii] if 0 <= ii < dd.shape[1] and 0 <= jj < dd.shape[0] else float('nan')
        J, I = np.nonzero((dd <= 0.0) & (dd != unk))
        W = (Mmo @ np.c_[ox + (I + .5) * res, oy + (J + .5) * res, np.ones(len(I))].T).T
        d = np.hypot(W[:, 0] - P[0], W[:, 1] - P[1]); k = d < R
        vs = '미지' if vp == unk else '%.2f' % vp
        if k.any():
            j = int(np.argmin(d)); nout = sum(1 for x, y in W[k, :2] if not inbox(x, y))
            row.append('nv %s · (%.2f, %.2f) %.0f cm · %d(밖 %d)' % (vs, W[j, 0], W[j, 1], 100 * d[j], k.sum(), nout))
        else: row.append('nv %s · 장애 없음' % vs)
    Z = last(sc, t)
    if Z is not None:
        fr, pts = Z; W = (Mmb @ chain(fr) @ pts.T).T; d = np.hypot(W[:, 0] - P[0], W[:, 1] - P[1]); k = d < R
        row.append('라이다 %d · %s' % (k.sum(), ('%.0f cm (%.2f, %.2f)' % (100 * d[k].min(), *W[k][np.argmin(d[k]), :2])) if k.any() else '-'))
    print(' | '.join(row)); t += STEP
