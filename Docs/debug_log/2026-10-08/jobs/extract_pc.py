# 10-08 §3.4: PC 판 bag 추출(rosbags) — render_rviz.py 와 같은 키 + MPPI 후보·최적 궤적(/trajectories, odom). 인자: bag 출력.npz
import math, sys, numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
ts = get_typestore(Stores.ROS2_HUMBLE)
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
mo, ob, CV, plans, gcm, lcm, scans, mp, MP = [], [], [], [], [], [], [], None, []
tg = tl = ts_ = 0
with AnyReader([Path(sys.argv[1])], default_typestore=ts) as r:
    con = [c for c in r.connections if c.topic in ('/tf', '/cmd_vel', '/plan', '/global_costmap/costmap', '/local_costmap/costmap', '/scan', '/map', '/trajectories')]
    for c, t_ns, raw in r.messages(connections=con):
        t = t_ns * 1e-9; tp = c.topic
        if tp == '/global_costmap/costmap' and t - tg < 1.0: continue
        if tp == '/local_costmap/costmap' and t - tl < 0.5: continue
        if tp == '/scan' and t - ts_ < 0.2: continue
        if tp == '/map' and mp is not None: continue
        m = r.deserialize(raw, c.msgtype)
        if tp == '/tf':
            for x in m.transforms:
                k = (x.header.frame_id, x.child_frame_id); v = (t, x.transform.translation.x, x.transform.translation.y, yaw(x.transform.rotation))
                if k == ('map', 'odom'): mo.append(v)
                elif k == ('odom', 'base_link'): ob.append(v)
        elif tp == '/cmd_vel': CV.append((t, m.linear.x, m.angular.z))
        elif tp == '/plan': plans.append((t, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses], np.float32)))
        elif tp == '/map': mp = (np.asarray(m.data, np.int8).reshape(m.info.height, m.info.width), m.info.resolution, m.info.origin.position.x, m.info.origin.position.y)
        elif tp == '/global_costmap/costmap':
            tg = t; gcm.append((t, np.asarray(m.data, np.int8).reshape(m.info.height, m.info.width), m.info.resolution, m.info.origin.position.x, m.info.origin.position.y))
        elif tp == '/local_costmap/costmap':
            tl = t; lcm.append((t, np.asarray(m.data, np.int8).reshape(m.info.height, m.info.width), m.info.resolution, m.info.origin.position.x, m.info.origin.position.y))
        elif tp == '/scan': ts_ = t; scans.append((t, np.asarray(m.ranges, np.float32), m.angle_min, m.angle_increment))
        elif tp == '/trajectories':
            cand = np.array([[x.pose.position.x, x.pose.position.y] for x in m.markers if x.ns == 'Candidate Trajectories'], np.float32)
            opt = np.array([[x.pose.position.x, x.pose.position.y] for x in m.markers if x.ns == 'Optimal Trajectory'], np.float32)
            if len(cand) == 800 and len(opt) == 32: MP.append((t, cand, opt))
mo, ob = np.array(mo), np.array(ob)
def pose_map(t):
    i = min(max(np.searchsorted(mo[:, 0], t) - 1, 0), len(mo) - 1); j = min(max(np.searchsorted(ob[:, 0], t) - 1, 0), len(ob) - 1)
    mx, my, mth = mo[i, 1:]; ox, oy, oth = ob[j, 1:]; c, s = math.cos(mth), math.sin(mth); return (mx + c * ox - s * oy, my + s * ox + c * oy, mth + oth)
traj = np.array([(t,) + pose_map(t) for t in ob[::3, 0]])
np.savez_compressed(sys.argv[2], traj=traj, mo=mo, cmd=np.array(CV), plan_t=np.array([p[0] for p in plans]), plan_n=np.array([len(p[1]) for p in plans]),
    plan_xy=np.concatenate([p[1] for p in plans]), map=mp[0], map_meta=np.array(mp[1:]),
    gcm_t=np.array([g[0] for g in gcm]), gcm=np.array([g[1] for g in gcm]), gcm_meta=np.array([g[2:] for g in gcm]),
    lcm_t=np.array([g[0] for g in lcm]), lcm=np.array([g[1] for g in lcm]), lcm_meta=np.array([g[2:] for g in lcm]),
    scan_t=np.array([s[0] for s in scans]), scan_r=np.array([s[1] for s in scans]), scan_a=np.array([s[2:] for s in scans]),
    mppi_t=np.array([x[0] for x in MP]), mppi_cand=np.array([x[1] for x in MP]), mppi_opt=np.array([x[2] for x in MP]))
print('궤적 %d · plan %d · 전역 %d · 로컬 %d · 스캔 %d · MPPI %d' % (len(traj), len(plans), len(gcm), len(lcm), len(scans), len(MP)))
