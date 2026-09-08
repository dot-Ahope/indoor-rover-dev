#!/usr/bin/env python3
"""local costmap 에서 depth 전용 관측점(−20°, 1.46m)이 마킹됐는지 확인 (정적, 주행 없음)."""
import rclpy, math, time, tf2_ros
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
rclpy.init(); n=Node('costchk'); buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n); got={}
qos=QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(OccupancyGrid,'/local_costmap/costmap',lambda m: got.__setitem__('g',m),qos)
t=time.time()
while time.time()-t<8 and ('g' not in got): rclpy.spin_once(n,timeout_sec=0.1)
if 'g' not in got: print("costmap 미수신"); raise SystemExit
g=got['g']; info=g.info
tr=None; t=time.time()
while tr is None and time.time()-t<10:
    rclpy.spin_once(n,timeout_sec=0.1)
    try: tr=buf.lookup_transform(g.header.frame_id,'base_link',rclpy.time.Time()).transform
    except Exception: pass
if tr is None: print("TF 실패(10s)"); raise SystemExit
q=tr.rotation; yaw=math.atan2(2*(q.w*q.z),1-2*q.z*q.z); bx,by=tr.translation.x,tr.translation.y
def cost_at(rx,ry):
    wx=bx+rx*math.cos(yaw)-ry*math.sin(yaw); wy=by+rx*math.sin(yaw)+ry*math.cos(yaw)
    cx=int((wx-info.origin.position.x)/info.resolution); cy=int((wy-info.origin.position.y)/info.resolution)
    if 0<=cx<info.width and 0<=cy<info.height: return g.data[cy*info.width+cx]
    return None
print(f"costmap {info.width}x{info.height} @ {info.resolution} m, frame {g.header.frame_id}")
for ang in (-20, 0, -12, 8):
    a=math.radians(ang); line=[]
    for rng in [0.6+0.05*k for k in range(19)]:   # 0.60~1.50 m, 5cm 간격
        c=cost_at(rng*math.cos(a), rng*math.sin(a)); line.append('.' if c==0 else ('#' if c is not None and c>=99 else ('+' if c is not None and c>0 else ' ')))
    print(f"  {ang:+4d}°  0.6m [{''.join(line)}] 1.5m   (.=자유 +=인플레이션 #=점유)")
