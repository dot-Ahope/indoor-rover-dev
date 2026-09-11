#!/usr/bin/env python3
"""로컬 costmap_raw(0~255)로 footprint 둘레 값을 본다 — behavior_server 의 충돌 검사와 같은 데이터.
   255(NO_INFORMATION)가 둘레에 있으면 BackUp/DriveOnHeading 이 'Collision Ahead' 로 즉시 실패한다."""
import math, time, rclpy, tf2_ros
from rclpy.node import Node
from nav2_msgs.msg import Costmap
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
HL, HW, PAD = 0.25, 0.165, 0.05
rclpy.init(); n = Node('raw284'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n); S = {}
qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(Costmap, '/local_costmap/costmap_raw', lambda m: S.__setitem__('c', m), qos)
t0 = time.time()
while time.time() - t0 < 15 and 'c' not in S: rclpy.spin_once(n, timeout_sec=0.1)
c = S['c']; md = c.metadata; frame = c.header.frame_id
t = buf.lookup_transform(frame, 'base_link', rclpy.time.Time()).transform; q = t.rotation
px, py, yaw = t.translation.x, t.translation.y, math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
print('frame %s  res %.3f  size %dx%d  origin (%.2f, %.2f)  로버 (%.3f, %.3f) hd %.1f°' % (frame, md.resolution, md.size_x, md.size_y, md.origin.position.x, md.origin.position.y, px, py, math.degrees(yaw)))
def cost(x, y):
    i = int((x - md.origin.position.x) / md.resolution); j = int((y - md.origin.position.y) / md.resolution)
    return c.data[j*md.size_x + i] if (0 <= i < md.size_x and 0 <= j < md.size_y) else -1
def perim(dx):
    co, si = math.cos(yaw), math.sin(yaw); L, W = HL+PAD, HW+PAD; vals = {}
    pts = []
    for k in range(13):
        s = k/12.0
        pts += [(-L+2*L*s, -W, '우변'), (-L+2*L*s, W, '좌변'), (-L, -W+2*W*s, '뒤'), (L, -W+2*W*s, '앞')]
    for fx, fy, side in pts:
        x = px + (dx+fx)*co - fy*si; y = py + (dx+fx)*si + fy*co
        v = cost(x, y); vals.setdefault(side, []).append(v)
    return vals
print('footprint 둘레 raw 값 (255=미지, 254=LETHAL, 253=inscribed):')
for dx in (0.0, -0.05, -0.10, -0.15, 0.10, 0.20):
    v = perim(dx); allv = [x for xs in v.values() for x in xs]
    print('  이동 %+.2f: 최대 %3d | 뒤 max %3d 255개수 %d | 좌변 max %3d 255개수 %d | 우변 max %3d 255개수 %d | 앞 max %3d'
          % (dx, max(allv), max(v['뒤']), v['뒤'].count(255), max(v['좌변']), v['좌변'].count(255), max(v['우변']), v['우변'].count(255), max(v['앞'])))
tot = sum(1 for x in c.data if x == 255); print('로컬 전체 셀 %d 중 255(미지) %d (%.0f%%)' % (len(c.data), tot, 100.0*tot/len(c.data)))
