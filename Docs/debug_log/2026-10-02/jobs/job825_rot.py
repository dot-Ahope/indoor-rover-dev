#!/usr/bin/env python3
"""10-02 §11: 통제 회전 시험 — bag 기록하며 /cmd_vel 로 제자리 ±90° × 3. 라이다 외곽 0.08 m 안이면 정지·중단. 인자: BAG_NAME"""
import sys, time, math, signal, subprocess, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
NAME = sys.argv[1]; W = 0.38
TOP = '/scan /tf /tf_static /map /local_costmap/costmap /nvblox_node/static_map_slice /odometry/filtered /wheel_odom /cmd_vel'.split()
rec = subprocess.Popen(['ros2', 'bag', 'record', '-o', '/tmp/' + NAME] + TOP, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_DFL))
rclpy.init(); n = Node('rot_test'); pub = n.create_publisher(Twist, '/cmd_vel', 10); st = {'yaw': None, 'gap': 9.0}
def cb_o(m):
    q = m.pose.pose.orientation; st['yaw'] = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def cb_s(m):
    r = np.array(m.ranges); a = m.angle_min + m.angle_increment * np.arange(len(r)) + math.pi - 0.04677; ok = np.isfinite(r) & (r > 0.2) & (r < 3)
    x = 0.152 + r[ok] * np.cos(a[ok]); y = r[ok] * np.sin(a[ok])
    dx = np.where(x > 0, np.maximum(x - 0.262, 0), np.maximum(-x - 0.248, 0)); dy = np.maximum(np.abs(y) - 0.165, 0); st['gap'] = float(np.hypot(dx, dy).min())
n.create_subscription(Odometry, '/odometry/filtered', cb_o, 10); n.create_subscription(LaserScan, '/scan', cb_s, qos_profile_sensor_data)
def spin(sec):
    t = time.time() + sec
    while time.time() < t: rclpy.spin_once(n, timeout_sec=0.02)
def stop():
    for _ in range(10): pub.publish(Twist()); spin(0.05)
spin(4.0); print('시작 epoch %.1f, yaw %.1f°, 외곽 최소 %.3f m' % (time.time(), math.degrees(st['yaw']), st['gap']), flush=True)
abort = False
for k in range(3):
    for sgn in (1, -1):
        y0 = st['yaw']; acc = 0.0; prev = y0; t0 = time.time()
        while acc < math.radians(90) and time.time() - t0 < 10:
            if st['gap'] < 0.08: abort = True; break
            tw = Twist(); tw.angular.z = sgn * W; pub.publish(tw); spin(0.05)
            d = (st['yaw'] - prev + math.pi) % (2 * math.pi) - math.pi; acc += abs(d); prev = st['yaw']
        stop(); print('  %d회 %s: %.0f° / %.1f s, 외곽 최소 %.3f m' % (k + 1, '+' if sgn > 0 else '-', math.degrees(acc), time.time() - t0, st['gap']), flush=True)
        if abort: print('  ★ 외곽 0.08 m 안 — 중단', flush=True); break
        spin(2.0)
    if abort: break
spin(3.0); print('끝 epoch %.1f' % time.time(), flush=True)
rec.send_signal(signal.SIGINT); rec.wait(timeout=15)
