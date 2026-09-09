#!/usr/bin/env python3
"""EKF 가 입력은 받는데 출력을 안 하는 원인 추적 — 헤더 타임스탬프와 시스템 시각을 비교한다.

robot_localization 은 입력 메시지의 stamp 가 필터 현재 시각보다 과거면 버리고,
미래로 크게 튀면 그 시각으로 필터를 끌고 간 뒤 이후 정상 메시지를 전부 '과거' 로 보고 버린다.
보드는 rmw_uros_sync_session 으로 60초마다 시각을 재동기하므로, 그 보정이 튀면 이 상태가 된다.
"""
import time, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu, LaserScan

rclpy.init(); n = Node('stamp147')
D = {}


def mk(k):
    def cb(m):
        st = m.header.stamp.sec + m.header.stamp.nanosec*1e-9
        D.setdefault(k, []).append((time.time(), st))
    return cb


n.create_subscription(Odometry, '/wheel_odom', mk('wheel_odom'), qos_profile_sensor_data)
n.create_subscription(Odometry, '/wheel_odom/conditioned', mk('conditioned'), qos_profile_sensor_data)
n.create_subscription(Imu, '/imu/data', mk('imu/data'), qos_profile_sensor_data)
n.create_subscription(LaserScan, '/scan', mk('scan'), qos_profile_sensor_data)
n.create_subscription(Odometry, '/odometry/filtered', mk('filtered'), 10)

t0 = time.time()
while time.time()-t0 < 12:
    rclpy.spin_once(n, timeout_sec=0.05)

print("현재 시스템 시각 = %.3f" % time.time())
print("%-14s %6s  %14s  %14s  %10s" % ("토픽", "수신", "마지막 stamp", "수신 host시각", "오프셋(s)"))
for k in ('wheel_odom', 'conditioned', 'imu/data', 'scan', 'filtered'):
    d = D.get(k, [])
    if not d:
        print("%-14s %6d  %s" % (k, 0, "— 수신 없음"))
        continue
    h, s = d[-1]
    span = d[-1][1] - d[0][1]
    print("%-14s %6d  %14.3f  %14.3f  %+10.3f   (stamp 진행 %.3f s / 실경과 %.3f s)"
          % (k, len(d), s, h, s - h, span, d[-1][0]-d[0][0]))

# stamp 가 뒤로 가는(역행) 샘플 탐지
print("\nstamp 역행 검사:")
for k, d in D.items():
    back = sum(1 for i in range(1, len(d)) if d[i][1] < d[i-1][1])
    jump = max((d[i][1]-d[i-1][1] for i in range(1, len(d))), default=0.0)
    print("  %-14s 역행 %d회, 최대 전진폭 %.3f s" % (k, back, jump))
rclpy.shutdown()
