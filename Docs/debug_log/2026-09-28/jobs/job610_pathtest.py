#!/usr/bin/env python3
"""f0a4 'p' 실패 진단(09-28): compute_path_to_pose 를 직접 불러 상태·경로 길이·오류를 출력(로버는 움직이지 않음)."""
import math, time, rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import ComputePathToPose
from geometry_msgs.msg import PoseStamped
rclpy.init(); n = Node('pathtest610'); ac = ActionClient(n, ComputePathToPose, 'compute_path_to_pose')
print('서버:', ac.wait_for_server(timeout_sec=5))
for use_ns in (False, True):
    g = ComputePathToPose.Goal(); g.goal = PoseStamped(); g.goal.header.frame_id = 'map'
    if use_ns: g.goal.header.stamp = n.get_clock().now().to_msg()
    g.goal.pose.position.x = 1.0; g.goal.pose.orientation.w = 1.0; g.use_start = False; g.planner_id = 'GridBased'
    f = ac.send_goal_async(g); t0 = time.time()
    while not f.done() and time.time() - t0 < 5: rclpy.spin_once(n, timeout_sec=0.05)
    gh = f.result(); print('stamp %s: 수락 %s' % ('now' if use_ns else '0', gh.accepted if gh else None))
    if not gh or not gh.accepted: continue
    rf = gh.get_result_async(); t0 = time.time()
    while not rf.done() and time.time() - t0 < 8: rclpy.spin_once(n, timeout_sec=0.05)
    if not rf.done(): print('  결과 시간 초과'); continue
    res = rf.result(); print('  상태 %d, 경로 점 %d, 계획 시간 %.3f s' % (res.status, len(res.result.path.poses), res.result.planning_time.sec + res.result.planning_time.nanosec * 1e-9))
rclpy.shutdown()
