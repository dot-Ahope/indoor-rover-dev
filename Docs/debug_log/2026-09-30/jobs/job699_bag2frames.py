#!/usr/bin/env python3
"""09-30 §7 주행 영상화용 추출: F0 bag → 10 Hz 프레임 데이터(npz). PC 에서 그림·ffmpeg 로 영상화.
   프레임마다: 로버 map 자세, 라이다 점(map 좌표, 5 m 안), 최신 전역 경로(/plan), 최신 로컬 궤적(/local_plan),
   최신 로컬 코스트맵(격자·원점·해상도 — 5 프레임마다), cmd v/ω, map→odom, stuck. 배경 = 마지막 /map.
   인자: BAG OUT.npz"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=sys.argv[1], storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
mo, ob, scans, plans, lplans, lcm, cmd, lastmap, l2b, stuck, odo = [], [], [], [], [], [], [], None, None, [], []
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if tp not in ('/tf', '/tf_static', '/scan', '/plan', '/local_plan', '/local_costmap/costmap', '/cmd_vel', '/map', '/rover/stuck', '/odometry/filtered'): continue
    m = deserialize_message(data, get_message(types[tp]))
    if tp in ('/tf', '/tf_static'):
        for tr in m.transforms:
            p, q = tr.transform.translation, tr.transform.rotation; v = (t, p.x, p.y, yaw(q))
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append(v)
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append(v)
            elif tr.header.frame_id == 'base_link' and tr.child_frame_id in ('lidar_link', 'laser'): l2b = v
    elif tp == '/scan':
        rs = np.array(m.ranges, dtype=np.float32); an = m.angle_min + np.arange(len(rs)) * m.angle_increment
        ok = np.isfinite(rs) & (rs > m.range_min) & (rs < 5.0); scans.append((t, rs[ok] * np.cos(an[ok]), rs[ok] * np.sin(an[ok])))
    elif tp == '/plan': plans.append((t, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses], dtype=np.float32)))
    elif tp == '/local_plan': lplans.append((t, m.header.frame_id, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses], dtype=np.float32)))
    elif tp == '/local_costmap/costmap':
        i = m.info; lcm.append((t, m.header.frame_id, i.origin.position.x, i.origin.position.y, i.resolution, np.array(m.data, dtype=np.int8).reshape(i.height, i.width)))
    elif tp == '/cmd_vel': cmd.append((t, m.linear.x, m.angular.z))
    elif tp == '/map': lastmap = m
    elif tp == '/rover/stuck': stuck.append(t)
    elif tp == '/odometry/filtered': odo.append((t, m.twist.twist.linear.x, m.twist.twist.angular.z))   # 09-30: 실제(EKF) 속도
mo.sort(); ob.sort()
mt = [x[0] for x in mo]; otl = [x[0] for x in ob]


def at(lst, keys, t):
    k = bisect.bisect_right(keys, t) - 1; return lst[max(k, 0)]


def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])


act = [c[0] for c in cmd if abs(c[1]) > 0.005 or abs(c[2]) > 0.01]
t0, t1 = act[0] - 3.0, act[-1] + 3.0
F = np.arange(t0, t1, 0.1)
st = [s[0] for s in scans]; pt = [p[0] for p in plans]; lpt = [p[0] for p in lplans]; lct = [c[0] for c in lcm]; ct = [c[0] for c in cmd]
pose, sx, sy, sidx, pl_i, lp_i, lc_i, v, w, moff, ov, ow, hz = [], [], [], [0], [], [], [], [], [], [], [], [], []
odt = [o[0] for o in odo]
lcm_keep = {}
for k, t in enumerate(F):
    A = at(mo, mt, t); B = at(ob, otl, t); o = (A[1], A[2], A[3]); P = comp(o, (B[1], B[2], B[3])); pose.append(P); moff.append((A[1], A[2], A[3]))
    S = at(scans, st, t); L = comp(P, (l2b[1], l2b[2], l2b[3])) if l2b else P
    c, s = math.cos(L[2]), math.sin(L[2]); sx.append(L[0] + c * S[1] - s * S[2]); sy.append(L[1] + s * S[1] + c * S[2]); sidx.append(sidx[-1] + len(S[1]))
    pl_i.append(bisect.bisect_right(pt, t) - 1); lp_i.append(bisect.bisect_right(lpt, t) - 1)
    ci = bisect.bisect_right(lct, t) - 1; lc_i.append(ci)
    if ci >= 0 and ci not in lcm_keep: lcm_keep[ci] = lcm[ci]
    kc = bisect.bisect_right(ct, t) - 1
    if kc >= 0 and t - cmd[kc][0] < 0.5: v.append(cmd[kc][1]); w.append(cmd[kc][2])
    else: v.append(0.0); w.append(0.0)
    ko = bisect.bisect_right(odt, t) - 1; ov.append(odo[ko][1] if ko >= 0 else 0.0); ow.append(odo[ko][2] if ko >= 0 else 0.0)
    hz.append(bisect.bisect_right(ct, t) - bisect.bisect_right(ct, t - 1.0))   # 직전 1 s 동안 /cmd_vel 메시지 수 = 발행 주기(Hz)
# 로컬 궤적은 odom 좌표일 수 있음 → 해당 시각 map→odom 으로 map 좌표화
lp_map = []
for (t, fr, pts) in lplans:
    if fr == 'odom' and len(pts):
        A = at(mo, mt, t); c, s = math.cos(A[3]), math.sin(A[3]); lp_map.append(np.c_[A[1] + c * pts[:, 0] - s * pts[:, 1], A[2] + s * pts[:, 0] + c * pts[:, 1]])
    else: lp_map.append(pts)
keys = sorted(lcm_keep); lmap = {k: i for i, k in enumerate(keys)}
lc_frame = np.array([lmap.get(ci, -1) for ci in lc_i])
lc_meta = []
for k in keys:
    t, fr, ox, oy, res, g = lcm_keep[k]
    if fr == 'odom':
        A = at(mo, mt, t); lc_meta.append((A[1], A[2], A[3], ox, oy, res))   # 격자는 odom 축 — map 변환 위해 map→odom 기록
    else: lc_meta.append((0.0, 0.0, 0.0, ox, oy, res))
out = dict(t=F - F[0], t_act0=act[0] - F[0], pose=np.array(pose), moff=np.array(moff), sx=np.concatenate(sx), sy=np.concatenate(sy), sidx=np.array(sidx),
           pl_i=np.array(pl_i), lp_i=np.array(lp_i), v=np.array(v), w=np.array(w), ov=np.array(ov), ow=np.array(ow), hz=np.array(hz), lc_frame=lc_frame, lc_meta=np.array(lc_meta),
           stuck=np.array(stuck) - F[0], bag_t0=F[0])
for i, (_, p) in enumerate(plans): out['plan_%d' % i] = p
for i, p in enumerate(lp_map): out['lplan_%d' % i] = p
for i, k in enumerate(keys): out['lcm_%d' % i] = lcm_keep[k][5]
mi = lastmap.info
out.update(map=np.array(lastmap.data, dtype=np.int8).reshape(mi.height, mi.width), map_meta=np.array([mi.origin.position.x, mi.origin.position.y, mi.resolution]),
           n_plan=len(plans), n_lplan=len(lp_map), n_lcm=len(keys))
np.savez_compressed(sys.argv[2], **out)
print('%s: 프레임 %d(%.0f s), 스캔 점 %d, 전역 경로 %d, 로컬 궤적 %d, 로컬 코스트맵 %d, 지도 %dx%d, 시작 bag 시각 %.3f'
      % (sys.argv[1], len(F), F[-1] - F[0], len(out['sx']), len(plans), len(lp_map), len(keys), mi.width, mi.height, F[0]))
