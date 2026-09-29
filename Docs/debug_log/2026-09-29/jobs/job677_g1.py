#!/usr/bin/env python3
"""09-29 §13 G1: nav_guard 시간 한도 실동작. nav_guard time_limit_override=15 로 두고 W3 (5.5, −2.2) 목표를 보낸다.
   기록: 목표 수락 시각 기준 — nav_guard 진단(/rover/guard) 시각, 목표 상태 CANCELED 시각, 휠 속도가 0 이 된 시각(|v|<0.005·|ω|<0.02 가 0.5 s 지속),
   정지까지 이동 거리(map). 판정: 진단·취소 ≤ 15 + 1 s, 취소 뒤 정지 ≤ 1 s. 끝나면 override 0 으로 원복."""
import time, math, subprocess
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import qos_profile_sensor_data
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import Odometry
from diagnostic_msgs.msg import DiagnosticArray
from geometry_msgs.msg import PoseStamped
from tf2_ros import Buffer, TransformListener

LIM = 15.0
print(subprocess.run(['ros2', 'param', 'set', '/nav_guard', 'time_limit_override', str(LIM)], capture_output=True, text=True).stdout.strip())
rclpy.init(); n = Node('g1_test'); tb = Buffer(); TransformListener(tb, n)
guard, wv = [], []
n.create_subscription(DiagnosticArray, '/rover/guard', lambda m: [guard.append((time.time(), s.message)) for s in m.status], 10)
n.create_subscription(Odometry, '/wheel_odom', lambda m: wv.append((time.time(), m.twist.twist.linear.x, m.twist.twist.angular.z)), qos_profile_sensor_data)


def mpos():
    try:
        t = tb.lookup_transform('map', 'base_link', rclpy.time.Time()); return t.transform.translation.x, t.transform.translation.y
    except Exception: return None


ac = ActionClient(n, NavigateToPose, 'navigate_to_pose')
if not ac.wait_for_server(timeout_sec=10): print('navigate_to_pose 없음'); raise SystemExit(1)
for _ in range(20): rclpy.spin_once(n, timeout_sec=0.05)
p0 = mpos()
g = NavigateToPose.Goal(); ps = PoseStamped(); ps.header.frame_id = 'map'; ps.pose.position.x = 5.5; ps.pose.position.y = -2.2; ps.pose.orientation.w = 1.0; g.pose = ps
f = ac.send_goal_async(g)
while not f.done(): rclpy.spin_once(n, timeout_sec=0.02)
gh = f.result(); t_acc = time.time(); print('목표 수락: %s, 출발 map %s' % (gh.accepted, p0))
res = gh.get_result_async(); t_end = None
while time.time() - t_acc < LIM + 20:
    rclpy.spin_once(n, timeout_sec=0.02)
    if res.done() and t_end is None: t_end = time.time()
    if t_end and time.time() - t_end > 3: break
st = res.result().status if res.done() else None
p1 = mpos()
# 정지 시각: t_end 이후 |v|<0.005 & |ω|<0.02 가 0.5 s 지속된 첫 시각
t_stop = None
for i, (t, v, w) in enumerate(wv):
    if t_end and t >= t_end - 0.5 and abs(v) < 0.005 and abs(w) < 0.02:
        if all(abs(x[1]) < 0.005 and abs(x[2]) < 0.02 for x in wv[i:] if x[0] <= t + 0.5): t_stop = t; break
print('nav_guard 진단: %s' % ('; '.join('%.2f s: %s' % (t - t_acc, m) for t, m in guard) if guard else '없음'))
print('목표 종료 상태 %s (5 = CANCELED) at %.2f s' % (st, (t_end - t_acc) if t_end else float('nan')))
print('휠 정지 at %.2f s (종료 뒤 %.2f s)' % ((t_stop - t_acc) if t_stop else float('nan'), (t_stop - t_end) if (t_stop and t_end) else float('nan')))
if p0 and p1: print('이동 map (%.2f, %.2f) → (%.2f, %.2f) = %.2f m' % (p0[0], p0[1], p1[0], p1[1], math.hypot(p1[0] - p0[0], p1[1] - p0[1])))
ok1 = bool(guard) and (guard[0][0] - t_acc) <= LIM + 1 and st == 5
ok2 = t_stop is not None and t_end is not None and (t_stop - t_end) <= 1.0
print('G1 판정: 취소 ≤ %.0f s %s · 정지 ≤ 1 s %s' % (LIM + 1, '통과' if ok1 else '불통과', '통과' if ok2 else '불통과'))
print(subprocess.run(['ros2', 'param', 'set', '/nav_guard', 'time_limit_override', '0.0'], capture_output=True, text=True).stdout.strip(), '(원복)')
