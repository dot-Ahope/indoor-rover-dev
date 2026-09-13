#!/usr/bin/env python3
"""bag 정체 순간 분석 (2026-09-11, v5 실패 원인).

  첫 충돌 감지 시각(nav2.log 'detected collision')에서
    - 로버 자세(map/odom) 와 /plan 접선의 각도 차, carrot(0.25 m) 방위
    - 경로가 상자 옆(전진 1.15~1.45 m 구간)을 지나는 횡좌표 (상자 좌측 가장자리 +0.05, 통로 중앙 +0.64)
    - 로컬 코스트맵(odom) LETHAL 셀 ↔ footprint 네 모서리 최소거리 — 현재 자세 / 경로 접선 정렬 자세 / +0.10 m 전진
  로버는 움직이지 않는다(bag 재생만).
"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import Path, OccupancyGrid
from geometry_msgs.msg import Twist

BAG = sys.argv[1] if len(sys.argv) > 1 else '/tmp/bag_v5'
T_COLL = float(sys.argv[2]) if len(sys.argv) > 2 else 1789116145.96
START = (float(sys.argv[3]), float(sys.argv[4]), math.radians(float(sys.argv[5]))) if len(sys.argv) > 5 else (-0.050, -0.016, math.radians(-2.9))
HL, HW, PAD = 0.25, 0.165, 0.03


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


r = rosbag2_py.SequentialReader()
r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
mo, ob, plans, lcs, cmds = [], [], [], [], []
while r.has_next():
    topic, data, ts = r.read_next()
    t = ts * 1e-9
    if topic == '/tf':
        m = deserialize_message(data, TFMessage)
        for tr in m.transforms:
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
    return (X, Y, myaw + oyaw, ox, oy, oyaw)


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


t0 = ob[0][0] if ob else 0
print('bag %s: tf odom->base %d, map->odom %d, plan %d, local costmap %d, cmd_vel %d' % (BAG, len(ob), len(mo), len(plans), len(lcs), len(cmds)))
print('첫 충돌 감지 T=%.2f (bag 첫 odom 후 %.1f s)' % (T_COLL, T_COLL - t0))
for dt in (-3.0, -1.5, -0.5, 0.0):
    t = T_COLL + dt
    p = compose(t); c = latest(cmds, cm_t, t)
    if p:
        print('  t%+.1f: map (%.3f,%.3f) yaw %+.1f° | odom (%.3f,%.3f) yaw %+.1f° | cmd v %+.3f w %+.3f'
              % (dt, p[0], p[1], math.degrees(p[2]), p[3], p[4], math.degrees(p[5]), c[1] if c else 0, c[2] if c else 0))
p = compose(T_COLL)
pl = latest(plans, pl_t, T_COLL)
tan = None
if pl and p:
    pts = [(q.pose.position.x, q.pose.position.y) for q in pl[1].poses]
    d = [math.hypot(x - p[0], y - p[1]) for x, y in pts]
    i = int(np.argmin(d))
    j = min(i + 5, len(pts) - 1); k = max(i - 1, 0)
    tan = math.atan2(pts[j][1] - pts[k][1], pts[j][0] - pts[k][0])
    acc = 0.0; ci = i
    for q in range(i, len(pts) - 1):
        acc += math.hypot(pts[q + 1][0] - pts[q][0], pts[q + 1][1] - pts[q][1]); ci = q + 1
        if acc >= 0.25:
            break
    car = math.atan2(pts[ci][1] - p[1], pts[ci][0] - p[0])
    print('경로(%.1f s 전 발행, %d점): 최근접점 %.3f m, 접선 %+.1f°, 로버 yaw %+.1f° → heading 오차 %+.1f° | carrot(0.25 m) 방위 로버기준 %+.1f°'
          % (T_COLL - pl[0], len(pts), d[i], math.degrees(tan), math.degrees(p[2]), math.degrees(wrap(p[2] - tan)), math.degrees(wrap(car - p[2]))))
    sx, sy, syaw = START
    loc = [((x - sx) * math.cos(syaw) + (y - sy) * math.sin(syaw), -(x - sx) * math.sin(syaw) + (y - sy) * math.cos(syaw)) for x, y in pts]
    for lo, hi in ((0.3, 0.6), (0.6, 0.9), (0.9, 1.15), (1.15, 1.45), (1.45, 1.8)):
        near = [ly for lx, ly in loc if lo <= lx < hi]
        if near:
            print('  경로 횡좌표 전진 %.2f~%.2f: %+.3f ~ %+.3f' % (lo, hi, min(near), max(near)))
    rl = ((p[0] - sx) * math.cos(syaw) + (p[1] - sy) * math.sin(syaw), -(p[0] - sx) * math.sin(syaw) + (p[1] - sy) * math.cos(syaw))
    print('  로버 시작프레임 위치: 전진 %.3f 횡 %+.3f' % rl)
g = latest(lcs, lc_t, T_COLL)
if g and p:
    G = g[1]; res = G.info.resolution
    ox0, oy0 = G.info.origin.position.x, G.info.origin.position.y
    W, H = G.info.width, G.info.height
    data = np.array(G.data, dtype=np.int16).reshape(H, W)
    jj, ii = np.where(data >= 100)
    cx = ox0 + (ii + 0.5) * res; cy = oy0 + (jj + 0.5) * res
    rx, ry, ryaw = p[3], p[4], p[5]
    print('로컬 코스트맵(%s, %.1f s 전, LETHAL %d셀) — 로버 odom yaw %+.1f°:' % (G.header.frame_id, T_COLL - g[0], len(ii), math.degrees(ryaw)))

    def corners(yaw, dx=0.0):
        L, Wd = HL + PAD, HW + PAD
        out = []
        for fx, fy, name in ((L, Wd, '앞좌'), (L, -Wd, '앞우'), (-L, -Wd, '뒤우'), (-L, Wd, '뒤좌')):
            X = rx + (dx + fx) * math.cos(yaw) - fy * math.sin(yaw)
            Y = ry + (dx + fx) * math.sin(yaw) + fy * math.cos(yaw)
            out.append((name, X, Y))
        return out

    def report(label, yaw, dx=0.0):
        s = []
        for name, X, Y in corners(yaw, dx):
            dd = np.hypot(cx - X, cy - Y)
            s.append('%s %.2f' % (name, dd.min() if len(dd) else 9))
        # 둘레 최대비용 (RPP inCollision 과 같은 기준)
        L, Wd = HL + PAD, HW + PAD
        mx = -1
        for a in np.linspace(-L, L, 21):
            for b in (-Wd, Wd):
                for lx, ly in ((a, b), (b * L / Wd if False else a, b)):
                    X = rx + (dx + lx) * math.cos(yaw) - ly * math.sin(yaw); Y = ry + (dx + lx) * math.sin(yaw) + ly * math.cos(yaw)
                    i_ = int((X - ox0) / res); j_ = int((Y - oy0) / res)
                    if 0 <= i_ < W and 0 <= j_ < H:
                        mx = max(mx, int(data[j_, i_]))
        for b in np.linspace(-Wd, Wd, 11):
            for a in (-L, L):
                X = rx + (dx + a) * math.cos(yaw) - b * math.sin(yaw); Y = ry + (dx + a) * math.sin(yaw) + b * math.cos(yaw)
                i_ = int((X - ox0) / res); j_ = int((Y - oy0) / res)
                if 0 <= i_ < W and 0 <= j_ < H:
                    mx = max(mx, int(data[j_, i_]))
        print('  %-30s 둘레최대 %3d %s | 모서리→LETHAL: %s' % (label, mx, 'BLOCK' if mx >= 100 else '     ', '  '.join(s)))

    report('현재 자세', ryaw)
    report('현재 자세 +0.10 m 전진', ryaw, 0.10)
    report('현재 자세 +0.20 m 전진', ryaw, 0.20)
    if tan is not None:
        a = latest(mo, mo_t, T_COLL)
        tan_odom = tan - a[3]
        report('경로 접선 정렬(%+.1f°)' % math.degrees(tan_odom), tan_odom)
        report('경로 접선 정렬 +0.10 m', tan_odom, 0.10)
        report('경로 접선 정렬 +0.20 m', tan_odom, 0.20)
    dx_ = cx - rx; dy_ = cy - ry
    bx = dx_ * math.cos(ryaw) + dy_ * math.sin(ryaw); by = -dx_ * math.sin(ryaw) + dy_ * math.cos(ryaw)
    near = (bx > -0.3) & (bx < 0.8) & (np.abs(by) < 0.9)
    if near.any():
        L = by[near] > 0; R = by[near] < 0
        if L.any():
            k = np.argmin(by[near][L]); print('  차체 좌측 최근접 LETHAL: 횡 %+.2f (전방 %+.2f)' % (by[near][L][k], bx[near][L][k]))
        if R.any():
            k = np.argmax(by[near][R]); print('  차체 우측 최근접 LETHAL: 횡 %+.2f (전방 %+.2f)' % (by[near][R][k], bx[near][R][k]))
        # 전방 0.0~0.6 m 띠에서 좌우 LETHAL 사이 틈
        band = near & (bx > 0.0) & (bx < 0.6)
        if band.any():
            Lb = by[band][by[band] > 0]; Rb = by[band][by[band] < 0]
            print('  전방 0~0.6 m 띠: 좌측 LETHAL 최소 횡 %s, 우측 최대 횡 %s → 틈 %s (차폭+2패딩 = %.2f)'
                  % ('%+.2f' % Lb.min() if len(Lb) else '없음', '%+.2f' % Rb.max() if len(Rb) else '없음',
                     '%.2f' % (Lb.min() - Rb.max()) if len(Lb) and len(Rb) else '-', 2 * (HW + PAD)))
