#!/usr/bin/env python3
"""09-29 §9 V1: cuVSLAM 출력 측정 (컨테이너 안에서 실행 — VisualSlamStatus 메시지 정의가 거기 있음).
   DUR 초 동안 /visual_slam/tracking/odometry 주기·위치/yaw 변화·최대 이탈, /visual_slam/status 의 vo_state 분포.
   인자: DUR [LABEL]"""
import sys, math, time
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
try:
    from isaac_ros_visual_slam_interfaces.msg import VisualSlamStatus
except Exception:
    VisualSlamStatus = None

DUR = float(sys.argv[1]); LAB = sys.argv[2] if len(sys.argv) > 2 else ''


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


rclpy.init(); n = Node('vslam_measure')
od, st = [], {}
n.create_subscription(Odometry, '/visual_slam/tracking/odometry',
                      lambda m: od.append((time.time(), m.pose.pose.position.x, m.pose.pose.position.y, m.pose.pose.position.z, yaw(m.pose.pose.orientation))), 50)
n.create_subscription(Odometry, '/visual_slam/tracking/odometry',
                      lambda m: None, qos_profile_sensor_data)
if VisualSlamStatus:
    n.create_subscription(VisualSlamStatus, '/visual_slam/status', lambda m: st.__setitem__(m.vo_state, st.get(m.vo_state, 0) + 1), 50)
t0 = time.time()
while time.time() - t0 < DUR: rclpy.spin_once(n, timeout_sec=0.05)
print('== V1 %s: %.0f s' % (LAB, DUR))
if len(od) < 2:
    print('  odometry 수신 %d 개 — 출력 없음' % len(od))
else:
    rate = (len(od) - 1) / (od[-1][0] - od[0][0])
    a, b = od[0], od[-1]
    dpos = math.hypot(b[1] - a[1], b[2] - a[2]); dz = b[3] - a[3]
    dyaw = math.degrees((b[4] - a[4] + math.pi) % (2 * math.pi) - math.pi)
    mx = max(math.hypot(o[1] - a[1], o[2] - a[2]) for o in od)
    gaps = [od[i + 1][0] - od[i][0] for i in range(len(od) - 1)]
    print('  odometry %.1f Hz (%d 개), 최대 간격 %.3f s' % (rate, len(od), max(gaps)))
    print('  처음→끝 xy 변화 %.2f cm (z %.2f cm), 최대 이탈 %.2f cm, yaw 변화 %+.3f°' % (100 * dpos, 100 * dz, 100 * mx, dyaw))
print('  vo_state 분포: %s (3.2 정의: 0 미상, 1 성공, 2 실패, 3 성공+IMU 없음 — 원문 정의는 메시지 주석 확인)' % (st if st else '수신 없음'))
