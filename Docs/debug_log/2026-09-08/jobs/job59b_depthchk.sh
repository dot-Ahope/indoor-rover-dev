#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo -n "depth_scan 프로세스: "; pgrep -fc "depthimage_to_laserscan_node"
echo -n "/camera/scan Hz: "; timeout 8 ros2 topic hz /camera/scan 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1; echo
python3 - << 'PY'
import rclpy, math, time
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
rclpy.init(); n=Node('chk'); got={}
def mk(k):
    def cb(m): got[k]=m
    return cb
n.create_subscription(LaserScan,'/camera/scan',mk('cam'),qos_profile_sensor_data)
n.create_subscription(LaserScan,'/scan',mk('lid'),qos_profile_sensor_data)
t=time.time()
while time.time()-t<6 and len(got)<2: rclpy.spin_once(n,timeout_sec=0.2)
if 'cam' in got:
    m=got['cam']; r=[x for x in m.ranges if math.isfinite(x) and m.range_min<x<m.range_max]
    ctr=len(m.ranges)//2; c=[x for x in m.ranges[ctr-5:ctr+6] if math.isfinite(x)]
    print(f"camera/scan: frame={m.header.frame_id} N={len(m.ranges)} 유효 {len(r)} ({100*len(r)/len(m.ranges):.0f}%) "
          f"각도 {math.degrees(m.angle_min):.1f}~{math.degrees(m.angle_max):.1f}° 정면 range {min(c) if c else None}")
else: print("camera/scan 미수신")
if 'lid' in got:
    m=got['lid']; a=[m.angle_min+i*m.angle_increment for i in range(len(m.ranges))]
    # 로버 정면 = 스캔각 ±π (LYAW=π)
    f=[m.ranges[i] for i in range(len(m.ranges)) if abs(math.atan2(math.sin(a[i]-math.pi),math.cos(a[i]-math.pi)))<math.radians(3) and math.isfinite(m.ranges[i]) and m.ranges[i]>0.2]
    print(f"lidar/scan 정면 range {min(f) if f else None} (라이다는 카메라보다 0.08m 뒤)")
PY
echo "== CPU(프로세스별, 1초 평균) =="; top -bn2 -d1 | awk '/^top/{i++} i==2 && /python3|realsen|depthimage|async_s|rplidar|ekf_node|foxglove/ {printf "%5s%% %s\n",$9,$12}' | head -9
echo "== python3 정체 =="; ps -eo pid,pcpu,args | grep -E "python3" | grep -vE "grep|ros2 launch" | awk '{printf "%5s%% %s\n",$2,$4}' | sed 's|/home/jetson/ros2_ws/install/rover_bringup/lib/rover_bringup/||' | head -6
