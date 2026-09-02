#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== slam transform_publish_period (map->odom 재발행 주기) ==="
ros2 param get /slam_toolbox transform_publish_period 2>/dev/null
echo "=== 정지 상태 map->odom stamp 갱신율 재측정 ==="
python3 - << 'PY'
import time, rclpy, tf2_ros
rclpy.init(); n=rclpy.create_node('m'); buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n)
t0=time.time(); ss=set()
while time.time()-t0<4:
    rclpy.spin_once(n,timeout_sec=0.02)
    try:
        h=buf.lookup_transform('map','odom',rclpy.time.Time()).header.stamp; ss.add(round(h.sec+h.nanosec*1e-9,3))
    except Exception: pass
print(f"  4초간 서로다른 map->odom stamp {len(ss)}개 (=재발행 ~{len(ss)/4:.0f}Hz)")
rclpy.shutdown()
PY
echo "=== foxglove_bridge 재시작 ==="
setsid nohup ros2 run foxglove_bridge foxglove_bridge > /tmp/fg.log 2>&1 &
sleep 5
ros2 node list 2>/dev/null | grep -q foxglove && echo "  foxglove 재시작됨 (클라이언트 재접속하세요)" || echo "  실패"
echo "  load: $(cat /proc/loadavg | cut -d' ' -f1-3)"
