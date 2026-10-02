#!/usr/bin/env python3
"""10-02 §11: 통제 회전 시험 전 — 벽까지 거리(라이다, 차체 기준)와 제자리 회전 여유 계산(모서리 반경 0.31 m)"""
import time, math, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
rclpy.init(); n = Node('wall_gap'); S = []
n.create_subscription(LaserScan, '/scan', lambda m: S.append(m), qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < 4 and len(S) < 10: rclpy.spin_once(n, timeout_sec=0.2)
m = S[-1]; r = np.array(m.ranges); a = m.angle_min + m.angle_increment * np.arange(len(r)) + math.pi - 0.04677
ok = np.isfinite(r) & (r > 0.2) & (r < 3); x = 0.152 + r[ok] * np.cos(a[ok]); y = r[ok] * np.sin(a[ok])
dx = np.where(x > 0, np.maximum(x - 0.262, 0), np.maximum(-x - 0.248, 0)); dy = np.maximum(np.abs(y) - 0.165, 0); d = np.hypot(dx, dy)
rc = np.hypot(x, y)
for nm, msk in (('왼쪽(y>0)', y > 0.165), ('오른쪽(y<0)', y < -0.165), ('앞', x > 0.262), ('뒤', x < -0.248)):
    if msk.any(): k = np.argmin(d[msk]); print('  %-10s 외곽까지 최소 %.3f m (점 차체기준 %+.2f, %+.2f)' % (nm, d[msk][k], x[msk][k], y[msk][k]))
print('  중심에서 가장 가까운 점 %.3f m → 제자리 회전 여유(모서리 반경 0.31 m) %.3f m' % (rc.min(), rc.min() - 0.31))
