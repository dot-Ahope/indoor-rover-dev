#!/bin/bash
# 스캔/오도 타이밍 정합 정적 분석 (주행 불필요) — "포인트 끌림" 원인 특정
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===세션 확인==="; timeout 5 ros2 topic hz /scan 2>&1 | grep -aE "average|does not" | tail -1
python3 - << 'PY'
import time, math, statistics, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
class A(Node):
    def __init__(s):
        super().__init__('t'); s.sl=[]; s.ol=[]; s.st=None; s.ot=None; s.meta=None
        s.create_subscription(LaserScan,'/scan',s.sc,qos_profile_sensor_data)
        s.create_subscription(Odometry,'/odometry/filtered',s.oc,qos_profile_sensor_data)
    def sc(s,m):
        now=s.get_clock().now().nanoseconds*1e-9; st=m.header.stamp.sec+m.header.stamp.nanosec*1e-9
        s.sl.append((now-st)*1000); s.st=st
        s.meta=(m.scan_time,m.time_increment,len(m.ranges),m.angle_min,m.angle_max)
    def oc(s,m):
        now=s.get_clock().now().nanoseconds*1e-9; st=m.header.stamp.sec+m.header.stamp.nanosec*1e-9
        s.ol.append((now-st)*1000); s.ot=st
rclpy.init(); n=A(); e=time.time()+6
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.05)
def stat(v,name):
    if v: print(f"  {name}: now-stamp mean={statistics.mean(v):+.1f}ms max={max(v):+.1f} min={min(v):+.1f} (n={len(v)})")
    else: print(f"  {name}: 없음")
stat(n.sl,"/scan       ")
stat(n.ol,"/odom_filtered")
if n.meta:
    st,ti,npts,a0,a1=n.meta
    print(f"  scan_time={st*1000:.1f}ms (한 스윕 소요), time_increment={ti*1e6:.1f}us/점, {npts}점")
    print(f"  → 스캔은 {st*1000:.0f}ms에 걸쳐 취득되나 slam은 1개 스탬프로 처리(deskew 없음).")
    print(f"    회전 0.28rad/s 시 스윕당 {math.degrees(0.28*st):.1f}deg 왜곡, 스탬프가 시작이면 반sweep 지연 {math.degrees(0.28*st/2):.1f}deg")
if n.st and n.ot: print(f"  scan-odom 스탬프차 = {(n.st-n.ot)*1000:+.1f}ms (0 근처여야 정합)")
n.destroy_node(); rclpy.shutdown()
PY
echo "===slam_toolbox 보정 관련 파라미터==="
for p in minimum_travel_heading minimum_travel_distance minimum_time_interval transform_timeout tf_buffer_duration use_scan_matching scan_buffer_size resolution; do
  echo -n "  $p: "; ros2 param get /slam_toolbox $p 2>/dev/null | tail -1
done
echo "===rplidar 파라미터 (타임스탬프 관련)==="
for p in scan_frequency angle_compensate scan_mode; do echo -n "  $p: "; ros2 param get /rplidar_node $p 2>/dev/null | tail -1; done
