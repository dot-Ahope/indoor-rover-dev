#!/bin/bash
# (10-19 §24.1) 노출 · 게인 설정 거부와 '자동 노출 끄면 끈 프레임에 점 무늬' 확인 — 파라미터 정의, CLI 설정 결과, 메타데이터 교대 · 레이저 출력, 영상 저장. 로버 안 움직임
set +u
PATS="nvblox_up.sh nvblox_node depth_relay.py navigation.launch slam.launch sensors.launch navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor nav_guard rf2o slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense2_camera foxglove_bridge"
for p in $PATS; do pkill -TERM -f "$p" 2>/dev/null; done; sleep 5; for p in $PATS; do pkill -9 -f "$p" 2>/dev/null; done
docker exec isaac_ros_dev-aarch64-container bash -c "pkill -f nvblox_node" 2>/dev/null
setsid nohup ros2 run realsense2_camera realsense2_camera_node --ros-args -r __node:=camera -r __ns:=/camera \
  -p enable_depth:=true -p enable_color:=false -p enable_infra1:=true -p enable_infra2:=true \
  -p depth_module.depth_profile:=640x480x30 -p depth_module.infra_profile:=640x480x30 \
  -p depth_module.emitter_enabled:=1 -p depth_module.emitter_on_off:=true -p decimation_filter.enable:=true -p decimation_filter.filter_magnitude:=4 \
  -p enable_gyro:=false -p enable_accel:=false -p initial_reset:=true -p publish_tf:=false > /tmp/irexp_cam.log 2>&1 < /dev/null &
sleep 14
for p in exposure gain enable_auto_exposure emitter_on_off emitter_enabled; do echo "== describe depth_module.$p"; timeout 8 ros2 param describe /camera/camera depth_module.$p 2>&1 | grep -aE "Type|Min|Max|Step|Read" | tr '\n' ' '; echo; done
seq_meta() { timeout 6 ros2 topic echo /camera/camera/infra1/metadata --field json_data 2>/dev/null | grep -aoE '"(frame_emitter_mode|frame_laser_power|actual_exposure|gain_level)":-?[0-9]+' | head -24 | paste -sd' '; }
echo "== 자동 노출 켬 — 메타데이터 연속"; seq_meta
echo "== CLI: 자동 노출 끔"; timeout 8 ros2 param set /camera/camera depth_module.enable_auto_exposure false 2>&1 | tail -1
echo "== CLI: 노출 30000"; timeout 8 ros2 param set /camera/camera depth_module.exposure 30000 2>&1 | tail -1
echo "== CLI: 게인 128"; timeout 8 ros2 param set /camera/camera depth_module.gain 128 2>&1 | tail -1
sleep 2; echo "== 자동 노출 끔 뒤 — 메타데이터 연속"; seq_meta
echo "== 드라이버 로그 경고"; grep -aiE "warn|error|exposure|gain" /tmp/irexp_cam.log | tail -6 | cut -c1-200
python3 - <<'PY'
# 끈/켠 프레임 한 장씩 저장(메타데이터로 분류) — 자동 노출 끔 상태
import rclpy, re, numpy as np, cv2, time
from rclpy.qos import qos_profile_sensor_data as q
from sensor_msgs.msg import Image
from realsense2_camera_msgs.msg import Metadata
rclpy.init(); n = rclpy.create_node('irexp_snap'); meta = {}; got = {}
ns = lambda h: h.stamp.sec * 1000000000 + h.stamp.nanosec
def om(m):
    g = re.search(r'"frame_emitter_mode":(\d+)', m.json_data)
    if g: meta[ns(m.header)] = int(g.group(1))
imgs = []
n.create_subscription(Metadata, '/camera/camera/infra1/metadata', om, q)
n.create_subscription(Image, '/camera/camera/infra1/image_rect_raw', lambda m: imgs.append((ns(m.header), np.frombuffer(bytes(m.data), np.uint8).reshape(m.height, m.step)[:, :m.width].copy())), q)
t0 = time.time()
while time.time() - t0 < 4: rclpy.spin_once(n, timeout_sec=0.05)
for t, a in imgs:
    md = meta.get(t)
    if md is not None and md not in got: got[md] = a; cv2.imwrite('/tmp/irexp_mode%d.png' % md, a)
print('저장: emitter_mode', sorted(got), '· 밝기', {k: round(float(v.mean()), 1) for k, v in got.items()}, '· 영상', len(imgs), '메타', len(meta))
PY
pkill -INT -f realsense2_camera_node; sleep 3; pkill -9 -f realsense2_camera_node 2>/dev/null
