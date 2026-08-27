#!/bin/bash
# 토픽별 수신 지연(now - header.stamp) 측정 — EKF 무음 폐기(old measurement) 가설 검증
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - << 'PY'
import rclpy, time, statistics
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry

class L(Node):
    def __init__(self):
        super().__init__('latency_probe')
        self.d = {'/imu/data': [], '/camera/camera/imu': [], '/wheel_odom': [], '/wheel_odom/conditioned': [], '/odometry/filtered': []}
        for t in ['/imu/data', '/camera/camera/imu']:
            self.create_subscription(Imu, t, lambda m, t=t: self.cb(t, m), qos_profile_sensor_data)
        for t in ['/wheel_odom', '/wheel_odom/conditioned', '/odometry/filtered']:
            self.create_subscription(Odometry, t, lambda m, t=t: self.cb(t, m), qos_profile_sensor_data)
    def cb(self, t, m):
        now = self.get_clock().now().nanoseconds * 1e-9
        st = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
        self.d[t].append((now - st) * 1000.0)

rclpy.init(); n = L(); end = time.time() + 4
while time.time() < end: rclpy.spin_once(n, timeout_sec=0.05)
for t, v in n.d.items():
    if v: print(f"{t:28s} n={len(v):4d}  now-stamp: mean={statistics.mean(v):+8.1f}ms  min={min(v):+8.1f}  max={max(v):+8.1f}")
    else: print(f"{t:28s} NO MSG")
n.destroy_node(); rclpy.shutdown()
PY
echo "===EKF timing params==="
for p in smooth_lagged_data history_length sensor_timeout transform_time_offset; do echo -n "$p: "; ros2 param get /ekf_filter_node $p 2>/dev/null | tail -1; done
