#!/usr/bin/env python3
"""anal_cell_src — 한 칸(x, y)의 전역 코스트맵 값을 판마다, 그리고 그때 출처 후보(nvblox 슬라이스 거리 · 직전 1 s 라이다 점 5 cm 안 개수)를 본다 (2026-10-28 §9, PC).
  anal_corridor_cell 과 같은 변환(map→odom→base_link→센서). 인자: bag폴더 x y"""
import sys, math, time
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
ts_ = get_typestore(Stores.ROS2_HUMBLE)
ts_.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
bag = Path(sys.argv[1]); P = np.array([float(sys.argv[2]), float(sys.argv[3])])
hs = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + '.%02d' % int((t % 1) * 100)
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def T3(tr):
    a = yaw(tr.rotation); c, s = math.cos(a), math.sin(a); return np.array([[c, -s, tr.translation.x], [s, c, tr.translation.y], [0, 0, 1]])
GM, SL, SC, mo, ob, static = [], [], [], [], [], {}
with AnyReader([bag], default_typestore=ts_) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/global_costmap/costmap', '/nvblox_node/static_map_slice', '/scan', '/tf', '/tf_static')]):
        ts = t * 1e-9; m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf_static':
            for tr in m.transforms: static[tr.child_frame_id] = (tr.header.frame_id, T3(tr.transform))
        elif c.topic == '/tf':
            for tr in m.transforms:
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append((ts, T3(tr.transform)))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append((ts, T3(tr.transform)))
        elif c.topic == '/global_costmap/costmap':
            i = m.info; g = np.array(m.data, np.int16).reshape(i.height, i.width)
            GM.append((ts, int(g[int((P[1] - i.origin.position.y) / i.resolution), int((P[0] - i.origin.position.x) / i.resolution)])))
        elif c.topic == '/nvblox_node/static_map_slice':
            SL.append((ts, m.origin.x, m.origin.y, m.resolution, np.array(m.data, np.float32).reshape(m.height, m.width), m.unknown_value))
        else:
            a = m.angle_min + m.angle_increment * np.arange(len(m.ranges)); r = np.array(m.ranges, np.float32); ok = np.isfinite(r) & (r > m.range_min) & (r < m.range_max)
            SC.append((ts, m.header.frame_id, np.c_[r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok]), np.ones(ok.sum())]))
def last(L, t): return L[max(np.searchsorted([x[0] for x in L], t, side='right') - 1, 0)]
def chain(f):
    M = np.eye(3)
    while f != 'base_link': p, mm = static[f]; M = mm @ M; f = p
    return M
print('칸 (%.3f, %.3f) — 판 시각 | 전역 값 | 로버 map | nvblox 거리(odom 슬라이스) | 라이다 점 5 cm 안(직전 1 s)' % tuple(P))
for ts, v in GM:
    M = last(mo, ts)[1] @ last(ob, ts)[1]
    q = np.linalg.inv(last(mo, ts)[1]) @ np.array([P[0], P[1], 1]); _, sx, sy, sr, sd, su = last(SL, ts); ii, jj = int((q[0] - sx) / sr), int((q[1] - sy) / sr)
    vn = float(sd[jj, ii]) if 0 <= ii < sd.shape[1] and 0 <= jj < sd.shape[0] else float('nan')
    nl = 0
    for z in [z for z in SC if ts - 1 <= z[0] <= ts]:
        L = (last(mo, z[0])[1] @ last(ob, z[0])[1] @ chain(z[1]) @ z[2].T).T[:, :2]; nl += int((np.hypot(L[:, 0] - P[0], L[:, 1] - P[1]) < 0.05).sum())
    print('  %s | %3d | (%.2f, %.2f) | %s | %d' % (hs(ts), v, M[0, 2], M[1, 2], '미지' if vn == su else '%.2f' % vn, nl))
