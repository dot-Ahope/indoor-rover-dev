#!/usr/bin/env python3
"""RPP 조향 진동 측정 (2026-09-08, 계획 §5.y). job53_bench 와 같은 목표 주행 + 20 Hz 트레이스.
  사용: python3 job56_osc.py <x> <y> <yaw_deg> <timeout> <csv이름>
트레이스 열: t, v_cmd, w_cmd, x_map, y_map, yaw_map, yaw_odom, lat_err(경로 최근접 횡오차 m)
지표(원인 가림용):
  - ω 부호반전/m           : 직진 구간(|v|>0.03)에서 ω 부호가 바뀐 횟수 / 주행거리
  - 횡오차 RMS             : 직진 구간의 경로 최근접 거리
  - map yaw 점프 횟수/합   : |Δyaw_map − Δyaw_odom| > 1° 인 샘플 (slam 보정 이벤트) → (d) 위치추정 점프
  - ω 스파이크 횟수         : |Δω| > 0.05 rad/s per 50 ms → (b) 경로 계단 / (a) 이득 과대
  - 회전 종료 후 3 s 부호반전: 제자리 회전(|v|<0.01, |ω|>0.2) 끝난 뒤 ω 부호 변화 → (c) 전환각"""
import math, time, sys, csv, statistics as st, rclpy, tf2_ros
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import Path, Odometry
from geometry_msgs.msg import PoseStamped, Twist
from action_msgs.srv import CancelGoal

GX, GY, GTH = float(sys.argv[1]), float(sys.argv[2]), math.radians(float(sys.argv[3]))
TMO, NAME = float(sys.argv[4]), sys.argv[5]

rclpy.init(); n = rclpy.create_node('osc')
buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
S = {'cmd': (0.0, 0.0), 'odom_yaw': None, 'path': []}
def cb_cmd(m): S['cmd'] = (m.linear.x, m.angular.z)
def cb_od(m):
    q = m.pose.pose.orientation; S['odom_yaw'] = math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))
def cb_path(m): S['path'] = [(p.pose.position.x, p.pose.position.y) for p in m.poses]
n.create_subscription(Twist, '/cmd_vel', cb_cmd, 10)
n.create_subscription(Odometry, '/odometry/filtered', cb_od, 10)
n.create_subscription(Path, '/plan', cb_path, 10)

def pose():
    try:
        t = buf.lookup_transform('map', 'base_link', rclpy.time.Time()).transform; q = t.rotation
        return (t.translation.x, t.translation.y, math.atan2(2*(q.w*q.z), 1-2*q.z*q.z))
    except Exception: return None
def lat_err(x, y):
    P = S['path']
    if len(P) < 2: return float('nan')
    best = 1e9
    for i in range(len(P)-1):
        ax, ay = P[i]; bx, by = P[i+1]; dx, dy = bx-ax, by-ay; L2 = dx*dx+dy*dy
        tt = 0.0 if L2 < 1e-9 else max(0.0, min(1.0, ((x-ax)*dx+(y-ay)*dy)/L2))
        d = math.hypot(x-(ax+tt*dx), y-(ay+tt*dy)); best = min(best, d)
    return best
def wrap(a): return math.atan2(math.sin(a), math.cos(a))

t0 = time.time()
while (pose() is None or S['odom_yaw'] is None) and time.time() < t0+8: rclpy.spin_once(n, timeout_sec=0.1)
p0 = pose()
if p0 is None: print("TF 없음"); raise SystemExit(1)
print(f"현재 ({p0[0]:.2f},{p0[1]:.2f}) hd={math.degrees(p0[2]):.1f}° → 목표 ({GX:.2f},{GY:.2f}) hd={math.degrees(GTH):.0f}°", flush=True)
ac = ActionClient(n, NavigateToPose, 'navigate_to_pose'); ac.wait_for_server(timeout_sec=10.0)
g = NavigateToPose.Goal(); g.pose = PoseStamped(); g.pose.header.frame_id = 'map'
g.pose.header.stamp = n.get_clock().now().to_msg()
g.pose.pose.position.x, g.pose.pose.position.y = GX, GY
g.pose.pose.orientation.z, g.pose.pose.orientation.w = math.sin(GTH/2), math.cos(GTH/2)
fut = ac.send_goal_async(g); rclpy.spin_until_future_complete(n, fut, timeout_sec=40.0)
gh = fut.result()
if gh is None or not gh.accepted:
    cli = n.create_client(CancelGoal, '/navigate_to_pose/_action/cancel_goal')
    if cli.wait_for_service(timeout_sec=5.0): cli.call_async(CancelGoal.Request())
    print("거부/무응답 — 취소"); raise SystemExit(1)

rf = gh.get_result_async(); t1 = time.time(); rows = []; nxt = t1
while not rf.done() and time.time()-t1 < TMO:
    rclpy.spin_once(n, timeout_sec=0.01)
    now = time.time()
    if now >= nxt:
        nxt += 0.05; p = pose()
        if p: rows.append((now-t1, S['cmd'][0], S['cmd'][1], p[0], p[1], p[2], S['odom_yaw'], lat_err(p[0], p[1])))
if not rf.done():
    gh.cancel_goal_async(); rclpy.spin_once(n, timeout_sec=2.0); res = 'TIMEOUT'
else:
    res = {4: 'SUCCEEDED', 5: 'CANCELED', 6: 'ABORTED'}.get(rf.result().status, str(rf.result().status))
el = time.time()-t1
with open(f'/tmp/{NAME}.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['t', 'v_cmd', 'w_cmd', 'x', 'y', 'yaw_map', 'yaw_odom', 'lat_err']); w.writerows(rows)

# ── 지표 ──
dist = sum(math.hypot(rows[i][3]-rows[i-1][3], rows[i][4]-rows[i-1][4]) for i in range(1, len(rows)))
straight = [r for r in rows if abs(r[1]) > 0.03]
flips = sum(1 for i in range(1, len(straight)) if straight[i][2]*straight[i-1][2] < 0 and abs(straight[i][2]) > 0.01 and abs(straight[i-1][2]) > 0.01)
lat = [r[7] for r in straight if not math.isnan(r[7])]
lat_rms = math.sqrt(sum(x*x for x in lat)/len(lat)) if lat else float('nan')
jumps = [abs(wrap((rows[i][5]-rows[i-1][5]) - (rows[i][6]-rows[i-1][6]))) for i in range(1, len(rows)) if rows[i][6] is not None and rows[i-1][6] is not None]
jump_n = sum(1 for j in jumps if j > math.radians(1.0)); jump_sum = math.degrees(sum(j for j in jumps if j > math.radians(1.0)))
spikes = sum(1 for i in range(1, len(rows)) if abs(rows[i][2]-rows[i-1][2]) > 0.05)
# 회전 종료 후 3 s 부호반전
post = 0; in_rot = False; t_end = None
for i, r in enumerate(rows):
    rot = abs(r[1]) < 0.01 and abs(r[2]) > 0.2
    if in_rot and not rot: t_end = r[0]; in_rot = False
    in_rot = in_rot or rot
    if t_end is not None and t_end < r[0] <= t_end+3.0 and i > 0 and r[2]*rows[i-1][2] < 0 and abs(r[2]) > 0.01: post += 1
wabs = [abs(r[2]) for r in straight]
print(f"결과: {res}  소요 {el:.1f}s  주행거리 {dist:.2f}m  샘플 {len(rows)}")
print(f"  직진 구간 ω: 평균 {st.mean(wabs) if wabs else 0:.3f} 최대 {max(wabs) if wabs else 0:.3f} rad/s | 부호반전 {flips}회 = {flips/max(dist,0.01):.1f}회/m")
print(f"  횡오차 RMS {lat_rms*100:.1f}cm (직진 구간 {len(lat)}샘플)")
print(f"  map yaw 점프(>1°): {jump_n}회, 합 {jump_sum:.1f}°   |  ω 스파이크(>0.05/50ms): {spikes}회")
print(f"  제자리회전 종료 후 3s ω 부호반전: {post}회  (회전 종료 t={t_end})")
p1 = pose(); print(f"  최종 위치오차 {math.hypot(p1[0]-GX,p1[1]-GY)*100:.1f}cm 자세오차 {math.degrees(wrap(p1[2]-GTH)):+.1f}°")
rclpy.shutdown()
