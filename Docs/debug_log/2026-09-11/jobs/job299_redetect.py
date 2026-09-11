#!/usr/bin/env python3
"""상자 재탐지 — 넓은 범위(x 0.3~2.0, 10점 이상)로 모든 낮은 클러스터를 나열하고, x 구간별 y-히스토그램을 찍는다."""
import time, math, numpy as np, rclpy, tf2_ros
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from rclpy.qos import qos_profile_sensor_data
rclpy.init(); n=Node('rd299'); buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n); S={}
n.create_subscription(PointCloud2,'/camera/camera/depth/color/points',lambda m:S.__setitem__('pc',m),qos_profile_sensor_data)
def Rq(q):
    w,x,y,z=q.w,q.x,q.y,q.z
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
t0=time.time()
while time.time()-t0<15 and 'pc' not in S: rclpy.spin_once(n,timeout_sec=0.1)
m=S['pc']
tw=time.time()
while time.time()-tw<15:
    try: t=buf.lookup_transform('base_link',m.header.frame_id,rclpy.time.Time()).transform; break
    except Exception: rclpy.spin_once(n,timeout_sec=0.1)
# 프레임 3개 누적 (점 밀도 확보)
frames=[]; t0=time.time(); S['pc']=None
while time.time()-t0<1.5 and len(frames)<3:
    rclpy.spin_once(n,timeout_sec=0.05)
    if S['pc'] is not None: frames.append(S['pc']); S['pc']=None
P=[]
for f in frames:
    off={x.name:x.offset for x in f.fields}; raw=np.frombuffer(f.data,dtype=np.uint8).reshape(-1,f.point_step)
    xyz=np.stack([raw[:,off[k]:off[k]+4].copy().view(np.float32).ravel() for k in ('x','y','z')],1); xyz=xyz[np.isfinite(xyz).all(1)]
    P.append(xyz@Rq(t.rotation).T+np.array([t.translation.x,t.translation.y,t.translation.z]))
P=np.concatenate(P); print('프레임 %d, 점 %d'%(len(frames),len(P)))
sel=P[(P[:,2]>0.05)&(P[:,2]<0.30)&(P[:,0]>0.3)&(P[:,0]<2.0)&(np.abs(P[:,1])<0.8)]
print('장애물층(z 0.05~0.30, x 0.3~2.0, |y|<0.8) 점 %d'%len(sel))
o=sel[np.argsort(sel[:,1])]; cl=[]; cur=[o[0]] if len(o) else []
for q in o[1:]:
    if q[1]-cur[-1][1]>0.08:
        if len(cur)>=10: cl.append(np.array(cur))
        cur=[q]
    else: cur.append(q)
if len(cur)>=10: cl.append(np.array(cur))
print('클러스터(y gap 0.08, ≥10점):')
for c in cl:
    print('  %4d점  x %.2f~%.2f (전면 %.2f)  y %+.2f~%+.2f (중앙 %+.2f)  z중앙 %.3f z최대 %.3f'%(len(c),c[:,0].min(),c[:,0].max(),np.percentile(c[:,0],5),c[:,1].min(),c[:,1].max(),np.median(c[:,1]),np.median(c[:,2]),c[:,2].max()))
print('x 구간별 y-히스토그램 (z 0.05~0.30, 10cm y-bin, 점수):')
for x0 in (0.6,0.8,1.0,1.2,1.4,1.6):
    q=sel[(sel[:,0]>=x0)&(sel[:,0]<x0+0.2)]
    h=np.histogram(q[:,1],bins=np.arange(-0.8,0.81,0.1))[0]
    print('  x %.1f~%.1f: '%(x0,x0+0.2)+' '.join('%3d'%v for v in h)+'   (y -0.8 → +0.8)')
# 바닥 높이 점검 (피치 오류로 상자가 z<0.05 로 눌렸는지)
fl=P[(P[:,0]>0.9)&(P[:,0]<1.5)&(np.abs(P[:,1])<0.2)]
if len(fl): print('x 0.9~1.5, |y|<0.2 전체 점 %d: z 5%% %.3f 50%% %.3f 95%% %.3f 최대 %.3f'%(len(fl),*np.percentile(fl[:,2],[5,50,95]),fl[:,2].max()))
