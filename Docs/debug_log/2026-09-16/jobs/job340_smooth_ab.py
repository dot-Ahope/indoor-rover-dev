#!/usr/bin/env python3
"""계획 A/B (정지, 주행 없음) — A 계획: 격자 모서리를 입구에서 멀리·완만하게 (2026-09-16 분석 문서 §4 A1/A2).

  변형: 'navfn'            : GridBased 그대로
        'navfn+smooth'     : GridBased → SmoothPath(simple_smoother) 후처리
        'navfn@infl'       : 전역 inflation_radius 를 INFL 로 바꾼 뒤 GridBased (끝나면 원복)
        'navfn@infl+smooth': 위 둘 다
  지표(시작프레임 = map, 로버가 (0,0,0) 에 있을 때):
    - 입구 접선각: 경로가 x = BX−0.45 를 지날 때의 진행방향(통로 방향 0° 대비, 작을수록 입구에서 꺾임이 적다)
    - 최대 진행방향·최대 곡률(0.1 m 창 헤딩 변화)·차선변경 시작 x(횡 > +0.10) 및 끝 x(횡이 통로값의 90 %)
    - 상자 셀(전역 LETHAL, 상자 영역)·좌측 셀과 경로점 최소거리, 통로(x 1.0~1.4) 계획횡, 길이
  인자: GOAL_X GOAL_Y BX BY [INFL=0.70] [SMOOTHER=simple_smoother]
"""
import sys, math, time
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav2_msgs.action import ComputePathToPose, SmoothPath
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseStamped
from rcl_interfaces.srv import SetParameters, GetParameters
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType
from builtin_interfaces.msg import Duration

GX, GY, BX, BY = [float(a) for a in sys.argv[1:5]]
INFL = float(sys.argv[5]) if len(sys.argv) > 5 else 0.70
SMO = sys.argv[6] if len(sys.argv) > 6 else 'simple_smoother'

rclpy.init(); n = Node('planab340')
G = {}
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: G.__setitem__('g', m), QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE))
plan_c = ActionClient(n, ComputePathToPose, '/compute_path_to_pose'); smooth_c = ActionClient(n, SmoothPath, '/smooth_path')
setp = n.create_client(SetParameters, '/global_costmap/global_costmap/set_parameters'); getp = n.create_client(GetParameters, '/global_costmap/global_costmap/get_parameters')
for c, name in ((plan_c, 'compute_path_to_pose'), (smooth_c, 'smooth_path')):
    if not c.wait_for_server(timeout_sec=10.0):
        print('액션 서버 없음:', name); sys.exit(1)
setp.wait_for_service(timeout_sec=5.0); getp.wait_for_service(timeout_sec=5.0)
t0 = time.time()
while 'g' not in G and time.time() - t0 < 10:
    rclpy.spin_once(n, timeout_sec=0.2)


def pose(x, y, yaw=0.0):
    p = PoseStamped(); p.header.frame_id = 'map'; p.header.stamp = n.get_clock().now().to_msg()
    p.pose.position.x = x; p.pose.position.y = y; p.pose.orientation.z = math.sin(yaw / 2); p.pose.orientation.w = math.cos(yaw / 2)
    return p


def call(client, goal):
    fut = client.send_goal_async(goal); rclpy.spin_until_future_complete(n, fut, timeout_sec=15.0)
    gh = fut.result()
    if gh is None or not gh.accepted:
        return None
    rf = gh.get_result_async(); rclpy.spin_until_future_complete(n, rf, timeout_sec=30.0)
    return rf.result().result if rf.result() else None


def get_infl():
    req = GetParameters.Request(); req.names = ['inflation_layer.inflation_radius']
    f = getp.call_async(req); rclpy.spin_until_future_complete(n, f, timeout_sec=5.0)
    return f.result().values[0].double_value if f.result() else float('nan')


def set_infl(v):
    req = SetParameters.Request(); req.parameters = [Parameter(name='inflation_layer.inflation_radius', value=ParameterValue(type=ParameterType.PARAMETER_DOUBLE, double_value=float(v)))]
    f = setp.call_async(req); rclpy.spin_until_future_complete(n, f, timeout_sec=5.0)
    return f.result().results[0].successful if f.result() else False


def plan(planner='GridBased'):
    g = ComputePathToPose.Goal(); g.goal = pose(GX, GY); g.start = pose(0.0, 0.0, 0.0); g.use_start = True; g.planner_id = planner
    r = call(plan_c, g)
    return r.path if r and r.path.poses else None


def smooth(path):
    g = SmoothPath.Goal(); g.path = path; g.smoother_id = SMO; g.max_smoothing_duration = Duration(sec=2); g.check_for_collisions = True
    r = call(smooth_c, g)
    if r is None:
        return None, 'no result'
    return (r.path if r.path.poses else None), ('완료' if r.was_completed else '미완료')


def lethal_cells():
    if 'g' not in G:
        return np.zeros((0, 2)), np.zeros((0, 2))
    g = G['g']; res = g.info.resolution
    d = np.array(g.data, dtype=np.int16).reshape(g.info.height, g.info.width); jj, ii = np.where(d >= 100)
    X = g.info.origin.position.x + (ii + 0.5) * res; Y = g.info.origin.position.y + (jj + 0.5) * res
    box = (X > BX - 0.10) & (X < BX + 0.40) & (Y > BY - 0.30) & (Y < BY + 0.30)
    left = (X > 0.3) & (X < 1.8) & (Y > BY + 0.30) & (Y < BY + 1.0)
    return np.stack([X[box], Y[box]], 1), np.stack([X[left], Y[left]], 1)


def metrics(path, label):
    pts = np.array([[p.pose.position.x, p.pose.position.y] for p in path.poses])
    seg = np.diff(pts, axis=0); ds = np.hypot(seg[:, 0], seg[:, 1]); s = np.concatenate([[0], np.cumsum(ds)])
    hd = np.degrees(np.arctan2(seg[:, 1], seg[:, 0]))
    # 0.1 m 창 헤딩 변화(곡률 지표)
    dh = []
    for i in range(len(pts) - 1):
        j = np.searchsorted(s, s[i] + 0.10)
        if j < len(hd):
            a = (hd[j] - hd[i] + 180) % 360 - 180; dh.append(abs(a))
    dhmax = max(dh) if dh else 0
    def hd_at_x(x):
        k = np.argmin(np.abs(pts[:-1, 0] - x)); return hd[k]
    mouth = hd_at_x(BX - 0.45)
    lat = pts[:, 1]
    xs_start = pts[np.argmax(lat > 0.10), 0] if (lat > 0.10).any() else float('nan')
    chan = lat[(pts[:, 0] > 1.0) & (pts[:, 0] < 1.4)]
    chan_lat = float(np.median(chan)) if chan.size else float('nan')
    xs_end = pts[np.argmax(lat > 0.9 * chan_lat), 0] if chan.size and (lat > 0.9 * chan_lat).any() else float('nan')
    boxc, leftc = lethal_cells()
    dbox = np.min(np.hypot(pts[:, 0, None] - boxc[None, :, 0], pts[:, 1, None] - boxc[None, :, 1])) if boxc.size else float('nan')
    dleft = np.min(np.hypot(pts[:, 0, None] - leftc[None, :, 0], pts[:, 1, None] - leftc[None, :, 1])) if leftc.size else float('nan')
    print('%-20s 점 %3d 길이 %.2f | 입구(x=%.2f) 접선 %+5.1f° | 최대 진행방향 %+5.1f° | 0.1 m 창 최대 꺾임 %4.1f° | 차선변경 x %.2f→%.2f | 통로 계획횡 %+.3f | 상자셀 최소 %.3f 좌측셀 %.3f'
          % (label, len(pts), s[-1], BX - 0.45, mouth, hd[np.argmax(np.abs(hd))], dhmax, xs_start, xs_end, chan_lat, dbox, dleft))
    prof = ' '.join('%.1f:%+.0f°' % (s[i], hd[i]) for i in range(0, len(hd), max(1, len(hd) // 12)))
    print('      헤딩 프로파일 s:heading  ' + prof)


infl0 = get_infl()
print('전역 inflation_radius 현재 %.2f, 상자 (%.2f, %.2f), 목표 (%.2f, %.2f), 스무더 %s' % (infl0, BX, BY, GX, GY, SMO))
p = plan()
if p is None:
    print('NavFn 계획 실패'); sys.exit(1)
metrics(p, 'navfn')
sp_, st = smooth(p)
if sp_ is not None:
    metrics(sp_, 'navfn+smooth(%s)' % st)
else:
    print('smooth 실패:', st)
if set_infl(INFL):
    time.sleep(3.0)
    for _ in range(15):
        rclpy.spin_once(n, timeout_sec=0.2)
    p2 = plan()
    if p2 is not None:
        metrics(p2, 'navfn@infl%.2f' % INFL)
        sp2, st2 = smooth(p2)
        if sp2 is not None:
            metrics(sp2, 'navfn@infl%.2f+smooth' % INFL)
    set_infl(infl0); time.sleep(1.0)
    print('inflation 원복 → %.2f' % get_infl())
else:
    print('inflation 변경 실패(동적 재설정 불가?)')
rclpy.shutdown()
