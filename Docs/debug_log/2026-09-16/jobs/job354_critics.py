#!/usr/bin/env python3
"""MPPI 크리틱 비용 재구성 — "상자 회피" 와 "경로 추종" 이 입구에서 어떻게 충돌하는가 (2026-09-16, mp4 bag).

  bag 의 로컬 코스트맵(odom)·변환 경로(/transformed_global_plan)·자세에서, 대표 후보 제어(정지·직진·우회전 호·제자리 우회전·
  후진 등)를 DiffDrive 로 3.2 s(32×0.1) 굴려 Humble MPPI 크리틱 공식으로 비용을 계산한다:
    Obstacles : 둘레(풋프린트) 최대 비용 → 거리 d = r_in − (ln c − ln 253)/scale ; LETHAL 이면 collision_cost 10000 ;
                d < collision_margin(0.05) 면 critical_weight(20)×(0.05−d) ; 아니면 repulsion_weight(1.5)×mean(inflation_r(0.40)−d)
    PathAlign : 끝단이 닿은 경로 index(furthest) ≥ offset(3) 일 때만, 3점마다 경로 최근접 거리 평균 × 14
    PathFollow: 끝단 ↔ 경로점[furthest+5] 거리 × 5
    PathAngle : 현재 자세→경로점[furthest+4] 각 > 0.5 rad 일 때만, 끝단 heading 과 그 점 방향의 각 × 2
    PreferForward: 후진량 × 5,  Constraint: 속도 한계 밖이면 4×초과
  주의: Humble 소스의 의미론을 따라 재구성한 근사(경로 창·정규화 등 세부는 다를 수 있음). 크기 순서·부호가 목적.
  인자: BAG t1,t2,... (bag 첫 odom 기준 초)
"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import OccupancyGrid, Path
from geometry_msgs.msg import Twist

BAG = sys.argv[1]; TS = [float(x) for x in sys.argv[2].split(',')]
# 로컬 코스트맵·MPPI 설정 (nav2_params.yaml 09-16)
R_IN, PAD = 0.175, 0.01; HL, HW = 0.25, 0.165
INFL_R, SCALE = 0.40, 2.5
REP_W, CRIT_W, COLL_COST, MARGIN = 1.5, 20.0, 10000.0, 0.05
ALIGN_W, ALIGN_OFF, ALIGN_STEP = 14.0, 3, 3
FOLLOW_W, FOLLOW_OFF = 5.0, 5
ANGLE_W, ANGLE_OFF, ANGLE_MAX = 2.0, 4, 0.5
FWD_W = 5.0
DT, STEPS = 0.1, 32
VMAX, VMIN, WMAX = 0.08, -0.06, 0.38


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


r = rosbag2_py.SequentialReader()
r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
ob, lcs, tplans, cmds = [], [], [], []
while r.has_next():
    topic, data, ts = r.read_next(); t = ts * 1e-9
    if topic == '/tf':
        for tr in deserialize_message(data, TFMessage).transforms:
            if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                ob.append((tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
    elif topic == '/local_costmap/costmap':
        lcs.append((t, deserialize_message(data, OccupancyGrid)))
    elif topic == '/transformed_global_plan':
        tplans.append((t, deserialize_message(data, Path)))
    elif topic == '/cmd_vel':
        m = deserialize_message(data, Twist); cmds.append((t, m.linear.x, m.angular.z))
ob.sort(); T0 = ob[0][0]
ob_t = [s[0] for s in ob]; lc_t = [s[0] for s in lcs]; tp_t = [s[0] for s in tplans]; cm_t = [s[0] for s in cmds]


def latest(seq, ts, t):
    i = bisect.bisect_right(ts, t) - 1
    return seq[i] if i >= 0 else None


class Grid:
    def __init__(self, G):
        self.res = G.info.resolution; self.ox = G.info.origin.position.x; self.oy = G.info.origin.position.y
        self.W = G.info.width; self.H = G.info.height
        self.d = np.array(G.data, dtype=np.int16).reshape(self.H, self.W)

    def cost(self, x, y):
        """OccupancyGrid(0~100) → costmap_2d 비용(0~254)"""
        i = int((x - self.ox) / self.res); j = int((y - self.oy) / self.res)
        if not (0 <= i < self.W and 0 <= j < self.H):
            return 255.0
        g = int(self.d[j, i])
        if g < 0: return 255.0
        if g == 0: return 0.0
        if g == 100: return 254.0
        if g == 99: return 253.0
        return 1.0 + (g - 1) * 251.0 / 97.0


PERIM = []
for a in np.linspace(-(HL + PAD), HL + PAD, 21):
    for b in (-(HW + PAD), HW + PAD):
        PERIM.append((a, b))
for b in np.linspace(-(HW + PAD), HW + PAD, 15):
    for a in (-(HL + PAD), HL + PAD):
        PERIM.append((a, b))
POSSIBLY_INSCRIBED = 253.0 * math.exp(-SCALE * (math.hypot(HL + PAD, HW + PAD) - R_IN))   # 외접 반경의 비용 ≈ 185


def pose_cost(g, x, y, th):
    c = g.cost(x, y); fp = False
    if c >= POSSIBLY_INSCRIBED:
        fp = True
        c = max(g.cost(x + a * math.cos(th) - b * math.sin(th), y + a * math.sin(th) + b * math.cos(th)) for a, b in PERIM)
    return c, fp


def rollout(x, y, th, ctrl):
    """ctrl: (v, w) 상수 또는 길이 STEPS 의 리스트"""
    pts = []
    for j in range(STEPS):
        v, w = ctrl[j] if isinstance(ctrl, list) else ctrl
        x += v * math.cos(th) * DT; y += v * math.sin(th) * DT; th = wrap(th + w * DT)
        pts.append((x, y, th, v, w))
    return pts


def critics(g, path, x0, y0, th0, pts):
    # --- Obstacles ---
    rep = 0.0; crit = 0.0; coll = None
    for j, (x, y, th, v, w) in enumerate(pts):
        c, fp = pose_cost(g, x, y, th)
        if c < 1.0: continue
        if c >= 254.0 or (c == 253.0 and not fp): coll = j; break
        d = (SCALE * R_IN - math.log(c) + math.log(253.0)) / SCALE
        if not fp: d -= R_IN
        if d < MARGIN: crit += (MARGIN - d)
        else: rep += (INFL_R - d)
    obst = COLL_COST if coll is not None else (CRIT_W * crit + REP_W * rep / STEPS)
    # --- 경로 관련 ---
    P = np.array(path); ex, ey, eth = pts[-1][0], pts[-1][1], pts[-1][2]
    furthest = int(np.argmin(np.hypot(P[:, 0] - ex, P[:, 1] - ey)))
    if furthest >= ALIGN_OFF:
        ds = []
        for j in range(0, STEPS, ALIGN_STEP):
            ds.append(np.min(np.hypot(P[:, 0] - pts[j][0], P[:, 1] - pts[j][1])))
        align = ALIGN_W * float(np.mean(ds))
    else:
        align = 0.0
    tf = P[min(furthest + FOLLOW_OFF, len(P) - 1)]
    follow = FOLLOW_W * math.hypot(tf[0] - ex, tf[1] - ey)
    ta = P[min(furthest + ANGLE_OFF, len(P) - 1)]
    cur_ang = abs(wrap(math.atan2(ta[1] - y0, ta[0] - x0) - th0))
    if cur_ang > ANGLE_MAX:
        angle = ANGLE_W * abs(wrap(math.atan2(ta[1] - ey, ta[0] - ex) - eth))
    else:
        angle = 0.0
    fwd = FWD_W * sum(max(0.0, -p[3]) for p in pts) * DT
    cons = 4.0 * sum(max(0.0, p[3] - VMAX) + max(0.0, VMIN - p[3]) + max(0.0, abs(p[4]) - WMAX) for p in pts) * DT
    return dict(obst=obst, coll=coll, align=align, follow=follow, angle=angle, fwd=fwd, cons=cons, furthest=furthest, cur_ang=cur_ang,
                end=(ex - x0, ey - y0, math.degrees(wrap(eth - th0))))


print('bag %s T0 %.2f: 로컬 %d, 변환경로 %d, cmd %d' % (BAG, T0, len(lcs), len(tplans), len(cmds)))
for at in TS:
    t = T0 + at
    p = latest(ob, ob_t, t); gl = latest(lcs, lc_t, t); tp = latest(tplans, tp_t, t); c = latest(cmds, cm_t, t)
    if not (p and gl and tp):
        print('t=%.1f 데이터 부족' % at); continue
    g = Grid(gl[1]); x0, y0, th0 = p[1], p[2], p[3]
    path = [(q.pose.position.x, q.pose.position.y) for q in tp[1].poses]
    if len(path) < 6:
        print('t=%.1f 경로 점 부족' % at); continue
    # 경로 방향(첫 0.3 m)
    acc = 0; k = 0
    for i in range(len(path) - 1):
        acc += math.hypot(path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]); k = i + 1
        if acc >= 0.30: break
    bearing = math.degrees(wrap(math.atan2(path[k][1] - y0, path[k][0] - x0) - th0))
    c0, fp0 = pose_cost(g, x0, y0, th0)
    print('\n=== t=%.1f s  자세 odom (%.3f, %.3f) yaw %+.1f°  경로 0.3 m 앞 방위 %+.1f°  현재 둘레비용 %.0f  실제 cmd v %+.3f w %+.3f ===' % (
        at, x0, y0, math.degrees(th0), bearing, c0, c[1] if c else 0, c[2] if c else 0))
    cands = [
        ('정지', (0.0, 0.0)), ('직진 0.08', (0.08, 0.0)), ('직진 0.04', (0.04, 0.0)),
        ('우호 0.08/-0.10', (0.08, -0.10)), ('우호 0.08/-0.20', (0.08, -0.20)), ('우호 0.08/-0.30', (0.08, -0.30)),
        ('우호 0.04/-0.20', (0.04, -0.20)), ('우호 0.04/-0.30', (0.04, -0.30)),
        ('제자리 우 -0.38', (0.0, -0.38)), ('제자리 우 -0.20', (0.0, -0.20)),
        ('우회전1s→직진', [(0.0, -0.38)] * 10 + [(0.08, 0.0)] * 22),
        ('좌호 0.08/+0.20', (0.08, 0.20)), ('제자리 좌 +0.38', (0.0, 0.38)),
        ('후진 -0.06', (-0.06, 0.0)), ('후진+우 -0.06/-0.20', (-0.06, -0.20)),
    ]
    if c:
        cands.append(('실제 cmd 유지', (c[1], c[2])))
    print('  %-18s %6s %6s %6s %6s %5s %5s | %7s  %s' % ('후보', 'Obst', 'Align', 'Follow', 'Angle', 'Fwd', 'Cons', '합계', '끝단 dx dy dθ / furthest / 충돌 index'))
    rows = []
    for name, ctrl in cands:
        pts = rollout(x0, y0, th0, ctrl); m = critics(g, path, x0, y0, th0, pts)
        tot = m['obst'] + m['align'] + m['follow'] + m['angle'] + m['fwd'] + m['cons']
        rows.append((tot, name, m))
    for tot, name, m in rows:
        print('  %-18s %6.2f %6.2f %6.2f %6.2f %5.2f %5.2f | %7.2f  (%+.2f,%+.2f,%+.0f°) f=%d %s' % (
            name, min(m['obst'], 999.99), m['align'], m['follow'], m['angle'], m['fwd'], m['cons'], min(tot, 9999.99), *m['end'], m['furthest'], ('충돌@%d' % m['coll']) if m['coll'] is not None else ''))
    best = min(rows, key=lambda r: r[0])
    print('  → 최저 비용: %s (%.2f) | PathAngle 활성 기준각 %.2f rad(현재 %.2f)' % (best[1], best[0], ANGLE_MAX, best[2]['cur_ang']))
