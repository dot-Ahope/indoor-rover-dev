#!/usr/bin/env python3
"""미끄러짐 검증 2 (09-23 n62b): 라이다 스캔만으로 실제 몸체 회전을 잰다(휠·IMU·SLAM 과 독립).
   구간 [끝−W, 끝] 의 1 s 간격 스캔 쌍마다, range 프로파일(0.5° 재표본)을 원형 이동시켜 상관이 최대인 각 = 회전량.
   같은 구간의 휠 오도·EKF yaw 변화와 나란히 출력. 마지막 /rover/stuck 진단 전문도 출력. 인자: BAG [W=8]"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
BAG = sys.argv[1]; W = float(sys.argv[2]) if len(sys.argv) > 2 else 8.0
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
sc, wo, ek, cmd, st = [], [], [], [], []
while r.has_next():
    tp, data, ts = r.read_next()
    if tp not in ('/scan', '/wheel_odom', '/odometry/filtered', '/cmd_vel', '/rover/stuck'): continue
    m = deserialize_message(data, get_message(types[tp])); t = ts * 1e-9
    if tp == '/scan':
        a = m.angle_min + np.arange(len(m.ranges)) * m.angle_increment; rr = np.asarray(m.ranges, dtype=float)
        grid = np.arange(-math.pi, math.pi, math.radians(0.5)); ok = np.isfinite(rr) & (rr > 0.15) & (rr < 12)
        prof = np.interp(grid, np.unwrap(a[ok]) if ok.any() else grid, rr[ok] if ok.any() else np.zeros_like(grid), period=2 * math.pi)
        sc.append((t, prof))
    elif tp == '/wheel_odom': wo.append((t, yaw(m.pose.pose.orientation)))
    elif tp == '/odometry/filtered': ek.append((t, yaw(m.pose.pose.orientation)))
    elif tp == '/cmd_vel': cmd.append((t, m.angular.z))
    elif tp == '/rover/stuck': st.append((t, m))
T1 = cmd[-1][0]; T0 = T1 - W
def at(arr, t):
    k = bisect.bisect_left([x[0] for x in arr], t); return arr[min(max(k, 0), len(arr) - 1)][1]
def uw(x): return (x + math.pi) % (2 * math.pi) - math.pi
def rot(p0, p1):   # p1 = p0 을 s 칸 회전 → 몸체 회전은 −s
    best, bs = -1e9, 0
    for s in range(-120, 121):   # ±60°
        c = -np.mean(np.abs(np.roll(p0, s) - p1));
        if c > best: best, bs = c, s
    return -bs * 0.5
print('  t(끝 기준) | 지령 ω | 휠 Δ° | EKF Δ° | 라이다 스캔 Δ° ')
tot = np.zeros(3); t = T0
while t < T1 - 0.05:
    t2 = min(t + 1.0, T1)
    dw = math.degrees(uw(at(wo, t2) - at(wo, t))); de = math.degrees(uw(at(ek, t2) - at(ek, t))); ds = rot(at(sc, t), at(sc, t2))
    tot += (dw, de, ds); print('  %5.1f | %+.2f | %+6.1f | %+6.1f | %+6.1f' % (t - T1, at(cmd, t), dw, de, ds)); t = t2
print('합계: 휠 %+.1f° / EKF %+.1f° / 라이다 %+.1f°  (스캔 %d 개, 0.5° 분해능)' % (tot[0], tot[1], tot[2], len(sc)))
for t, m in st[-3:]:
    print('stuck @%+.1f s: ' % (t - T1) + ' | '.join('lvl=%s msg=%s %s' % (s.level, s.message, ' '.join('%s=%s' % (kv.key, kv.value) for kv in s.values)) for s in m.status)[:300])
