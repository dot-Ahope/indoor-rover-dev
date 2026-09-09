#!/usr/bin/env python3
"""경로 생성 실패 진단 — 전역/로컬 코스트맵을 로버 전방 부채꼴로 훑어 어디가 막혔는지 본다."""
import math, sys, time, rclpy, tf2_ros
import numpy as np
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy

rclpy.init(); n = Node('probe131')
buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n); G = {}
qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: G.__setitem__('g', m), qos)
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: G.__setitem__('l', m), qos)
n.create_subscription(OccupancyGrid, '/map', lambda m: G.__setitem__('m', m), qos)


def pose(frame):
    try:
        t = buf.lookup_transform(frame, 'base_link', rclpy.time.Time()).transform
        q = t.rotation
        return (t.translation.x, t.translation.y, math.atan2(2*(q.w*q.z), 1-2*q.z*q.z))
    except Exception:
        return None


t0 = time.time()
while time.time()-t0 < 12 and (pose('map') is None or len(G) < 2):
    rclpy.spin_once(n, timeout_sec=0.1)
p = pose('map')
if p is None:
    print("TF 실패"); raise SystemExit(1)
print("로버 map (%.2f,%.2f) hd=%.1f°" % (p[0], p[1], math.degrees(p[2])))
for k, name in (('g', '전역'), ('l', '로컬'), ('m', 'SLAM맵')):
    if k in G:
        i = G[k].info
        print("  %s: %dx%d @%.3f, origin (%.2f,%.2f), frame %s"
              % (name, i.width, i.height, i.resolution, i.origin.position.x, i.origin.position.y,
                 G[k].header.frame_id))


def cost(key, x, y):
    if key not in G:
        return None
    g = G[key]; i = g.info
    if g.header.frame_id != 'map':
        try:
            t = buf.lookup_transform(g.header.frame_id, 'map', rclpy.time.Time()).transform
            q = t.rotation; th = math.atan2(2*(q.w*q.z), 1-2*q.z*q.z)
            c, s = math.cos(th), math.sin(th)
            x, y = t.translation.x + x*c - y*s, t.translation.y + x*s + y*c
        except Exception:
            return None
    cx = int((x-i.origin.position.x)/i.resolution); cy = int((y-i.origin.position.y)/i.resolution)
    if not (0 <= cx < i.width and 0 <= cy < i.height):
        return -9      # 범위 밖
    return g.data[cy*i.width+cx]


def sym(c):
    if c is None: return '?'
    if c == -9: return 'X'      # 코스트맵 범위 밖
    if c == -1: return 'u'      # 미탐사
    if c >= 99: return '#'
    if c >= 50: return '+'
    if c > 0:   return '-'
    return '.'


print("\n전방 부채꼴 (0.4m → 2.4m, 0.1m 간격). X=범위밖 u=미탐사 #=점유 +=고비용 -=저비용 .=자유")
print("        전역                        로컬                        SLAM맵")
for adeg in (-30, -20, -10, 0, 10, 20, 30):
    a = p[2] + math.radians(adeg)
    ch, sh = math.cos(a), math.sin(a)
    rows = []
    for key in ('g', 'l', 'm'):
        rows.append(''.join(sym(cost(key, p[0]+d*ch, p[1]+d*sh)) for d in np.arange(0.4, 2.45, 0.1)))
    print("  %+3d° %s  %s  %s" % (adeg, rows[0], rows[1], rows[2]))

for D in (1.20, 1.60):
    gx, gy = p[0] + D*math.cos(p[2]), p[1] + D*math.sin(p[2])
    print("\n목표 전방 %.2fm = map (%.2f,%.2f): 전역 %s, 로컬 %s, SLAM %s"
          % (D, gx, gy, cost('g', gx, gy), cost('l', gx, gy), cost('m', gx, gy)))
rclpy.shutdown()
