#!/usr/bin/env python3
"""09-30 §4 F1-1a: 지금 로버 map 자세(5 s 평균)와 오른쪽 앞 모서리의 출발 표시 대비 예측(출발 = map 원점, 출발 yaw 는 원점 자세).
   오른쪽 앞 모서리 = base_link (+0.262, −0.165) (09-30 §2). 인자: 없음"""
import time, math
import rclpy
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener

rclpy.init(); n = Node('pose_now'); tb = Buffer(); TransformListener(tb, n)


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


xs = []; t0 = time.time()
while time.time() - t0 < 7:
    rclpy.spin_once(n, timeout_sec=0.05)
    if time.time() - t0 < 2: continue
    try:
        t = tb.lookup_transform('map', 'base_link', rclpy.time.Time()).transform
        xs.append((t.translation.x, t.translation.y, yaw(t.rotation)))
    except Exception: pass
x = sum(a[0] for a in xs) / len(xs); y = sum(a[1] for a in xs) / len(xs)
th = math.atan2(sum(math.sin(a[2]) for a in xs), sum(math.cos(a[2]) for a in xs))
c, s = math.cos(th), math.sin(th)
cx, cy = x + c * 0.262 - s * (-0.165), y + s * 0.262 + c * (-0.165)
print('지금 map 자세 (%.4f, %.4f, %.2f°) [%d 표본]' % (x, y, math.degrees(th), len(xs)))
print('오른쪽 앞 모서리 예측 — 출발 표시(0.262, −0.165) 대비: 세로 %+.4f m(+ 앞), 가로 %+.4f m(+ 왼쪽), 방향 %+.2f°'
      % (cx - 0.262, cy + 0.165, math.degrees(th)))
