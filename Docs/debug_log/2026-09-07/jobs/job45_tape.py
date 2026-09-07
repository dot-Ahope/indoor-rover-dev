#!/usr/bin/env python3
"""직진 스케일 캘리브레이션 (2026-09-07, PWM 20kHz 이후 VX_SCALE 재측정).
지령 V 로 T 초 직진하며 4가지 거리를 비교:
  ① 지령 적산 (V×T, 가감속 제외한 이상치)
  ② 원시 휠 오도 (/wheel_odom pose.x — 펌웨어 자체 적산, 스케일 미적용)
  ③ EKF (/odometry/filtered — VX_SCALE 0.783 적용본 + 자이로)
  ④ 라이다 전방벽 거리 변화 (정면 ±5° 중앙값, 자동 GT)
  사용: python3 job45_tape.py [V=0.06] [T=25]"""
import sys, time, math, statistics as st, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from diagnostic_msgs.msg import DiagnosticArray

V = float(sys.argv[1]) if len(sys.argv) > 1 else 0.06
T = float(sys.argv[2]) if len(sys.argv) > 2 else 25.0

rclpy.init(); n = Node('tapecal')
pub = n.create_publisher(Twist, '/cmd_vel', 10)
raw = [None, None]; ekf = [None, None, None]; front = [None]; evt = []

def lvl(x): return x[0] if isinstance(x, (bytes, bytearray)) else int(x)
def wo_cb(m): raw[0] = m.pose.pose.position.x; raw[1] = m.pose.pose.position.y
def ek_cb(m):
    q = m.pose.pose.orientation
    ekf[0] = m.pose.pose.position.x; ekf[1] = m.pose.pose.position.y
    ekf[2] = math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))
def sc_cb(m):
    # 정면 ±5° 유효거리 중앙값. 라이다 yaw=pi 장착 → 정면은 스캔각 ±pi 부근
    vals = []
    for i, r in enumerate(m.ranges):
        if not (m.range_min < r < m.range_max): continue
        a = m.angle_min + i * m.angle_increment
        d = abs(math.atan2(math.sin(a - math.pi), math.cos(a - math.pi)))
        if d <= math.radians(5): vals.append(r)
    if len(vals) >= 3: front[0] = st.median(vals)
def st_cb(m):
    for s in m.status:
        if lvl(s.level) != 0: evt.append((round(time.time() % 1000, 1), lvl(s.level), s.message))
n.create_subscription(Odometry, '/wheel_odom', wo_cb, qos_profile_sensor_data)
n.create_subscription(Odometry, '/odometry/filtered', ek_cb, 10)
n.create_subscription(LaserScan, '/scan', sc_cb, qos_profile_sensor_data)
n.create_subscription(DiagnosticArray, '/rover/status', st_cb, qos_profile_sensor_data)

tw = time.time() + 8.0            # 디스커버리 대기 (최대 8s)
while time.time() < tw and (raw[0] is None or ekf[0] is None or front[0] is None):
    rclpy.spin_once(n, timeout_sec=0.1)
if raw[0] is None or ekf[0] is None:
    print(f"오도메트리 수신 실패 (wheel_odom={raw[0]}, ekf={ekf[0]}, scan front={front[0]})"); sys.exit(1)
r0, e0, ey0, f0 = (raw[0], raw[1]), (ekf[0], ekf[1]), ekf[2], front[0]
print(f"시작: wheel_odom x={r0[0]:.3f}  ekf x={e0[0]:.3f} yaw={math.degrees(ey0):+.1f}°  전방벽={f0 if f0 is None else round(f0,3)}m", flush=True)
print(f"지령 {V} m/s × {T}s = {V*T:.3f} m 주행 시작", flush=True)

cmd = Twist(); cmd.linear.x = V
t0 = time.time(); nxt = t0
while time.time() - t0 < T:
    rclpy.spin_once(n, timeout_sec=0.01)
    if time.time() >= nxt: pub.publish(cmd); nxt += 0.05
for _ in range(25): pub.publish(Twist()); rclpy.spin_once(n, timeout_sec=0.04)
tw = time.time() + 2.0
while time.time() < tw: rclpy.spin_once(n, timeout_sec=0.05)

r1, e1, ey1, f1 = (raw[0], raw[1]), (ekf[0], ekf[1]), ekf[2], front[0]
d_raw = math.hypot(r1[0]-r0[0], r1[1]-r0[1])
d_ekf = math.hypot(e1[0]-e0[0], e1[1]-e0[1])
d_cmd = abs(V) * T
print()
print(f"① 지령 적산      : {d_cmd*100:7.1f} cm")
print(f"② 원시 휠 오도    : {d_raw*100:7.1f} cm   (지령 대비 {d_raw/d_cmd:.4f})")
print(f"③ EKF(0.783 적용) : {d_ekf*100:7.1f} cm   (지령 대비 {d_ekf/d_cmd:.4f})")
if f0 and f1:
    d_lid = abs(f1 - f0)
    print(f"④ 라이다 전방벽   : {d_lid*100:7.1f} cm   (원시/라이다 = {d_raw/d_lid:.4f}  ← 새 VX_SCALE 후보 = {d_lid/d_raw:.4f})")
else:
    print("④ 라이다 전방벽   : 측정 불가 (정면 ±5° 유효점 부족)")
print(f"요yaw 변화: {math.degrees(ey1-ey0):+.2f}°   횡변위(EKF): {(e1[1]-e0[1])*100:+.1f} cm")
if evt: print("이상 상태:", evt[:5])
print("\n※ 줄자 실측값을 알려주면 라이다 GT 와 교차검증합니다.")
