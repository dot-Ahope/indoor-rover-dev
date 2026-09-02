#!/bin/bash
# foxglove 끄고 CPU 확보 후, 스크립트 회전 중 map->odom 갱신되는지 확인.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== foxglove_bridge 종료 ==="
pkill -f foxglove; sleep 4
echo "  load(foxglove off): $(cat /proc/loadavg | cut -d' ' -f1-3)"
python3 - << 'PY'
import math, time, numpy as np, rclpy, tf2_ros
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
rclpy.init(); n=rclpy.create_node('fg')
buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n)
pub=n.create_publisher(Twist,'/cmd_vel',10)
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
clr=[None]; tyaw=[None]
def sc(m):
    r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r)); ok=np.isfinite(r)&(r>0.05)
    if ok.sum():
        th=a[ok]+LYAW; px=LX+r[ok]*np.cos(th); py=r[ok]*np.sin(th)
        dx=np.maximum.reduce([XMIN-px,np.zeros_like(px),px-XMAX]); dy=np.maximum.reduce([YMIN-py,np.zeros_like(py),py-YMAX]); clr[0]=float(np.min(np.sqrt(dx*dx+dy*dy)))
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
print("12초 회전 + map->odom 갱신 확인...")
tw=Twist(); tw.angular.z=0.6; last_m=None; m_ch=[]; tm=t0=time.time(); yaws=[]; ABORT=False
while time.time()-t0<12:
    pub.publish(tw); rclpy.spin_once(n,timeout_sec=0.02); now=time.time()
    if clr[0] is not None and clr[0]<0.05: print("가드정지"); ABORT=True; break
    m=tf('map','odom')
    if m and m!=last_m:
        if last_m is not None: m_ch.append(now-tm)
        tm=now; last_m=m
    if tyaw[0] is not None: yaws.append(tyaw[0])
t=Twist()
for _ in range(15): pub.publish(t); time.sleep(0.02)
import statistics as st
if yaws: print(f"  회전량 {math.degrees(np.unwrap(yaws)[-1]-np.unwrap(yaws)[0]):.0f}deg")
if m_ch: print(f"  ★ map->odom 값변화 {len(m_ch)}회, 간격 평균={st.mean(m_ch)*1000:.0f}ms 최대={max(m_ch)*1000:.0f}ms")
else: print("  ★ map->odom 여전히 변화없음(고정)")
print(f"  load(회전 후): {open('/proc/loadavg').read().split()[0]}")
rclpy.shutdown()
PY
echo "완료 — foxglove는 다음 단계에서 재시작"
