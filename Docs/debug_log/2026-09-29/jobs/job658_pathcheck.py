#!/usr/bin/env python3
"""09-29 §12.1 F0-b 출발 전 점검: GridBased(NavFn)에게 (0,0)→(5.5,−2.2) 경로를 물어 길이·문 통과 여부를 본다(주행 없음).
   문 = y −0.65 선의 x 1.85~2.65(지도 §12). 인자: 없음"""
import math, time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import ComputePathToPose
from geometry_msgs.msg import PoseStamped

rclpy.init(); n = Node('f0b_pathcheck'); ac = ActionClient(n, ComputePathToPose, 'compute_path_to_pose')
if not ac.wait_for_server(timeout_sec=10): print('planner 없음'); raise SystemExit(1)
g = ComputePathToPose.Goal(); g.planner_id = 'GridBased'; g.use_start = False
p = PoseStamped(); p.header.frame_id = 'map'; p.pose.position.x = 5.5; p.pose.position.y = -2.2; p.pose.orientation.w = 1.0; g.goal = p
f = ac.send_goal_async(g); t0 = time.time()
while not f.done() and time.time() - t0 < 10: rclpy.spin_once(n, timeout_sec=0.05)
gh = f.result(); r = gh.get_result_async(); t0 = time.time()
while not r.done() and time.time() - t0 < 15: rclpy.spin_once(n, timeout_sec=0.05)
P = [(q.pose.position.x, q.pose.position.y) for q in r.result().result.path.poses]
if not P: print('경로 없음'); raise SystemExit(1)
L = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(P, P[1:]))
cross = [x for (x, y), (x2, y2) in zip(P, P[1:]) if (y - (-0.65)) * (y2 - (-0.65)) <= 0]
print('경로 %d 점, 길이 %.2f m, 시작 (%.2f, %.2f) 끝 (%.2f, %.2f)' % (len(P), L, P[0][0], P[0][1], P[-1][0], P[-1][1]))
print('y −0.65 선을 지나는 x: %s → 문(1.85~2.65) 통과 %s' % (', '.join('%.2f' % x for x in cross), '예' if cross and all(1.85 <= x <= 2.65 for x in cross) else '아니오/확인 필요'))
for k in range(0, len(P), max(1, len(P) // 10)): print('  (%.2f, %.2f)' % P[k], end='')
print()
