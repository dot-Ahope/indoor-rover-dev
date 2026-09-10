#!/usr/bin/env python3
"""상자 검출을 클러스터링으로 고치고, 그 자리의 코스트맵 비용을 직접 읽는다 (2026-09-10).

  왜: job125 의 detect_box 는 z 0.05~0.30 / |y|<0.5 안의 점을 **한 덩어리로 보고**
      median(y) 을 중심으로 삼았다. 이 범위에는 우측 벽(z중앙 0.26, 487점)이 상자
      (z중앙 0.07, 119점)보다 많이 들어와 중심이 벽으로 끌려간다. 거기에 fx 는
      5퍼센타일 x(=상자 쪽)를 써서, 벽의 y 와 상자의 x 를 조합한 **빈 자리**에
      사각형을 만들었다. 그 안의 점이 0 이 되는 것은 당연하다.
      → 정지 60초 측정(job209)에서 상자 깊이점은 253~275 로 완벽히 안정적이었다.
        "카메라가 근접 시 상자를 못 본다" 는 결론은 이 아티팩트였다.

  고침: y 축 1D 클러스터링(gap 0.08m)으로 덩어리를 나누고, 각 덩어리의 z 중앙값·점수로
        낮은 물체를 고른 뒤 **로버 진행축(y=0)에 가장 가까운** 것을 상자로 택한다.
  로버는 움직이지 않는다.
"""
import sys, time, math
import numpy as np
import rclpy, tf2_ros
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import OccupancyGrid
from rclpy.qos import qos_profile_sensor_data, QoSProfile, DurabilityPolicy, ReliabilityPolicy

rclpy.init(); n = Node('cl210')
buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
S = {}
qos_tl = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                    reliability=ReliabilityPolicy.RELIABLE)
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
    except Exception as e:
        print('  TF 실패:', e); return None
    off = {f.name: f.offset for f in m.fields}
    raw = np.frombuffer(m.data, dtype=np.uint8).reshape(-1, m.point_step)
    xyz = np.stack([raw[:, off[k]:off[k]+4].copy().view(np.float32).ravel()
                    for k in ('x', 'y', 'z')], axis=1)
    xyz = xyz[np.isfinite(xyz).all(axis=1)]
    return xyz @ Rq(tr.rotation).T + np.array([tr.translation.x, tr.translation.y, tr.translation.z])


def pose():
    t = buf.lookup_transform('map', 'base_link', rclpy.time.Time()).transform
    q = t.rotation
    return (t.translation.x, t.translation.y, math.atan2(2*(q.w*q.z), 1-2*q.z*q.z))


def clusters(sel, gap=0.08, minpts=25):
    """y 축 1D 클러스터링. sel 은 base_link 점군."""
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


t0 = time.time()
while time.time() - t0 < 15 and ('pc' not in S or 'lc' not in S or 'gc' not in S):
    rclpy.spin_once(n, timeout_sec=0.1)
for k in ('pc', 'lc', 'gc'):
    if k not in S:
        print('%s 수신 실패' % k); sys.exit(1)
# 카메라 정적 TF 대기 — /tf_static 전달이 늦으면 cloud() 가 통째로 None 이 된다(job125 주석 참조)
tw = time.time()
while time.time() - tw < 20:
    try:
        buf.lookup_transform('base_link', 'camera_depth_optical_frame', rclpy.time.Time())
        print('카메라 TF OK (%.1fs 대기)' % (time.time()-tw)); break
    except Exception:
        rclpy.spin_once(n, timeout_sec=0.1)
else:
    print('카메라 TF 없음 — base_link <- camera_depth_optical_frame'); sys.exit(1)

P = cloud('base_link')
p0 = pose()
print('로버 map (%.3f, %.3f) hd=%.1f°' % (p0[0], p0[1], math.degrees(p0[2])))
sel = P[(P[:, 2] > 0.05) & (P[:, 2] < 0.30) & (P[:, 0] > 0.5) & (P[:, 0] < 1.5) & (np.abs(P[:, 1]) < 0.5)]
print('job125 와 같은 범위의 점: %d개' % len(sel))
print('  → job125 방식 median(y) = %+.3f   (5퍼센타일 x = %.3f)'
      % (float(np.median(sel[:, 1])), float(np.percentile(sel[:, 0], 5))))
print()
cl = clusters(sel)
print('클러스터 %d개 (y축 gap 0.08m, 최소 25점)' % len(cl))
print('   #   점수   y중앙    y범위          x중앙   x최소   z중앙   |y|')
cands = []
for i, c in enumerate(cl):
    ym, xm, zm = np.median(c[:, 1]), np.median(c[:, 0]), np.median(c[:, 2])
    print('  %2d  %5d  %+.3f  %+.3f~%+.3f  %6.3f  %6.3f  %6.3f  %.3f'
          % (i, len(c), ym, c[:, 1].min(), c[:, 1].max(), xm,
             np.percentile(c[:, 0], 5), zm, abs(ym)))
    cands.append((abs(ym), i, c, ym, zm))
low = [t for t in cands if t[4] < 0.20]
print()
if not low:
    print('낮은 물체(z중앙<0.20) 클러스터 없음 — 상자를 못 찾음'); sys.exit(2)
low.sort()
_, bi, bc, by, bz = low[0]
bx = float(np.percentile(bc[:, 0], 5))
print('상자 선택 = 클러스터 #%d  (base_link 전면 x=%.3f, 중심 y=%+.3f, z중앙 %.3f, %d점)'
      % (bi, bx, by, bz, len(bc)))

c, s = math.cos(p0[2]), math.sin(p0[2])
BOX_W, BOX_D = 0.18, 0.11
cx_b, cy_b = bx + BOX_D/2, by
mx = p0[0] + cx_b*c - cy_b*s
my = p0[1] + cx_b*s + cy_b*c
print('상자 중심 map = (%.3f, %.3f)' % (mx, my))
print()


def cost_at(g, x, y):
    i = int((x - g.info.origin.position.x) / g.info.resolution)
    j = int((y - g.info.origin.position.y) / g.info.resolution)
    if 0 <= i < g.info.width and 0 <= j < g.info.height:
        return g.data[j*g.info.width + i]
    return None


print('=== 상자 자리 코스트맵 비용 (중심 ±0.10m 격자) ===')
for key, name in (('lc', '로컬'), ('gc', '전역')):
    g = S[key]
    vals = []
    for dx in (-0.10, -0.05, 0.0, 0.05, 0.10):
        row = []
        for dy in (-0.10, -0.05, 0.0, 0.05, 0.10):
            v = cost_at(g, mx+dx, my+dy)
            row.append(-1 if v is None else v)
        vals.append(row)
    arr = np.array(vals)
    print('  %s (해상도 %.3f):  최대 %d  중앙 %d' % (name, g.info.resolution, arr.max(), int(np.median(arr))))
    for r in vals:
        print('      ' + ' '.join('%4d' % v for v in r))
