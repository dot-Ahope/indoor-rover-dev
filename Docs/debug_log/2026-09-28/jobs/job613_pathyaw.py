#!/usr/bin/env python3
"""경로 끝 방향 조회(단독 프로세스, 2026-09-28 §20): 현재 위치 → (GX, GY) 경로를 planner(GridBased)에서 받아 끝 0.3 m 구간 방향(rad)을 출력.
  러너(job550)와 같은 노드에서 compute_path_to_pose 를 부른 뒤 navigate_to_pose 응답이 오지 않아 멈춘 사고(f0a5 1 차) 때문에 분리.
  출력 마지막 줄: 'YAW <rad> <점수> <구간 m>' 또는 'FAIL <이유>'. 인자: GX GY FALLBACK_RAD"""
import sys, math, time, rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import ComputePathToPose
from geometry_msgs.msg import PoseStamped
gx, gy, fb = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
rclpy.init(); n = Node('pathyaw613'); ac = ActionClient(n, ComputePathToPose, 'compute_path_to_pose')
def out(s): print(s, flush=True); rclpy.shutdown(); sys.exit(0)
if not ac.wait_for_server(timeout_sec=5): out('FAIL 서버 없음')
g = ComputePathToPose.Goal(); g.goal = PoseStamped(); g.goal.header.frame_id = 'map'
g.goal.pose.position.x, g.goal.pose.position.y = gx, gy; g.goal.pose.orientation.z, g.goal.pose.orientation.w = math.sin(fb / 2), math.cos(fb / 2)
g.use_start = False; g.planner_id = 'GridBased'
f = ac.send_goal_async(g); t0 = time.time()
while not f.done() and time.time() - t0 < 5: rclpy.spin_once(n, timeout_sec=0.05)
gh = f.result() if f.done() else None
if gh is None or not gh.accepted: out('FAIL 요청 거부/무응답')
rf = gh.get_result_async(); t0 = time.time()
while not rf.done() and time.time() - t0 < 5: rclpy.spin_once(n, timeout_sec=0.05)
if not rf.done(): out('FAIL 결과 시간 초과')
P = rf.result().result.path.poses
if len(P) < 2: out('FAIL 경로 없음(상태 %d)' % rf.result().status)
ex, ey = P[-1].pose.position.x, P[-1].pose.position.y; k = len(P) - 2
while k > 0 and math.hypot(P[k].pose.position.x - ex, P[k].pose.position.y - ey) < 0.30: k -= 1
out('YAW %.6f %d %.3f' % (math.atan2(ey - P[k].pose.position.y, ex - P[k].pose.position.x), len(P), math.hypot(ex - P[k].pose.position.x, ey - P[k].pose.position.y)))
