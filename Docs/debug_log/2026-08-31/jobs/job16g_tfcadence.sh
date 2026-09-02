#!/bin/bash
# odom->base 와 map->odom 값 변화 주기 측정 (20초, 회전 중). /odometry/filtered 토픽도 병행.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - << 'PY'
import math, time, rclpy, tf2_ros
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
rclpy.init(); n=rclpy.create_node('cad')
buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n)
topic_yaw=[None]
def ocb(m):
    q=m.pose.pose.orientation; topic_yaw[0]=math.atan2(2*(q.w*q.z),1-2*q.z*q.z)
n.create_subscription(Odometry,'/odometry/filtered',ocb,qos_profile_sensor_data)
def yaw(a,b):
    try:
        t=buf.lookup_transform(a,b,rclpy.time.Time()).transform; q=t.rotation
        return (round(t.translation.x,4),round(t.translation.y,4),round(math.atan2(2*(q.w*q.z),1-2*q.z*q.z),4))
    except Exception: return None
print(">>> 지금부터 20초간 로버를 계속 회전시키세요 <<<")
ob=[]; mo=[]; tp=[]; t0=time.time()
last_o=None; last_m=None; o_ch=[]; m_ch=[]; to=t0; tm=t0
while time.time()-t0<20:
    rclpy.spin_once(n,timeout_sec=0.02)
    now=time.time()
    o=yaw('odom','base_link'); m=yaw('map','odom')
    if o and o!=last_o:
        if last_o is not None: o_ch.append(now-to)
        to=now; last_o=o
    if m and m!=last_m:
        if last_m is not None: m_ch.append(now-tm)
        tm=now; last_m=m
    ob.append(o); tp.append(topic_yaw[0])
import statistics as st
def summ(name,ch):
    if ch: print(f"  {name}: 값변화 {len(ch)}회, 변화간격 평균={st.mean(ch)*1000:.0f}ms 최대={max(ch)*1000:.0f}ms 최소={min(ch)*1000:.0f}ms")
    else: print(f"  {name}: 변화 없음(고정)")
print("=== 결과 (20초) ===")
summ("odom->base (로봇 위치 TF)", o_ch)
summ("map->odom (slam 보정)", m_ch)
# 토픽 yaw 변화폭
tv=[x for x in tp if x is not None]
if len(tv)>1: print(f"  /odometry/filtered yaw 범위: {math.degrees(min(tv)):.1f} ~ {math.degrees(max(tv)):.1f}deg (토픽은 매끄럽게 변하는지)")
rclpy.shutdown()
PY
