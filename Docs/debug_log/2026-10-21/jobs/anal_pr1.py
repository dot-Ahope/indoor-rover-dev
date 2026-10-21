#!/usr/bin/env python3
"""anal_pr1 — 10-21 §21 깊이 프리셋 정지 시험(호스트, 로버 안 움직임).
  운용 카메라 깊이(/camera/camera/depth/image_rect_raw, 데시메이션 4)를 nvblox 와 같은 기준으로 재현해 센다:
  화소 → base_link, 수평 거리 ≤ 1.4 m, 높이 띠 0.06~0.30 m, 5 cm 복셀별 '찍힌 프레임 비율'.
  깜빡 복셀(0 < 비율 < 30 %) = 유령 후보, 안정 복셀(≥ 80 %) = 실제 물체 후보(0.10 m 연결로 묶음).
  인자: 측정 s · 이름(P0a 등). 그림용으로 /tmp/pr1_<이름>.npz(복셀 비율) · _depth.png · _ir.png 저장"""
import sys, time, math
import numpy as np, cv2
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data as Q
from sensor_msgs.msg import Image, CameraInfo
from rclpy.time import Time
from tf2_ros import Buffer, TransformListener

DUR = float(sys.argv[1]); TAG = sys.argv[2]
RMAX, ZLO, ZHI, V = 1.4, 0.06, 0.30, 0.05


def quat_mat(q):
    x, y, z, w = q.x, q.y, q.z, q.w
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


class M(Node):
    def __init__(self):
        super().__init__('anal_pr1')
        self.tb = Buffer(); self.tl = TransformListener(self.tb, self)
        self.K = None; self.T = None; self.n = 0; self.hits = {}; self.fill = []; self.floor = []; self.band = []
        self.last_depth = None; self.last_ir = None; self.on = False
        self.create_subscription(CameraInfo, '/camera/camera/depth/camera_info', self.on_info, Q)
        self.create_subscription(Image, '/camera/camera/depth/image_rect_raw', self.on_depth, Q)
        self.create_subscription(Image, '/camera/raw/infra1/image_rect_raw', self.on_ir, Q)

    def on_info(self, m):
        self.K = (m.k[0], m.k[4], m.k[2], m.k[5], m.width, m.height)

    def on_ir(self, m):
        self.last_ir = np.frombuffer(bytes(m.data), np.uint8).reshape(m.height, m.step)[:, :m.width].copy()

    def on_depth(self, m):
        if self.T is None:
            try:
                t = self.tb.lookup_transform('base_link', m.header.frame_id, Time())
                self.T = (quat_mat(t.transform.rotation), np.array([t.transform.translation.x, t.transform.translation.y, t.transform.translation.z]))
                self.get_logger().info('TF base_link <- %s 위치 %s' % (m.header.frame_id, np.round(self.T[1], 3)))
            except Exception:
                return
        if not self.on or self.K is None: return
        a = np.frombuffer(bytes(m.data), np.uint16).reshape(m.height, m.width)
        fx, fy, cx, cy, w0, h0 = self.K; s = m.width / w0   # camera_info 가 데시메이션 전 크기면 비율로 맞춤
        fx, fy, cx, cy = fx * s, fy * s, cx * s, cy * s
        v, u = np.nonzero(a); z = a[v, u] * 0.001
        P = np.c_[(u - cx) * z / fx, (v - cy) * z / fy, z] @ self.T[0].T + self.T[1]
        self.fill.append(len(z) / a.size); self.last_depth = a.copy()
        r = np.hypot(P[:, 0], P[:, 1]); near = r <= RMAX
        self.floor.append(int(np.sum(near & (np.abs(P[:, 2]) < 0.04))))
        b = P[near & (P[:, 2] >= ZLO) & (P[:, 2] < ZHI)]; self.band.append(len(b))
        for k in set(map(tuple, np.floor(b / V).astype(int))):
            self.hits[k] = self.hits.get(k, 0) + 1
        self.n += 1


rclpy.init(); n = M(); t0 = time.time()
while n.T is None and time.time() - t0 < 10: rclpy.spin_once(n, timeout_sec=0.05)
n.on = True; t0 = time.time()
while time.time() - t0 < DUR: rclpy.spin_once(n, timeout_sec=0.02)
el = time.time() - t0
if n.n == 0:
    print('[%s] 깊이 0 장 (TF %s)' % (TAG, 'OK' if n.T is not None else '없음')); sys.exit(1)
fr = {k: c / n.n for k, c in n.hits.items()}
flick = [k for k, f in fr.items() if f < 0.30]; stab = [k for k, f in fr.items() if f >= 0.80]
# 안정 복셀 묶기(xy 0.10 m 연결)
cl = []
for k in stab:
    p = (np.array(k[:2]) + 0.5) * V
    for c in cl:
        if min(np.hypot(*(p - q)) for q in c) <= 0.101: c.append(p); break
    else: cl.append([p])
merged = True
while merged:   # 사슬로 이어진 묶음 합치기
    merged = False
    for i in range(len(cl)):
        for j in range(i + 1, len(cl)):
            if min(np.hypot(*(p - q)) for p in cl[i] for q in cl[j]) <= 0.101:
                cl[i] += cl.pop(j); merged = True; break
        if merged: break
print('[%s] 측정 %.1f s · 깊이 %d 장(%.1f Hz)' % (TAG, el, n.n, n.n / el))
print('  채움률 중앙 %.3f · 바닥 점(|z|<0.04, ≤1.4 m) 중앙 %d · 띠 점(0.06~0.30) 중앙 %d (5~95 %% %d~%d)' % (
    np.median(n.fill), np.median(n.floor), np.median(n.band), np.percentile(n.band, 5), np.percentile(n.band, 95)))
print('  복셀(띠 · ≤1.4 m): 찍힘 %d · 깜빡(<30 %%) %d · 중간 %d · 안정(≥80 %%) %d' % (len(fr), len(flick), len(fr) - len(flick) - len(stab), len(stab)))
fd = np.array([np.hypot((k[0] + .5) * V, (k[1] + .5) * V) for k in flick]) if flick else np.zeros(0)
fz = np.array([(k[2] + .5) * V for k in flick]) if flick else np.zeros(0)
if len(fd):
    print('  깜빡 복셀 거리 분포: <0.8 m %d · 0.8~1.1 %d · 1.1~1.4 %d · 높이 0.05~0.10 %d · 0.10~0.15 %d · ≥0.15 %d' % (
        np.sum(fd < 0.8), np.sum((fd >= 0.8) & (fd < 1.1)), np.sum(fd >= 1.1), np.sum(fz < 0.10), np.sum((fz >= 0.10) & (fz < 0.15)), np.sum(fz >= 0.15)))
print('  안정 묶음(복셀 수 ≥ 3): ' + ' '.join('(%.2f,%.2f)×%d' % (np.mean([p[0] for p in c]), np.mean([p[1] for p in c]), len(c)) for c in sorted(cl, key=len, reverse=True) if len(c) >= 3))
np.savez('/tmp/pr1_%s.npz' % TAG, keys=np.array(list(fr.keys())), frac=np.array(list(fr.values())), n=n.n)
if n.last_depth is not None:
    d = n.last_depth; cv2.imwrite('/tmp/pr1_%s_depth.png' % TAG, np.where(d > 0, 255 - np.clip(d / 4000.0 * 230, 0, 230), 0).astype(np.uint8))
if n.last_ir is not None:
    cv2.imwrite('/tmp/pr1_%s_ir.png' % TAG, n.last_ir)
n.destroy_node(); rclpy.shutdown()
