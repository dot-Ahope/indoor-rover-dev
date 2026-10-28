#!/usr/bin/env python3
"""chk_scan_align — 지금 라이다 한 판을 정적 /map 에 맞춰 보고 yaw 를 얼마나 돌려야 가장 잘 맞는지(10-28 §16, 로버 안 움직임).
  점수 = 라이다 점 중 정적 점유 칸(≥65) 1 칸 안에 드는 비율. 지금 TF(0°)와 최적 yaw 차가 크면 로버 방향 추정이 틀린 것.
  같이 찍음: map→odom · odom→base_link(yaw) — 정지 중 어느 쪽이 움직였는지."""
import math, time, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy, qos_profile_sensor_data
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan
from tf2_ros import Buffer, TransformListener
rclpy.init(); n = Node('chk_scan_align'); S = []; M = []
n.create_subscription(LaserScan, '/scan', S.append, qos_profile_sensor_data)
n.create_subscription(OccupancyGrid, '/map', M.append, QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE))
buf = Buffer(); TransformListener(buf, n); t0 = time.time(); T = {}
yaw = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
while time.time() - t0 < 20 and (not S or not M or len(T) < 3):
    rclpy.spin_once(n, timeout_sec=0.2)
    for k, (a, b) in {'ml': ('map', None), 'mo': ('map', 'odom'), 'ob': ('odom', 'base_link')}.items():
        try: T[k] = buf.lookup_transform(a, b or (S[-1].header.frame_id if S else 'x'), rclpy.time.Time())
        except Exception: pass
for k in ('mo', 'ob'):
    t = T[k].transform; print('%s: (%.3f, %.3f, %.1f°)' % ({'mo': 'map→odom', 'ob': 'odom→base_link'}[k], t.translation.x, t.translation.y, math.degrees(yaw(t.rotation))))
m = M[-1]; i = m.info; g = np.array(m.data, np.int16).reshape(i.height, i.width) >= 65
from scipy.ndimage import binary_dilation
g = binary_dilation(g, iterations=1)
tl = T['ml'].transform; lx, ly, la = tl.translation.x, tl.translation.y, yaw(tl.rotation)
sc = S[-1]; r = np.array(sc.ranges); a = sc.angle_min + sc.angle_increment * np.arange(len(r)); ok = np.isfinite(r) & (r > sc.range_min) & (r < min(sc.range_max, 6))
r, a = r[ok], a[ok]
def score(d):
    x = lx + r * np.cos(la + d + a); y = ly + r * np.sin(la + d + a)
    J = ((y - i.origin.position.y) / i.resolution).astype(int); I = ((x - i.origin.position.x) / i.resolution).astype(int)
    v = (J >= 0) & (J < g.shape[0]) & (I >= 0) & (I < g.shape[1]); return float(g[J[v], I[v]].mean())
res = [(score(math.radians(d)), d) for d in np.arange(-40, 40.5, 0.5)]
print('라이다 점 %d · 지금 TF(0°) 점수 %.3f' % (len(r), score(0.0)))
for s, d in sorted(res, reverse=True)[:5]: print('  yaw %+5.1f° → %.3f' % (d, s))
