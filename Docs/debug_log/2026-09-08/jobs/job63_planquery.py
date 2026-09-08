#!/usr/bin/env python3
"""무주행 경로 질의 — 로버를 움직이지 않고 '경로가 존재하는가' 를 Nav2 플래너에 직접 묻는다.
  사용: python3 job63_planquery.py <x> <y> <yaw_deg>
출력: 성공 여부 / 경로 길이·직선거리 / 경로의 최대 |y| (어느 쪽으로 우회하는지) / 경로점의 코스트맵 비용 최대값.
주행 전에 이걸로 먼저 확인하면 배터리·충돌 위험 없이 통과 가능성을 판정할 수 있다."""
import math, sys, time, rclpy, tf2_ros
from rclpy.action import ActionClient
from nav2_msgs.action import ComputePathToPose
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import OccupancyGrid
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy

GX, GY = float(sys.argv[1]), float(sys.argv[2])
GTH = math.radians(float(sys.argv[3]) if len(sys.argv) > 3 else 0.0)
rclpy.init(); n = rclpy.create_node('planq')
buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n); grids = {}
qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: grids.__setitem__('g', m), qos)

def pose():
    try:
        t = buf.lookup_transform('map', 'base_link', rclpy.time.Time()).transform; q = t.rotation
        return (t.translation.x, t.translation.y, math.atan2(2*(q.w*q.z), 1-2*q.z*q.z))
    except Exception: return None
t0 = time.time()
while pose() is None and time.time()-t0 < 8: rclpy.spin_once(n, timeout_sec=0.1)
p0 = pose()
if p0 is None: print("TF 없음"); raise SystemExit(1)
print(f"현재 ({p0[0]:.2f},{p0[1]:.2f}) hd={math.degrees(p0[2]):.0f}° → 목표 ({GX:.2f},{GY:.2f})")

ac = ActionClient(n, ComputePathToPose, 'compute_path_to_pose')
if not ac.wait_for_server(timeout_sec=10.0): print("planner 액션 없음"); raise SystemExit(1)
g = ComputePathToPose.Goal(); g.use_start = False
g.goal = PoseStamped(); g.goal.header.frame_id = 'map'
g.goal.header.stamp = n.get_clock().now().to_msg()
g.goal.pose.position.x, g.goal.pose.position.y = GX, GY
g.goal.pose.orientation.z, g.goal.pose.orientation.w = math.sin(GTH/2), math.cos(GTH/2)
fut = ac.send_goal_async(g); rclpy.spin_until_future_complete(n, fut, timeout_sec=20.0)
gh = fut.result()
if gh is None or not gh.accepted: print("경로 질의 거부"); raise SystemExit(1)
rf = gh.get_result_async(); rclpy.spin_until_future_complete(n, rf, timeout_sec=25.0)
res = rf.result()
if res is None or res.status != 4 or not res.result.path.poses:
    print(f"❌ 경로 없음 (status={None if res is None else res.status}) — 통과 불가 판정")
    raise SystemExit(0)
P = [(q.pose.position.x, q.pose.position.y) for q in res.result.path.poses]
L = sum(math.hypot(P[i][0]-P[i-1][0], P[i][1]-P[i-1][1]) for i in range(1, len(P)))
straight = math.hypot(GX-p0[0], GY-p0[1])
# 로버 기준 횡편차 (출발 헤딩 기준)
c, s = math.cos(-p0[2]), math.sin(-p0[2])
lat = [ (q[0]-p0[0])*s + (q[1]-p0[1])*c for q in P ]
t1 = time.time()
while 'g' not in grids and time.time()-t1 < 5: rclpy.spin_once(n, timeout_sec=0.1)
cmax = None
if 'g' in grids:
    gr = grids['g']; info = gr.info; vals = []
    for x, y in P:
        cx = int((x-info.origin.position.x)/info.resolution); cy = int((y-info.origin.position.y)/info.resolution)
        if 0 <= cx < info.width and 0 <= cy < info.height: vals.append(gr.data[cy*info.width+cx])
    cmax = max(vals) if vals else None
print(f"✅ 경로 있음: {len(P)}점, 길이 {L:.2f}m (직선 {straight:.2f}m, 비 {L/max(straight,1e-6):.2f})")
print(f"   우회 방향: 최대 좌 {max(lat):+.2f}m / 최대 우 {min(lat):+.2f}m")
print(f"   경로점 최대 비용: {cmax}  ({'0=완전 자유' if cmax==0 else '고비용 구간 통과' if cmax and cmax<253 else '경성 근접!' if cmax else '-'})")
rclpy.shutdown()
