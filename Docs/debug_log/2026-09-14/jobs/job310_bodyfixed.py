#!/usr/bin/env python3
"""주행 bag 에서 '차체 고정점' 을 찾는다 (2026-09-14, 사용자 관찰: 우측 전방에 로버 이동과 무관하게 같은 거리에 찍히는 점).
  정지 측정으로는 정지 물체와 구분이 안 되므로 주행 bag 을 쓴다.
    (1) /scan: 각도 인덱스별 거리 σ — 로버가 ≥0.3 m 움직였는데 σ < 1 cm 이고 80 % 이상 스캔에 있으면 차체 고정 반환
    (2) /local_costmap/costmap: LETHAL 셀을 차체좌표(5 cm 반올림)로 옮겨 프레임 간 지속률 — 80 % 이상이면 차체 고정 마킹
  판정: 실제 물체라면 로버가 움직일 때 차체좌표가 변해야 한다. 변하지 않으면 자기반사/아티팩트다.
"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan
from collections import Counter

BAG = sys.argv[1]


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


r = rosbag2_py.SequentialReader()
r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
ob, scans, grids = [], [], []
static = {}
while r.has_next():
    topic, data, ts = r.read_next()
    t = ts * 1e-9
    if topic == '/tf':
        for tr in deserialize_message(data, TFMessage).transforms:
            if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                ob.append((tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
    elif topic == '/tf_static':
        for tr in deserialize_message(data, TFMessage).transforms:
            static[(tr.header.frame_id, tr.child_frame_id)] = (tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation))
    elif topic == '/scan':
        scans.append((t, deserialize_message(data, LaserScan)))
    elif topic == '/local_costmap/costmap':
        grids.append((t, deserialize_message(data, OccupancyGrid)))
ob.sort(); ob_t = [s[0] for s in ob]
lb = static.get(('base_link', scans[0][1].header.frame_id), (0.152, 0.0, math.pi)) if scans else (0.152, 0.0, math.pi)


def latest(t):
    i = bisect.bisect_right(ob_t, t) - 1
    return ob[i] if i >= 0 else None


path = 0.0
for a, b in zip(ob[:-1], ob[1:]):
    path += math.hypot(b[1] - a[1], b[2] - a[2])
yaw_span = math.degrees(max(s[3] for s in ob) - min(s[3] for s in ob)) if ob else 0
print('bag %s: 스캔 %d, 코스트맵 %d, odom 이동 경로 %.2f m, yaw 범위 %.0f°' % (BAG, len(scans), len(grids), path, yaw_span))
if path < 0.3:
    print('로버가 0.3 m 이상 움직이지 않았다 — 고정점 판정 불가')

# (1) 스캔 각도 인덱스별 거리 통계 (로버 이동 중 스캔만)
N = len(scans[0][1].ranges)
R = np.full((len(scans), N), np.nan)
for k, (t, s) in enumerate(scans):
    rr = np.array(s.ranges, dtype=float)
    ok = np.isfinite(rr) & (rr > s.range_min) & (rr < 2.0)
    R[k, ok] = rr[ok]
pres = np.mean(~np.isnan(R), axis=0)
sd = np.nanstd(R, axis=0); med = np.nanmedian(R, axis=0)
cand = np.where((pres >= 0.8) & (sd < 0.01))[0]
print('(1) /scan: 80 %% 이상 스캔에 있고 거리 σ < 1 cm 인 각도 인덱스: %d개' % len(cand))
print('    idx   각도(lidar)   차체 x     y     거리중앙  σ(m)    지속률')
s0 = scans[0][1]
groups = []
for i in cand:
    if groups and i - groups[-1][-1] <= 2:
        groups[-1].append(i)
    else:
        groups.append([i])
for g in groups:
    i = g[len(g) // 2]
    a = s0.angle_min + i * s0.angle_increment
    lx, ly = med[i] * math.cos(a), med[i] * math.sin(a)
    bx = lb[0] + lx * math.cos(lb[2]) - ly * math.sin(lb[2]); by = lb[1] + lx * math.sin(lb[2]) + ly * math.cos(lb[2])
    print('    %4d(%d빔) %+7.1f°     %+.3f  %+.3f   %.3f   %.4f   %3.0f%%' % (i, len(g), math.degrees(a), bx, by, med[i], sd[i], 100 * pres[i]))
if not groups:
    print('    없음 → 주행 중 차체좌표가 고정된 라이다 반환은 없다')
# 비교: 실제 정지 물체 예 — 지속률 80 % 이상이지만 σ 큰 인덱스 수
real = np.where((pres >= 0.8) & (sd >= 0.01))[0]
print('    (대조) 지속률 ≥80 %% 이지만 σ ≥ 1 cm 인 인덱스 %d개 — 정지 물체는 이동 중 거리가 변한다' % len(real))

# (2) 코스트맵 LETHAL 의 차체좌표 지속률
cnt = Counter(); nfr = 0
for t, g in grids:
    p = latest(t)
    if not p:
        continue
    nfr += 1
    res = g.info.resolution; ox, oy = g.info.origin.position.x, g.info.origin.position.y
    d = np.array(g.data, dtype=np.int16).reshape(g.info.height, g.info.width)
    jj, ii = np.where(d >= 100)
    X = ox + (ii + 0.5) * res; Y = oy + (jj + 0.5) * res
    dx, dy = X - p[1], Y - p[2]
    bx = dx * math.cos(p[3]) + dy * math.sin(p[3]); by = -dx * math.sin(p[3]) + dy * math.cos(p[3])
    seen = set()
    for x, y in zip(bx, by):
        if math.hypot(x, y) < 1.5:
            seen.add((round(x / 0.05) * 0.05, round(y / 0.05) * 0.05))
    for c in seen:
        cnt[c] += 1
fixed = [(c, k) for c, k in cnt.items() if k >= 0.8 * nfr]
print('(2) 로컬 코스트맵 %d프레임: 차체좌표(5 cm)에서 80 %% 이상 지속되는 LETHAL 셀 %d개' % (nfr, len(fixed)))
for (x, y), k in sorted(fixed, key=lambda z: -z[1])[:15]:
    print('    차체 (%+.2f, %+.2f)  %3.0f%%' % (x, y, 100 * k / nfr))
if not fixed:
    print('    없음 → 주행 중 차체에 붙어 다니는 LETHAL 마킹은 없다')
