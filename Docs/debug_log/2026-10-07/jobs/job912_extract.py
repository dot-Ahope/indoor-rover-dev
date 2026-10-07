#!/usr/bin/env python3
"""10-07 §2.5: f2c2 bag 추출(시각화용) — 지도 자세 궤적(map→odom∘odom→base_link, EKF B), 그림자 A(odom), /plan 전부, 전역 코스트맵(2 s 간격),
   로컬 코스트맵(1 s 간격, 구간 안), 스캔(1 s), cmd_vel. 인자: BAG TA TB OUT (epoch)"""
import sys, math, numpy as np, rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
BAG, TA, TB, OUT = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
mo, ob, A, CV, plans, gcm, lcm, scans = [], [], [], [], [], [], [], []; tg = tl = ts_ = 0; mp = None
for_msg = lambda tp, d: deserialize_message(d, get_message(types[tp]))
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if tp == '/map' and mp is None:
        m = for_msg(tp, data); mp = (np.array(m.data, np.int8).reshape(m.info.height, m.info.width), m.info.resolution, m.info.origin.position.x, m.info.origin.position.y)
    if t < TA or t > TB: continue
    if tp == '/tf':
        for x in for_msg(tp, data).transforms:
            k = (x.header.frame_id, x.child_frame_id); v = (t, x.transform.translation.x, x.transform.translation.y, yaw(x.transform.rotation))
            if k == ('map', 'odom'): mo.append(v)
            elif k == ('odom', 'base_link'): ob.append(v)
    elif tp == '/odometry/ekf_a':
        p = for_msg(tp, data).pose.pose; A.append((t, p.position.x, p.position.y, yaw(p.orientation)))
    elif tp == '/cmd_vel':
        m = for_msg(tp, data); CV.append((t, m.linear.x, m.angular.z))
    elif tp == '/plan':
        m = for_msg(tp, data); plans.append((t, np.array([[q.pose.position.x, q.pose.position.y] for q in m.poses], np.float32)))
    elif tp == '/global_costmap/costmap' and t - tg >= 2:
        tg = t; m = for_msg(tp, data); gcm.append((t, np.array(m.data, np.int8).reshape(m.info.height, m.info.width), m.info.resolution, m.info.origin.position.x, m.info.origin.position.y))
    elif tp == '/local_costmap/costmap' and t - tl >= 1:
        tl = t; m = for_msg(tp, data); lcm.append((t, np.array(m.data, np.int8).reshape(m.info.height, m.info.width), m.info.resolution, m.info.origin.position.x, m.info.origin.position.y))
    elif tp == '/scan' and t - ts_ >= 1:
        ts_ = t; m = for_msg(tp, data); scans.append((t, np.array(m.ranges, np.float32), m.angle_min, m.angle_increment))
mo, ob = np.array(mo), np.array(ob)
def pose_map(t):
    i = min(max(np.searchsorted(mo[:, 0], t) - 1, 0), len(mo) - 1); j = min(max(np.searchsorted(ob[:, 0], t) - 1, 0), len(ob) - 1)
    mx, my, mth = mo[i, 1:]; ox, oy, oth = ob[j, 1:]; c, s = math.cos(mth), math.sin(mth); return (mx + c * ox - s * oy, my + s * ox + c * oy, mth + oth)
traj = np.array([(t,) + pose_map(t) for t in ob[::3, 0]])
# 그림자 A 를 같은 map→odom 으로 올림(같은 보정을 받았다고 가정한 비교용)
Am = []
for t, x, y, th in A[::3]:
    i = min(max(np.searchsorted(mo[:, 0], t) - 1, 0), len(mo) - 1); mx, my, mth = mo[i, 1:]; c, s = math.cos(mth), math.sin(mth); Am.append((t, mx + c * x - s * y, my + s * x + c * y, mth + th))
np.savez_compressed(OUT, traj=traj, A=np.array(Am), mo=mo, cmd=np.array(CV), plan_t=np.array([p[0] for p in plans]), plan_n=np.array([len(p[1]) for p in plans]),
    plan_xy=np.concatenate([p[1] for p in plans]) if plans else np.zeros((0, 2)), map=mp[0], map_meta=np.array(mp[1:]),
    gcm_t=np.array([g[0] for g in gcm]), gcm=np.array([g[1] for g in gcm]) if gcm else np.zeros(0), gcm_meta=np.array([g[2:] for g in gcm]),
    lcm_t=np.array([g[0] for g in lcm]), lcm=np.array([g[1] for g in lcm]) if lcm else np.zeros(0), lcm_meta=np.array([g[2:] for g in lcm]),
    scan_t=np.array([s[0] for s in scans]), scan_r=np.array([s[1] for s in scans]), scan_a=np.array([s[2:] for s in scans]))
print('궤적 %d · A %d · plan %d · 전역 %d · 로컬 %d · 스캔 %d · cmd %d' % (len(traj), len(Am), len(plans), len(gcm), len(lcm), len(scans), len(CV)))
