#!/usr/bin/env python3
"""제자리 회전 캘리브레이션 — 라이다 스캔 정합을 GT 로 사용 (2026-09-07).
지령 ω 로 T 초 회전한 뒤, 회전 전/후 스캔의 각도 상관으로 실제 회전각을 산출.
  사용: python3 job46_rot.py [W=0.4] [T=6]
비교: ① 지령 적산 ② 원시 휠 적분(/wheel_odom vyaw, 슬립보정 전) ③ EKF yaw ④ 라이다 정합 GT
GT 방식: 1° 빈 range 프로파일을 만들고 Δ 를 -180~180° 로 돌려가며 |rA-rB| 중앙값이 최소인 Δ.
        제자리 회전이므로 병진 성분이 작아 유효 (정합 잔차도 함께 출력)."""
import sys, time, math, statistics as st, rclpy
import numpy as np
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan, Imu

W = float(sys.argv[1]) if len(sys.argv) > 1 else 0.4
T = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
BINS = 360

rclpy.init(); n = Node('rotcal')
pub = n.create_publisher(Twist, '/cmd_vel', 10)
state = {'scan': None, 'ekf_yaw': None, 'wheel_yaw': 0.0, 'wheel_t': None, 'wz': 0.0,
         'gyro_yaw': 0.0, 'gyro_t': None, 'gx': 0.0, 'gy': 0.0}

def sc_cb(m):
    prof = np.full(BINS, np.nan)
    a = m.angle_min + m.angle_increment * np.arange(len(m.ranges))
    r = np.asarray(m.ranges, dtype=np.float32)
    ok = np.isfinite(r) & (r > m.range_min) & (r < min(m.range_max, 12.0))
    idx = (np.degrees(a[ok]) % 360).astype(int) % BINS
    for i, v in zip(idx, r[ok]):
        if math.isnan(prof[i]) or v < prof[i]: prof[i] = v
    state['scan'] = prof
def ek_cb(m):
    q = m.pose.pose.orientation
    state['ekf_yaw'] = math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))
def wo_cb(m):
    now = time.time(); wz = m.twist.twist.angular.z
    if state['wheel_t'] is not None:
        state['wheel_yaw'] += wz * (now - state['wheel_t'])
    state['wheel_t'] = now; state['wz'] = wz
def im_cb(m):
    now = time.time()
    if state['gyro_t'] is not None:
        dt = now - state['gyro_t']
        state['gyro_yaw'] += m.angular_velocity.z * dt
        state['gx'] += m.angular_velocity.x * dt
        state['gy'] += m.angular_velocity.y * dt
    state['gyro_t'] = now
n.create_subscription(Imu, '/imu/data', im_cb, qos_profile_sensor_data)
n.create_subscription(LaserScan, '/scan', sc_cb, qos_profile_sensor_data)
n.create_subscription(Odometry, '/odometry/filtered', ek_cb, 10)
n.create_subscription(Odometry, '/wheel_odom', wo_cb, qos_profile_sensor_data)

def wait(sec):
    t = time.time() + sec
    while time.time() < t: rclpy.spin_once(n, timeout_sec=0.05)

wait(3.0)
if state['scan'] is None or state['ekf_yaw'] is None:
    print("수신 실패"); sys.exit(1)
A = state['scan'].copy(); y0 = state['ekf_yaw']
state['wheel_yaw'] = 0.0; state['wheel_t'] = None
state['gyro_yaw'] = 0.0; state['gyro_t'] = None; state['gx'] = 0.0; state['gy'] = 0.0
print(f"회전 시작: 지령 ω={W} rad/s × {T}s = {math.degrees(W*T):+.1f}°", flush=True)

cmd = Twist(); cmd.angular.z = W
t0 = time.time(); nxt = t0
while time.time() - t0 < T:
    rclpy.spin_once(n, timeout_sec=0.01)
    if time.time() >= nxt: pub.publish(cmd); nxt += 0.05
for _ in range(25): pub.publish(Twist()); rclpy.spin_once(n, timeout_sec=0.04)
wait(2.5)
B = state['scan'].copy(); y1 = state['ekf_yaw']

# 각도 상관: B 를 -d 만큼 돌려 A 와 맞추는 d 탐색
best = None
for d in range(-179, 180):
    Br = np.roll(B, d)
    m = np.isfinite(A) & np.isfinite(Br)
    if m.sum() < BINS * 0.3: continue
    cost = float(np.median(np.abs(A[m] - Br[m])))
    if best is None or cost < best[1]: best = (d, cost, int(m.sum()))
gt = None
if best:
    # 0.1° 세밀화: 선형보간으로 이웃 2점 포함 포물선 피팅
    d0 = best[0]
    def cost_of(dd):
        Br = np.roll(B, dd); m = np.isfinite(A) & np.isfinite(Br)
        return float(np.median(np.abs(A[m] - Br[m]))) if m.sum() > BINS*0.3 else 1e9
    c0, cm, cp = cost_of(d0), cost_of(d0-1), cost_of(d0+1)
    denom = (cm - 2*c0 + cp)
    sub = 0.5*(cm - cp)/denom if abs(denom) > 1e-9 else 0.0
    gt = d0 + max(-1.0, min(1.0, sub))

d_cmd = math.degrees(W*T)
d_wheel = math.degrees(state['wheel_yaw'])
d_ekf = math.degrees(math.atan2(math.sin(y1-y0), math.cos(y1-y0)))
d_gyro = math.degrees(state['gyro_yaw'])
print()
print(f"① 지령 적산        : {d_cmd:+8.1f}°")
print(f"② 원시 휠 적분      : {d_wheel:+8.1f}°   (지령 대비 {d_wheel/d_cmd:.4f})")
print(f"③ EKF yaw          : {d_ekf:+8.1f}°   (자이로+휠 융합, ±180 랩)")
gx_d, gy_d = math.degrees(state['gx']), math.degrees(state['gy'])
print(f"③' 자이로 적분(D455f 프레임): x={gx_d:+7.1f}°  y={gy_d:+7.1f}°  z={d_gyro:+7.1f}°")
best_ax = max((abs(gx_d),'x',gx_d), (abs(gy_d),'y',gy_d), (abs(d_gyro),'z',d_gyro))
print(f"   → 최대축 {best_ax[1]} = {best_ax[2]:+.1f}°   휠/자이로 = {d_wheel/best_ax[2]:.4f} → SLIP {best_ax[2]/d_wheel:.3f}")
if gt is not None:
    print(f"④ 라이다 정합 GT    : {gt:+8.1f}°   잔차 {best[1]*100:.1f}cm, 유효빈 {best[2]}/{BINS}")
    print(f"   → 원시휠/GT = {d_wheel/gt:.4f}   (현 SLIP 0.46 대비, 스케일 정정 후 예상 SLIP = {gt/d_wheel/0.777:.3f})")
    print(f"   → EKF/GT   = {d_ekf/gt:.4f}")
else:
    print("④ 라이다 정합 GT    : 실패")
