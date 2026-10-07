#!/bin/bash
# 10-07 §8.3: 전역 STVL 이 상자를 왜 안 표시하나(읽기만) — 점군 발행률·상자 근처 점 수·로컬 코스트맵·STVL 로그
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "points_filtered: $(timeout 6 ros2 topic hz /camera/depth/points_filtered 2>&1 | grep -a average | tail -1) | 원본: $(timeout 6 ros2 topic hz /camera/camera/depth/color/points 2>&1 | grep -a average | tail -1)"
timeout 8 ros2 topic info /camera/depth/points_filtered 2>&1 | grep -a count
python3 - <<'PY'
import rclpy, numpy as np, time, math
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2 as pc2
from nav_msgs.msg import OccupancyGrid
rclpy.init(); n = Node('chk925'); M = {}
n.create_subscription(PointCloud2, '/camera/depth/points_filtered', lambda m: M.__setitem__('p', m), qos_profile_sensor_data)
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: M.__setitem__('l', m), 1)
t = time.time()
while time.time() - t < 6 and not ('p' in M and 'l' in M): rclpy.spin_once(n, timeout_sec=0.1)
if 'p' in M:
    m = M['p']; P = np.array([[p[0], p[1], p[2]] for p in pc2.read_points(m, field_names=('x', 'y', 'z'), skip_nans=True)])
    print('점군 frame %s, 점 %d' % (m.header.frame_id, len(P)))
    if len(P): print('  축별 범위 x %.2f~%.2f · y %.2f~%.2f · z %.2f~%.2f' % (P[:,0].min(), P[:,0].max(), P[:,1].min(), P[:,1].max(), P[:,2].min(), P[:,2].max()))
if 'l' in M:
    m = M['l']; g = np.array(m.data).reshape(m.info.height, m.info.width); r = m.info.resolution; ox, oy = m.info.origin.position.x, m.info.origin.position.y
    iy, ix = np.nonzero(g >= 99); print('로컬 코스트맵(%s) 치명·내접 칸 %d, 로버 앞 0.5~1.3 m 띠: %d' % (m.header.frame_id, len(ix), int(((ox + ix * r > 0.5) & (ox + ix * r < 1.3) & (np.abs(oy + iy * r) < 0.3)).sum())))
PY
grep -ai "stvl\|spatio\|voxel" /tmp/nav2.log | grep -aiv "Message Filter" | tail -6 | cut -c1-200
