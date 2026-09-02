#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 소스별 stamp vs 현재시각 (delay 직접 측정) ==="
python3 - << 'PY'
import rclpy, time
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu, LaserScan
rclpy.init()
n=rclpy.create_node('ts')
got={}
def mk(topic,typ):
    def cb(m):
        if topic not in got:
            st=m.header.stamp; got[topic]=st.sec+st.nanosec*1e-9
    n.create_subscription(typ,topic,cb,qos_profile_sensor_data)
mk('/wheel_odom',Odometry); mk('/odometry/filtered',Odometry); mk('/camera/camera/imu',Imu); mk('/scan',LaserScan); mk('/scan_raw',LaserScan)
t0=time.time()
while len(got)<5 and time.time()<t0+6: rclpy.spin_once(n,timeout_sec=0.1)
now=n.get_clock().now().nanoseconds*1e-9
print(f"현재 ROS시각(Jetson): {now:.3f}  (use_sim_time 아니면 wall clock)")
for k in ['/wheel_odom','/odometry/filtered','/camera/camera/imu','/scan_raw','/scan']:
    if k in got: print(f"  {k:26s} stamp={got[k]:.3f}  delay(now-stamp)={now-got[k]:+.3f}s")
    else: print(f"  {k:26s} (미수신)")
if '/wheel_odom' in got and '/camera/camera/imu' in got:
    print(f"\n  ★ 보드(wheel_odom) vs 카메라(imu) stamp 차이 = {got['/wheel_odom']-got['/camera/camera/imu']:+.3f}s")
    print(f"    (0에 가까워야 정상. 크면 보드 micro-ROS 클럭이 Jetson과 어긋남)")
rclpy.shutdown()
PY
