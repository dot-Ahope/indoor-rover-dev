#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
timeout 15 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" > /dev/null 2>&1 && echo "local 초기화" 
timeout 15 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" > /dev/null 2>&1 && echo "global 초기화"
sleep 4
python3 /tmp/job59g_costchk.py | tail -4
python3 - << 'PY'
import rclpy, math, time, tf2_ros
from rclpy.node import Node
rclpy.init(); n=Node('posechk'); buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n); t=time.time(); p=None
while time.time()-t<8 and p is None:
    rclpy.spin_once(n,timeout_sec=0.1)
    try:
        tr=buf.lookup_transform('map','base_link',rclpy.time.Time()).transform; q=tr.rotation
        p=(tr.translation.x,tr.translation.y,math.degrees(math.atan2(2*(q.w*q.z),1-2*q.z*q.z)))
    except Exception: pass
print(f"현재 map 위치: ({p[0]:.3f},{p[1]:.3f}) hd={p[2]:.1f}°" if p else "TF 실패")
PY
