#!/bin/bash
# 스크립트가 직접 제자리 회전(0.6rad/s, 15s) + 동시 TF주기 로깅. 넓은공간·가드.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - << 'PY'
import math, time, numpy as np, rclpy, tf2_ros
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
rclpy.init(); n=rclpy.create_node('rotlog')
buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n)
pub=n.create_publisher(Twist,'/cmd_vel',10)
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
clr=[None]; tyaw=[None]
def sc(m):
    r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r)); ok=np.isfinite(r)&(r>0.05)
    if ok.sum():
        th=a[ok]+LYAW; px=LX+r[ok]*np.cos(th); py=r[ok]*np.sin(th)
        dx=np.maximum.reduce([XMIN-px,np.zeros_like(px),px-XMAX]); dy=np.maximum.reduce([YMIN-py,np.zeros_like(py),py-YMAX])
        clr[0]=float(np.min(np.sqrt(dx*dx+dy*dy)))
def ocb(m):
    q=m.pose.pose.orientation; tyaw[0]=math.atan2(2*(q.w*q.z),1-2*q.z*q.z)
n.create_subscription(LaserScan,'/scan',sc,qos_profile_sensor_data)
n.create_subscription(Odometry,'/odometry/filtered',ocb,qos_profile_sensor_data)
def tf(a,b):
    try:
        t=buf.lookup_transform(a,b,rclpy.time.Time()).transform; q=t.rotation
        return (round(t.translation.x,4),round(t.translation.y,4),round(math.atan2(2*(q.w*q.z),1-2*q.z*q.z),4))
    except Exception: return None
t0=time.time()
while (clr[0] is None or tyaw[0] is None) and time.time()<t0+3: rclpy.spin_once(n,timeout_sec=0.1)
print("15초 제자리 회전 + TF 로깅 시작...")
tw=Twist(); tw.angular.z=0.6
last_o=None; last_m=None; o_ch=[]; m_ch=[]; to=t0=time.time(); tm=t0; yaws=[]; ABORT=False
while time.time()-t0<15:
    pub.publish(tw); rclpy.spin_once(n,timeout_sec=0.02); now=time.time()
    if clr[0] is not None and clr[0]<0.05: print(f"가드 {clr[0]*100:.0f}cm 정지"); ABORT=True; break
    o=tf('odom','base_link'); m=tf('map','odom')
    if o and o!=last_o:
        if last_o is not None: o_ch.append(now-to)
        to=now; last_o=o
    if m and m!=last_m:
        if last_m is not None: m_ch.append(now-tm)
        tm=now; last_m=m
    if tyaw[0] is not None: yaws.append(tyaw[0])
t=Twist()
for _ in range(15): pub.publish(t); time.sleep(0.02)
import statistics as st
def summ(nm,ch):
    if ch: print(f"  {nm}: 변화 {len(ch)}회, 간격 평균={st.mean(ch)*1000:.0f}ms 최대={max(ch)*1000:.0f}ms")
    else: print(f"  {nm}: 변화 없음(고정)")
print(f"=== 결과 (중단={ABORT}) ===")
if yaws:
    # unwrap해서 총 회전량
    uw=np.unwrap(yaws); print(f"  /odometry/filtered yaw 총 변화 = {math.degrees(uw[-1]-uw[0]):.0f}deg (실제 회전 확인)")
summ("odom->base (로봇 TF)", o_ch)
summ("map->odom (slam 보정)", m_ch)
rclpy.shutdown()
PY
