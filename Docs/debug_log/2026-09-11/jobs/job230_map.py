#!/usr/bin/env python3
"""로버 주변 로컬 코스트맵을 격자로 찍고, 같은 영역의 라이다·깊이 점을 겹쳐 본다 (2026-09-11).
   클리어 직후에도 차체 좌측 뒤(차체좌표 -0.18, +0.215)에 100(LETHAL)이 다시 찍힌다.
   라이다는 그 방향에 아무것도 없다고 하므로, 어느 센서가 찍는지 가른다. 로버는 정지."""
import math
import sys
import time
import numpy as np
import rclpy
import tf2_ros
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan, PointCloud2
from rclpy.qos import qos_profile_sensor_data, QoSProfile, DurabilityPolicy, ReliabilityPolicy

rclpy.init()
n = Node('map230')
buf = tf2_ros.Buffer()
tl = tf2_ros.TransformListener(buf, n)
S = {}
qos_tl = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                    reliability=ReliabilityPolicy.RELIABLE)
TOPIC = sys.argv[1] if len(sys.argv) > 1 else '/local_costmap/costmap'
n.create_subscription(OccupancyGrid, TOPIC, lambda m: S.__setitem__('lc', m), qos_tl)
n.create_subscription(OccupancyGrid, '/map', lambda m: S.__setitem__('sm', m), qos_tl)
n.create_subscription(LaserScan, '/scan', lambda m: S.__setitem__('sc', m),
                      qos_profile_sensor_data)
n.create_subscription(PointCloud2, '/camera/camera/depth/color/points',
                      lambda m: S.__setitem__('pc', m), qos_profile_sensor_data)


def pose_in(frame):
    """코스트맵 셀을 차체 좌표로 옮길 때는 **그 코스트맵의 frame_id**(로컬=odom, 전역=map) 기준 자세를 써야 한다.
    2026-09-11 정정: map 자세로 로컬(odom) 셀을 변환해 map->odom 보정(0.1~0.2 m)만큼 어긋난 '유령' 을 만들었다."""
    t = buf.lookup_transform(frame, 'base_link', rclpy.time.Time()).transform
    q = t.rotation
    return (t.translation.x, t.translation.y, math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z)))


def pose():
    try:
        t = buf.lookup_transform('map', 'base_link', rclpy.time.Time()).transform
        q = t.rotation
        return (t.translation.x, t.translation.y,
                math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z)))
    except Exception:
        return None


def Rq(q):
    w, x, y, z = q.w, q.x, q.y, q.z
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])


t0 = time.time()
while time.time() - t0 < 25 and (pose() is None or 'lc' not in S or 'sc' not in S):
    rclpy.spin_once(n, timeout_sec=0.1)
p = pose()
g = S.get('lc')
if p is None or g is None:
    print('준비 실패')
    raise SystemExit(1)
res = g.info.resolution
ox, oy = g.info.origin.position.x, g.info.origin.position.y
p = pose_in(g.header.frame_id)   # 그 코스트맵의 frame 기준 자세
print('대상 토픽: %s (frame %s)' % (TOPIC, g.header.frame_id))
print('로버 map (%.3f, %.3f) hd=%.2f deg' % (p[0], p[1], math.degrees(p[2])))

# 로버 중심 +-0.8m 격자 (차체 좌표계로 출력)
print()
print('=== 로컬 코스트맵 (차체 좌표계, 행=x 앞->뒤, 열=y 좌->우) ===')
print('    상단이 전방. .=0  -=1~50  +=51~98  I=99(내접)  X=100(LETHAL)  ?=미지')
hdr = '        '
ys = [round(-0.8 + 0.05*k, 3) for k in range(33)]
xs = [round(0.8 - 0.05*k, 3) for k in range(33)]


def sym(v):
    if v < 0:
        return '?'
    if v == 0:
        return '.'
    if v >= 100:
        return 'X'
    if v >= 99:
        return 'I'
    if v > 50:
        return '+'
    return '-'


co, si = math.cos(p[2]), math.sin(p[2])
print('        y=+0.8 ......... 0 ......... -0.8')
for lx in xs:
    row = ''
    for ly in ys[::-1]:
        mx = p[0] + lx*co - ly*si
        my = p[1] + lx*si + ly*co
        i = int((mx - ox) / res)
        j = int((my - oy) / res)
        v = g.data[j*g.info.width + i] if (0 <= i < g.info.width and 0 <= j < g.info.height) else -1
        row += sym(v)
    mark = ' <-- 차체 뒤끝' if abs(lx + 0.25) < 0.026 else (' <-- 차체 앞끝' if abs(lx - 0.25) < 0.026 else '')
    print('  x=%+.2f %s%s' % (lx, row, mark))

# 라이다 점을 차체 좌표로
print()
print('=== 라이다 점 중 차체 근처(반경 0.6m) ===')
sc = S.get('sc')
cnt = 0
if sc:
    try:
        tr = buf.lookup_transform('base_link', sc.header.frame_id, rclpy.time.Time()).transform
        R = Rq(tr.rotation)
        T = np.array([tr.translation.x, tr.translation.y, tr.translation.z])
        r = np.array(sc.ranges)
        ang = sc.angle_min + np.arange(len(r)) * sc.angle_increment
        ok = np.isfinite(r) & (r > sc.range_min) & (r < sc.range_max)
        pts = np.stack([r[ok]*np.cos(ang[ok]), r[ok]*np.sin(ang[ok]), np.zeros(ok.sum())], axis=1)
        pb = pts @ R.T + T
        near = pb[np.hypot(pb[:, 0], pb[:, 1]) < 0.6]
        cnt = len(near)
        print('  %d개' % cnt)
        for q in near[:12]:
            print('    차체좌표 (%+.3f, %+.3f)  거리 %.3f' % (q[0], q[1], math.hypot(q[0], q[1])))
    except Exception as e:
        print('  라이다 TF 실패:', e)
if cnt == 0:
    print('  없음 — 라이다는 차체 반경 0.6m 안에 아무것도 안 본다')

# 깊이 점 중 차체 뒤쪽
print()
print('=== 깊이 점 중 차체 뒤쪽(x<0) 또는 좌측 0.6m 안 ===')
if 'pc' in S:
    m = S['pc']
    try:
        tr = buf.lookup_transform('base_link', m.header.frame_id, rclpy.time.Time()).transform
        off = {f.name: f.offset for f in m.fields}
        raw = np.frombuffer(m.data, dtype=np.uint8).reshape(-1, m.point_step)
        xyz = np.stack([raw[:, off[k]:off[k]+4].copy().view(np.float32).ravel()
                        for k in ('x', 'y', 'z')], axis=1)
        xyz = xyz[np.isfinite(xyz).all(axis=1)]
        pb = xyz @ Rq(tr.rotation).T + np.array(
            [tr.translation.x, tr.translation.y, tr.translation.z])
        back = pb[(pb[:, 0] < 0.0) & (np.hypot(pb[:, 0], pb[:, 1]) < 0.8)]
        print('  차체 뒤쪽 깊이점: %d개' % len(back))
        left = pb[(pb[:, 1] > 0.1) & (np.hypot(pb[:, 0], pb[:, 1]) < 0.6)
                  & (pb[:, 2] > 0.05) & (pb[:, 2] < 0.5)]
        print('  좌측 0.6m 안 장애물높이 깊이점: %d개' % len(left))
        if len(left):
            print('    예: ', [(round(float(q[0]), 2), round(float(q[1]), 2), round(float(q[2]), 2))
                              for q in left[:6]])
    except Exception as e:
        print('  깊이 TF 실패:', e)


# slam 정적 지도(/map)에서 같은 영역을 본다 — static_layer 가 옛 장애물을 들고 있는지
sm = S.get('sm')
print()
if sm is None:
    print('=== /map 수신 못함 ===')
else:
    print('=== slam 정적 지도(/map) 같은 영역 ===')
    print('    .=free(0)  -=1~49  +=50~99  X=100(occupied)  ?=미지(-1)')
    smres = sm.info.resolution
    sox, soy = sm.info.origin.position.x, sm.info.origin.position.y

    def ssym(v):
        if v < 0:
            return '?'
        if v == 0:
            return '.'
        if v >= 100:
            return 'X'
        if v >= 50:
            return '+'
        return '-'

    for lx in xs:
        row = ''
        for ly in ys[::-1]:
            mx = p[0] + lx*co - ly*si
            my = p[1] + lx*si + ly*co
            i = int((mx - sox) / smres)
            j = int((my - soy) / smres)
            v = sm.data[j*sm.info.width + i] if (0 <= i < sm.info.width and 0 <= j < sm.info.height) else -1
            row += ssym(v)
        print('  x=%+.2f %s' % (lx, row))
