#!/usr/bin/env python3
"""mp2(NavFn+MPPI) 왼쪽 쏠림·정지 원인 분석 (2026-09-16).

  bag 재생만(로버는 움직이지 않음). 1 s 간격으로
    - 로버 map 자세(x, y, yaw), cmd_vel, 경로 접선·carrot 방위(로버 기준), 경로 대비 횡편차(+ = 경로의 왼쪽)
    - 로컬 코스트맵: 풋프린트 둘레 최대비용, 4 모서리 ↔ LETHAL 최소거리(왼쪽/오른쪽 군집 분리)
    - 헤딩 대안 실현가능성: 제자리 dθ 회전 후 0.15 m 전진 시 둘레 최대비용 (MPPI 가 고를 수 있었던 선택지)
  지정 시각에는 로컬 코스트맵 ASCII (# LETHAL, o 99, + 50~98, . 1~49, R 풋프린트, p 경로, G 목표)
사용: job327_mp2why.py BAG [sx sy yaw_deg] [ascii_t1,ascii_t2,...]
"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import Path, OccupancyGrid
from geometry_msgs.msg import Twist

BAG = sys.argv[1] if len(sys.argv) > 1 else '/tmp/bag_mp2'
START = (float(sys.argv[2]), float(sys.argv[3]), math.radians(float(sys.argv[4]))) if len(sys.argv) > 4 else (0.0, 0.0, 0.0)
ASCII_T = [float(x) for x in sys.argv[5].split(',')] if len(sys.argv) > 5 else [10.0, 14.0, 18.0, 22.0, 27.0]
HL, HW, PAD = 0.25, 0.165, 0.01     # footprint 반길이·반폭 + footprint_padding(09-14 0.01)


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


r = rosbag2_py.SequentialReader()
r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
mo, ob, plans, lcs, cmds = [], [], [], [], []
while r.has_next():
    topic, data, ts = r.read_next()
    t = ts * 1e-9
    if topic == '/tf':
        for tr in deserialize_message(data, TFMessage).transforms:
            tt = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                mo.append((tt, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                ob.append((tt, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
    elif topic == '/plan':
        plans.append((t, deserialize_message(data, Path)))
    elif topic == '/local_costmap/costmap':
        lcs.append((t, deserialize_message(data, OccupancyGrid)))
    elif topic == '/cmd_vel':
        m = deserialize_message(data, Twist)
        cmds.append((t, m.linear.x, m.angular.z))
mo.sort(); ob.sort()
mo_t = [s[0] for s in mo]; ob_t = [s[0] for s in ob]
pl_t = [s[0] for s in plans]; lc_t = [s[0] for s in lcs]; cm_t = [s[0] for s in cmds]
T0 = ob[0][0]
print('bag %s: T0=%.2f  tf odom->base %d, map->odom %d, plan %d, local costmap %d, cmd_vel %d' % (BAG, T0, len(ob), len(mo), len(plans), len(lcs), len(cmds)))


def latest(seq, ts, t):
    i = bisect.bisect_right(ts, t) - 1
    return seq[i] if i >= 0 else None


def compose(t):
    a = latest(mo, mo_t, t); b = latest(ob, ob_t, t)
    if not a or not b:
        return None
    _, mx, my, myaw = a; _, ox, oy, oyaw = b
    X = mx + ox * math.cos(myaw) - oy * math.sin(myaw)
    Y = my + ox * math.sin(myaw) + oy * math.cos(myaw)
    return (X, Y, wrap(myaw + oyaw), ox, oy, oyaw, mx, my, myaw)


def map_to_odom_pt(mx_, my_, mo_):
    # map 좌표를 odom 좌표로 (로컬 코스트맵은 odom 프레임)
    _, tx, ty, tyaw = mo_[0], mo_[1], mo_[2], mo_[3]
    dx, dy = mx_ - tx, my_ - ty
    return (dx * math.cos(tyaw) + dy * math.sin(tyaw), -dx * math.sin(tyaw) + dy * math.cos(tyaw))


class Grid:
    def __init__(self, G):
        self.res = G.info.resolution; self.ox = G.info.origin.position.x; self.oy = G.info.origin.position.y
        self.W = G.info.width; self.H = G.info.height
        self.d = np.array(G.data, dtype=np.int16).reshape(self.H, self.W)
        jj, ii = np.where(self.d >= 100)
        self.lx = self.ox + (ii + 0.5) * self.res; self.ly = self.oy + (jj + 0.5) * self.res

    def cost(self, x, y):
        i = int((x - self.ox) / self.res); j = int((y - self.oy) / self.res)
        if 0 <= i < self.W and 0 <= j < self.H:
            return int(self.d[j, i])
        return -1


def perimeter(rx, ry, yaw, dx=0.0):
    L, Wd = HL + PAD, HW + PAD
    pts = []
    for a in np.linspace(-L, L, 21):
        for b in (-Wd, Wd):
            pts.append((a, b))
    for b in np.linspace(-Wd, Wd, 15):
        for a in (-L, L):
            pts.append((a, b))
    out = []
    for lx, ly in pts:
        X = rx + (dx + lx) * math.cos(yaw) - ly * math.sin(yaw); Y = ry + (dx + lx) * math.sin(yaw) + ly * math.cos(yaw)
        out.append((X, Y))
    return out


def perim_max(g, rx, ry, yaw, dx=0.0):
    return max(g.cost(X, Y) for X, Y in perimeter(rx, ry, yaw, dx))


def corners(rx, ry, yaw):
    L, Wd = HL + PAD, HW + PAD
    out = []
    for fx, fy, name in ((L, Wd, '앞좌'), (L, -Wd, '앞우'), (-L, -Wd, '뒤우'), (-L, Wd, '뒤좌')):
        X = rx + fx * math.cos(yaw) - fy * math.sin(yaw); Y = ry + fx * math.sin(yaw) + fy * math.cos(yaw)
        out.append((name, X, Y))
    return out


def lethal_side_dist(g, rx, ry, yaw):
    """LETHAL 셀을 로버 기준 좌(y>0)/우(y<0)로 나눠, 각 군집 ↔ 풋프린트 모서리 최소거리"""
    if len(g.lx) == 0:
        return (9, 9, 0, 0)
    dx = g.lx - rx; dy = g.ly - ry
    bx = dx * math.cos(yaw) + dy * math.sin(yaw); by = -dx * math.sin(yaw) + dy * math.cos(yaw)
    near = (np.abs(bx) < 1.0) & (np.abs(by) < 1.0)
    left = near & (by > 0); right = near & (by <= 0)
    res = []
    for m in (left, right):
        if m.sum() == 0:
            res.append(9.0); continue
        best = 9.0
        for name, X, Y in corners(rx, ry, yaw):
            dd = np.hypot(g.lx[m] - X, g.ly[m] - Y).min()
            best = min(best, dd)
        res.append(best)
    return (res[0], res[1], int(left.sum()), int(right.sum()))


def feasibility(g, rx, ry, yaw):
    """dθ ∈ -50..+50 (10° 간격): 제자리 회전 스윕 최대비용 / 회전 후 0.15 m 전진 최대비용"""
    out = []
    for dth in range(-50, 51, 10):
        th = yaw + math.radians(dth)
        rot = max(perim_max(g, rx, ry, yaw + math.radians(s)) for s in np.linspace(0, dth, max(2, abs(dth) // 5 + 1)))
        fwd = max(perim_max(g, rx, ry, th, d) for d in np.arange(0.025, 0.151, 0.025))
        out.append((dth, rot, fwd))
    return out


def sym(c):
    if c >= 100: return '#'
    if c == 99: return 'o'
    if c >= 50: return '+'
    if c >= 1: return '.'
    if c < 0: return '?'
    return ' '


def ascii_map(g, p, plan_pts_odom, goal_odom, half=0.9):
    rx, ry, yaw = p[3], p[4], p[5]
    n = int(half / g.res)
    ci = int((rx - g.ox) / g.res); cj = int((ry - g.oy) / g.res)
    canvas = {}
    for X, Y in perimeter(rx, ry, yaw):
        canvas[(int((X - g.ox) / g.res), int((Y - g.oy) / g.res))] = 'R'
    fx = rx + (HL + PAD + 0.03) * math.cos(yaw); fy = ry + (HL + PAD + 0.03) * math.sin(yaw)
    canvas[(int((fx - g.ox) / g.res), int((fy - g.oy) / g.res))] = '>'
    for X, Y in plan_pts_odom:
        k = (int((X - g.ox) / g.res), int((Y - g.oy) / g.res))
        if k not in canvas:
            canvas[k] = 'p'
    if goal_odom:
        canvas[(int((goal_odom[0] - g.ox) / g.res), int((goal_odom[1] - g.oy) / g.res))] = 'G'
    lines = []
    for j in range(cj + n, cj - n - 1, -1):
        row = ''
        for i in range(ci - n, ci + n + 1):
            if (i, j) in canvas:
                row += canvas[(i, j)]
            elif 0 <= i < g.W and 0 <= j < g.H:
                row += sym(int(g.d[j, i]))
            else:
                row += '?'
        lines.append('%+5.2f |%s|' % ((j - cj) * g.res, row))
    return '\n'.join(lines)


sx, sy, syaw = START


def to_start(X, Y):
    return ((X - sx) * math.cos(syaw) + (Y - sy) * math.sin(syaw), -(X - sx) * math.sin(syaw) + (Y - sy) * math.cos(syaw))


print('%5s | %6s %6s %6s | %6s %6s | %6s %6s %6s | %4s | %5s %5s %4s %4s | %s' % (
    't', '전진', '횡', 'yaw°', 'v', 'w', '접선°', 'carrot°', '횡편차', '둘레', '좌L', '우L', 'nL', 'nR', '대안 dθ:회전/전진 (# ≥100, o 99)'))
tend = min(ob[-1][0], T0 + 92)
t = T0
prev_plan_id = None
while t <= tend:
    p = compose(t); c = latest(cmds, cm_t, t); pl = latest(plans, pl_t, t); gl = latest(lcs, lc_t, t)
    if p and gl:
        g = Grid(gl[1])
        fx_, lx_ = to_start(p[0], p[1])
        tan_s = car_s = lat_s = '   nan'
        if pl:
            pts = [(q.pose.position.x, q.pose.position.y) for q in pl[1].poses]
            if len(pts) > 3:
                d = [math.hypot(x - p[0], y - p[1]) for x, y in pts]
                i = int(np.argmin(d)); j = min(i + 5, len(pts) - 1); k = max(i - 1, 0)
                tan = math.atan2(pts[j][1] - pts[k][1], pts[j][0] - pts[k][0])
                acc = 0.0; ci = i
                for q in range(i, len(pts) - 1):
                    acc += math.hypot(pts[q + 1][0] - pts[q][0], pts[q + 1][1] - pts[q][1]); ci = q + 1
                    if acc >= 0.25:
                        break
                car = math.atan2(pts[ci][1] - p[1], pts[ci][0] - p[0])
                # 횡편차: 경로 최근접점에서 접선 기준 로버의 좌(+)/우(-) 편차
                lat = -(p[0] - pts[i][0]) * math.sin(tan) + (p[1] - pts[i][1]) * math.cos(tan)
                tan_s = '%+6.1f' % math.degrees(wrap(tan - p[2])); car_s = '%+6.1f' % math.degrees(wrap(car - p[2])); lat_s = '%+6.3f' % lat
        pm = perim_max(g, p[3], p[4], p[5])
        dl, dr, nl, nr = lethal_side_dist(g, p[3], p[4], p[5])
        fe = feasibility(g, p[3], p[4], p[5])
        fe_s = ' '.join('%+d:%s%s' % (a, sym(b) if b >= 99 else str(b), sym(cc) if cc >= 99 else str(cc)) for a, b, cc in fe)
        print('%5.1f | %+6.3f %+6.3f %+6.1f | %+6.3f %+6.3f | %6s %6s %6s | %4d | %5.2f %5.2f %4d %4d | %s' % (
            t - T0, fx_, lx_, math.degrees(p[2]), c[1] if c else 0, c[2] if c else 0, tan_s, car_s, lat_s, pm, dl, dr, nl, nr, fe_s))
    t += 1.0

for at in ASCII_T:
    t = T0 + at
    p = compose(t); pl = latest(plans, pl_t, t); gl = latest(lcs, lc_t, t)
    if not (p and gl):
        continue
    g = Grid(gl[1]); mo_ = latest(mo, mo_t, t)
    plan_odom = []
    goal_odom = None
    if pl:
        plan_odom = [map_to_odom_pt(q.pose.position.x, q.pose.position.y, mo_) for q in pl[1].poses]
        if pl[1].poses:
            goal_odom = plan_odom[-1]
    print('\n=== t=%.1f s 로컬 코스트맵(odom, %.1f s 전 발행) 로버 map(%.3f,%.3f) yaw %+.1f° — 위=+y(왼쪽), 오른쪽=+x ===' % (at, t - gl[0], p[0], p[1], math.degrees(p[2])))
    # 로버 heading 을 위로 보기 쉽도록 회전하지 않고 odom 축 그대로 출력 (경로 p, 목표 G)
    print(ascii_map(g, p, plan_odom, goal_odom))
