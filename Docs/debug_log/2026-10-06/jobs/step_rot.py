#!/usr/bin/env python3
"""10-06 §4 단계별 회전 실측(10-02 §17 사용자 제안): 한 번 실행 = 제자리 90° 한 단계(또는 init).
   매 단계 정지 2 s 뒤 네 추정(EKF B=/odometry/filtered, EKF A=/odometry/ekf_a, rf2o 차체 중심 환산, SLAM map→base_link)으로
   **오른쪽 앞끝(+0.262, −0.165)** 의 시작 대비 위치를 계산 → 시작 표시까지 예측 대각 거리. 사용자가 줄자로 잰 값과 비교.
   인자: init | +90 | -90      상태 /tmp/step_state.json"""
import sys, json, math, time, os, numpy as np, rclpy, tf2_ros
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
CORNER = (0.262, -0.165); LX = 0.152; W = 0.38; ST = '/tmp/step_state.json'
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
rclpy.init(); n = Node('step_rot'); pub = n.create_publisher(Twist, '/cmd_vel', 10)
buf = tf2_ros.Buffer(); tf2_ros.TransformListener(buf, n)
P = {}; G = {'gap': 9.0}
def sub(tp, k): n.create_subscription(Odometry, tp, lambda m: P.__setitem__(k, (m.pose.pose.position.x, m.pose.pose.position.y, yaw(m.pose.pose.orientation))), qos_profile_sensor_data)
sub('/odometry/filtered', 'B'); sub('/odometry/ekf_a', 'A'); sub('/odom_rf2o', 'R')
def cb_s(m):
    r = np.array(m.ranges); a = m.angle_min + m.angle_increment * np.arange(len(r)) + math.pi - 0.04677; ok = np.isfinite(r) & (r > 0.2) & (r < 3)
    if not ok.any(): return   # 유효 점 없는 스캔(단계 3 첫 시도 오류)
    x = LX + r[ok] * np.cos(a[ok]); y = r[ok] * np.sin(a[ok])
    dx = np.where(x > 0, np.maximum(x - 0.262, 0), np.maximum(-x - 0.248, 0)); dy = np.maximum(np.abs(y) - 0.165, 0); G['gap'] = float(np.hypot(dx, dy).min())
n.create_subscription(LaserScan, '/scan', cb_s, qos_profile_sensor_data)
def spin(sec):
    t = time.time() + sec
    while time.time() < t: rclpy.spin_once(n, timeout_sec=0.02)
def snap():
    spin(1.0); out = {k: list(v) for k, v in P.items()}
    tr = buf.lookup_transform('map', 'base_link', rclpy.time.Time()).transform
    out['S'] = [tr.translation.x, tr.translation.y, yaw(tr.rotation)]; return out
def corner(p): c, s = math.cos(p[2]), math.sin(p[2]); return np.array([p[0] + c * CORNER[0] - s * CORNER[1], p[1] + s * CORNER[0] + c * CORNER[1]])
def rf2o_center(r, r0):
    # rf2o 자세는 라이다 위치이며 병진 부호가 반대(라이다 뒤집힘, 10-02 §13.2·§18) → 시작 기준 라이다 이동을 반전, 지렛대 0.152 m 빼서 중심으로
    c0, s0 = math.cos(r0[2]), math.sin(r0[2]); dx, dy = r[0] - r0[0], r[1] - r0[1]
    lx, ly = -(c0 * dx + s0 * dy), -(-s0 * dx + c0 * dy); th = r[2] - r0[2]
    return [lx - LX * math.cos(th) + LX, ly - LX * math.sin(th), th]
def rel(p, p0):
    c0, s0 = math.cos(p0[2]), math.sin(p0[2]); dx, dy = p[0] - p0[0], p[1] - p0[1]; return [c0 * dx + s0 * dy, -s0 * dx + c0 * dy, p[2] - p0[2]]
arg = sys.argv[1]
if arg == 'init':
    spin(3.0); s0 = snap(); json.dump({'s0': s0, 'steps': []}, open(ST, 'w'))
    print('init: 추정 %s 기록, 외곽 최근접 %.3f m — 오른쪽 앞끝 바닥에 표시가 있는지 확인' % (sorted(s0), G['gap'])); sys.exit(0)
S = json.load(open(ST)); sgn = 1 if arg.startswith('+') else -1
t_w = time.time()
while ('B' not in P or 'A' not in P or 'R' not in P) and time.time() - t_w < 8: spin(0.2)   # DDS 발견 지연(단계 2 첫 시도 KeyError)
spin(0.5); prev = P['B'][2]; acc = 0.0; t0 = time.time(); stop = False
while acc < math.radians(90) and time.time() - t0 < 10:
    if G['gap'] < 0.08: stop = True; break
    tw = Twist(); tw.angular.z = sgn * W; pub.publish(tw); spin(0.05)
    d = (P['B'][2] - prev + math.pi) % (2 * math.pi) - math.pi; acc += abs(d); prev = P['B'][2]
for _ in range(10): pub.publish(Twist()); spin(0.05)
spin(1.5); s = snap(); k = len(S['steps']) + 1
row = {'k': k, 'dir': arg, 'deg': math.degrees(acc), 'gap': G['gap'], 'abort': stop, 'pose': s}
S['steps'].append(row); json.dump(S, open(ST, 'w'))
c0 = np.array(CORNER); print('단계 %d (%s): %.0f° / %.1f s, 외곽 최근접 %.3f m%s' % (k, arg, row['deg'], time.time() - t0, G['gap'], '  ★ 0.08 m 안 — 중단' if stop else ''))
for key, nm in (('B', 'EKF B(rf2o)'), ('A', 'EKF A(지금)'), ('R', 'rf2o 중심'), ('S', 'SLAM')):
    if key not in s or key not in S['s0']: print('   %-12s 없음' % nm); continue
    p = rf2o_center(s['R'], S['s0']['R']) if key == 'R' else rel(s[key], S['s0'][key])
    cn = corner(p); d = cn - c0
    print('   %-12s 중심 (%+.3f, %+.3f) %+5.0f° | 오른쪽 앞끝 이동 (%+.3f, %+.3f) → 예측 대각 거리 %.3f m' % (nm, p[0], p[1], math.degrees(p[2]), d[0], d[1], math.hypot(*d)))
print('→ 줄자: 시작 표시 ↔ 오른쪽 앞끝 대각 거리를 재 주세요')
