#!/usr/bin/env python3
"""09-29 §12.3 W3 부근 전선 밟기 영향 (사용자 관찰: "W3 목적지 위치에 긴 전선이 있어 밟으면서 흔들림·오차").
   1 s 창마다: ① 기울기 흔들림 = 카메라 IMU 자이로 중 yaw 축(광학 y)이 아닌 두 축(x, z)의 RMS(°/s),
   ② 가속도 크기 표준편차(m/s²), ③ map→odom 이동 변화(cm) = SLAM 이 그 1 s 동안 odom 을 고친 양,
   ④ 휠 속도 vs map 속도 차(cm/s) = 헛돎·긁힘 흔적. 로버 map 위치와 W3 까지 거리를 같이 적는다.
   인자: BAG"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

W3 = (5.5, -2.2)


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=sys.argv[1], storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
imu, wo, mo, ob, cmd = [], [], [], [], []
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if tp not in ('/imu/data', '/wheel_odom', '/tf', '/cmd_vel'): continue
    m = deserialize_message(data, get_message(types[tp]))
    if tp == '/imu/data':
        a, g = m.linear_acceleration, m.angular_velocity; imu.append((t, g.x, g.y, g.z, math.sqrt(a.x ** 2 + a.y ** 2 + a.z ** 2)))
    elif tp == '/wheel_odom': wo.append((t, m.twist.twist.linear.x))
    elif tp == '/cmd_vel': cmd.append((t, m.linear.x, m.angular.z))
    else:
        for tr in m.transforms:
            p, q = tr.transform.translation, tr.transform.rotation; v = (t, p.x, p.y, yaw(q))
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append(v)
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append(v)
mo.sort(); ob.sort(); imu = np.array(imu); wo = np.array(wo)
print('IMU %d 개(%.0f Hz), 휠 %d, map→odom %d' % (len(imu), len(imu) / (imu[-1, 0] - imu[0, 0]), len(wo), len(mo)))


def at(lst, t):
    k = bisect.bisect_left([x[0] for x in lst], t); return lst[min(max(k, 0), len(lst) - 1)]


def mpose(t):
    A = at(mo, t); B = at(ob, t); c, s = math.cos(A[3]), math.sin(A[3])
    return A[1] + c * B[1] - s * B[2], A[2] + s * B[1] + c * B[2]


act = [c[0] for c in cmd if abs(c[1]) > 0.005 or abs(c[2]) > 0.01]
t0, t1 = act[0], act[-1]
rows = []
t = t0
while t + 1 <= t1:
    m = (imu[:, 0] >= t) & (imu[:, 0] < t + 1)
    tilt = math.degrees(math.sqrt(np.mean(imu[m, 1] ** 2 + imu[m, 3] ** 2))) if m.sum() > 10 else float('nan')
    acs = float(np.std(imu[m, 4])) if m.sum() > 10 else float('nan')
    a, b = at(mo, t), at(mo, t + 1); dmo = 100 * math.hypot(b[1] - a[1], b[2] - a[2])
    p0, p1 = mpose(t), mpose(t + 1); vmap = 100 * math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    w = (wo[:, 0] >= t) & (wo[:, 0] < t + 1); vw = 100 * float(np.mean(np.abs(wo[w, 1]))) if w.sum() else float('nan')
    dw3 = math.hypot(p0[0] - W3[0], p0[1] - W3[1])
    rows.append((t - t0, p0[0], p0[1], dw3, tilt, acs, dmo, vw, vmap)); t += 1
R = np.array(rows)
near = R[:, 3] < 0.8; far = ~near
med_t, med_a = np.nanmedian(R[far, 4]), np.nanmedian(R[far, 5])
print('기준(W3 0.8 m 밖, %d 창): 기울기 흔들림 중앙값 %.2f °/s (90 %% %.2f), 가속도 표준편차 중앙값 %.3f m/s², map→odom 1 s 변화 중앙값 %.2f cm'
      % (far.sum(), med_t, np.nanpercentile(R[far, 4], 90), med_a, np.median(R[far, 6])))
print('W3 0.8 m 안(%d 창): 기울기 흔들림 중앙값 %.2f °/s · 최대 %.2f, 가속도 표준편차 최대 %.3f, map→odom 1 s 변화 최대 %.2f cm'
      % (near.sum(), np.nanmedian(R[near, 4]), np.nanmax(R[near, 4]), np.nanmax(R[near, 5]), R[near, 6].max()))
print('\n기울기 흔들림 상위 10 창 (t s | map x, y | W3 까지 | 기울기 °/s | 가속 표준편차 | map→odom cm | 휠 cm/s | map cm/s):')
for k in np.argsort(-np.nan_to_num(R[:, 4]))[:10]:
    x = R[k]; print('  %5.0f | (%5.2f, %5.2f) | %4.2f m | %5.2f | %.3f | %5.2f | %4.1f | %4.1f' % tuple(x))
print('\nmap→odom 1 s 변화 상위 8 창:')
for k in np.argsort(-R[:, 6])[:8]:
    x = R[k]; print('  %5.0f | (%5.2f, %5.2f) | %4.2f m | %5.2f | %.3f | %5.2f | %4.1f | %4.1f' % tuple(x))
print('\nW3 0.8 m 안 전체 창:')
for x in R[near]: print('  %5.0f | (%5.2f, %5.2f) | %4.2f m | %5.2f | %.3f | %5.2f | %4.1f | %4.1f' % tuple(x))
