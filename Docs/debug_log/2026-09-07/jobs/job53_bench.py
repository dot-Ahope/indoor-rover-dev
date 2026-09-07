#!/usr/bin/env python3
"""Nav2 컨트롤러 벤치마크 (2026-09-07, 스케일 교정 후 재측정).
  사용: python3 job53_bench.py <x> <y> <yaw_deg> <timeout> [BT파일명|-]
BT 파일명을 주면 goal.behavior_tree 로 지정 → 재시작 없이 컨트롤러 전환
  (nav_to_pose_no_spin.xml = RPP, nav_to_pose_mppi.xml = MPPI).
측정: 소요시간 / 경로길이 / 최단거리 대비 효율 / 위치·자세 오차 / |v|,|ω| 통계 /
     지령 급변(jerk 대용) / 정지 구간 비율 / /rover/status 이상 이벤트."""
import math, time, sys, statistics as st, rclpy, tf2_ros
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped, Twist
from diagnostic_msgs.msg import DiagnosticArray
from rclpy.qos import qos_profile_sensor_data

GX, GY = float(sys.argv[1]), float(sys.argv[2])
GTH = math.radians(float(sys.argv[3]))
TMO = float(sys.argv[4])
BT = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] != '-' else None
BTDIR = '/home/jetson/ros2_ws/install/rover_navigation/share/rover_navigation/config/'

rclpy.init(); n = rclpy.create_node('bench')
buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
cmds = []          # (t, v, w)
events = []

def cb_cmd(m): cmds.append((time.time(), m.linear.x, m.angular.z))
def lvl(x): return x[0] if isinstance(x, (bytes, bytearray)) else int(x)
def cb_st(m):
    for s in m.status:
        if lvl(s.level) != 0 and 'cmd_vel timeout' not in s.message:
            events.append((round(time.time() % 1000, 1), lvl(s.level), s.message))
n.create_subscription(Twist, '/cmd_vel', cb_cmd, 10)
n.create_subscription(DiagnosticArray, '/rover/status', cb_st, qos_profile_sensor_data)

def pose():
    try:
        t = buf.lookup_transform('map', 'base_link', rclpy.time.Time()).transform; q = t.rotation
        return (t.translation.x, t.translation.y, math.atan2(2*(q.w*q.z), 1-2*q.z*q.z))
    except Exception:
        return None

t0 = time.time()
while pose() is None and time.time() < t0 + 8: rclpy.spin_once(n, timeout_sec=0.1)
p0 = pose()
if p0 is None: print("TF 없음"); raise SystemExit(1)
straight = math.hypot(GX-p0[0], GY-p0[1])
print(f"[{BT or 'RPP(기본)'}] 현재 ({p0[0]:.3f},{p0[1]:.3f}) hd={math.degrees(p0[2]):.1f}° "
      f"→ 목표 ({GX:.2f},{GY:.2f}) hd={math.degrees(GTH):.0f}°  직선거리 {straight:.2f}m", flush=True)

ac = ActionClient(n, NavigateToPose, 'navigate_to_pose'); ac.wait_for_server(timeout_sec=10.0)
g = NavigateToPose.Goal(); g.pose = PoseStamped(); g.pose.header.frame_id = 'map'
g.pose.header.stamp = n.get_clock().now().to_msg()
g.pose.pose.position.x = GX; g.pose.pose.position.y = GY
g.pose.pose.orientation.z = math.sin(GTH/2); g.pose.pose.orientation.w = math.cos(GTH/2)
if BT: g.behavior_tree = BTDIR + BT
# BT XML 을 처음 지정하면 bt_navigator 가 새 트리를 파싱하므로 수락 응답이 늦다 (10s 부족 → 실측).
# 응답을 못 받고 종료하면 목표가 서버에서 살아 움직일 수 있어 위험 → 넉넉히 대기 + 실패 시 강제 취소.
fut = ac.send_goal_async(g); rclpy.spin_until_future_complete(n, fut, timeout_sec=40.0)
gh = fut.result()
if gh is None or not gh.accepted:
    print("거부/무응답 — 안전 취소 시도")
    try:
        from action_msgs.srv import CancelGoal
        cli = n.create_client(CancelGoal, '/navigate_to_pose/_action/cancel_goal')
        if cli.wait_for_service(timeout_sec=5.0):
            ft = cli.call_async(CancelGoal.Request()); rclpy.spin_until_future_complete(n, ft, timeout_sec=5.0)
    except Exception as e: print("취소 실패:", e)
    pub = n.create_publisher(Twist, '/cmd_vel', 10)
    for _ in range(20): pub.publish(Twist()); rclpy.spin_once(n, timeout_sec=0.03)
    raise SystemExit(1)

rf = gh.get_result_async(); t1 = time.time(); last = 0
path = 0.0; prev = p0; track = []
while not rf.done() and time.time() - t1 < TMO:
    rclpy.spin_once(n, timeout_sec=0.05)
    p = pose()
    if p:
        d = math.hypot(p[0]-prev[0], p[1]-prev[1])
        if d > 0.002: path += d; prev = p
        track.append(p)
    if time.time() - last > 4.0:
        last = time.time()
        v, w = (cmds[-1][1], cmds[-1][2]) if cmds else (0, 0)
        print(f"  t={time.time()-t1:5.1f}s ({p[0]:+.2f},{p[1]:+.2f}) hd={math.degrees(p[2]):+6.1f}° "
              f"남은={math.hypot(p[0]-GX,p[1]-GY):.2f}m cmd(v={v:+.3f} w={w:+.3f})", flush=True)

codes = {4: 'SUCCEEDED', 5: 'CANCELED', 6: 'ABORTED'}
if not rf.done():
    gh.cancel_goal_async(); rclpy.spin_once(n, timeout_sec=2.0)
    pub = n.create_publisher(Twist, '/cmd_vel', 10)
    for _ in range(12): pub.publish(Twist()); time.sleep(0.05)
    res = 'TIMEOUT'
else:
    res = codes.get(rf.result().status, str(rf.result().status))
el = time.time() - t1
p1 = pose()
err = math.hypot(p1[0]-GX, p1[1]-GY)
dth = math.degrees(((p1[2]-GTH+math.pi) % (2*math.pi)) - math.pi)

vs = [abs(c[1]) for c in cmds]; ws = [abs(c[2]) for c in cmds]
jerk = sum(abs(cmds[i][1]-cmds[i-1][1]) + abs(cmds[i][2]-cmds[i-1][2]) for i in range(1, len(cmds)))
idle = sum(1 for c in cmds if abs(c[1]) < 0.005 and abs(c[2]) < 0.02) / max(1, len(cmds))
rev = sum(1 for i in range(1, len(cmds)) if cmds[i][1]*cmds[i-1][1] < -1e-6)
print(f"결과: {res}  소요 {el:.1f}s")
print(f"  경로 {path:.2f}m / 직선 {straight:.2f}m = 효율 {straight/path if path>0 else 0:.3f}")
print(f"  위치오차 {err*100:.1f}cm  자세오차 {dth:+.1f}°")
print(f"  |v| 평균 {st.mean(vs) if vs else 0:.3f} 최대 {max(vs) if vs else 0:.3f} m/s | "
      f"|w| 평균 {st.mean(ws) if ws else 0:.3f} 최대 {max(ws) if ws else 0:.3f} rad/s")
print(f"  지령 급변합 {jerk:.1f} ({jerk/max(el,1):.2f}/s)  정지비율 {idle*100:.0f}%  전후반전 {rev}회  샘플 {len(cmds)}")
if events: print(f"  이상: {events[:5]}")
rclpy.shutdown()
