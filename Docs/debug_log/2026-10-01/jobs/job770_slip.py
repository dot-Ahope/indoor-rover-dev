#!/usr/bin/env python3
"""10-01 §8.26: f2a9 케이블 가드 통과 — 0.5 s 마다 명령 v, 휠 v(트랙이 돈 속도), SLAM(map) 실제 속도, 자이로 피치·롤 각속도(IMU x·z),
   가속도(전후·상하), /rover/status 내용(있으면). 미끄러짐 = 휠 v 는 있는데 실제 속도 ≈ 0. 토크 부족 = 명령은 있는데 휠 v ≈ 0."""
import sys, math, numpy as np, rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=sys.argv[1], storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
cmd, wh, imu, mo, ob, st = [], [], [], [], [], []
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if tp == '/cmd_vel': m = deserialize_message(data, get_message(types[tp])); cmd.append((t, m.linear.x))
    elif tp == '/wheel_odom': m = deserialize_message(data, get_message(types[tp])); wh.append((t, m.twist.twist.linear.x))
    elif tp == '/imu/data':
        m = deserialize_message(data, get_message(types[tp])); imu.append((t, m.angular_velocity.x, m.angular_velocity.z, m.linear_acceleration.x, m.linear_acceleration.y, m.linear_acceleration.z))
    elif tp == '/rover/status' and len(st) < 3: st.append(str(deserialize_message(data, get_message(types[tp])))[:400])
    elif tp == '/tf':
        for x in deserialize_message(data, get_message(types[tp])).transforms:
            k = (x.header.frame_id, x.child_frame_id); v = (t, x.transform.translation.x, x.transform.translation.y, yaw(x.transform.rotation))
            if k == ('map', 'odom'): mo.append(v)
            elif k == ('odom', 'base_link'): ob.append(v)
cmd, wh, imu, mo, ob = map(np.array, (cmd, wh, imu, mo, ob))
print('status 예시:', st[:1])
def mb(t):
    i = max(np.searchsorted(ob[:, 0], t) - 1, 0); j = max(np.searchsorted(mo[:, 0], t) - 1, 0)
    ox, oy, oth = ob[i, 1:]; mx, my, mth = mo[j, 1:]; c, s = math.cos(mth), math.sin(mth); return mx + c * ox - s * oy, my + s * ox + c * oy
def mean(a, t0, t1, c):
    m = (a[:, 0] >= t0) & (a[:, 0] < t1); return a[m, c].mean() if m.any() else float('nan')
def amax(a, t0, t1, c):
    m = (a[:, 0] >= t0) & (a[:, 0] < t1); return np.abs(a[m, c]).max() if m.any() else float('nan')
T0 = cmd[0, 0]
print('  t    위치(map)       | 명령 v | 휠 v  | 실제 v(SLAM) | 휠÷실제 | 롤·피치 각속도 최대 | 가속 상하 최대')
for t in np.arange(T0, cmd[-1, 0], 0.5):
    p0, p1 = mb(t), mb(t + 0.5); vr = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / 0.5; vw = mean(wh, t, t + .5, 1)
    flag = ' ← 미끄러짐?' if abs(vw) > 0.03 and vr < 0.4 * abs(vw) else (' ← 휠 정지?' if mean(cmd, t, t + .5, 1) > 0.03 and abs(vw) < 0.01 else '')
    print('%5.1f (%+.2f, %+.2f) | %.3f | %.3f | %.3f | %5.1f | %.2f·%.2f rad/s | %.1f m/s²%s' % (t - T0, p0[0], p0[1], mean(cmd, t, t + .5, 1), vw, vr, abs(vw) / max(vr, 1e-3),
          amax(imu, t, t + .5, 1), amax(imu, t, t + .5, 2), amax(imu, t, t + .5, 5) if True else 0, flag))
