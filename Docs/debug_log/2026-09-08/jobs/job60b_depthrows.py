#!/usr/bin/env python3
"""깊이 이미지 행 띠별 최소 거리 (정면 열 ±40px). 상자가 어느 행(=높이)에 나타나는지 확인."""
import rclpy, time, math, numpy as np
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, CameraInfo
rclpy.init(); n=Node('drows'); got={}
n.create_subscription(Image,'/camera/camera/depth/image_rect_raw',lambda m: got.__setitem__('img',m),qos_profile_sensor_data)
n.create_subscription(CameraInfo,'/camera/camera/depth/camera_info',lambda m: got.__setitem__('ci',m),qos_profile_sensor_data)
t=time.time()
while time.time()-t<6 and len(got)<2: rclpy.spin_once(n,timeout_sec=0.1)
if len(got)<2: print("수신 실패",list(got)); raise SystemExit
m=got['img']; ci=got['ci']; fy=ci.k[4]; cy=ci.k[5]; fx=ci.k[0]; cx=ci.k[2]
print(f"depth {m.width}x{m.height} {m.encoding}  fx={fx:.1f} fy={fy:.1f} cx={cx:.1f} cy={cy:.1f}")
d=np.frombuffer(m.data,dtype=np.uint16).reshape(m.height,m.width).astype(np.float32)/1000.0
CAM_Z=0.143
print("행 띠     피치(°)   정면열 최소거리(m)  그 거리에서의 높이(m)   유효%   [좌30° 최소 | 우30° 최소]")
c0=int(cx); L=int(cx - fx*math.tan(math.radians(30))); R=int(cx + fx*math.tan(math.radians(30)))
for r0 in range(int(cy)-100, int(cy)+161, 20):
    band=d[r0:r0+20, c0-40:c0+41]; v=band[(band>0.25)&(band<4.0)]
    pitch=math.degrees(math.atan((r0+10-cy)/fy))   # + = 아래
    if v.size==0: print(f"{r0:3d}-{r0+19:3d}  {pitch:+5.1f}     -"); continue
    mn=float(v.min()); z=CAM_Z - mn*math.tan(math.radians(pitch))
    def side(cc):
        b=d[r0:r0+20, max(0,cc-30):cc+31]; vv=b[(b>0.25)&(b<4.0)]; return f"{vv.min():.2f}" if vv.size else " -  "
    print(f"{r0:3d}-{r0+19:3d}  {pitch:+5.1f}     {mn:5.2f}            {z:+.3f}            {100*v.size/band.size:3.0f}%   [{side(L)} | {side(R)}]")
print(f"scan_height 50 → 행 {int(cy)-25}~{int(cy)+25} 만 사용 중")
