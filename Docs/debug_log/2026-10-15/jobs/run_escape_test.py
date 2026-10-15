#!/usr/bin/env python3
"""run_escape_test — MonotoneEscape 실제 시험 단계별 도구(Jetson 에서 실행). (2026-10-15 §27)
  단계(인자 1):
    goto x y yaw_deg      — Nav2 NavigateToPose(map)로 이동(시험 출발 자리). 결과만 출력.
    gap                   — 카메라 깊이 점군(높이 0.06~0.30, 몸체 좌표 x 0.4~1.6 · y −0.6~0.05)에서 오른쪽 앞 상자의 왼쪽 옆면 y · 앞면 x 와
                            '곧게 가면 차체 오른쪽 옆면(−0.165) ↔ 상자 왼쪽 옆면' 예상 간격, 그리고 nvblox 거리 지도 ≤0 칸 수(구역 안).
    creep dist_m          — Nav2 없이 /cmd_vel 0.05 m/s 직진(10 Hz), odom 이동 dist_m 이면 정지. 안전: 라이다 점이 차체 직사각형(패딩 없는 0.25/−0.25/±0.165)에서
                            4 cm 안이면 즉시 정지(앞 절반 몸체 x > 0 점만, §27.1), 시간 한도 dist/0.05 + 5 s.
    clear                 — 로컬 코스트맵 치명 칸 ↔ 차체(패딩 포함) 최소 거리(몸체 좌표, 칸 중심)와 가장 가까운 칸 위치.
    escape                — /monotone_escape(BackUp 형식) 호출, 결과 · 걸린 시간.
    backup                — 비교용 Nav2 기본 BackUp(/backup, 0.15 m · 0.03 m/s) 호출 — 실패 때와 같은 '0.0 s 실패'가 나는지.
    turn stop_cm max_deg [dir] — 제자리 회전(dir −1 = 오른쪽(기본) · +1 = 왼쪽, 0.08 rad/s). 로컬 코스트맵이 올 때마다 차체(패딩 포함) ↔ 치명 칸
                            정확 거리를 재서 stop_cm 이하면 정지, max_deg 회전하면 정지(§27.3). 라이다 앞 절반 점 4 cm 안이면 즉시 정지.
  출력은 사람이 읽는 한 줄들. 로버를 움직이는 단계: goto · creep · turn · escape · backup."""
import sys, time, math
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, qos_profile_sensor_data
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import OccupancyGrid, Odometry
from sensor_msgs.msg import PointCloud2, LaserScan
from nav2_msgs.action import NavigateToPose, BackUp
from nvblox_msgs.msg import DistanceMapSlice
import tf2_ros
def qmat(q):
    x, y, z, w = q.x, q.y, q.z, q.w
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
class N(Node):
    def __init__(s):
        super().__init__('run_escape_test'); s.buf = tf2_ros.Buffer(); s.tl = tf2_ros.TransformListener(s.buf, s)
    def tf(s, target, frame):
        t = s.buf.lookup_transform(target, frame, rclpy.time.Time()); tr = t.transform
        return np.array([tr.translation.x, tr.translation.y, tr.translation.z]), qmat(tr.rotation)
    def spin_for(s, sec):
        t0 = time.time()
        while time.time() - t0 < sec: rclpy.spin_once(s, timeout_sec=0.05)
rclpy.init(); n = N(); cmd = sys.argv[1]; n.spin_for(1.5)
if cmd == 'goto':
    x, y, yd = float(sys.argv[2]), float(sys.argv[3]), math.radians(float(sys.argv[4]))
    ac = ActionClient(n, NavigateToPose, 'navigate_to_pose'); ac.wait_for_server(timeout_sec=10)
    g = NavigateToPose.Goal(); g.pose.header.frame_id = 'map'; g.pose.pose.position.x = x; g.pose.pose.position.y = y
    g.pose.pose.orientation.z = math.sin(yd / 2); g.pose.pose.orientation.w = math.cos(yd / 2)
    f = ac.send_goal_async(g); rclpy.spin_until_future_complete(n, f); h = f.result(); r = h.get_result_async(); t0 = time.time()
    while not r.done() and time.time() - t0 < 90: rclpy.spin_once(n, timeout_sec=0.1)
    T, R = n.tf('map', 'base_link'); print('goto 결과 상태 %s · 로버 지도 (%.3f, %.3f, %+.1f°) · %.1f s' % (r.result().status if r.done() else '시간초과', T[0], T[1], math.degrees(math.atan2(R[1, 0], R[0, 0])), time.time() - t0))
elif cmd == 'gap':
    P = []; S = [None]
    def cb_pc(m):
        try: T, R = n.tf('base_link', m.header.frame_id)
        except Exception: return
        off = {f.name: f.offset for f in m.fields}; a = np.frombuffer(m.data, np.uint8).reshape(-1, m.point_step)
        xyz = np.stack([a[:, off[k]:off[k] + 4].copy().view(np.float32).ravel() for k in ('x', 'y', 'z')], 1); xyz = xyz[np.isfinite(xyz).all(1)]; w = xyz @ R.T + T
        k = (w[:, 2] > 0.06) & (w[:, 2] < 0.30) & (w[:, 0] > 0.4) & (w[:, 0] < 1.6) & (w[:, 1] > -0.6) & (w[:, 1] < 0.05); P.append(w[k])
    def cb_sl(m):
        try: T, R = n.tf('base_link', m.header.frame_id)
        except Exception: return
        d = np.array(m.data, np.float32).reshape(m.height, m.width); iy, ix = np.indices(d.shape)
        lx = m.origin.x + (ix + 0.5) * m.resolution; ly = m.origin.y + (iy + 0.5) * m.resolution
        wx = T[0] + R[0, 0] * lx + R[0, 1] * ly; wy = T[1] + R[1, 0] * lx + R[1, 1] * ly
        S[0] = int(((wx > 0.4) & (wx < 1.6) & (wy > -0.6) & (wy < 0.05) & (d <= 0) & (d != m.unknown_value)).sum())
    n.create_subscription(PointCloud2, '/camera/camera/depth/color/points', cb_pc, qos_profile_sensor_data)
    n.create_subscription(DistanceMapSlice, '/nvblox_node/static_map_slice', cb_sl, 5); n.spin_for(5.0)
    Q = np.concatenate(P) if P else np.zeros((0, 3))
    if len(Q) < 200: print('gap: 상자 점 부족 %d' % len(Q))
    else:
        left = np.percentile(Q[:, 1], 98); front = np.percentile(Q[:, 0], 2)
        print('gap: 상자 점 %d · 왼쪽 옆면 y %.3f · 앞면 x %.3f · 곧게 가면 차체 오른쪽 옆면(y −0.165) ↔ 상자 왼쪽 옆면 예상 간격 %.1f cm(+ = 비켜 지나감, − = 겹침) · 거리 지도 ≤0 칸 %s'
              % (len(Q), left, front, 100 * (-0.165 - left), S[0]))
elif cmd == 'creep':
    dist = float(sys.argv[2]); pub = n.create_publisher(Twist, '/cmd_vel', 10); sc = [None]; od = [None]
    n.create_subscription(LaserScan, '/scan', lambda m: sc.__setitem__(0, m), qos_profile_sensor_data)
    n.create_subscription(Odometry, '/odometry/filtered', lambda m: od.__setitem__(0, m), 10); n.spin_for(1.0)
    p0 = od[0].pose.pose.position; t0 = time.time(); why = '거리 도달'; minc = 9.0
    while True:
        rclpy.spin_once(n, timeout_sec=0.0); p = od[0].pose.pose.position; moved = math.hypot(p.x - p0.x, p.y - p0.y)
        if moved >= dist: break
        if time.time() - t0 > dist / 0.05 + 5: why = '시간 한도'; break
        m = sc[0]
        if m is not None:
            T, R = n.tf('base_link', m.header.frame_id); r = np.array(m.ranges); an = m.angle_min + np.arange(len(r)) * m.angle_increment; ok = np.isfinite(r) & (r > m.range_min) & (r < 1.5)
            pts = np.stack([r[ok] * np.cos(an[ok]), r[ok] * np.sin(an[ok]), np.zeros(ok.sum())], 1) @ R.T + T
            pts = pts[pts[:, 0] > 0.0]  # 곧은 전진에서는 옆·뒤 점의 옆 간격이 줄지 않으므로 앞 절반(몸체 x > 0) 점만 안전 판정 — §27.1 왼쪽 뒤 옆 1~2 cm 물체
            bx, by = pts[:, 0], pts[:, 1]; d = np.hypot(np.maximum(np.maximum(-0.25 - bx, bx - 0.25), 0), np.maximum(np.abs(by) - 0.165, 0))
            if len(d): minc = min(minc, d.min())
            if len(d) and d.min() < 0.04: why = '라이다 4 cm 안 — 안전 정지'; break
        t = Twist(); t.linear.x = 0.05; pub.publish(t); time.sleep(0.1)
    for _ in range(5): pub.publish(Twist()); time.sleep(0.05)
    print('creep: %s · 이동 %.3f m · %.1f s · 라이다 최소 여유 %.1f cm' % (why, moved, time.time() - t0, 100 * minc))
elif cmd == 'clear':
    L = [None]
    n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: L.__setitem__(0, m), QoSProfile(depth=2, reliability=ReliabilityPolicy.RELIABLE, durability=DurabilityPolicy.TRANSIENT_LOCAL)); n.spin_for(3.0)
    m = L[0]; T, R = n.tf('base_link', m.header.frame_id); a = np.array(m.data, np.int16).reshape(m.info.height, m.info.width); iy, ix = np.nonzero(a >= 100)
    lx = m.info.origin.position.x + (ix + 0.5) * m.info.resolution; ly = m.info.origin.position.y + (iy + 0.5) * m.info.resolution
    bx = T[0] + R[0, 0] * lx + R[0, 1] * ly; by = T[1] + R[1, 0] * lx + R[1, 1] * ly
    ins = (bx >= -0.258) & (bx <= 0.272) & (np.abs(by) <= 0.175)
    d = np.where(ins, 0, np.hypot(np.maximum(np.maximum(-0.258 - bx, bx - 0.272), 0), np.maximum(np.abs(by) - 0.175, 0))); k = int(np.argmin(d))
    print('clear: 차체(패딩 포함) ↔ 로컬 치명 칸 중심 최소 %.1f cm · 그 칸 몸체 (%.3f, %.3f) · 5 cm 안 칸 %d' % (100 * d[k], bx[k], by[k], int((d < 0.05).sum())))
elif cmd == 'turn':
    stop_m = float(sys.argv[2]) / 100; maxr = math.radians(float(sys.argv[3])); dirn = float(sys.argv[4]) if len(sys.argv) > 4 else -1.0
    pub = n.create_publisher(Twist, '/cmd_vel', 10); L = [None]; sc = [None]
    n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: L.__setitem__(0, m), QoSProfile(depth=2, reliability=ReliabilityPolicy.RELIABLE, durability=DurabilityPolicy.TRANSIENT_LOCAL))
    n.create_subscription(LaserScan, '/scan', lambda m: sc.__setitem__(0, m), qos_profile_sensor_data); n.spin_for(1.0)
    def yaw_now():
        T, R = n.tf('odom', 'base_link'); return math.atan2(R[1, 0], R[0, 0])
    def clear_now(m):
        T, R = n.tf('base_link', m.header.frame_id); a = np.array(m.data, np.int16).reshape(m.info.height, m.info.width); iy, ix = np.nonzero(a >= 100)
        lx = m.info.origin.position.x + (ix + 0.5) * m.info.resolution; ly = m.info.origin.position.y + (iy + 0.5) * m.info.resolution
        bx = T[0] + R[0, 0] * lx + R[0, 1] * ly; by = T[1] + R[1, 0] * lx + R[1, 1] * ly
        ins = (bx >= -0.258) & (bx <= 0.272) & (np.abs(by) <= 0.175)
        d = np.where(ins, 0, np.hypot(np.maximum(np.maximum(-0.258 - bx, bx - 0.272), 0), np.maximum(np.abs(by) - 0.175, 0))); k = int(np.argmin(d)); return d[k], bx[k], by[k]
    y0 = yaw_now(); t0 = time.time(); why = '최대 각도'; last = None; c0 = clear_now(L[0])[0]
    while True:
        rclpy.spin_once(n, timeout_sec=0.0); turned = abs(math.atan2(math.sin(yaw_now() - y0), math.cos(yaw_now() - y0)))
        if turned >= maxr: break
        if time.time() - t0 > maxr / 0.08 + 8: why = '시간 한도'; break
        if L[0] is not None and L[0] is not last:
            last = L[0]; c = clear_now(last)
            if c[0] <= stop_m: why = '지도 여유 %.1f cm ≤ %.1f' % (100 * c[0], 100 * stop_m); break
        m = sc[0]
        if m is not None:
            T, R = n.tf('base_link', m.header.frame_id); r = np.array(m.ranges); an = m.angle_min + np.arange(len(r)) * m.angle_increment; ok = np.isfinite(r) & (r > m.range_min) & (r < 1.5)
            pts = np.stack([r[ok] * np.cos(an[ok]), r[ok] * np.sin(an[ok]), np.zeros(ok.sum())], 1) @ R.T + T; pts = pts[pts[:, 0] > 0.0]
            d = np.hypot(np.maximum(np.maximum(-0.25 - pts[:, 0], pts[:, 0] - 0.25), 0), np.maximum(np.abs(pts[:, 1]) - 0.165, 0))
            if len(d) and d.min() < 0.04: why = '라이다 4 cm 안 — 안전 정지'; break
        t = Twist(); t.angular.z = 0.08 * dirn; pub.publish(t); time.sleep(0.05)
    for _ in range(5): pub.publish(Twist()); time.sleep(0.05)
    n.spin_for(1.5); c = clear_now(L[0])
    print('turn: %s · 회전 %.1f° · %.1f s · 지도 여유 시작 %.1f → 정지 1.5 s 뒤 %.1f cm(칸 몸체 (%.3f, %.3f))' % (why, math.degrees(turned), time.time() - t0, 100 * c0, 100 * c[0], c[1], c[2]))
elif cmd == 'backup':
    ac = ActionClient(n, BackUp, 'backup'); ok = ac.wait_for_server(timeout_sec=10)
    if not ok: print('backup: 서버 없음')
    else:
        g = BackUp.Goal(); g.target.x = -0.15; g.speed = -0.03; g.time_allowance.sec = 10
        t0 = time.time(); f = ac.send_goal_async(g); rclpy.spin_until_future_complete(n, f); h = f.result(); r = h.get_result_async()
        while not r.done() and time.time() - t0 < 20: rclpy.spin_once(n, timeout_sec=0.1)
        print('backup: 상태 %s · %.1f s (4 = 성공, 6 = 실패)' % (r.result().status if r.done() else '시간초과', time.time() - t0))
elif cmd == 'escape':
    ac = ActionClient(n, BackUp, 'monotone_escape'); ac.wait_for_server(timeout_sec=10)
    g = BackUp.Goal(); g.target.x = -0.30; g.speed = -0.03; g.time_allowance.sec = 20
    t0 = time.time(); f = ac.send_goal_async(g); rclpy.spin_until_future_complete(n, f); h = f.result()
    if not h.accepted: print('escape: 거부됨')
    else:
        r = h.get_result_async()
        while not r.done() and time.time() - t0 < 30: rclpy.spin_once(n, timeout_sec=0.1)
        print('escape: 상태 %s · %.1f s (4 = 성공, 6 = 실패)' % (r.result().status if r.done() else '시간초과', time.time() - t0))
n.destroy_node(); rclpy.shutdown()
