#!/usr/bin/env python3
"""depth 가상스캔 vs 라이다 각도별 비교 (로버 기준각). 카메라는 라이다보다 x +0.080m 앞.
낮은 장애물 후보 = 깊이 range 가 (라이다 range − 0.08) 보다 0.15m 이상 짧은 방위."""
import rclpy, math, time, numpy as np
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
rclpy.init(); n=Node('dcmp'); got={}
def mk(k):
    def cb(m): got.setdefault(k,[]).append(m)
    return cb
n.create_subscription(LaserScan,'/camera/scan',mk('cam'),qos_profile_sensor_data)
n.create_subscription(LaserScan,'/scan',mk('lid'),qos_profile_sensor_data)
t=time.time()
while time.time()-t<4: rclpy.spin_once(n,timeout_sec=0.1)
def prof(msgs, yaw_off, maxr):
    P=np.full(360,np.nan)
    for m in msgs:
        r=np.asarray(m.ranges); a=m.angle_min+m.angle_increment*np.arange(len(r))+yaw_off
        ok=np.isfinite(r)&(r>m.range_min)&(r<maxr)
        idx=(np.degrees(a[ok])%360).astype(int)
        for i,v in zip(idx,r[ok]):
            if np.isnan(P[i]) or v<P[i]: P[i]=v
    return P
if 'cam' not in got or 'lid' not in got: print("수신 실패", list(got)); raise SystemExit
C=prof(got['cam'],0.0,1.5); L=prof(got['lid'],math.pi,12.0)
print(f"스캔 수 cam {len(got['cam'])} lid {len(got['lid'])}")
print("각도  depth   lidar-0.08  차이   (음수=깊이가 더 가까움)")
low=[]
for d in list(range(-36,37,4)):
    i=d%360; c=C[i]; l=L[i]
    if np.isnan(c) or np.isnan(l): print(f"{d:+4d}°  {'-' if np.isnan(c) else f'{c:.2f}':>5}   {'-' if np.isnan(l) else f'{l-0.08:.2f}':>5}"); continue
    diff=c-(l-0.08); flag=" ◀ 낮은 장애물 후보" if diff<-0.15 else ""
    print(f"{d:+4d}°  {c:5.2f}   {l-0.08:5.2f}   {diff:+.2f}{flag}")
    if diff<-0.15: low.append(d)
valid=np.isfinite(C).sum(); print(f"깊이 유효 방위 {valid}/79 (±39°)  낮은 장애물 후보 방위: {low}")
