#!/usr/bin/env python3
"""09-29 §10 M1: 프로젝터 켬/끔 깊이 비교. /camera/camera/depth/image_rect_raw(16UC1 mm) + camera_info 를 N 프레임 모아
   유효 화소 비율(전체·아래 절반) 과 base_link 기준 상자 부피 안 점 수(프레임 평균)를 낸다.
   프로젝터는 `ros2 param set /camera/camera depth_module.emitter_enabled E` 로 바꾸고 2 s 기다린 뒤 잰다.
   인자: E(0|1) N"""
import sys, math, time, subprocess
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, CameraInfo
from tf2_ros import Buffer, TransformListener

E = sys.argv[1]; N = int(sys.argv[2])
BOX = ((1.10, 1.30), (-0.20, 0.03), (0.02, 0.30))       # base_link 기준 상자 부피(prep 측정: 전면 1.15, y −0.18~0.00)
print(subprocess.run(['ros2', 'param', 'set', '/camera/camera', 'depth_module.emitter_enabled', E], capture_output=True, text=True).stdout.strip())
time.sleep(2.0)
rclpy.init(); n = Node('depth_emit_probe'); tb = Buffer(); TransformListener(tb, n)
info, frames = [None], []
n.create_subscription(CameraInfo, '/camera/camera/depth/camera_info', lambda m: info.__setitem__(0, m), qos_profile_sensor_data)
n.create_subscription(Image, '/camera/camera/depth/image_rect_raw', lambda m: frames.append(m) if len(frames) < N else None, qos_profile_sensor_data)
t0 = time.time()
while (len(frames) < N or info[0] is None) and time.time() - t0 < 30: rclpy.spin_once(n, timeout_sec=0.05)
if not frames or info[0] is None: print('깊이 수신 없음'); sys.exit(1)
K = np.array(info[0].k).reshape(3, 3); fx, fy, cx, cy = K[0, 0], K[1, 1], K[0, 2], K[1, 2]
fr = frames[0].header.frame_id
tf = None
for _ in range(40):
    try: tf = tb.lookup_transform('base_link', fr, rclpy.time.Time()); break
    except Exception: rclpy.spin_once(n, timeout_sec=0.05)
if tf is None: print('TF base_link←%s 없음' % fr); sys.exit(1)
q = tf.transform.rotation; t = tf.transform.translation
x, y, z, w = q.x, q.y, q.z, q.w
R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
              [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
              [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]); T = np.array([t.x, t.y, t.z])
va, vl, nb = [], [], []
for m in frames:
    d = np.frombuffer(m.data, dtype=np.uint16).reshape(m.height, m.width).astype(np.float32) * 0.001
    va.append((d > 0).mean()); vl.append((d[m.height // 2:] > 0).mean())
    v, u = np.nonzero((d > 0.2) & (d < 3.0)); zc = d[v, u]
    P = np.c_[(u - cx) * zc / fx, (v - cy) * zc / fy, zc] @ R.T + T
    ok = np.ones(len(P), bool)
    for k, (lo, hi) in enumerate(BOX): ok &= (P[:, k] >= lo) & (P[:, k] <= hi)
    nb.append(int(ok.sum()))
print('M1 프로젝터=%s: %d 프레임 | 유효 화소 전체 %.1f %% · 아래 절반 %.1f %% | 상자 부피 안 점 평균 %.0f (최소 %d, 최대 %d)'
      % (E, len(frames), 100 * np.mean(va), 100 * np.mean(vl), np.mean(nb), min(nb), max(nb)))
