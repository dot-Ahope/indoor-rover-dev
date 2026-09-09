#!/usr/bin/env python3
"""job125 의 상자 검출이 왜 실패하는지 — 같은 필터를 단계별로 풀어서 점 수를 센다."""
import math, time, rclpy, tf2_ros
import numpy as np
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2

rclpy.init(); n = Node('det137')
buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n); S = {}
n.create_subscription(PointCloud2, '/camera/camera/depth/color/points',
                      lambda m: S.__setitem__('pc', m), qos_profile_sensor_data)


def Rq(q):
    w, x, y, z = q.w, q.x, q.y, q.z
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])


t0 = time.time()
while time.time()-t0 < 15 and 'pc' not in S:
    rclpy.spin_once(n, timeout_sec=0.1)
if 'pc' not in S:
    print("포인트클라우드 수신 실패"); raise SystemExit(1)
m = S['pc']
print("수신 OK: frame=%s, %dx%d, point_step=%d, stamp=%d.%09d"
      % (m.header.frame_id, m.width, m.height, m.point_step,
         m.header.stamp.sec, m.header.stamp.nanosec))
try:
    tr = buf.lookup_transform('base_link', m.header.frame_id, rclpy.time.Time()).transform
    print("TF base_link←%s OK: t=(%.3f,%.3f,%.3f)"
          % (m.header.frame_id, tr.translation.x, tr.translation.y, tr.translation.z))
except Exception as e:
    print("TF 실패:", e); raise SystemExit(1)

off = {f.name: f.offset for f in m.fields}
raw = np.frombuffer(m.data, dtype=np.uint8).reshape(-1, m.point_step)
xyz = np.stack([raw[:, off[k]:off[k]+4].copy().view(np.float32).ravel() for k in ('x', 'y', 'z')], axis=1)
fin = np.isfinite(xyz).all(axis=1)
P = xyz[fin] @ Rq(tr.rotation).T + np.array([tr.translation.x, tr.translation.y, tr.translation.z])
print("전체 %d, 유한 %d" % (len(xyz), len(P)))

steps = [
    ("z > 0.05",            P[:, 2] > 0.05),
    ("z < 0.30",            P[:, 2] < 0.30),
    ("x > 0.5",             P[:, 0] > 0.5),
    ("x < 1.5",             P[:, 0] < 1.5),
    ("|y| < 0.5",           np.abs(P[:, 1]) < 0.5),
]
mask = np.ones(len(P), bool)
for name, mk in steps:
    mask &= mk
    print("  누적 %-14s → %6d" % (name, int(mask.sum())))
print("job125 판정: %d (>=40 이어야 통과)" % int(mask.sum()))

print("\n각 조건을 단독으로 적용했을 때:")
for name, mk in steps:
    print("  %-14s → %6d" % (name, int(mk.sum())))

sel = P[mask]
if len(sel):
    print("\n통과 점군: x %.2f~%.2f, y %+.2f~%+.2f, z %.3f~%.3f"
          % (sel[:, 0].min(), sel[:, 0].max(), sel[:, 1].min(), sel[:, 1].max(),
             sel[:, 2].min(), sel[:, 2].max()))
# job62c 와 같은 조건도 같이
alt = (P[:, 2] > 0.06) & (P[:, 2] < 0.40) & (P[:, 0] > 0.3) & (P[:, 0] < 1.45)
print("job62c 조건(z .06~.40, x .3~1.45, y 무제한) → %d" % int(alt.sum()))
if alt.sum():
    A = P[alt]
    print("  그 점군 y 범위 %+.2f~%+.2f, x %.2f~%.2f" % (A[:, 1].min(), A[:, 1].max(), A[:, 0].min(), A[:, 0].max()))
rclpy.shutdown()
