#!/usr/bin/env python3
"""nvblox 감쇠 정지 측정 (09-22 §2): 슬라이스에서 상자 구역(base x 0.9~1.5, y −0.35~+0.15)의 ≤0 셀 수·최소 거리·미지/자유 셀 수를 1 초마다 찍는다.
  호스트에서 실행(nvblox_msgs 호스트 빌드). 인자: NAME BX BY SEC. 로버 정지 가정 → TF 는 처음 한 번만 조회.
  깊이 입력을 끊은 뒤(enable_depth false) 상자 셀이 사라지는 시각 = ESDF 이탈(가중 < min_weight), 자유가 되는 시각 = 완전 감쇠(decayed_free_distance)."""
import sys, time, math
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
import tf2_ros
from nvblox_msgs.msg import DistanceMapSlice
NAME, BX, BY, SEC = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
rclpy.init(); n = Node('decay506'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
S = {}
n.create_subscription(DistanceMapSlice, '/nvblox_node/static_map_slice', lambda m: S.__setitem__('m', m), qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < 10 and 'm' not in S: rclpy.spin_once(n, timeout_sec=0.1)
if 'm' not in S: print('슬라이스 없음'); sys.exit(1)
fr = S['m'].header.frame_id; P = None
while time.time() - t0 < 15 and P is None:
    try:
        t = buf.lookup_transform(fr, 'base_link', rclpy.time.Time()).transform; q = t.rotation
        P = (t.translation.x, t.translation.y, math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z)))
    except Exception: rclpy.spin_once(n, timeout_sec=0.1)
if P is None: print('TF 없음'); sys.exit(1)
px, py, pth = P; c, s = math.cos(-pth), math.sin(-pth)
print('==== %s: 프레임 %s, 상자 hint %.3f/%.3f, %d s' % (NAME, fr, BX, BY, SEC)); print('  t(s)  ≤0셀  최소거리  미지  자유  | 상자 구역 셀 수 기준')
first_zero = None; first_free = None; base_free = None; tstart = time.time(); last = -1
while time.time() - tstart < SEC:
    rclpy.spin_once(n, timeout_sec=0.05)
    el = time.time() - tstart
    if int(el) == last or 'm' not in S: continue
    last = int(el); m = S['m']
    d = np.asarray(m.data, dtype=np.float32).reshape(m.height, m.width); jj, ii = np.indices(d.shape)
    X = m.origin.x + (ii + 0.5) * m.resolution - px; Y = m.origin.y + (jj + 0.5) * m.resolution - py
    rx = X * c - Y * s; ry = X * s + Y * c
    box = (rx > 0.9) & (rx < 1.5) & (ry > -0.35) & (ry < 0.15)
    v = d[box]; unk = v == m.unknown_value; ob = (~unk) & (v <= 0); fre = (~unk) & (v > 0)
    mn = float(v[~unk].min()) if (~unk).any() else float('nan')
    print('  %4d  %4d  %7.2f  %4d  %4d' % (last, ob.sum(), mn, unk.sum(), fre.sum()), flush=True)
    if base_free is None: base_free = int(fre.sum())
    if first_zero is None and ob.sum() == 0 and last > 0: first_zero = last
    if first_free is None and fre.sum() > base_free + 5 and last > 0: first_free = last
print('==== 상자 ≤0 셀이 0 이 된 시각: %s s | 자유 셀이 늘기 시작한 시각: %s s (깊이 차단은 t=5 s)' % (first_zero, first_free))
rclpy.shutdown()
