#!/bin/bash
# 회전 방해물 방위 진단 (무동작): 30도 섹터별 중심기준 최소거리
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - << 'PY'
import math, numpy as np, rclpy, time
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
LX,LYAW=0.152,math.pi; XMAX,YMAX=0.25,0.165
SWEEP=math.hypot(XMAX,YMAX)
rclpy.init(); n=rclpy.create_node('w'); acc=[]
def cb(m):
    if len(acc)<5: acc.append(m)
n.create_subscription(LaserScan,'/scan',cb,qos_profile_sensor_data)
t0=time.time()
while len(acc)<5 and time.time()<t0+6: rclpy.spin_once(n,timeout_sec=0.1)
if not acc: print("NO /scan"); raise SystemExit
PX=[];PY=[]
for m in acc:
    r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r))
    ok=np.isfinite(r)&(r>0.05)&(r<12); th=a[ok]+LYAW
    PX.append(LX+r[ok]*np.cos(th)); PY.append(r[ok]*np.sin(th))
px=np.concatenate(PX); py=np.concatenate(PY)
dc=np.hypot(px,py); ang=np.degrees(np.arctan2(py,px))
print(f"스윕 반경(필요) = {SWEEP*100:.0f}cm  (이보다 가까우면 회전 시 충돌)")
print("방위별 중심기준 최소거리 (로버 기준, 0=정면 / +=좌 / -=우):")
names={0:'정면',30:'좌30',60:'좌60',90:'좌(90)',120:'좌후120',150:'좌후150',
       180:'후면',-150:'우후150',-120:'우후120',-90:'우(90)',-60:'우60',-30:'우30'}
worst=[]
for c in [0,30,60,90,120,150,180,-150,-120,-90,-60,-30]:
    d=np.abs(((ang-c+180)%360)-180); mk=d<15
    if mk.any():
        v=float(np.min(dc[mk]))
        flag='  ← 회전 방해!' if v<SWEEP+0.05 else ''
        print(f"  {names[c]:>7s} : {v*100:5.0f}cm{flag}")
        if v<SWEEP+0.05: worst.append((names[c],v))
    else:
        print(f"  {names[c]:>7s} :   (점없음)")
i=int(np.argmin(dc))
print(f"\n최근접: {dc[i]*100:.0f}cm, 방위 {ang[i]:+.0f}도 ({'좌' if ang[i]>0 else '우'}쪽)")
if worst:
    print(f"→ 치우거나 로버를 옮겨야 할 방향: {', '.join(w[0] for w in worst)}")
else:
    print("→ 회전 가능")
rclpy.shutdown()
PY
