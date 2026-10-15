#!/usr/bin/env python3
"""anal_near_cells_src — 기준 순간에 차체에서 R 안에 있던 로컬 치명 칸들을 지도 좌표로 뽑고, 칸마다 (1) 그 순간 라이다 점이 3.5 cm 안에 있었나 (2) 다른 순간들에도 그 칸이 치명이었나. (2026-10-15 §5, 오늘만)
  왜: f2v1 멈춘 순간 왼쪽 치명 칸이 차체에서 3.6 cm, 9 분 뒤 같은 자리 복귀 출발 때는 10.1 cm(§5 anal_motion_probe). 그 칸이 라이다 벽인지 카메라 칸인지, 언제 사라졌는지.
  인자: R(m) 기준=bag@HH:MM:SS.f 비교=bag@HH:MM:SS.f ..."""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
XF, XR, HW = 0.272, -0.258, 0.175
R = float(sys.argv[1])
def snap(spec):
    nm, rest = spec.split('='); bag, hh = rest.split('@'); hms, _, fr = hh.partition('.'); ob = mo = lid = None; lc = sc = None
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        T = None
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/local_costmap/costmap', '/scan')]):
            ts = t / 1e9
            if T is None: T = time.mktime(time.strptime(time.strftime('%Y-%m-%d ', time.localtime(ts)) + hms, '%Y-%m-%d %H:%M:%S')) + (float('0.' + fr) if fr else 0)
            if ts > T: break
            m = rd.deserialize(raw, c.msgtype)
            if c.topic in ('/tf', '/tf_static'):
                for tr in m.transforms:
                    v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                    if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob = v
                    elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo = v
                    elif tr.child_frame_id == 'lidar_link':
                        q = tr.transform.rotation; lid = (v[0], v[1], np.array([[1 - 2 * (q.y * q.y + q.z * q.z), 2 * (q.x * q.y - q.z * q.w)], [2 * (q.x * q.y + q.z * q.w), 1 - 2 * (q.x * q.x + q.z * q.z)]]))
            elif c.topic == '/scan': sc = m
            else: lc = m
    tm = lambda x, y, P: (P[0] + math.cos(P[2]) * x - math.sin(P[2]) * y, P[1] + math.sin(P[2]) * x + math.cos(P[2]) * y)
    a = np.array(lc.data, np.int16).reshape(lc.info.height, lc.info.width); iy, ix = np.nonzero(a >= 100)
    ox = lc.info.origin.position.x + (ix + 0.5) * lc.info.resolution; oy = lc.info.origin.position.y + (iy + 0.5) * lc.info.resolution
    cmx, cmy = tm(ox, oy, mo)
    r = np.array(sc.ranges); an = sc.angle_min + np.arange(len(r)) * sc.angle_increment; ok = np.isfinite(r) & (r > sc.range_min) & (r < sc.range_max)
    px, py = r[ok] * np.cos(an[ok]), r[ok] * np.sin(an[ok]); bx = lid[0] + lid[2][0, 0] * px + lid[2][0, 1] * py; by = lid[1] + lid[2][1, 0] * px + lid[2][1, 1] * py
    lx, ly = tm(*tm(bx, by, ob), mo)
    return nm, hh, ob, mo, np.c_[cmx, cmy, ox, oy], np.c_[lx, ly]
base = snap(sys.argv[2]); others = [snap(s) for s in sys.argv[3:]]
nm, hh, ob, mo, C, L = base
c_, s_ = math.cos(ob[2]), math.sin(ob[2]); bx = c_ * (C[:, 2] - ob[0]) + s_ * (C[:, 3] - ob[1]); by = -s_ * (C[:, 2] - ob[0]) + c_ * (C[:, 3] - ob[1])
dx = np.maximum(np.maximum(XR - bx, bx - XF), 0); dy = np.maximum(np.abs(by) - HW, 0); d = np.hypot(dx, dy); sel = np.argsort(d)[:(d <= R).sum()]
print('기준 %s %s: 차체에서 %.0f cm 안 치명 칸 %d 개 (지도 좌표 · 차체 좌표 · 거리 · 라이다 점 3.5 cm 안 · 다른 순간에도 치명?)' % (nm, hh, 100 * R, len(sel)))
for k in sel:
    lid_n = int((np.hypot(L[:, 0] - C[k, 0], L[:, 1] - C[k, 1]) < 0.035).sum())
    seen = []
    for o in others:
        hit = (np.hypot(o[4][:, 0] - C[k, 0], o[4][:, 1] - C[k, 1]) < 0.03).any(); seen.append('%s %s' % (o[0], '예' if hit else '아니오'))
    print('  map (%.3f, %.3f) · 차체 (%+.2f, %+.2f) · %4.1f cm · 라이다 %d · %s' % (C[k, 0], C[k, 1], bx[k], by[k], 100 * d[k], lid_n, ' · '.join(seen)))
print('map→odom 기준 (%.3f, %.3f, %+.2f°)' % (mo[0], mo[1], math.degrees(mo[2])) + ''.join(' · %s (%.3f, %.3f, %+.2f°)' % (o[0], o[3][0], o[3][1], math.degrees(o[3][2])) for o in others))
