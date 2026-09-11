#!/usr/bin/env python3
"""(1) 유령 띠 다중 프레임 감사: 30 프레임 동안 차체 좌측 띠(x -0.5~0.5, y +0.20~+0.35, z 0.06~0.40)에
    깊이 장애물점이 나타나는 빈도. 간헐 노이즈면 일부 프레임에만 나타난다.
(2) 원시 센서 스윕 게이트: 후진 경로 사각형(footprint+5cm, 뒤로 D m) 안에 라이다/깊이 장애물점이 없으면
(3) 후진 D m (cmd_vel 직접). RPP·코스트맵은 개입하지 않는다 — 코스트맵의 LETHAL 이 센서 근거 없음이 확인됐기 때문."""
import sys, time, math
import numpy as np
import rclpy, tf2_ros
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, LaserScan
from geometry_msgs.msg import Twist
from rclpy.qos import qos_profile_sensor_data
HL, HW, PAD, M = 0.25, 0.165, 0.05, 0.05
rclpy.init(); n = Node('g275'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
S = {'frames': []}
n.create_subscription(PointCloud2, '/camera/camera/depth/color/points', lambda m: S['frames'].append(m), qos_profile_sensor_data)
n.create_subscription(LaserScan, '/scan', lambda m: S.__setitem__('sc', m), qos_profile_sensor_data)
pub = n.create_publisher(Twist, '/cmd_vel', 10)
def Rq(q):
    w,x,y,z=q.w,q.x,q.y,q.z
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def tfm(a,b):
    t=buf.lookup_transform(a,b,rclpy.time.Time()).transform; return Rq(t.rotation), np.array([t.translation.x,t.translation.y,t.translation.z])
def cloud_b(m):
    R,T=tfm('base_link',m.header.frame_id); off={f.name:f.offset for f in m.fields}
    raw=np.frombuffer(m.data,dtype=np.uint8).reshape(-1,m.point_step)
    xyz=np.stack([raw[:,off[k]:off[k]+4].copy().view(np.float32).ravel() for k in ('x','y','z')],1)
    return xyz[np.isfinite(xyz).all(1)]@R.T+T
def pose():
    try:
        t=buf.lookup_transform('map','base_link',rclpy.time.Time()).transform; q=t.rotation
        return (t.translation.x,t.translation.y,math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z)))
    except Exception: return None
t0=time.time()
while time.time()-t0<15 and (pose() is None or 'sc' not in S or len(S['frames'])<2): rclpy.spin_once(n,timeout_sec=0.05)
try: tfm('base_link',S['frames'][-1].header.frame_id); tfm('base_link',S['sc'].header.frame_id)
except Exception as e: print('TF 실패',e); sys.exit(1)
# (1) 30 프레임 수집
S['frames']=[]; t0=time.time()
while time.time()-t0<3.0 and len(S['frames'])<30: rclpy.spin_once(n,timeout_sec=0.02)
fr=S['frames']; hits=0; per=[]
for m in fr:
    P=cloud_b(m); band=P[(P[:,0]>-0.5)&(P[:,0]<0.5)&(P[:,1]>0.20)&(P[:,1]<0.35)&(P[:,2]>0.06)&(P[:,2]<0.40)]
    per.append(len(band)); hits+= (len(band)>0)
print('(1) 유령 띠(x -0.5~0.5, y +0.20~+0.35, z 0.06~0.40) 깊이점: %d 프레임 중 %d 프레임에 존재, 프레임당 점수 %s'%(len(fr),hits,per))
band_all=np.concatenate([cloud_b(m) for m in fr]); bb=band_all[(band_all[:,0]>-0.5)&(band_all[:,0]<0.5)&(band_all[:,1]>0.20)&(band_all[:,1]<0.35)&(band_all[:,2]>0.06)&(band_all[:,2]<0.40)]
if len(bb): print('    누적 %d점, z 중앙 %.3f, z 최대 %.3f, x 범위 %.2f~%.2f'%(len(bb),np.median(bb[:,2]),bb[:,2].max(),bb[:,0].min(),bb[:,0].max()))
# (2) 스윕 게이트
p=pose(); D=math.hypot(p[0],p[1]); back=p[2]+math.pi; err=math.degrees((math.atan2(-p[1],-p[0])-back+math.pi)%(2*math.pi)-math.pi)
print('(2) 현재 (%.3f, %.3f) yaw %.1f°, 원점 %.3f m, 후진 방향 오차 %.1f°'%(p[0],p[1],math.degrees(p[2]),D,err))
if abs(err)>15: print('    ★ 후진 방향 어긋남 — 중단'); sys.exit(1)
R,T=tfm('base_link',S['sc'].header.frame_id); sc=S['sc']; r=np.array(sc.ranges); ang=sc.angle_min+np.arange(len(r))*sc.angle_increment
ok=np.isfinite(r)&(r>sc.range_min)&(r<sc.range_max); L=np.stack([r[ok]*np.cos(ang[ok]),r[ok]*np.sin(ang[ok]),np.zeros(ok.sum())],1)@R.T+T
P=cloud_b(fr[-1]); dep=P[(P[:,2]>0.06)&(P[:,2]<0.40)]
x0,x1=-(D+HL+PAD+M),HL+PAD+M; y0,y1=-(HW+PAD+M),(HW+PAD+M)
inl=L[(L[:,0]>x0)&(L[:,0]<x1)&(L[:,1]>y0)&(L[:,1]<y1)]; ind=dep[(dep[:,0]>x0)&(dep[:,0]<x1)&(dep[:,1]>y0)&(dep[:,1]<y1)]
print('    스윕 사각형 x %.2f~%.2f, y %.2f~%.2f: 라이다 %d점, 깊이 장애물점 %d점'%(x0,x1,y0,y1,len(inl),len(ind)))
ly=L[(L[:,0]>-0.3)&(L[:,0]<0.3)&(L[:,1]>0)]; print('    라이다 좌측(|x|<0.3) 최근접 %.2f m'%(ly[:,1].min() if len(ly) else -1))
if len(inl) or len(ind): print('    ★ 스윕 경로에 센서 점 — 중단'); sys.exit(1)
# (3) 후진
print('(3) 후진 %.3f m'%D)
p0=pose(); cmd=Twist(); cmd.linear.x=-0.04; t0=time.time()
while time.time()-t0<D/0.04+10:
    rclpy.spin_once(n,timeout_sec=0.02); pub.publish(cmd); q=pose()
    if q and math.hypot(q[0]-p0[0],q[1]-p0[1])>=D: break
z=Twist()
for _ in range(5): pub.publish(z); time.sleep(0.05)
q=pose(); print('    최종 (%.3f, %.3f) yaw %.1f°  원점 오차 %.3f m'%(q[0],q[1],math.degrees(q[2]),math.hypot(q[0],q[1])))
