#!/usr/bin/env python3
"""anal_westpass_cells — 서쪽 통로 정지 자리에서 로버 오른쪽 치명 칸이 두 주행에서 왜 달랐나(사용자 관찰). 오늘만. (2026-10-14)
  지정 시각마다: 로버 자세, 차체에서 0.6 m 안 로컬 치명 칸 수·최소 여유(칸 가장자리)·그중 오른쪽(y<0) 것,
  같은 자리의 nvblox 슬라이스 장애물 칸 수(카메라), 라이다 점 수(차체 0.6 m 안), 지도 보정(map→odom) 값.
  인자: bag HH:MM:SS ..."""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
bag = sys.argv[1]; hs = sys.argv[2:]
ts_ = get_typestore(Stores.ROS2_HUMBLE)
ts_.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
def T3(tr):
    q = tr.rotation; x, y, z, w = q.x, q.y, q.z, q.w; M = np.eye(4)
    M[:3, :3] = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    M[:3, 3] = [tr.translation.x, tr.translation.y, tr.translation.z]; return M
static = {}; ob = []; mo = []; loc = []; sl = []; scans = []
with AnyReader([Path(bag)], default_typestore=ts_) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/local_costmap/costmap', '/nvblox_node/static_map_slice', '/scan')]):
        ts = t / 1e9; m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf_static':
            for tr in m.transforms: static[tr.child_frame_id] = (tr.header.frame_id, T3(tr.transform))
        elif c.topic == '/tf':
            for tr in m.transforms:
                if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob.append((ts, T3(tr.transform)))
                elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo.append((ts, T3(tr.transform)))
        elif c.topic == '/local_costmap/costmap': loc.append((ts, m.info.origin.position.x, m.info.origin.position.y, m.info.resolution, np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width)))
        elif c.topic == '/scan':
            r = np.array(m.ranges); a = m.angle_min + np.arange(len(r)) * m.angle_increment; ok = np.isfinite(r) & (r > m.range_min) & (r < 3); scans.append((ts, m.header.frame_id, np.c_[r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok]), np.zeros(ok.sum()), np.ones(ok.sum())]))
        else: sl.append((ts, m.origin.x, m.origin.y, m.resolution, m.unknown_value, np.asarray(m.data, np.float32).reshape(m.height, m.width)))
def chain(frame):
    M = np.eye(4)
    while frame != 'base_link': par, mm = static[frame]; M = mm @ M; frame = par
    return M
last = lambda L, t: L[max(np.searchsorted([x[0] for x in L], t, side='right') - 1, 0)]
day = time.strftime('%Y-%m-%d ', time.localtime(ob[0][0])); ep = lambda s: time.mktime(time.strptime(day + s, '%Y-%m-%d %H:%M:%S'))
def clr(P): return np.hypot(np.maximum.reduce([-0.248 - P[:, 0], np.zeros(len(P)), P[:, 0] - 0.262]), np.maximum.reduce([-0.165 - P[:, 1], np.zeros(len(P)), P[:, 1] - 0.165]))
print('시각       로버 map (x, y, 방향)     | 로컬 치명: 0.6 m 안 칸 · 최소 여유 · 오른쪽 칸 수(최소 여유) | nvblox 장애물 칸(0.6 m 안 · 오른쪽) | 라이다 점(0.6 m 안 · 오른쪽) | map→odom (x, y, 각)')
for h in hs:
    t = ep(h); Mob = last(ob, t)[1]; Mmo = last(mo, t)[1]; Mmb = Mmo @ Mob; yaw = math.degrees(math.atan2(Mmb[1, 0], Mmb[0, 0]))
    _, ox, oy, res, G = last(loc, t); L = np.argwhere(G >= 100); P = (np.linalg.inv(Mob) @ np.c_[ox + (L[:, 1] + 0.5) * res, oy + (L[:, 0] + 0.5) * res, np.zeros(len(L)), np.ones(len(L))].T).T[:, :2]
    d = clr(P) - res / 2; nb = d < 0.6; R = nb & (P[:, 1] < 0)
    s = last(sl, t); Ls = np.argwhere(s[5] <= 0); Ps = (np.linalg.inv(Mob) @ np.c_[s[1] + (Ls[:, 1] + 0.5) * s[3], s[2] + (Ls[:, 0] + 0.5) * s[3], np.zeros(len(Ls)), np.ones(len(Ls))].T).T[:, :2]; ds = clr(Ps) - s[3] / 2
    sc = last(scans, t); Pl = (chain(sc[1]) @ sc[2].T).T[:, :2]; dl = clr(Pl)
    am = math.degrees(math.atan2(Mmo[1, 0], Mmo[0, 0]))
    print('%s   (%.2f, %.2f, %+4.0f°)   |  %3d 칸 · %.1f cm · 오른쪽 %3d (%s)               |  %3d · %3d                    |  %3d · %3d          | (%+.3f, %+.3f, %+.2f°)' % (
        h, Mmb[0, 3], Mmb[1, 3], yaw, nb.sum(), d.min() * 100 if len(d) else -1, R.sum(), '%.1f cm' % (d[R].min() * 100) if R.any() else '-', (ds < 0.6).sum(), ((ds < 0.6) & (Ps[:, 1] < 0)).sum(), (dl < 0.6).sum(), ((dl < 0.6) & (Pl[:, 1] < 0)).sum(), Mmo[0, 3], Mmo[1, 3], am))
# --- 덧붙임: 차체 8 cm 안 로컬 치명 칸 하나하나가 카메라 칸인지 라이다 점이 있는지(차체 좌표 x 앞 · y 왼쪽)
print('\n차체 8 cm 안 로컬 치명 칸: 시각 · 칸(차체 좌표) · 여유 · 그 칸에 nvblox 장애물? · 5 cm 안 라이다 점 수')
for h in hs:
    t = ep(h); Mob = last(ob, t)[1]; Mmo = last(mo, t)[1]; Mmb = Mmo @ Mob
    _, ox, oy, res, G = last(loc, t); L = np.argwhere(G >= 100); W = np.c_[ox + (L[:, 1] + 0.5) * res, oy + (L[:, 0] + 0.5) * res, np.zeros(len(L)), np.ones(len(L))]; P = (np.linalg.inv(Mob) @ W.T).T[:, :2]
    d = clr(P) - res / 2; k = np.where(d < 0.08)[0]
    s = last(sl, t); sc = last(scans, t); Pl = (chain(sc[1]) @ sc[2].T).T[:, :2]
    out = []
    for i in k[np.argsort(d[k])][:8]:
        a = int(math.floor((W[i, 1] - s[2]) / s[3])); b = int(math.floor((W[i, 0] - s[1]) / s[3])); nv = (0 <= a < s[5].shape[0] and 0 <= b < s[5].shape[1] and s[5][a, b] <= 0)
        nl = int((np.hypot(Pl[:, 0] - P[i, 0], Pl[:, 1] - P[i, 1]) < 0.05).sum()); out.append('(%+.2f, %+.2f) %.1f cm 카메라%s 라이다 %d' % (P[i, 0], P[i, 1], d[i] * 100, 'O' if nv else 'X', nl))
    print('  %s  %s' % (h, ' | '.join(out) if out else '없음'))
