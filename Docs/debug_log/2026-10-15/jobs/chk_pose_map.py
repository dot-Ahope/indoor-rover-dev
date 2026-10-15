#!/usr/bin/env python3
"""chk_pose_map — 로버 지도 자세(map→base_link). 로버 안 움직임."""
import time, math, rclpy, tf2_ros
rclpy.init(); n = rclpy.create_node('chk_pose_map'); b = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(b, n); t0 = time.time()
while time.time() - t0 < 2.0: rclpy.spin_once(n, timeout_sec=0.05)
t = b.lookup_transform('map', 'base_link', rclpy.time.Time()).transform; q = t.rotation
print('pose: 지도 (%.3f, %.3f, %+.1f°)' % (t.translation.x, t.translation.y, math.degrees(math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z)))))
