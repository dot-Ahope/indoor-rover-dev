#!/usr/bin/env python3
"""전역 코스트맵 진단: 목표 주변 비용/미지영역, 로버→목표 직선의 셀 상태."""
import rclpy, math, time, tf2_ros
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
rclpy.init(); n=Node('gdiag'); buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n); G={}
qos=QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL,reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(OccupancyGrid,'/global_costmap/costmap',lambda m: G.__setitem__('g',m),qos)
n.create_subscription(OccupancyGrid,'/map',lambda m: G.__setitem__('m',m),qos)
t=time.time(); p=None
while time.time()-t<10 and (len(G)<2 or p is None):
    rclpy.spin_once(n,timeout_sec=0.1)
    try:
        tr=buf.lookup_transform('map','base_link',rclpy.time.Time()).transform; q=tr.rotation
        p=(tr.translation.x,tr.translation.y,math.atan2(2*(q.w*q.z),1-2*q.z*q.z))
    except Exception: pass
if 'g' not in G or p is None: print("수신 실패",list(G)); raise SystemExit
def probe(grid,x,y):
    i=grid.info; cx=int((x-i.origin.position.x)/i.resolution); cy=int((y-i.origin.position.y)/i.resolution)
    return grid.data[cy*i.width+cx] if 0<=cx<i.width and 0<=cy<i.height else None
g=G['g']; i=g.info
print(f"global costmap {i.width}x{i.height} @{i.resolution:.2f} origin=({i.origin.position.x:.2f},{i.origin.position.y:.2f}) frame={g.header.frame_id}")
if 'm' in G:
    mi=G['m'].info; print(f"slam /map      {mi.width}x{mi.height} @{mi.resolution:.2f} origin=({mi.origin.position.x:.2f},{mi.origin.position.y:.2f})")
vals=[v for v in g.data]
from collections import Counter
c=Counter(vals); print(f"전역 셀 분포: 미지(-1) {c[-1]}  자유(0) {c[0]}  치명(≥99) {sum(v for k,v in c.items() if k>=99 and k!=-1) and sum(n_ for k,n_ in c.items() if k>=99)}  기타 {len(vals)-c[-1]-c[0]-sum(n_ for k,n_ in c.items() if k>=99)}")
print(f"\n로버({p[0]:.2f},{p[1]:.2f}) → 목표(1.60,0.00) 직선상 전역 비용 (로버 헤딩 기준 전방):")
ch,sh=math.cos(p[2]),math.sin(p[2])
for d in [0.2*k for k in range(0,10)]:
    x=p[0]+d*ch; y=p[1]+d*sh
    v=probe(g,x,y); vm=probe(G['m'],x,y) if 'm' in G else None
    print(f"  전방 {d:.1f}m ({x:+.2f},{y:+.2f}) 전역={v}  map={vm}")
print("\n목표(1.60,0) 주변 ±0.3m 전역 비용:")
for dy in (0.3,0.15,0.0,-0.15,-0.3):
    row=[probe(g,1.6+dx,dy) for dx in (-0.2,0.0,0.2)]
    print(f"  y={dy:+.2f}: x=1.4→{row[0]}  1.6→{row[1]}  1.8→{row[2]}")
