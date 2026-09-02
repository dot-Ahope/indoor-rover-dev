#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== slam.log 경고/드롭/타임아웃 (최근) ==="
grep -aiE "drop|transform|timeout|no match|warn|error|fail|queue" /tmp/slam.log 2>/dev/null | tail -15 || echo "  (해당 로그 없음)"
echo ""
echo "=== slam.log 마지막 10줄 ==="
tail -10 /tmp/slam.log 2>/dev/null
echo ""
echo "=== map->odom 브로드캐스트 지속 확인 (stamp 갱신되나) ==="
python3 - << 'PY'
import time, rclpy, tf2_ros
rclpy.init(); n=rclpy.create_node('mo')
buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n)
t0=time.time(); stamps=[]
while time.time()-t0<4:
    rclpy.spin_once(n,timeout_sec=0.05)
    try:
        t=buf.lookup_transform('map','odom',rclpy.time.Time())
        s=t.header.stamp.sec+t.header.stamp.nanosec*1e-9; stamps.append(round(s,3))
    except Exception: pass
u=sorted(set(stamps))
print(f"  4초간 map->odom stamp 종류 {len(u)}개: 최신 {u[-3:] if len(u)>=3 else u}")
print(f"  → stamp가 계속 갱신되면 브로드캐스트는 됨(값만 고정), 안 되면 slam이 발행 중단")
rclpy.shutdown()
PY
echo ""
echo "=== slam 파라미터 (관련) ==="
for p in minimum_time_interval minimum_travel_distance minimum_travel_heading transform_timeout tf_buffer_duration throttle_scans mode; do
  echo -n "  $p: "; ros2 param get /slam_toolbox $p 2>/dev/null | grep -aoE "value is:.*" || echo "?"
done
echo ""
echo "=== CPU 부하 ==="; uptime | grep -oE "load average.*"; echo -n "slam CPU%: "; top -bn1 | grep -i sync_slam_toolbox_node | head -1 | awk '{print $9}' || echo "?"
