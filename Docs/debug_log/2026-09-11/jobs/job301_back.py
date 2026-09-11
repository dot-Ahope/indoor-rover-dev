#!/usr/bin/env python3
"""원시 센서 스윕 게이트 후 현재 heading 그대로 직선 후진 D m, 그 뒤 face 0 는 별도."""
import sys, time, math, numpy as np, rclpy, tf2_ros
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, LaserScan
from geometry_msgs.msg import Twist
from rclpy.qos import qos_profile_sensor_data
D=float(sys.argv[1]) if len(sys.argv)>1 else 0.8
HL,HW,PAD,M=0.25,0.165,0.03,0.07
rclpy.init(); n=Node('b301'); buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n); S={}
n.create_subscription(PointCloud2,'/camera/camera/depth/color/points',lambda m:S.__setitem__('pc',m),qos_profile_sensor_data)
n.create_subscription(LaserScan,'/scan',lambda m:S.__setitem__('sc',m),qos_profile_sensor_data)
pub=n.create_publisher(Twist,'/cmd_vel',10)
def Rq(q):
    w,x,y,z=q.w,q.x,q.y,q.z
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def tfm(a,b):
    t=buf.lookup_transform(a,b,rclpy.time.Time()).transform; return Rq(t.rotation),np.array([t.translation.x,t.translation.y,t.translation.z])
t0=time.time()
while time.time()-t0<15 and ('sc' not in S or 'pc' not in S): rclpy.spin_once(n,timeout_sec=0.05)
tw=time.time()
while time.time()-tw<15:
    try: tfm('base_link',S['sc'].header.frame_id); tfm('base_link',S['pc'].header.frame_id); break
    except Exception: rclpy.spin_once(n,timeout_sec=0.1)
R,T=tfm('base_link',S['sc'].header.frame_id); sc=S['sc']; r=np.array(sc.ranges); ang=sc.angle_min+np.arange(len(r))*sc.angle_increment
ok=np.isfinite(r)&(r>sc.range_min)&(r<sc.range_max); L=np.stack([r[ok]*np.cos(ang[ok]),r[ok]*np.sin(ang[ok]),np.zeros(ok.sum())],1)@R.T+T
R,T=tfm('base_link',S['pc'].header.frame_id); m=S['pc']; off={f.name:f.offset for f in m.fields}
raw=np.frombuffer(m.data,dtype=np.uint8).reshape(-1,m.point_step); xyz=np.stack([raw[:,off[k]:off[k]+4].copy().view(np.float32).ravel() for k in ('x','y','z')],1); xyz=xyz[np.isfinite(xyz).all(1)]
P=xyz@R.T+T; dep=P[(P[:,2]>0.06)&(P[:,2]<0.40)]
x0,x1=-(D+HL+PAD+M),(HL+PAD+M); y0,y1=-(HW+PAD+M),(HW+PAD+M)
inl=L[(L[:,0]>x0)&(L[:,0]<x1)&(L[:,1]>y0)&(L[:,1]<y1)]; ind=dep[(dep[:,0]>x0)&(dep[:,0]<x1)&(dep[:,1]>y0)&(dep[:,1]<y1)]
rear=L[(L[:,0]<-0.2)&(np.abs(L[:,1])<0.4)]
print('스윕 사각형 x %.2f~%.2f y %.2f~%.2f: 라이다 %d점, 깊이 장애물점 %d점 | 후방 최근접 %.2f m'%(x0,x1,y0,y1,len(inl),len(ind),(-rear[:,0]).min() if len(rear) else -1))
if len(inl) or len(ind):
    pts=np.concatenate([inl,ind[:,:2] if len(ind) else np.zeros((0,2))]) if len(ind) else inl
    print('★ 후진 경로에 센서 점 — 중단. 위치(차체좌표): '+', '.join('(%+.2f,%+.2f)'%(a,b) for a,b in pts[:10]))
    sys.exit(1)
def pose():
    try:
        t=buf.lookup_transform('odom','base_link',rclpy.time.Time()).transform; return (t.translation.x,t.translation.y)
    except Exception: return None
tw=time.time()
while time.time()-tw<10 and pose() is None: rclpy.spin_once(n,timeout_sec=0.1)
p0=pose()
if p0 is None: print('★ odom->base_link TF 없음 — 후진하지 않음'); sys.exit(1)
# 2026-09-11: pose 가 None 이면 거리 판정이 안 돼 D/0.04+10 초까지 달렸다(0.8 요청에 1.13 m). 시간 상한을 D/0.04 로 고정.
cmd=Twist(); cmd.linear.x=-0.04; t0=time.time()
while time.time()-t0<D/0.04:
    rclpy.spin_once(n,timeout_sec=0.02); pub.publish(cmd); q=pose()
    if q and p0 and math.hypot(q[0]-p0[0],q[1]-p0[1])>=D: break
z=Twist()
for _ in range(5): pub.publish(z); time.sleep(0.05)
q=pose(); print('후진 %.3f m 완료'%(math.hypot(q[0]-p0[0],q[1]-p0[1]) if q and p0 else -1))
