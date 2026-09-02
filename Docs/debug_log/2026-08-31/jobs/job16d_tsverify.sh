#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 안정 후 odom->base 재측정 ==="
timeout 13 ros2 run tf2_ros tf2_monitor odom base_link 2>/dev/null | grep -aiE "Net delay|Node:|Max Delay" | head -5
echo ""
echo "=== 각 소스 stamp vs 현재시각 (delay 직접 확인) ==="
python3 - << 'PY'
import rclpy, time
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu, LaserScan
n=rclpy.create_node('ts')
got={}
def mk(topic,typ):
    def cb(m):
        if topic not in got:
            st=m.header.stamp; got[topic]=st.sec+st.nanosec*1e-9
    n.create_subscription(typ,topic,cb,qos_profile_sensor_data)
mk('/wheel_odom',Odometry); mk('/odometry/filtered',Odometry); mk('/camera/camera/imu',Imu); mk('/scan',LaserScan)
t0=time.time()
while len(got)<4 and time.time()<t0+5: rclpy.spin_once(n,timeout_sec=0.1)
now=n.get_clock().now().nanoseconds*1e-9
print(f"현재 ROS시각: {now:.3f}")
for k,v in got.items():
    print(f"  {k:26s} stamp={v:.3f}  delay={now-v:+.3f}s")
if '/wheel_odom' in got and '/scan' in got:
    print(f"  → wheel_odom vs scan stamp 차이: {abs(got['/wheel_odom']-got['/scan']):.3f}s")
PY
