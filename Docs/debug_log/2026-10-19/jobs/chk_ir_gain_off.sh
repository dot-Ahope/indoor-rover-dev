#!/bin/bash
# (10-19 §24.2) 번갈이 없이 프로젝터 끔에서 수동 게인 · 노출이 되는지, 되면 IR 이 얼마나 밝아지고 특징이 생기는지. 로버 안 움직임(스택은 앞 시험에서 이미 내림)
set +u
pkill -9 -f realsense2_camera_node 2>/dev/null; sleep 1
setsid nohup ros2 run realsense2_camera realsense2_camera_node --ros-args -r __node:=camera -r __ns:=/camera \
  -p enable_depth:=false -p enable_color:=false -p enable_infra1:=true -p enable_infra2:=true -p depth_module.infra_profile:=640x480x30 \
  -p depth_module.emitter_enabled:=0 -p enable_gyro:=false -p enable_accel:=false -p initial_reset:=true -p publish_tf:=false > /tmp/irgain_cam.log 2>&1 < /dev/null &
sleep 14
snap() { python3 - "$1" <<'PY'
import sys, time, rclpy, numpy as np, cv2
from rclpy.qos import qos_profile_sensor_data as q
from sensor_msgs.msg import Image
rclpy.init(); n = rclpy.create_node('irgain_snap'); L = []; f = cv2.FastFeatureDetector_create(threshold=20)
n.create_subscription(Image, '/camera/camera/infra1/image_rect_raw', lambda m: L.append(np.frombuffer(bytes(m.data), np.uint8).reshape(m.height, m.step)[:, :m.width].copy()), q)
t0 = time.time()
while time.time() - t0 < 3: rclpy.spin_once(n, timeout_sec=0.05)
if L: cv2.imwrite('/tmp/irgain_%s.png' % sys.argv[1], L[-1])
print('  %-10s 장 %d · 밝기 %.1f · FAST 중앙 %.0f' % (sys.argv[1], len(L), np.median([a.mean() for a in L]) if L else -1, np.median([len(f.detect(a, None)) for a in L]) if L else -1))
PY
}
echo "== 프로젝터 끔 · 자동 노출"; snap auto
timeout 8 ros2 param set /camera/camera depth_module.enable_auto_exposure false | tail -1
for g in 64 128 248; do echo -n "  게인 $g: "; timeout 8 ros2 param set /camera/camera depth_module.gain $g 2>&1 | tail -1; sleep 1.5; snap gain$g; done
echo -n "  노출 33000: "; timeout 8 ros2 param set /camera/camera depth_module.exposure 33000 2>&1 | tail -1
timeout 6 ros2 topic echo /camera/camera/infra1/metadata --field json_data 2>/dev/null | grep -aoE '"(actual_exposure|gain_level|frame_laser_power)":-?[0-9]+' | head -3 | paste -sd' '
pkill -INT -f realsense2_camera_node; sleep 3; pkill -9 -f realsense2_camera_node 2>/dev/null
