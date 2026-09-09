#!/usr/bin/env python3
"""현재 자세 기준 전방 D m 목표에 대한 무주행 경로 질의.
  사용: python3 job91_query.py [D=1.80]
inflation 0.40/패딩 0.02 변경의 직접 검증 — 경로가 상자를 붙어 지나가는지, 여유 쪽으로 크게 도는지."""
import math, sys, time, rclpy, tf2_ros
import numpy as np
from rclpy.action import ActionClient
from nav2_msgs.action import ComputePathToPose
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import OccupancyGrid
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy

D = float(sys.argv[1]) if len(sys.argv) > 1 else 1.80
rclpy.init(); n = rclpy.create_node('q91')
buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n); G = {}
qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: G.__setitem__('g', m), qos)

def pose():
    try:
        t = buf.lookup_transform('map', 'base_link', rclpy.time.Time()).transform; q = t.rotation
        return (t.translation.x, t.translation.y, math.atan2(2*(q.w*q.z), 1-2*q.z*q.z))
    except Exception: return None
t0 = time.time()
while time.time()-t0 < 10 and (pose() is None or 'g' not in G): rclpy.spin_once(n, timeout_sec=0.1)
p = pose()
if p is None: print("TF 실패"); raise SystemExit(1)
ch, sh = math.cos(p[2]), math.sin(p[2])
GX, GY = p[0] + D*ch, p[1] + D*sh
print(f"현재 map ({p[0]:.2f},{p[1]:.2f}) hd={math.degrees(p[2]):.1f}°  → 목표 ({GX:.2f},{GY:.2f}) = 전방 {D}m")

ac = ActionClient(n, ComputePathToPose, 'compute_path_to_pose'); ac.wait_for_server(timeout_sec=10.0)
g = ComputePathToPose.Goal(); g.goal = PoseStamped(); g.goal.header.frame_id = 'map'
g.goal.header.stamp = n.get_clock().now().to_msg()
g.goal.pose.position.x, g.goal.pose.position.y = GX, GY
g.goal.pose.orientation.z, g.goal.pose.orientation.w = math.sin(p[2]/2), math.cos(p[2]/2)
g.use_start = False
fut = ac.send_goal_async(g); rclpy.spin_until_future_complete(n, fut, timeout_sec=15.0)
gh = fut.result()
if gh is None or not gh.accepted: print("플래너 거부"); raise SystemExit(1)
rf = gh.get_result_async(); rclpy.spin_until_future_complete(n, rf, timeout_sec=20.0)
if rf.result() is None: print("플래너 무응답"); raise SystemExit(1)
path = rf.result().result.path.poses
if not path: print("경로 없음 (도달 불가)"); raise SystemExit(1)
XY = np.array([[q.pose.position.x, q.pose.position.y] for q in path])
L = float(np.sum(np.hypot(np.diff(XY[:,0]), np.diff(XY[:,1]))))
# 로버 기준 좌표로 변환 (전방 x, 좌 +y)
rel = XY - np.array([p[0], p[1]])
fx = rel[:,0]*ch + rel[:,1]*sh
fy = -rel[:,0]*sh + rel[:,1]*ch
i = int(np.argmax(np.abs(fy)))
# 경로점 비용
cmax = 0; costs = []
if 'g' in G:
    grid = G['g']; info = grid.info
    for x, y in XY:
        cx = int((x-info.origin.position.x)/info.resolution); cy = int((y-info.origin.position.y)/info.resolution)
        if 0 <= cx < info.width and 0 <= cy < info.height:
            c = grid.data[cy*info.width+cx]; costs.append(c); cmax = max(cmax, c)
print(f"경로 길이 {L:.2f}m / 직선 {D:.2f}m (여유 {(L/D-1)*100:+.1f}%), 점 {len(path)}개")
print(f"최대 횡변위 {fy[i]:+.3f}m ({'좌' if fy[i]>0 else '우'}) @ 전방 {fx[i]:.2f}m")
print(f"경로 비용: 최대 {cmax}, 평균 {np.mean(costs):.0f}" if costs else "비용 조회 실패")
print("전방 0.6~1.6m 구간 횡변위 프로파일:")
for d in np.arange(0.6, 1.65, 0.2):
    k = int(np.argmin(np.abs(fx-d)))
    print(f"  x={fx[k]:.2f}m → y={fy[k]:+.3f}m")
rclpy.shutdown()
