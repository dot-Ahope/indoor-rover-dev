#!/usr/bin/env python3
"""RPP 가 무엇과 충돌한다고 보는지 찾는다 (2026-09-11).

  증상: BT 를 ClearCostmapExceptRegion 으로 고친 뒤 로컬이 상자를 유지하게 됐지만,
        RPP 가 출발부터 "collision ahead" 를 내고 BackUp 마저 "Collision Ahead" 로 실패한다.
        앞뒤가 모두 막혔다는 뜻이므로, 상자만의 문제가 아닐 수 있다.

  방법: 로버 현재 자세에서 footprint(+padding) 를 코스트맵에 투영해
        - 차체 안에 내접비용(발행 99 = raw 253) 셀이 있는지
        - 전방/후방 투영 경로에 어디서 처음 막히는지
        를 직접 센다. 로버는 움직이지 않는다.
"""
import math
import time
import rclpy
import tf2_ros
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan
from rclpy.qos import qos_profile_sensor_data, QoSProfile, DurabilityPolicy, ReliabilityPolicy

HL, HW = 0.25, 0.165
PAD = 0.05
INSCRIBED_PUB = 99          # Costmap2DPublisher 에서 raw 253 -> 99
# 2026-09-11 정정: RPP inCollision() 은 footprint 둘레 최대비용 >= LETHAL(254 = 발행 100) 일 때만
#   충돌이다. inscribed(99)는 '중심이 여기면 충돌' 이라 이미 반경이 반영된 값 — footprint 를
#   투영하면서 99 를 쓰면 반경을 두 번 센다. 이 오류로 "통과 불가" 를 잘못 판정했다(job247).
LETHAL_PUB = 100

rclpy.init()
n = Node('why228')
buf = tf2_ros.Buffer()
tl = tf2_ros.TransformListener(buf, n)
S = {}
qos_tl = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                    reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(OccupancyGrid, '/local_costmap/costmap',
                      lambda m: S.__setitem__('lc', m), qos_tl)
n.create_subscription(LaserScan, '/scan', lambda m: S.__setitem__('sc', m),
                      qos_profile_sensor_data)


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


t0 = time.time()
while time.time() - t0 < 25 and (pose() is None or 'lc' not in S or 'sc' not in S):
    rclpy.spin_once(n, timeout_sec=0.1)
p = pose()
if p is None or 'lc' not in S:
    print('TF/코스트맵 준비 실패 (map 프레임은 로버가 멈춰 있으면 늦게 온다)')
    raise SystemExit(1)
g = S['lc']
res = g.info.resolution
p = pose_in(g.header.frame_id)   # 로컬 코스트맵 frame(odom) 기준 자세
print('로버 %s (%.3f, %.3f) hd=%.2f deg' % (g.header.frame_id, p[0], p[1], math.degrees(p[2])))
print('로컬 코스트맵 %dx%d res %.3f origin (%.2f, %.2f)'
      % (g.info.width, g.info.height, res, g.info.origin.position.x, g.info.origin.position.y))
print()


def cost(mx, my):
    i = int((mx - g.info.origin.position.x) / res)
    j = int((my - g.info.origin.position.y) / res)
    if 0 <= i < g.info.width and 0 <= j < g.info.height:
        return g.data[j * g.info.width + i]
    return -128


def body_scan(dx, dy, dth):
    """차체를 (dx,dy,dth) 만큼 옮겼을 때 footprint(+pad) 안의 최대 비용과 그 위치."""
    th = p[2] + dth
    cx = p[0] + dx * math.cos(p[2]) - dy * math.sin(p[2])
    cy = p[1] + dx * math.sin(p[2]) + dy * math.cos(p[2])
    best, bp = -128, None
    L, W = HL + PAD, HW + PAD
    steps = 11
    for a in range(steps):
        for b in range(steps):
            lx = -L + 2*L*a/(steps-1)
            ly = -W + 2*W*b/(steps-1)
            mx = cx + lx*math.cos(th) - ly*math.sin(th)
            my = cy + lx*math.sin(th) + ly*math.cos(th)
            v = cost(mx, my)
            if v > best:
                best, bp = v, (lx, ly, mx, my)
    return best, bp


v0, bp0 = body_scan(0, 0, 0)
print('=== 제자리 (현재 자세) ===')
print('  footprint(+pad %.2f) 안 최대 비용 = %d  %s'
      % (PAD, v0, '<-- LETHAL, RPP 충돌' if v0 >= LETHAL_PUB else ('(inscribed 99 — RPP 는 충돌로 안 봄)' if v0 >= INSCRIBED_PUB else '')))
if bp0:
    print('    최대 지점: 차체좌표 (%.3f, %.3f)  map (%.3f, %.3f)' % bp0)
print()

print('=== 전진 투영 (차체를 앞으로 옮겨 본다) ===')
print('   전진(m)  footprint 최대비용   막히는가')
for d in [0.05*k for k in range(0, 13)]:
    v, bp = body_scan(d, 0, 0)
    flag = 'BLOCK' if v >= LETHAL_PUB else ('inscr' if v >= INSCRIBED_PUB else '')
    extra = ''
    if flag and bp:
        extra = '  차체좌표(%+.2f,%+.2f)' % (bp[0], bp[1])
    print('   %5.2f      %4d              %s%s' % (d, v, flag, extra))

print()
print('=== 후진 투영 ===')
print('   후진(m)  footprint 최대비용   막히는가')
for d in [0.05*k for k in range(0, 7)]:
    v, bp = body_scan(-d, 0, 0)
    flag = 'BLOCK' if v >= LETHAL_PUB else ('inscr' if v >= INSCRIBED_PUB else '')
    extra = ''
    if flag and bp:
        extra = '  차체좌표(%+.2f,%+.2f)' % (bp[0], bp[1])
    print('   %5.2f      %4d              %s%s' % (d, v, flag, extra))

print()
print('=== 제자리 회전 투영 ===')
print('   회전(deg)  footprint 최대비용   막히는가')
for a in range(-60, 61, 15):
    v, bp = body_scan(0, 0, math.radians(a))
    flag = 'BLOCK' if v >= LETHAL_PUB else ('inscr' if v >= INSCRIBED_PUB else '')
    print('   %+6d      %4d              %s' % (a, v, flag))

print()
print('=== 라이다 방위별 최근접 (차체 외곽 기준) ===')
sc = S.get('sc')
if sc:
    import numpy as np
    r = np.array(sc.ranges)
    ang = sc.angle_min + np.arange(len(r)) * sc.angle_increment
    ok = np.isfinite(r) & (r > sc.range_min) & (r < sc.range_max)
    r, ang = r[ok], ang[ok]
    for lo, hi, name in [(-15, 15, '정면'), (15, 60, '좌전'), (60, 120, '좌'),
                         (120, 165, '좌후'), (165, 180, '후'), (-180, -165, '후'),
                         (-165, -120, '우후'), (-120, -60, '우'), (-60, -15, '우전')]:
        m = (np.degrees(ang) >= lo) & (np.degrees(ang) < hi)
        if m.any():
            print('  %-5s %5.0f cm' % (name, 100*r[m].min()))
