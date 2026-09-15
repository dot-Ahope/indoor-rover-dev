#!/usr/bin/env python3
"""세션 누적 오차 점검 (2026-09-15, 사용자 우려: 시간이 지나 ROS 세션에 오차가 쌓였는가). 정지 30 s, 주행 없음.
   - /wheel_odom, /odometry/filtered, /scan, 깊이: 수신률과 stamp 지연(now − header.stamp)
   - EKF yaw 드리프트: /odometry/filtered yaw 의 30 s 변화(°/min) ; 휠 odom 위치 변화(정지인데 움직이나)
   - TF: map→odom, odom→base_link 최신 stamp 지연 / 정지 중 변화
"""
import math, time, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan, PointCloud2
import tf2_ros
DUR = 30.0
rclpy.init(); n = Node('drift321'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
S = {k: [] for k in ('wo', 'of', 'sc', 'pc')}
def yaw(q): return math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
def mk(k, has_pose):
    def cb(m):
        now = n.get_clock().now().nanoseconds * 1e-9; st = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
        rec = [now, now - st]
        if has_pose: p = m.pose.pose; rec += [p.position.x, p.position.y, yaw(p.orientation)]
        S[k].append(rec)
    return cb
n.create_subscription(Odometry, '/wheel_odom', mk('wo', True), qos_profile_sensor_data)
n.create_subscription(Odometry, '/odometry/filtered', mk('of', True), qos_profile_sensor_data)
n.create_subscription(LaserScan, '/scan', mk('sc', False), qos_profile_sensor_data)
n.create_subscription(PointCloud2, '/camera/depth/points_filtered', mk('pc', False), qos_profile_sensor_data)
tfs = []
t0 = time.time(); last_tf = 0
while time.time() - t0 < DUR:
    rclpy.spin_once(n, timeout_sec=0.05)
    if time.time() - last_tf > 2.0:
        last_tf = time.time()
        try:
            a = buf.lookup_transform('map', 'odom', rclpy.time.Time()); b = buf.lookup_transform('odom', 'base_link', rclpy.time.Time())
            now = n.get_clock().now().nanoseconds * 1e-9
            tfs.append((now - (a.header.stamp.sec + a.header.stamp.nanosec*1e-9), a.transform.translation.x, a.transform.translation.y, yaw(a.transform.rotation),
                        now - (b.header.stamp.sec + b.header.stamp.nanosec*1e-9), b.transform.translation.x, b.transform.translation.y, yaw(b.transform.rotation)))
        except Exception as e:
            tfs.append(None)
print('=== 수신률·stamp 지연 (%.0f s) ===' % DUR)
for k, name in (('wo', '/wheel_odom'), ('of', '/odometry/filtered'), ('sc', '/scan'), ('pc', '깊이(필터)')):
    A = np.array([r[:2] for r in S[k]]) if S[k] else np.zeros((0, 2))
    if len(A): print('  %-20s %5.1f Hz  지연 중앙 %6.1f ms  최대 %6.1f ms' % (name, len(A) / DUR, 1e3 * np.median(A[:, 1]), 1e3 * A[:, 1].max()))
    else: print('  %-20s 수신 없음' % name)
for k, name in (('wo', '휠 odom'), ('of', 'EKF')):
    P = np.array([r[2:] for r in S[k]]) if S[k] else np.zeros((0, 3))
    if len(P) > 10:
        dyaw = math.degrees(P[-1, 2] - P[0, 2]); dxy = math.hypot(P[-1, 0] - P[0, 0], P[-1, 1] - P[0, 1])
        print('  %s 정지 %.0f s: 위치 변화 %.4f m, yaw 변화 %+.3f° (%+.2f °/min)' % (name, DUR, dxy, dyaw, dyaw * 60 / DUR))
T = [t for t in tfs if t]
if T:
    T = np.array(T)
    print('=== TF ===')
    print('  map→odom: stamp 지연 중앙 %.2f s | 정지 중 변화 x %.4f y %.4f yaw %.3f°' % (np.median(T[:, 0]), T[:, 1].max() - T[:, 1].min(), T[:, 2].max() - T[:, 2].min(), math.degrees(T[:, 3].max() - T[:, 3].min())))
    print('  odom→base: stamp 지연 중앙 %.3f s | 정지 중 변화 x %.4f y %.4f yaw %.3f°' % (np.median(T[:, 4]), T[:, 5].max() - T[:, 5].min(), T[:, 6].max() - T[:, 6].min(), math.degrees(T[:, 7].max() - T[:, 7].min())))
    print('  (map→odom 지연이 크면 SLAM 이 정지 중 갱신을 안 하는 것 — 정상. 손 배치 뒤엔 재기동으로 원점 재설정)')
print('  TF 조회 실패 %d/%d' % (sum(1 for t in tfs if t is None), len(tfs)))
