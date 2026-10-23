#!/usr/bin/env python3
"""query_planners — 오프라인 planner_server(ROS_DOMAIN_ID 42, planner_offline.yaml)에 장면마다 지도를 넣고 계획기별로 경로를 받는다 (2026-10-23, Jetson, 로버 안 움직임).
  왜: Phase P §4 — NavFn(B0)과 Smac Hybrid 변형을 같은 지도 · 출발 · 목표로 비교(P5 · P7). 실제 planner_server 플러그인을 그대로 부름(흉내 아님).
  순서(장면마다): 기록 지도의 치명 칸(100)과 미지(−1)만 /offline_map(transient local)로 발행 → 재구성된 /global_costmap/costmap 이 그 지도 크기 · 원점으로
    바뀌고 치명 칸 수가 같아질 때까지 기다림 → 기록 지도와 칸 값 비교(재구성 일치율) → planner_id 마다 ComputePathToPose(use_start) → 경로 · 계획 시간 · 실패 저장.
  출력: npz(장면/계획기별 경로 x, y, yaw · 시간 · 상태, 재구성 일치율) + 표준출력 요약. 인자: 장면.npz 결과.npz planner_id...(쉼표)"""
import sys, json, math, time
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import ComputePathToPose

scenes = np.load(sys.argv[1]); out = sys.argv[2]; PIDS = sys.argv[3].split(',')
meta = json.loads(str(scenes['meta']))


def pose(node, x, y, yaw):
    p = PoseStamped(); p.header.frame_id = 'map'; p.header.stamp = node.get_clock().now().to_msg()
    p.pose.position.x, p.pose.position.y = float(x), float(y); p.pose.orientation.z, p.pose.orientation.w = math.sin(yaw / 2), math.cos(yaw / 2); return p


class Q(Node):
    def __init__(self):
        super().__init__('plan_offline_query')
        tl = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
        self.pub = self.create_publisher(OccupancyGrid, '/offline_map', tl)
        self.cm = None; self.create_subscription(OccupancyGrid, '/global_costmap/costmap', self.on_cm, tl)
        self.ac = ActionClient(self, ComputePathToPose, '/compute_path_to_pose')
    def on_cm(self, m): self.cm = m


rclpy.init(); n = Q(); res = {}; summary = []
def spin(sec):
    t = time.time()
    while time.time() - t < sec: rclpy.spin_once(n, timeout_sec=0.05)
if not n.ac.wait_for_server(timeout_sec=30): print('계획 서버 없음'); sys.exit(1)
for sc in meta:
    k = sc['name']; G = scenes[k + '/grid']; ox, oy, r, _ = scenes[k + '/info']; st = scenes[k + '/start']; gl = scenes[k + '/goal']
    m = OccupancyGrid(); m.header.frame_id = 'map'; m.header.stamp = n.get_clock().now().to_msg()
    m.info.resolution = float(r); m.info.width, m.info.height = G.shape[1], G.shape[0]; m.info.origin.position.x, m.info.origin.position.y = float(ox), float(oy); m.info.origin.orientation.w = 1.0
    S = np.where(G >= 100, 100, np.where(G < 0, -1, 0)).astype(np.int8); m.data = S.ravel().tolist()
    n.cm = None; n.pub.publish(m); t0 = time.time(); ok = False
    while time.time() - t0 < 20:   # 재구성 지도가 이 장면 것인지: 크기 · 원점 · 치명 칸 수
        spin(0.2)
        if n.cm is not None and n.cm.info.width == G.shape[1] and abs(n.cm.info.origin.position.x - ox) < 1e-3:
            C = np.array(n.cm.data, dtype=np.int16).reshape(G.shape)
            if (C == 100).sum() == (G == 100).sum(): ok = True; break
    if not ok: print('%s: 재구성 지도 대기 실패' % k); continue
    spin(1.2)   # 다음 갱신 한 번 더(팽창 반영)
    C = np.array(n.cm.data, dtype=np.int16).reshape(G.shape); Gi = G.astype(np.int16)
    agree = float((C == Gi).mean()); near = float((np.abs(C - Gi) <= 1).mean()); a99 = float(((C == 99) == (Gi == 99)).mean())
    res[k + '/recon'] = C.astype(np.int8)
    line = '%s: 재구성 일치 %.4f (±1 %.4f, 내접 칸 일치 %.4f, 내접 칸 수 기록 %d · 재구성 %d)' % (k, agree, near, a99, (Gi == 99).sum(), (C == 99).sum()); print(line); summary.append(line)
    for pid in PIDS:
        goal = ComputePathToPose.Goal(); goal.start = pose(n, *st); goal.goal = pose(n, *gl); goal.planner_id = pid; goal.use_start = True
        t1 = time.time(); fut = n.ac.send_goal_async(goal); rclpy.spin_until_future_complete(n, fut, timeout_sec=10)
        gh = fut.result(); rf = gh.get_result_async(); rclpy.spin_until_future_complete(n, rf, timeout_sec=15); wall = time.time() - t1
        r_ = rf.result(); P = r_.result.path.poses if r_ is not None else []
        arr = np.array([[p.pose.position.x, p.pose.position.y, 2 * math.atan2(p.pose.orientation.z, p.pose.orientation.w)] for p in P]) if P else np.zeros((0, 3))
        pt = r_.result.planning_time.sec + r_.result.planning_time.nanosec * 1e-9 if r_ is not None else -1
        res['%s/%s/path' % (k, pid)] = arr; res['%s/%s/t' % (k, pid)] = np.array([pt, wall, r_.status if r_ is not None else -1])
        L = float(np.hypot(*np.diff(arr[:, :2], axis=0).T).sum()) if len(arr) > 1 else 0.0
        line = '   %-14s %s · 점 %4d · 길이 %5.2f m · 계획 %.3f s (왕복 %.2f s)' % (pid, '성공' if len(arr) else '실패(상태 %s)' % (r_.status if r_ else '?'), len(arr), L, pt, wall); print(line); summary.append(line)
res['meta'] = scenes['meta']; res['summary'] = np.array('\n'.join(summary))
np.savez_compressed(out, **res); print('저장', out)
n.destroy_node(); rclpy.shutdown()
