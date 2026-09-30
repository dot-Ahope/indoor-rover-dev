#!/usr/bin/env python3
"""09-30 §3 SLAM 앞뒤 치우침 시험: 출발 테이프에서 직진 DIST m(EKF 기준) 뒤 정지, SLAM 이동 vs 사용자 줄자.
   정지 5 s 평균 map→base_link 자세를 전·후로 잡아 출발 방향 기준 (세로, 가로) 이동과 오른쪽 앞 모서리 예측을 낸다.
   오른쪽 앞 모서리 = base_link 기준 (+0.262, −0.165) (09-30 §2 실측). 인자: DIST [V=0.07]"""
import sys, time, math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from tf2_ros import Buffer, TransformListener

DIST = float(sys.argv[1]); V = float(sys.argv[2]) if len(sys.argv) > 2 else 0.07
FX, FY = 0.262, -0.165
rclpy.init(); n = Node('slam_bias_test'); tb = Buffer(); TransformListener(tb, n)
pub = n.create_publisher(Twist, '/cmd_vel', 10)


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def pose(frame):
    t = tb.lookup_transform(frame, 'base_link', rclpy.time.Time()); p = t.transform
    return p.translation.x, p.translation.y, yaw(p.rotation)


def avg(frame, dur):
    xs = []; t0 = time.time()
    while time.time() - t0 < dur:
        rclpy.spin_once(n, timeout_sec=0.05)
        try: xs.append(pose(frame))
        except Exception: pass
    x = sum(a[0] for a in xs) / len(xs); y = sum(a[1] for a in xs) / len(xs)
    th = math.atan2(sum(math.sin(a[2]) for a in xs), sum(math.cos(a[2]) for a in xs))
    return x, y, th, len(xs)


def corner(p):
    c, s = math.cos(p[2]), math.sin(p[2]); return p[0] + c * FX - s * FY, p[1] + s * FX + c * FY


t0 = time.time()
while time.time() - t0 < 3: rclpy.spin_once(n, timeout_sec=0.05)
M0 = avg('map', 5.0); O0 = avg('odom', 1.0)
print('출발 map (%.4f, %.4f, %.2f°) [%d 표본] | odom (%.4f, %.4f)' % (M0[0], M0[1], math.degrees(M0[2]), M0[3], O0[0], O0[1]))
ts = time.time(); d = 0.0
while d < DIST - 0.005 and time.time() - ts < DIST / V * 2 + 5:
    m = Twist(); m.linear.x = V; pub.publish(m)
    te = time.time() + 0.05
    while time.time() < te: rclpy.spin_once(n, timeout_sec=0.01)
    try: o = pose('odom'); d = math.hypot(o[0] - O0[0], o[1] - O0[1])
    except Exception: pass
for _ in range(20): pub.publish(Twist()); time.sleep(0.05)
print('주행 %.1f s, EKF 이동 %.4f m 에서 정지 지령' % (time.time() - ts, d))
t1 = time.time()
while time.time() - t1 < 6: rclpy.spin_once(n, timeout_sec=0.05)
M1 = avg('map', 5.0); O1 = avg('odom', 1.0)
c, s = math.cos(M0[2]), math.sin(M0[2]); dx, dy = M1[0] - M0[0], M1[1] - M0[1]
print('도착 map (%.4f, %.4f, %.2f°) [%d 표본]' % (M1[0], M1[1], math.degrees(M1[2]), M1[3]))
print('SLAM 이동(출발 방향 기준): 세로 %.4f m, 가로 %+.4f m, 방향 %+.2f°' % (c * dx + s * dy, -s * dx + c * dy, math.degrees(M1[2] - M0[2])))
eo = math.hypot(O1[0] - O0[0], O1[1] - O0[1]); print('EKF 이동 %.4f m (SLAM 대비 %+.4f)' % (eo, eo - math.hypot(dx, dy)))
C0, C1 = corner(M0), corner(M1); ex, ey = C1[0] - C0[0], C1[1] - C0[1]
print('줄자 예측: 오른쪽 앞 모서리가 출발 표시에서 세로 %.4f m 앞, 가로 %+.4f m(+ 왼쪽)' % (c * ex + s * ey, -s * ex + c * ey))
