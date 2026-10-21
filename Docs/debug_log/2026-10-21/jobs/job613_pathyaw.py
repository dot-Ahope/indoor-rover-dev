#!/usr/bin/env python3
"""경로 끝 방향 조회(단독 프로세스, 2026-09-28 §20): 현재 위치 → (GX, GY) 경로를 planner(GridBased)에서 받아 끝 0.3 m 구간 방향(rad)을 출력.
  러너(job550)와 같은 노드에서 compute_path_to_pose 를 부른 뒤 navigate_to_pose 응답이 오지 않아 멈춘 사고(f0a5 1 차) 때문에 분리.
  출력: 'YAW <rad> <점수> <구간 m>' 또는 'FAIL <이유>'.
  사용 ① 한 번: job613_pathyaw.py GX GY FALLBACK_RAD
       ② 상주(10-13 §4): job613_pathyaw.py --serve → 'READY' 를 낸 뒤 표준입력 한 줄('GX GY FALLBACK_RAD')마다 결과 한 줄. 입력이 닫히면 끝.
          왜: 목표마다 새 프로세스(= 새 DDS 참여자)를 띄우면 그때마다 2~14 s 탐색 통신 급증·소켓 손실이 생겼다(10-13 §2.1). 참여자를 주행 내내 1 개로."""
import sys, math, time, rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import ComputePathToPose
from geometry_msgs.msg import PoseStamped
serve = len(sys.argv) > 1 and sys.argv[1] == '--serve'
rclpy.init(); n = Node('pathyaw613'); ac = ActionClient(n, ComputePathToPose, 'compute_path_to_pose')


def query(gx, gy, fb):
    if not ac.wait_for_server(timeout_sec=5): return 'FAIL 서버 없음'
    g = ComputePathToPose.Goal(); g.goal = PoseStamped(); g.goal.header.frame_id = 'map'
    g.goal.pose.position.x, g.goal.pose.position.y = gx, gy; g.goal.pose.orientation.z, g.goal.pose.orientation.w = math.sin(fb / 2), math.cos(fb / 2)
    g.use_start = False; g.planner_id = 'GridBased'
    f = ac.send_goal_async(g); t0 = time.time()
    while not f.done() and time.time() - t0 < 5: rclpy.spin_once(n, timeout_sec=0.05)
    gh = f.result() if f.done() else None
    if gh is None or not gh.accepted: return 'FAIL 요청 거부/무응답'
    rf = gh.get_result_async(); t0 = time.time()
    while not rf.done() and time.time() - t0 < 5: rclpy.spin_once(n, timeout_sec=0.05)
    if not rf.done(): return 'FAIL 결과 시간 초과'
    P = rf.result().result.path.poses
    if len(P) < 2: return 'FAIL 경로 없음(상태 %d)' % rf.result().status
    ex, ey = P[-1].pose.position.x, P[-1].pose.position.y; k = len(P) - 2
    while k > 0 and math.hypot(P[k].pose.position.x - ex, P[k].pose.position.y - ey) < 0.30: k -= 1
    return 'YAW %.6f %d %.3f' % (math.atan2(ey - P[k].pose.position.y, ex - P[k].pose.position.x), len(P), math.hypot(ex - P[k].pose.position.x, ey - P[k].pose.position.y))


if serve:
    print('READY', flush=True)
    for line in sys.stdin:
        p = line.split()
        if len(p) < 3: continue
        try: r = query(float(p[0]), float(p[1]), float(p[2]))
        except Exception as e: r = 'FAIL %s' % e
        print(r, flush=True)
else:
    print(query(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])), flush=True)
rclpy.shutdown()
