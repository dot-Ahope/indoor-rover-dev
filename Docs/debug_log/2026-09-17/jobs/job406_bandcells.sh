#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
echo "=== 감사: 근거 없는 셀 좌표 ==="
BOX_HINT='1.15 -0.03' python3 /tmp/job248_audit.py 2>&1 | grep -aE "^  로컬\[|^  전역\[|근거 없는 셀 x 범위" -A1 | cut -c1-300 | head -8
echo "=== 원시 깊이 낮은 점(통로 띠 x 0.3~1.6, y -0.1~0.5, z 0.05~0.3) 지금 ==="
python3 - <<'PY'
import time, math, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2 as pc2
import tf2_ros
rclpy.init(); n = Node('band406'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n); F = []
n.create_subscription(PointCloud2, '/camera/depth/points_filtered', lambda m: F.append(m), qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < 4: rclpy.spin_once(n, timeout_sec=0.1)
m = F[-1]; T = buf.lookup_transform('base_link', m.header.frame_id, rclpy.time.Time(), timeout=rclpy.duration.Duration(seconds=2)).transform
q = T.rotation; x_, y_, z_, w_ = q.x, q.y, q.z, q.w
R = np.array([[1-2*(y_*y_+z_*z_), 2*(x_*y_-z_*w_), 2*(x_*z_+y_*w_)], [2*(x_*y_+z_*w_), 1-2*(x_*x_+z_*z_), 2*(y_*z_-x_*w_)], [2*(x_*z_-y_*w_), 2*(y_*z_+x_*w_), 1-2*(x_*x_+y_*y_)]])
a = pc2.read_points(m, field_names=('x','y','z'), skip_nans=True); P = np.stack([a['x'], a['y'], a['z']], 1).astype(float) @ R.T + [T.translation.x, T.translation.y, T.translation.z]
s = (P[:,0] > 0.3) & (P[:,0] < 1.6) & (P[:,1] > -0.1) & (P[:,1] < 0.5) & (P[:,2] > 0.05) & (P[:,2] < 0.3)
box = s & (P[:,0] > 1.1) & (P[:,0] < 1.35) & (P[:,1] < 0.12)
o = s & ~box
print('띠 안 점 %d (상자 %d, 그 외 %d)' % (s.sum(), box.sum(), o.sum()))
if o.any():
    print('  그 외 점 x %.2f~%.2f, y %+.2f~%+.2f, z %.2f~%.2f' % (P[o,0].min(), P[o,0].max(), P[o,1].min(), P[o,1].max(), P[o,2].min(), P[o,2].max()))
PY
