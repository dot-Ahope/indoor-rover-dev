#!/usr/bin/env python3
"""로컬 코스트맵을 부채꼴로 훑어 x=0.9~1.3m 구간에서 로버 중심이 지날 수 있는 y 슬롯을 찾는다."""
import rclpy, math, time, tf2_ros
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
rclpy.init(); n=Node('fan'); buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n); got={}
qos=QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL,reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(OccupancyGrid,'/local_costmap/costmap',lambda m: got.__setitem__('g',m),qos)
t=time.time(); tr=None
while time.time()-t<10 and ('g' not in got or tr is None):
    rclpy.spin_once(n,timeout_sec=0.1)
    if 'g' in got and tr is None:
        try: tr=buf.lookup_transform(got['g'].header.frame_id,'base_link',rclpy.time.Time()).transform
        except Exception: pass
if 'g' not in got or tr is None: print("수신/TF 실패"); raise SystemExit
g=got['g']; info=g.info; q=tr.rotation; yaw=math.atan2(2*(q.w*q.z),1-2*q.z*q.z); bx,by=tr.translation.x,tr.translation.y
def cost(rx,ry):
    wx=bx+rx*math.cos(yaw)-ry*math.sin(yaw); wy=by+rx*math.sin(yaw)+ry*math.cos(yaw)
    cx=int((wx-info.origin.position.x)/info.resolution); cy=int((wy-info.origin.position.y)/info.resolution)
    return g.data[cy*info.width+cx] if 0<=cx<info.width and 0<=cy<info.height else -1
print("   y(m)   x=0.6 0.7 0.8 0.9 1.0 1.1 1.2 1.3   (.=자유 +=비용 #=치명 ?=범위밖)")
def sym(c): return '?' if c<0 else ('.' if c==0 else ('#' if c>=99 else '+'))
free_y=[]
for iy in range(12,-13,-1):
    y=iy*0.05; row=[cost(x,y) for x in (0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3)]
    mark=" ◀ 통과가능" if all(c==0 for c in row) else ""
    if mark: free_y.append(y)
    print(f"  {y:+.2f}    "+"   ".join(sym(c) for c in row)+mark)
print(f"\n전 구간 자유인 y: {[round(v,2) for v in free_y]}")
if free_y: print(f"→ 슬롯 중앙 y={sum(free_y)/len(free_y):+.2f}, 폭 {max(free_y)-min(free_y)+0.05:.2f}m")
