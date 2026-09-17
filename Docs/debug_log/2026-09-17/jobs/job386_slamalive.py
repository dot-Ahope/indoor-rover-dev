#!/usr/bin/env python3
"""SLAM 생존 게이트 (2026-09-17 mp7): slam_toolbox 프로세스가 살아 있어도 그래프에서 사라지거나 map->odom 이 끊길 수 있다.
   5 s 동안 /tf 의 map->odom 수신 간격 최대·수신 지연을 잰다. 마지막 줄: OK / FAIL"""
import time, rclpy
from rclpy.node import Node
from tf2_msgs.msg import TFMessage
rclpy.init(); n = Node('slamalive386'); rx = []
def cb(m):
    now = n.get_clock().now().nanoseconds * 1e-9
    for tr in m.transforms:
        if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
            rx.append((now, now - (tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9)))
n.create_subscription(TFMessage, '/tf', cb, 100)
t0 = time.time()
while time.time() - t0 < 5.0:
    rclpy.spin_once(n, timeout_sec=0.05)
if len(rx) < 2:
    print('map->odom 수신 %d 개 (5 s) — SLAM 무응답' % len(rx)); print('FAIL')
else:
    gap = max(rx[i][0] - rx[i - 1][0] for i in range(1, len(rx))); lag = max(r[1] for r in rx)
    print('map->odom %d 개/5 s, 최대 간격 %.2f s, 최대 stamp 지연 %.2f s' % (len(rx), gap, lag))
    # 09-17: 정상 SLAM 의 stamp 지연은 -0.08~+0.55 s 로 흔들린다(job393) → 지연 문턱 1.0 s. mp7 고장 때는 간격 5.1 s·지연 4.8 s
    print('OK' if (gap < 0.5 and lag < 1.0) else 'FAIL')
