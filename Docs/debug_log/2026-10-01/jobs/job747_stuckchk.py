#!/usr/bin/env python3
"""10-01 §8.11: f2a4 STUCK(14:02:52) 앞 8 s — 0.5 s 마다 명령 v·ω, 휠 v·ω, EKF v, 자이로 ω, map 위치 변화(SLAM), 최근접 라이다 점 거리(차체 외곽 기준 아님, 라이다 중심)."""
import sys, math, datetime, numpy as np, rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=sys.argv[1], storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
T1 = datetime.datetime.now().replace(hour=14, minute=2, second=52, microsecond=700000).timestamp(); T0 = T1 - 8
D = {k: [] for k in ('cmd', 'wh', 'ekf', 'gy', 'mo', 'ob', 'sc')}
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if not (T0 - 1 <= t <= T1 + 1): continue
    if tp not in ('/cmd_vel', '/wheel_odom', '/odometry/filtered', '/imu/data', '/tf', '/scan'): continue
    m = deserialize_message(data, get_message(types[tp]))
    if tp == '/cmd_vel': D['cmd'].append((t, m.linear.x, m.angular.z))
    elif tp == '/wheel_odom': D['wh'].append((t, m.twist.twist.linear.x, m.twist.twist.angular.z))
    elif tp == '/odometry/filtered': D['ekf'].append((t, m.twist.twist.linear.x, m.twist.twist.angular.z))
    elif tp == '/imu/data': D['gy'].append((t, -m.angular_velocity.y, 0))
    elif tp == '/scan':
        rr = np.array(m.ranges); rr = rr[np.isfinite(rr) & (rr > 0.15)]; D['sc'].append((t, rr.min() if len(rr) else np.nan, 0))
    elif tp == '/tf':
        for x in m.transforms:
            k = (x.header.frame_id, x.child_frame_id); v = (t, x.transform.translation.x, x.transform.translation.y, yaw(x.transform.rotation))
            if k == ('map', 'odom'): D['mo'].append(v)
            elif k == ('odom', 'base_link'): D['ob'].append(v)
D = {k: np.array(v) for k, v in D.items() if v}
def mean(k, a, b, c):
    x = D[k]; m = (x[:, 0] >= a) & (x[:, 0] < b); return x[m, c].mean() if m.any() else float('nan')
def mapxy(t):
    i = np.searchsorted(D['ob'][:, 0], t) - 1; j = np.searchsorted(D['mo'][:, 0], t) - 1
    ox, oy, oth = D['ob'][i, 1:]; mx, my, mth = D['mo'][j, 1:]; c, s = math.cos(mth), math.sin(mth)
    return mx + c * ox - s * oy, my + s * ox + c * oy
print(' 시각      명령 v  ω   | 휠 v   ω    | EKF v | 자이로ω | map 이동(0.5 s) | 최근접 라이다')
for a in np.arange(T0, T1, 0.5):
    p0, p1 = mapxy(a), mapxy(a + 0.5)
    print('%s  %+.3f %+.2f | %+.3f %+.2f | %+.3f | %+.2f  | %5.1f cm        | %.2f m' % (datetime.datetime.fromtimestamp(a).strftime('%H:%M:%S.%f')[:10],
        mean('cmd', a, a + .5, 1), mean('cmd', a, a + .5, 2), mean('wh', a, a + .5, 1), mean('wh', a, a + .5, 2), mean('ekf', a, a + .5, 1), mean('gy', a, a + .5, 1),
        math.hypot(p1[0] - p0[0], p1[1] - p0[1]) * 100, mean('sc', a, a + .5, 1)))
