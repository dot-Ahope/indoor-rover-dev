#!/usr/bin/env python3
"""N3 정지 A/B 보조 (2026-09-21): 로컬 코스트맵(OccupancyGrid)과 nvblox 슬라이스를 base_link 기준 10 cm ASCII 지도로 찍어 어디가 LETHAL/미지인지 본다. 인자: NAME [SLICE=1]
  코스트맵 값: 100 LETHAL '#', 99 내접 'o', 1~98 '.', 0 ' ', -1 미지 '?'.  슬라이스: 거리≤0 '#', 미지 '?', 그 외 ' '.  범위 x −0.5~2.0, y +1.0~−1.0(위가 왼쪽).
"""
import sys, time, math
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy, qos_profile_sensor_data
from nav_msgs.msg import OccupancyGrid
import tf2_ros
NAME = sys.argv[1] if len(sys.argv) > 1 else 'grid'; DO_SLICE = (sys.argv[2] if len(sys.argv) > 2 else '1') == '1'
TOPIC = sys.argv[3] if len(sys.argv) > 3 else '/local_costmap/costmap'   # 09-22 N6-1: 전역은 /global_costmap/costmap(map 프레임, TF map←base_link)
if DO_SLICE:
    from nvblox_msgs.msg import DistanceMapSlice
rclpy.init(); n = Node('gridcmp489'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
S = {}
qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(OccupancyGrid, TOPIC, lambda m: S.__setitem__('cm', m), qos)
if DO_SLICE:
    n.create_subscription(DistanceMapSlice, '/nvblox_node/static_map_slice', lambda m: S.__setitem__('sl', m), qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < 12 and ('cm' not in S or (DO_SLICE and 'sl' not in S)):
    rclpy.spin_once(n, timeout_sec=0.1)
t1 = time.time()   # TF 버퍼 채우기(odom→base_link 는 30 Hz, 첫 조회가 너무 이르면 실패)
while time.time() - t1 < 4 and not buf.can_transform(S['cm'].header.frame_id if 'cm' in S else 'odom', 'base_link', rclpy.time.Time()):
    rclpy.spin_once(n, timeout_sec=0.1)


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def pose_in(frame):
    for _ in range(50):
        try:
            t = buf.lookup_transform(frame, 'base_link', rclpy.time.Time()).transform
            return t.translation.x, t.translation.y, yaw_of(t.rotation)
        except Exception:
            rclpy.spin_once(n, timeout_sec=0.1)
    return None


def ascii_map(X, Y, ch, title):
    """base_link 좌표 점들을 10 cm 격자 문자로."""
    xs = np.arange(-0.5, 2.01, 0.1); ys = np.arange(1.0, -1.01, -0.1)
    g = [[' '] * len(xs) for _ in ys]
    pri = {'#': 4, 'o': 3, '?': 2, '.': 1, ' ': 0}
    for x, y, c in zip(X, Y, ch):
        i = int(round((x + 0.5) / 0.1)); j = int(round((1.0 - y) / 0.1))
        if 0 <= i < len(xs) and 0 <= j < len(ys) and pri[c] > pri[g[j][i]]:
            g[j][i] = c
    print(title); print('      x: ' + ''.join(('%d' % (int(round(abs(x) * 10)) % 10)) for x in xs) + '  (−0.5 … 2.0, 0.1 m)')
    for j, y in enumerate(ys):
        print('  y%+.1f |%s|' % (y, ''.join(g[j])))


if 'cm' in S:
    m = S['cm']; p = pose_in(m.header.frame_id)
    if p:
        px, py, pth = p; d = np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width)
        jj, ii = np.indices(d.shape); X = m.info.origin.position.x + (ii + 0.5) * m.info.resolution - px; Y = m.info.origin.position.y + (jj + 0.5) * m.info.resolution - py
        c, s = math.cos(-pth), math.sin(-pth); rx = (X * c - Y * s).ravel(); ry = (X * s + Y * c).ravel(); v = d.ravel()
        ch = np.where(v >= 100, '#', np.where(v == 99, 'o', np.where(v < 0, '?', np.where(v > 0, '.', ' '))))
        print('==== %s 로컬 코스트맵 %dx%d @%.2f: LETHAL %d, 내접 %d, 미지 %d, 비용>0 %d' % (NAME, m.info.width, m.info.height, m.info.resolution, (v >= 100).sum(), (v == 99).sum(), (v < 0).sum(), ((v > 0) & (v < 99)).sum()))
        ascii_map(rx, ry, ch, '  코스트맵 (# LETHAL, o 내접, . 비용, ? 미지)')
        lt = (v >= 100) & (rx > 0.3) & (rx < 1.6) & (np.abs(ry) < 0.9)
        print('  앞 0.3~1.6 m LETHAL 셀 %d: y 분포 ' % lt.sum() + ' '.join('%+.1f:%d' % (yb, ((ry[lt] >= yb) & (ry[lt] < yb + 0.2)).sum()) for yb in np.arange(-0.9, 0.9, 0.2)))
        import json   # 09-21: 시각화용 원자료(base_link 좌표, 5 cm 셀) — 코스트맵 전체 값
        json.dump({'res': m.info.resolution, 'cells': [[round(float(a), 3), round(float(b), 3), int(c)] for a, b, c in zip(rx, ry, v) if c != 0]}, open('/tmp/grid_%s_costmap.json' % NAME, 'w'))
    else:
        print('코스트맵 TF 없음')
else:
    print('코스트맵 수신 없음')
if DO_SLICE and 'sl' in S:
    m = S['sl']; p = pose_in(m.header.frame_id)
    if p:
        px, py, pth = p; d = np.asarray(m.data, dtype=np.float32).reshape(m.height, m.width)
        jj, ii = np.indices(d.shape); X = m.origin.x + (ii + 0.5) * m.resolution - px; Y = m.origin.y + (jj + 0.5) * m.resolution - py
        c, s = math.cos(-pth), math.sin(-pth); rx = (X * c - Y * s).ravel(); ry = (X * s + Y * c).ravel(); v = d.ravel()
        unk = v == m.unknown_value; ob = (~unk) & (v <= 0.0)
        ch = np.where(ob, '#', np.where(unk, '?', ' '))
        print('==== %s nvblox 슬라이스 %dx%d @%.2f (%s): 장애물(≤0) %d, 미지 %d, 자유 %d | 거리 최소 %.2f 최대 %.2f' % (NAME, m.width, m.height, m.resolution, m.header.frame_id, ob.sum(), unk.sum(), ((~unk) & (v > 0)).sum(), v[~unk].min() if (~unk).any() else 0, v[~unk].max() if (~unk).any() else 0))
        ascii_map(rx, ry, ch, '  슬라이스 (# 거리≤0, ? 미지)')
        import json
        json.dump({'res': m.resolution, 'cells': [[round(float(a), 3), round(float(b), 3), (None if u else round(float(c), 3))] for a, b, c, u in zip(rx, ry, v, unk)]}, open('/tmp/grid_%s_slice.json' % NAME, 'w'))
rclpy.shutdown()
