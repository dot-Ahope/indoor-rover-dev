#!/usr/bin/env python3
"""전역 코스트맵·slam map 을 로버 기준 ASCII 로 출력 (전방 위쪽, 좌측 왼쪽)."""
import rclpy, math, time, tf2_ros, sys
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
rclpy.init(); n=Node('amap'); buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n); G={}
qos=QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL,reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(OccupancyGrid,'/global_costmap/costmap',lambda m:G.__setitem__('g',m),qos)
n.create_subscription(OccupancyGrid,'/map',lambda m:G.__setitem__('m',m),qos)
t=time.time(); p=None
while time.time()-t<10 and (len(G)<2 or p is None):
    rclpy.spin_once(n,timeout_sec=0.1)
    try:
        tr=buf.lookup_transform('map','base_link',rclpy.time.Time()).transform; q=tr.rotation
        p=(tr.translation.x,tr.translation.y,math.atan2(2*(q.w*q.z),1-2*q.z*q.z))
    except Exception: pass
if p is None or 'g' not in G: print("수신 실패"); raise SystemExit
def sym(v):
    if v is None: return ' '
    if v<0: return '?'
    if v>=100: return '#'
    if v>=99: return 'X'
    if v>0: return '+'
    return '.'
def probe(grid,x,y):
    i=grid.info; cx=int((x-i.origin.position.x)/i.resolution); cy=int((y-i.origin.position.y)/i.resolution)
    return grid.data[cy*i.width+cx] if 0<=cx<i.width and 0<=cy<i.height else None
ch,sh=math.cos(p[2]),math.sin(p[2])
print(f"로버 map=({p[0]:.2f},{p[1]:.2f}) hd={math.degrees(p[2]):.0f}°   (.=자유 +=비용 X=내접 #=치명 ?=미지 R=로버)")
for name in ('g','m'):
    if name not in G: continue
    print(f"\n--- {'global_costmap' if name=='g' else 'slam /map'} --- (위=전방 2.4m, 아래=후방 0.6m, 좌우 ±1.2m, 0.1m 격자)")
    for fwd in [2.4-0.1*k for k in range(31)]:
        row=''
        for lat in [1.2-0.1*k for k in range(25)]:
            x=p[0]+fwd*ch-lat*sh; y=p[1]+fwd*sh+lat*ch
            row+= 'R' if (abs(fwd)<0.05 and abs(lat)<0.05) else sym(probe(G[name],x,y))
        print(f"{fwd:+5.1f} {row}")
