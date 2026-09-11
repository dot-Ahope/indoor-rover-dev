#!/usr/bin/env python3
"""회피 주행 계측판 (2026-09-09) — job92 의 여유 측정이 틀렸던 것을 고친다.

job92 의 오류: '최소 여유' 를 실시간 깊이 포인트클라우드에서 쟀다. 로버가 상자 옆을 지나기
시작하면 상자가 카메라 화각을 벗어나 그 값이 멀리 있는 다른 물체로 바뀐다. job124 에서
28.0cm 로 보고했지만 CSV 로 기하 계산한 실제 최근접은 0.0cm(접촉)였다.

여기서는 세 가지를 동시에 기록해 '경로가 안쪽으로 옮겨갔는지' vs '코스트맵이 상자를 잃었는지'
를 가른다:
  1) clear_geo : 출발 시 map 에 고정한 상자 사각형 ↔ 차체 사각형의 실제 거리 (카메라 무관)
  2) plan_clear: 그 순간의 /plan 이 상자에서 얼마나 떨어져 있는가 (차체 반폭 제외한 여유)
  3) lc_box / gc_box : 로컬·전역 코스트맵이 상자 자리에 아직 비용을 갖고 있는가
사용: python3 job125_avoid3.py [D=1.80] [timeout=90] [csv이름=job125]
"""
import math, sys, time, csv, rclpy, tf2_ros
import numpy as np
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import Path, OccupancyGrid
from sensor_msgs.msg import PointCloud2
from geometry_msgs.msg import PoseStamped, Twist
from rclpy.qos import qos_profile_sensor_data, QoSProfile, DurabilityPolicy, ReliabilityPolicy

D = float(sys.argv[1]) if len(sys.argv) > 1 else 1.80
TMO = float(sys.argv[2]) if len(sys.argv) > 2 else 90.0
NAME = sys.argv[3] if len(sys.argv) > 3 else 'job125'
HL, HW = 0.25, 0.165          # 차체 반길이 / 반폭 (실제 외곽, 패딩 제외)
BOX_W, BOX_D = 0.18, 0.11     # 사용자 실측: 폭(가로) 0.18, 정면(세로) 0.11

rclpy.init(); n = Node('avoid125')
buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
S = {'cmd': (0.0, 0.0), 'path': []}
qos_tl = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                    reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(Twist, '/cmd_vel', lambda m: S.__setitem__('cmd', (m.linear.x, m.angular.z)), 10)
n.create_subscription(Path, '/plan',
                      lambda m: S.__setitem__('path', [(p.pose.position.x, p.pose.position.y) for p in m.poses]), 10)
n.create_subscription(PointCloud2, '/camera/camera/depth/color/points',
                      lambda m: S.__setitem__('pc', m), qos_profile_sensor_data)
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: S.__setitem__('lc', m), qos_tl)
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: S.__setitem__('gc', m), qos_tl)


def Rq(q):
    w, x, y, z = q.w, q.x, q.y, q.z
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])


def cloud(frame):
    if 'pc' not in S:
        return None
    m = S['pc']
    try:
        tr = buf.lookup_transform(frame, m.header.frame_id, rclpy.time.Time()).transform
    except Exception:
        return None
    off = {f.name: f.offset for f in m.fields}
    raw = np.frombuffer(m.data, dtype=np.uint8).reshape(-1, m.point_step)
    xyz = np.stack([raw[:, off[k]:off[k]+4].copy().view(np.float32).ravel() for k in ('x', 'y', 'z')], axis=1)
    xyz = xyz[np.isfinite(xyz).all(axis=1)]
    return xyz @ Rq(tr.rotation).T + np.array([tr.translation.x, tr.translation.y, tr.translation.z])


def pose(frame='map'):
    try:
        t = buf.lookup_transform(frame, 'base_link', rclpy.time.Time()).transform
        q = t.rotation
        return (t.translation.x, t.translation.y, math.atan2(2*(q.w*q.z), 1-2*q.z*q.z))
    except Exception:
        return None


def dist_pt_to_footprint(px, py):
    """차체 좌표계 점 → 차체 외곽 사각형까지 거리 (내부면 0)."""
    return math.hypot(max(abs(px)-HL, 0.0), max(abs(py)-HW, 0.0))


# ── 1) TF/센서 준비 ─────────────────────────────────────────────
t0 = time.time()
while time.time()-t0 < 20 and (pose() is None or 'pc' not in S or 'lc' not in S):
    rclpy.spin_once(n, timeout_sec=0.1)
p0 = pose()
if p0 is None:
    print("TF 실패"); raise SystemExit(1)

# ── 2) 상자 map 좌표 확정 ───────────────────────────────────────
# 2026-09-09: 카메라 정적 TF 를 명시적으로 기다린다. pose() 는 map→base_link 만 요구하므로
#   그것이 성립해도 camera_depth_optical_frame 은 아직 버퍼에 없을 수 있다(다른 발행자).
#   foxglove_bridge 가 CPU 를 많이 쓰는 상태에서 /tf_static 전달이 늦어 검출이 실패했다(job136).
tw = time.time()
while time.time()-tw < 20:
    try:
        buf.lookup_transform('base_link', 'camera_depth_optical_frame', rclpy.time.Time())
        break
    except Exception:
        rclpy.spin_once(n, timeout_sec=0.1)
else:
    print("카메라 TF 대기 실패 (base_link ← camera_depth_optical_frame)"); raise SystemExit(1)

def _clusters_y(sel, gap=0.08, minpts=25):
    """y 축 1D 클러스터링 — 인접 점의 y 간격이 gap 을 넘으면 다른 물체로 본다.
       상자 폭 0.18m 이므로 0.08m 이면 벽과 상자를 확실히 가른다."""
    if len(sel) == 0:
        return []
    o = sel[np.argsort(sel[:, 1])]
    out, cur = [], [o[0]]
    for p in o[1:]:
        if p[1] - cur[-1][1] > gap:
            if len(cur) >= minpts:
                out.append(np.array(cur))
            cur = [p]
        else:
            cur.append(p)
    if len(cur) >= minpts:
        out.append(np.array(cur))
    return out


def detect_box(pnow):
    """현재 자세에서 상자를 검출해 map 좌표 네 꼭짓점을 낸다. 실패 시 None.

    2026-09-10: 주행 중에도 **보일 때마다 재고정**한다.
      이유: 상자를 출발 시 map 좌표에 한 번만 고정하면 SLAM 의 map→odom 보정이
      쌓일수록 실물과 어긋난다. job196 에서 주행 내내 상자 사각형 안 깊이점이 0 이 되어
      ①·⑤ 지표가 통째로 무의미해졌다(그 시점 보정량 11.6cm, 상자 폭 18cm).
      보일 때 갱신하고 안 보이면 마지막 관측을 유지하면, 우리가 관심 있는
      '안 보이는 구간' 만 외삽이 되고 나머지는 항상 최신이다.
    """
    P = cloud('base_link')
    if P is None:
        return None
    sel = P[(P[:, 2] > 0.05) & (P[:, 2] < 0.30) & (P[:, 0] > 0.5) & (P[:, 0] < 1.5) & (np.abs(P[:, 1]) < 0.5)]
    if len(sel) < 40:
        return None
    # 2026-09-10 정정 ★ 이 범위에는 상자만 있는 게 아니다.
    #   실측 씬: 우측 벽 487점(z중앙 0.26) vs 상자 119점(z중앙 0.09).
    #   덩어리를 나누지 않고 median(y) 를 쓰면 중심이 **점이 많은 벽 쪽으로 끌려간다**.
    #   게다가 fx 는 5퍼센타일 x(=더 가까운 상자 쪽)라, 벽의 y 와 상자의 x 를 조합한
    #   **아무것도 없는 자리**에 사각형이 생긴다. 그 안의 깊이점이 0 이 되는 것은 당연하다.
    #   → 이것이 job167 "카메라가 근접 시 상자를 못 본다", job196 "지표 전량 0",
    #     job205 "미관측 37.6초" 의 정체다. 정지 60초 측정(job209)에서 상자 깊이점은
    #     253~275 로 완벽히 안정적이었다 — 카메라는 처음부터 잘 보고 있었다.
    #   고침: y 축 1D 클러스터링으로 덩어리를 나누고, 낮은 물체(z중앙<0.20) 중
    #        **진행축(y=0)에 가장 가까운** 것을 상자로 택한다.
    cl = _clusters_y(sel)
    low = [(abs(float(np.median(c[:, 1]))), c) for c in cl
           if float(np.median(c[:, 2])) < 0.20]
    if not low:
        return None
    low.sort(key=lambda t: t[0])
    sel = low[0][1]
    if len(sel) < 40:
        return None
    cy = float(np.median(sel[:, 1]))
    fx = float(np.percentile(sel[:, 0], 5))     # 전면 x
    c, s = math.cos(pnow[2]), math.sin(pnow[2])
    corners = []
    for bx, by in ((fx, cy-BOX_W/2), (fx, cy+BOX_W/2),
                   (fx+BOX_D, cy+BOX_W/2), (fx+BOX_D, cy-BOX_W/2)):
        corners.append((pnow[0] + bx*c - by*s, pnow[1] + bx*s + by*c))
    return dict(corners=corners, n=len(sel), base=(fx, cy))


BOX = None
for attempt in range(60):
    BOX = detect_box(p0)
    if BOX is not None:
        break
    rclpy.spin_once(n, timeout_sec=0.2)
if BOX is None:
    P = cloud('base_link')
    nn = 0 if P is None else int(((P[:, 2] > 0.05) & (P[:, 2] < 0.30) &
                                  (P[:, 0] > 0.5) & (P[:, 0] < 1.5) & (np.abs(P[:, 1]) < 0.5)).sum())
    print("상자 검출 실패 — 조건 통과 점 %d개(40 필요). 전방 0.5~1.5m 에 낮은 물체가 보여야 합니다"
          % nn); raise SystemExit(1)

def make_peri(box):
    """상자 둘레를 촘촘히 샘플링 (사각형↔사각형 거리를 점-사각형 거리의 최소로 근사)."""
    CS = box['corners']
    peri = []
    for i in range(4):
        ax, ay = CS[i]; bx, by = CS[(i+1) % 4]
        for k in range(21):
            u = k/20.0
            peri.append((ax + u*(bx-ax), ay + u*(by-ay)))
    return np.array(peri)


PERI = make_peri(BOX)
bx_min, bx_max = PERI[:, 0].min(), PERI[:, 0].max()
by_min, by_max = PERI[:, 1].min(), PERI[:, 1].max()
BOXC = (float(PERI[:, 0].mean()), float(PERI[:, 1].mean()))
REFIX_MAX = 0.30      # 재고정 허용 이동량(m). 이보다 멀면 다른 물체로 보고 무시한다
last_fix_t = 0.0      # 마지막 재고정 시각(주행 시작 기준)
print("상자 확정: map x %.3f~%.3f, y %+.3f~%+.3f (검출점 %d, base 전면 %.2f)"
      % (bx_min, bx_max, by_min, by_max, BOX['n'], BOX['base'][0]))


def clear_geo(px, py, yaw):
    """차체 외곽 ↔ 상자 외곽 최소 거리 (m). 0 이면 접촉."""
    c, s = math.cos(-yaw), math.sin(-yaw)
    dx = PERI[:, 0] - px; dy = PERI[:, 1] - py
    rx = dx*c - dy*s; ry = dx*s + dy*c            # 차체 좌표계
    ex = np.maximum(np.abs(rx) - HL, 0.0)
    ey = np.maximum(np.abs(ry) - HW, 0.0)
    return float(np.min(np.hypot(ex, ey)))


def plan_clear():
    """현재 /plan 이 상자에서 떨어진 최소 거리 − 차체 반폭. 음수면 계획 자체가 접촉 경로."""
    P = S['path']
    if len(P) < 2:
        return float('nan'), float('nan')
    A = np.array(P)
    # 경로점 ↔ 상자 둘레 최소 거리
    d = np.min(np.hypot(A[:, None, 0] - PERI[None, :, 0], A[:, None, 1] - PERI[None, :, 1]))
    # 상자 x 근처에서의 경로 횡좌표 (출발 자세 기준)
    c, s = math.cos(p0[2]), math.sin(p0[2])
    fx = (A[:, 0]-p0[0])*c + (A[:, 1]-p0[1])*s
    fy = -(A[:, 0]-p0[0])*s + (A[:, 1]-p0[1])*c
    bxf = (BOXC[0]-p0[0])*c + (BOXC[1]-p0[1])*s
    k = int(np.argmin(np.abs(fx - bxf)))
    return d - HW, float(fy[k])


def box_points():
    """상자 사각형(수평 투영) 안에 들어오는 깊이점 수. 2026-09-09 추가.
    '카메라가 점을 못 만든다' vs '코스트맵이 점을 안 쓴다' 를 가른다.
    job152 에서 마킹이 끊긴 시점의 카메라~상자 거리는 0.518m 였는데 실측 최소측정거리는
    0.22~0.25m 였다 — 거리상 보여야 하는데 마킹이 끊겼으므로 둘 중 어느 쪽인지 확인이 필요하다."""
    P = cloud('map')
    if P is None:
        return -1
    m = ((P[:, 0] >= bx_min) & (P[:, 0] <= bx_max) &
         (P[:, 1] >= by_min) & (P[:, 1] <= by_max) &
         (P[:, 2] > 0.03) & (P[:, 2] < 0.40))
    return int(m.sum())


def cost_at(key, frame, x, y):
    """map 좌표 (x,y) 의 코스트맵 비용. 로컬은 odom 프레임이라 변환한다."""
    if key not in S:
        return -1
    g = S[key]; i = g.info
    if frame != 'map':
        try:
            t = buf.lookup_transform(frame, 'map', rclpy.time.Time()).transform
            q = t.rotation; th = math.atan2(2*(q.w*q.z), 1-2*q.z*q.z)
            c, s = math.cos(th), math.sin(th)
            x, y = t.translation.x + x*c - y*s, t.translation.y + x*s + y*c
        except Exception:
            return -1
    cx = int((x-i.origin.position.x)/i.resolution); cy = int((y-i.origin.position.y)/i.resolution)
    if not (0 <= cx < i.width and 0 <= cy < i.height):
        return -1
    return g.data[cy*i.width+cx]


# ── 3) 목표 전송 ────────────────────────────────────────────────
ch, sh = math.cos(p0[2]), math.sin(p0[2])
GX, GY = p0[0] + D*ch, p0[1] + D*sh
print("출발 (%.2f,%.2f) hd=%.1f° → 목표 (%.2f,%.2f)" % (p0[0], p0[1], math.degrees(p0[2]), GX, GY), flush=True)
ac = ActionClient(n, NavigateToPose, 'navigate_to_pose'); ac.wait_for_server(timeout_sec=10.0)
g = NavigateToPose.Goal(); g.pose = PoseStamped(); g.pose.header.frame_id = 'map'
g.pose.header.stamp = n.get_clock().now().to_msg()
g.pose.pose.position.x, g.pose.pose.position.y = GX, GY
g.pose.pose.orientation.z, g.pose.pose.orientation.w = math.sin(p0[2]/2), math.cos(p0[2]/2)
fut = ac.send_goal_async(g); rclpy.spin_until_future_complete(n, fut, timeout_sec=30.0)
gh = fut.result()
if gh is None or not gh.accepted:
    print("목표 거부"); raise SystemExit(1)

rf = gh.get_result_async(); t1 = time.time(); rows = []; nxt = t1; log = t1
last_fix_t = 0.0
print("  t   전진   횡변위 | 실여유 계획여유 계획횡 | lc gc 깊이점 미관측s | v_cmd  w_cmd", flush=True)
while not rf.done() and time.time()-t1 < TMO:
    rclpy.spin_once(n, timeout_sec=0.01)
    now = time.time(); p = pose()
    if p is None or now < nxt:
        continue
    nxt += 0.1
    # ── 상자 재고정 (0.5초마다, 보일 때만) ──────────────────────────
    if (now - t1) - last_fix_t >= 0.5:
        nb = detect_box(p)
        if nb is not None:
            npi = make_peri(nb)
            nc = (float(npi[:, 0].mean()), float(npi[:, 1].mean()))
            if math.hypot(nc[0]-BOXC[0], nc[1]-BOXC[1]) <= REFIX_MAX:
                PERI = npi
                bx_min, bx_max = PERI[:, 0].min(), PERI[:, 0].max()
                by_min, by_max = PERI[:, 1].min(), PERI[:, 1].max()
                BOXC = nc
                last_fix_t = now - t1
    box_age = (now - t1) - last_fix_t     # 마지막 재고정 이후 경과(초)
    rel = (p[0]-p0[0], p[1]-p0[1])
    fwd = rel[0]*ch + rel[1]*sh; lat = -rel[0]*sh + rel[1]*ch
    cg = clear_geo(p[0], p[1], p[2])
    pc, pfy = plan_clear()
    lb = cost_at('lc', 'odom', *BOXC); gb = cost_at('gc', 'map', *BOXC)
    bp = box_points()
    rows.append((now-t1, fwd, lat, cg, pc, pfy, lb, gb, S['cmd'][0], S['cmd'][1], bp, box_age))
    if now >= log:
        log += 1.0
        print("%5.1f %+.3f %+.3f | %6.3f %8.3f %+6.3f | %5d %5d %6d | %+.3f %+.3f"
              % (now-t1, fwd, lat, cg, pc, pfy, lb, gb, bp, S['cmd'][0], S['cmd'][1]), flush=True)

if not rf.done():
    gh.cancel_goal_async(); rclpy.spin_once(n, timeout_sec=2.0); res = 'TIMEOUT'
else:
    res = {4: 'SUCCEEDED', 5: 'CANCELED', 6: 'ABORTED'}.get(rf.result().status, str(rf.result().status))

with open('/tmp/%s.csv' % NAME, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['t', 'fwd', 'lat', 'clear_geo', 'plan_clear', 'plan_lat_at_box', 'lc_box', 'gc_box', 'v', 'w', 'box_pts', 'box_age'])
    w.writerows(rows)

cg = [r[3] for r in rows]
pcl = [r[4] for r in rows if not math.isnan(r[4])]
k = int(np.argmin(cg))
# 2026-09-11: 조향 지표에서 **목표 도달 후 자세 정렬 구간을 제외**한다.
#   사용자 관찰: "목표 도달 후 자세를 바꾸려 제자리 회전을 하는데, 마찰과 좌우 바퀴 속도
#   차이로 뒤로 밀리면서 회전한다." job242 에서 부호반전 7회 중 2회가 전진 1.45m 이상
#   (목표 부근)에서 났고 그 둘만 크기가 컸다(w 0.170 / 0.109). 나머지는 0.02~0.03 의
#   미세 진동이다. S4 의 '직진 중 w 부호반전' 은 **회피 주행의 안정성**을 보는 지표이지
#   자세 정렬을 보는 것이 아니다 — 정렬 구간이 섞이면 지표가 통째로 오염된다.
#   job242 재계산: 전체 기준 1.3 회/m(미달) → 주행구간 기준 **0.46 회/m**(통과).
GOAL_NEAR = 0.30      # m — Nav2 xy_goal_tolerance(0.25) 보다 약간 크게
_gi = len(rows)
for _i, _r in enumerate(rows):
    if math.hypot(_r[1] - D, _r[2]) < GOAL_NEAR:
        _gi = _i
        break
drive_rows = rows[:_gi]
drive_dist = sum(math.hypot(drive_rows[i][1]-drive_rows[i-1][1], drive_rows[i][2]-drive_rows[i-1][2])
                 for i in range(1, len(drive_rows)))
straight = [r for r in drive_rows if abs(r[8]) > 0.03]
flips = sum(1 for i in range(1, len(straight))
            if straight[i][9]*straight[i-1][9] < 0 and abs(straight[i][9]) > 0.01 and abs(straight[i-1][9]) > 0.01)
dist = sum(math.hypot(rows[i][1]-rows[i-1][1], rows[i][2]-rows[i-1][2]) for i in range(1, len(rows)))
print("")
print("결과 %s  소요 %.1fs  주행 %.2fm  샘플 %d" % (res, rows[-1][0], dist, len(rows)))
print("  ① 실제 최근접(차체↔상자 기하): %.1f cm @ t=%.1fs 전진 %.2f 횡 %+.3f   ← 0 이면 접촉"
      % (min(cg)*100, rows[k][0], rows[k][1], rows[k][2]))
if pcl:
    j = int(np.argmin(pcl))
    print("  ② 계획의 최소 여유: %.1f cm (최근접 시점 %.1f cm)   ← 음수면 계획 자체가 접촉 경로"
          % (min(pcl)*100, rows[k][4]*100))
print("  ③ 상자 자리 비용 — 로컬 최소/최근접시 %d/%d, 전역 최소/최근접시 %d/%d  ← 0 이면 기억 소실"
      % (min(r[6] for r in rows), rows[k][6], min(r[7] for r in rows), rows[k][7]))
# ④ 경로 좌우 전환 — 양안정성 지표. 상자 x 위치에서의 계획 횡좌표 부호가 바뀐 횟수.
#    |y| < 0.05 인 애매한 구간은 노이즈로 보고 직전 부호를 유지한다.
side, flips_plan, first = 0, 0, None
for r in rows:
    v = r[5]
    if math.isnan(v) or abs(v) < 0.05:
        continue
    sgn = 1 if v > 0 else -1
    if first is None:
        first = sgn
    elif sgn != side:
        flips_plan += 1
    side = sgn
neg = sum(1 for r in rows if not math.isnan(r[4]) and r[4] < 0)
print("  ④ 경로 좌우 전환 %d회 (최초 선택 %s), 계획이 접촉 경로였던 샘플 %d/%d (%.0f%%)"
      % (flips_plan, {1: '좌', -1: '우', None: '?'}[first], neg, len(rows), 100.0*neg/max(len(rows), 1)))
# ⑤ 마킹 중단이 카메라 탓인지 코스트맵 탓인지
lost = [r for r in rows if r[6] == 0]          # 로컬 코스트맵이 상자를 잃은 샘플
if lost:
    withpts = sum(1 for r in lost if r[10] > 0)
    print("  ⑤ 로컬이 상자를 잃은 %d샘플 중 깊이점이 있었던 것 %d (%.0f%%) — 평균 %.1f점"
          % (len(lost), withpts, 100.0*withpts/len(lost), sum(r[10] for r in lost)/len(lost)))
    print("     (점이 있는데 잃었다 → 코스트맵 쪽 / 점이 없다 → 카메라 쪽)")
print("  깊이점: 최대 %d, 최소 %d" % (max(r[10] for r in rows), min(r[10] for r in rows)))
print("  ⑥ 상자 미관측 최대 %.1f초 — 이 구간의 ①·⑤ 는 마지막 관측의 외삽이다"
      % max(r[11] for r in rows))
print("  조향(주행구간 %.2fm, 목표부근 %d샘플 제외): 직진 중 |ω| 평균 %.3f 최대 %.3f rad/s, 부호반전 %d회 = %.2f회/m"
      % (drive_dist, len(rows)-len(drive_rows),
         sum(abs(r[9]) for r in straight)/max(len(straight), 1),
         max((abs(r[9]) for r in straight), default=0), flips, flips/max(drive_dist, 0.01)))
rclpy.shutdown()
