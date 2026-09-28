#!/usr/bin/env python3
"""직진 전·후진 분석 (2026-09-28 §23, bag 만으로):
  ① 구간(지령 |v|>0.01)마다 실제 이동 = 정지 스캔 ICP. **초기값 = EKF 이동**(job620 은 초기 이동 0 이라 0.6 m 직진에서 엉뚱한 해로 수렴 — 전진이 −0.155 m 로 나옴)
  ② 휠 적분 거리(/wheel_odom vx), EKF 이동·방향 변화, 스캔 방향 변화
  ③ 바퀴별 목표·측정 속도·듀티·pps(/rover/status L·R) — 구간 시작 1 s 뒤부터 평균(러너는 QoS 불일치로 못 받음)
  인자: BAG"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
from scipy.spatial import cKDTree


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def uw(a): return (a + math.pi) % (2 * math.pi) - math.pi


BAG = sys.argv[1]
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
scans, cmd, ob, wo, st, l2b = [], [], [], [], [], None
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if tp not in ('/tf', '/tf_static', '/scan', '/cmd_vel', '/wheel_odom', '/rover/status'): continue
    m = deserialize_message(data, get_message(types[tp]))
    if tp == '/scan': scans.append((t, m))
    elif tp == '/cmd_vel': cmd.append((t, m.linear.x))
    elif tp == '/wheel_odom': wo.append((t, m.twist.twist.linear.x))
    elif tp == '/rover/status':
        d = {}
        for s in m.status:
            for kv in s.values:
                if kv.key in ('L', 'R'):
                    try: d[kv.key] = {a: int(b) for a, b in (p.split('=') for p in kv.value.split())}
                    except Exception: pass
        if d: st.append((t, d))
    else:
        for tr in m.transforms:
            if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append((t, tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation)))
            elif tr.child_frame_id == 'lidar_link': l2b = (tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))
print('스캔 %d, 휠 %d, status %d(%.1f Hz)' % (len(scans), len(wo), len(st), (len(st) - 1) / (st[-1][0] - st[0][0]) if len(st) > 1 else 0))


def pts(m):
    rr = np.asarray(m.ranges, dtype=float); a = m.angle_min + np.arange(len(rr)) * m.angle_increment
    ok = np.isfinite(rr) & (rr > 0.40) & (rr < 8.0); x = rr[ok] * np.cos(a[ok]); y = rr[ok] * np.sin(a[ok]); c, s = math.cos(l2b[2]), math.sin(l2b[2])
    return np.c_[l2b[0] + c * x - s * y, l2b[1] + s * x + c * y][::2]


def icp(P0, P1, th, t):
    tree = cKDTree(P0); t = np.array(t, dtype=float)
    for it in range(60):
        c, s = math.cos(th), math.sin(th); R = np.array([[c, -s], [s, c]]); Q = P1 @ R.T + t
        d, idx = tree.query(Q); lim = min(max(0.08, 0.5 * 0.9 ** it), max(0.08, np.percentile(d, 80))); k = d < lim
        A = P1[k]; B = P0[idx[k]]; ca, cb = A.mean(0), B.mean(0); U, S_, Vt = np.linalg.svd((A - ca).T @ (B - cb)); Rn = Vt.T @ U.T
        if np.linalg.det(Rn) < 0: Vt[1] *= -1; Rn = Vt.T @ U.T
        th = math.atan2(Rn[1, 0], Rn[0, 0]); t = cb - Rn @ ca
    return t, th, float(np.sqrt((d[k] ** 2).mean()))


def at(arr, t):
    k = bisect.bisect_left([a[0] for a in arr], t); return arr[min(max(k, 0), len(arr) - 1)]


segs = []
for t, v in cmd:
    if abs(v) > 0.01:
        if segs and t - segs[-1][1] < 0.5 and (v > 0) == segs[-1][2]: segs[-1][1] = t
        else: segs.append([t, t, v > 0])
segs = [s for s in segs if s[1] - s[0] > 2.0]
rows = []
for k, (a, b, fwd) in enumerate(segs):
    tA, tB = a - 0.8, b + 2.5
    oA, oB = at(ob, tA), at(ob, tB)
    c, s = math.cos(oA[3]), math.sin(oA[3]); dx, dy = oB[1] - oA[1], oB[2] - oA[2]
    ex, ey = c * dx + s * dy, -s * dx + c * dy; eth = uw(oB[3] - oA[3])
    res = []
    for da, db in ((0.0, 0.0), (-0.3, 0.3), (-0.6, 0.6)):
        sA, sB = at(scans, tA + da), at(scans, tB + db)
        t_, th_, rms = icp(pts(sA[1]), pts(sB[1]), eth, (ex, ey)); res.append((t_[0], t_[1], th_, rms))
    R_ = np.median(np.array(res), axis=0)
    wd = sum(abs(v) * (t2 - t1) for (t1, v), (t2, _) in zip(wo, wo[1:]) if a <= t1 <= b + 1.5)
    real = math.hypot(R_[0], R_[1])
    ss = [d for t, d in st if a + 1.0 <= t <= b]
    def av(side, key): v = [d[side][key] for d in ss if side in d and key in d[side]]; return sum(v) / len(v) if v else float('nan')
    rows.append((fwd, wd, real, math.hypot(ex, ey), math.degrees(eth), math.degrees(R_[2])))
    print('구간 %d %s: 휠 %.3f m | EKF %.3f m | 스캔 실제 (%+.3f, %+.3f) = %.3f m, rms %.3f | 휠/실제 %.3f | 방향 변화 EKF %+.2f° 스캔 %+.2f°'
          % (k + 1, '전진' if fwd else '후진', wd, math.hypot(ex, ey), R_[0], R_[1], real, R_[3], wd / max(real, 1e-6), math.degrees(eth), math.degrees(R_[2])))
    print('   L 목표 %+.0f 측정 %+.0f mm/s 듀티 %+.1f %% pps %.0f | R 목표 %+.0f 측정 %+.0f mm/s 듀티 %+.1f %% pps %.0f (status %d 개)'
          % (av('L', 'tgt'), av('L', 'v'), av('L', 'd'), av('L', 'pps'), av('R', 'tgt'), av('R', 'v'), av('R', 'd'), av('R', 'pps'), len(ss)))
for f, nm in ((True, '전진'), (False, '후진')):
    rr = [x for x in rows if x[0] == f]
    if rr: print('%s 평균: 휠/실제 %.3f, 방향 변화 EKF %+.2f° 스캔 %+.2f°' % (nm, sum(x[1] for x in rr) / sum(x[2] for x in rr), sum(x[4] for x in rr) / len(rr), sum(x[5] for x in rr) / len(rr)))
