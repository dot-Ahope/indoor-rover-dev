#!/usr/bin/env python3
"""bag 의 특정 시각에 로컬 코스트맵 LETHAL 군집이 무엇인지 감사한다 (2026-09-11).

  job303 결과: v5 정체 순간 로버 좌측 0.41 m(시작프레임 횡 ≈ +0.76) 에 LETHAL 이 있어 코스트맵상 틈이
  0.54 m 뿐이었다. 물리 통로(상자 좌측 +0.05 ~ 벽 +1.24)는 1.2 m 인데 무엇이 거기 있는가.
  - LETHAL 셀을 8-연결 군집으로 나눠 시작프레임 중심·크기·로버와의 거리
  - 각 군집의 라이다 근거: 같은 시각 /scan 점(odom 투영)이 군집 셀 0.10 m 안에 있는 비율
  - 각 군집이 처음 LETHAL 이 된 시각(첫 코스트맵 이후 경과)
  - 시작프레임 ASCII 지도 (# LETHAL, + inscribed, . 라이다점)
"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan

BAG = sys.argv[1]
T = float(sys.argv[2])
START = (float(sys.argv[3]), float(sys.argv[4]), math.radians(float(sys.argv[5])))
TOPIC = sys.argv[6] if len(sys.argv) > 6 else '/local_costmap/costmap'


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


r = rosbag2_py.SequentialReader()
r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
topics = {t.name: t.type for t in r.get_all_topics_and_types()}
print('bag 토픽:', ', '.join(sorted(topics)))
mo, ob, grids, scans = [], [], [], []
static = {}
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
    elif topic == '/tf_static':
        for tr in deserialize_message(data, TFMessage).transforms:
            static[(tr.header.frame_id, tr.child_frame_id)] = (tr.transform.translation.x, tr.transform.translation.y, tr.transform.translation.z, yaw_of(tr.transform.rotation))
    elif topic == TOPIC:
        grids.append((t, deserialize_message(data, OccupancyGrid)))
    elif topic == '/scan':
        scans.append((t, deserialize_message(data, LaserScan)))
mo.sort(); ob.sort()
mo_t = [s[0] for s in mo]; ob_t = [s[0] for s in ob]


def latest(seq, ts, t):
    i = bisect.bisect_right(ts, t) - 1
    return seq[i] if i >= 0 else None


# laser -> base_link (정적 체인 합성; 회전은 yaw 만)
def chain(child, root='base_link'):
    x = y = yaw = 0.0
    cur = child; hops = 0
    while cur != root and hops < 8:
        found = None
        for (p, c), tr in static.items():
            if c == cur:
                found = (p, tr); break
        if not found:
            return None
        p, (tx, ty, tz, tyaw) = found
        x, y = tx + x * math.cos(tyaw) - y * math.sin(tyaw), ty + x * math.sin(tyaw) + y * math.cos(tyaw)
        yaw += tyaw; cur = p; hops += 1
    return (x, y, yaw) if cur == root else None


sc = latest(scans, [s[0] for s in scans], T)
laser_frame = sc[1].header.frame_id if sc else 'laser'
l2b = chain(laser_frame)
print('라이다 프레임 %s -> base_link: %s' % (laser_frame, ('(%.3f, %.3f, yaw %.1f°)' % (l2b[0], l2b[1], math.degrees(l2b[2]))) if l2b else '정적 TF 없음 → base_link 와 동일로 가정'))
if not l2b:
    l2b = (0.0, 0.0, 0.0)

g = latest(grids, [s[0] for s in grids], T)
G = g[1]; res = G.info.resolution
ox0, oy0 = G.info.origin.position.x, G.info.origin.position.y
W, H = G.info.width, G.info.height
data = np.array(G.data, dtype=np.int16).reshape(H, W)
frame = G.header.frame_id
print('%s (%s) %dx%d res %.3f, T 대비 %.1f s 전 발행' % (TOPIC, frame, W, H, res, T - g[0]))
ob_p = latest(ob, ob_t, T); mo_p = latest(mo, mo_t, T)
if frame == 'odom':
    rx, ry, ryaw = ob_p[1], ob_p[2], ob_p[3]
else:
    _, mx, my, myaw = mo_p; _, oxx, oyy, oyaw = ob_p
    rx = mx + oxx * math.cos(myaw) - oyy * math.sin(myaw); ry = my + oxx * math.sin(myaw) + oyy * math.cos(myaw); ryaw = myaw + oyaw
print('로버 %s 자세 (%.3f, %.3f) yaw %+.1f°' % (frame, rx, ry, math.degrees(ryaw)))


def to_start(X, Y):
    """frame 좌표 → 시작프레임(전진, 횡). START 는 map 기준이므로 odom 이면 map 으로 먼저 올린다."""
    if frame == 'odom':
        _, mx, my, myaw = mo_p
        X, Y = mx + X * math.cos(myaw) - Y * math.sin(myaw), my + X * math.sin(myaw) + Y * math.cos(myaw)
    sx, sy, syaw = START
    return ((X - sx) * math.cos(syaw) + (Y - sy) * math.sin(syaw), -(X - sx) * math.sin(syaw) + (Y - sy) * math.cos(syaw))


scan_xy = np.zeros((0, 2))
if sc:
    s = sc[1]; rr = np.array(s.ranges); ang = s.angle_min + np.arange(len(rr)) * s.angle_increment
    ok = np.isfinite(rr) & (rr > s.range_min) & (rr < s.range_max)
    rr, ang = rr[ok], ang[ok]
    lx = rr * np.cos(ang); ly = rr * np.sin(ang)
    bx = l2b[0] + lx * math.cos(l2b[2]) - ly * math.sin(l2b[2]); by = l2b[1] + lx * math.sin(l2b[2]) + ly * math.cos(l2b[2])
    sp = latest(ob, ob_t, sc[0])
    px, py, pyaw = sp[1], sp[2], sp[3]
    if frame == 'map':
        _, mx, my, myaw = mo_p
        px, py, pyaw = mx + px * math.cos(myaw) - py * math.sin(myaw), my + px * math.sin(myaw) + py * math.cos(myaw), myaw + pyaw
    X = px + bx * math.cos(pyaw) - by * math.sin(pyaw); Y = py + bx * math.sin(pyaw) + by * math.cos(pyaw)
    scan_xy = np.column_stack([X, Y])
    print('/scan: %d 유효점 (T 대비 %.2f s 전)' % (len(X), T - sc[0]))

# LETHAL 군집 (8-연결)
jj, ii = np.where(data >= 100)
cells = set(zip(ii.tolist(), jj.tolist()))
seen = set(); clusters = []
for c in list(cells):
    if c in seen:
        continue
    q = [c]; seen.add(c); comp = []
    while q:
        a = q.pop(); comp.append(a)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                b = (a[0] + dx, a[1] + dy)
                if b in cells and b not in seen:
                    seen.add(b); q.append(b)
    clusters.append(comp)
print('LETHAL %d셀, 군집 %d개. 로버 1.6 m 이내 군집:' % (len(cells), len(clusters)))
print('   #   셀수  시작프레임 중심(전진,횡)   횡범위          전진범위        로버거리  라이다근거   첫 LETHAL')
grid_t = [s[0] for s in grids]
rows = []
for comp in clusters:
    cx = np.array([ox0 + (i + 0.5) * res for i, j in comp]); cy = np.array([oy0 + (j + 0.5) * res for i, j in comp])
    d = np.hypot(cx - rx, cy - ry)
    if d.min() > 1.6:
        continue
    st = np.array([to_start(x, y) for x, y in zip(cx, cy)])
    if len(scan_xy):
        sup = np.mean([np.hypot(scan_xy[:, 0] - x, scan_xy[:, 1] - y).min() < 0.10 for x, y in zip(cx, cy)])
    else:
        sup = float('nan')
    first = None
    for tg, gg in grids:
        dd = np.array(gg.data, dtype=np.int16).reshape(gg.info.height, gg.info.width)
        hit = False
        for i, j in comp:
            i2 = int((ox0 + (i + 0.5) * res - gg.info.origin.position.x) / res); j2 = int((oy0 + (j + 0.5) * res - gg.info.origin.position.y) / res)
            if 0 <= i2 < gg.info.width and 0 <= j2 < gg.info.height and dd[j2, i2] >= 100:
                hit = True; break
        if hit:
            first = tg; break
    rows.append((d.min(), len(comp), st[:, 0].mean(), st[:, 1].mean(), st[:, 1].min(), st[:, 1].max(), sup, (first - grid_t[0]) if first else float('nan'), st[:, 0].min(), st[:, 0].max()))
rows.sort()
for k, (dm, n, fx, fy, ymin, ymax, sup, first, xmin, xmax) in enumerate(rows):
    print('  %2d  %4d   (%+.2f, %+.2f)          %+.2f~%+.2f    %+.2f~%+.2f     %.2f     %s      +%.1f s'
          % (k, n, fx, fy, ymin, ymax, xmin, xmax, dm, ('%3.0f%%' % (100 * sup)) if sup == sup else ' n/a', first))

# ASCII 지도 (시작프레임, 0.05 m 셀)
print()
print('시작프레임 지도 (행=전진, 위가 멀리; 열=횡, 왼쪽이 +좌측) # LETHAL, + inscribed(99), o 비용>50, - 비용>0, . 라이다점, R 로버')
step = 0.05
fw = np.arange(2.2, -0.3, -step); lat = np.arange(1.5, -0.6, -step)
canvas = [[' '] * len(lat) for _ in fw]
sx, sy, syaw = START
for a, f in enumerate(fw):
    for b, l in enumerate(lat):
        X = sx + f * math.cos(syaw) - l * math.sin(syaw); Y = sy + f * math.sin(syaw) + l * math.cos(syaw)
        if frame == 'odom':
            _, mx, my, myaw = mo_p
            X, Y = (X - mx) * math.cos(-myaw) - (Y - my) * math.sin(-myaw), (X - mx) * math.sin(-myaw) + (Y - my) * math.cos(-myaw)
        i = int((X - ox0) / res); j = int((Y - oy0) / res)
        if 0 <= i < W and 0 <= j < H:
            v = data[j, i]
            canvas[a][b] = '#' if v >= 100 else ('+' if v >= 99 else ('o' if v > 50 else ('-' if v > 0 else ' ')))
for x, y in scan_xy:
    f, l = to_start(x, y)
    a = int(round((2.2 - f) / step)); b = int(round((1.5 - l) / step))
    if 0 <= a < len(fw) and 0 <= b < len(lat) and canvas[a][b] != '#':
        canvas[a][b] = '.'
rf, rl = to_start(rx, ry)
a = int(round((2.2 - rf) / step)); b = int(round((1.5 - rl) / step))
if 0 <= a < len(fw) and 0 <= b < len(lat):
    canvas[a][b] = 'R'
hdr = ''.join(('|' if abs(l - round(l * 2) / 2) < 1e-6 else ' ') for l in lat)
print('        횡: ' + hdr + '   (| = 0.5 m 눈금: +1.5 +1.0 +0.5 0 -0.5)')
for a, f in enumerate(fw):
    print('  %+5.2f  ' % f + ''.join(canvas[a]))
