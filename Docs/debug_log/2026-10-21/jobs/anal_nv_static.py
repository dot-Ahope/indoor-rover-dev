#!/usr/bin/env python3
"""anal_nv_static — 10-21 §18 3번 정지 시험 nv1 측정(새 이미지 컨테이너 안에서, 로버 안 움직임).
  (1) 원시 깊이 · IR1 을 메타데이터 frame_emitter_mode 로 나눠 지표 분포 → 어느 값이 실제 '켬' 인가(깊이 유효 비율 · IR 점무늬 |라플라시안|)
  (2) NVIDIA 분리 노드 출력: 깊이(켬이어야) 유효 비율 · 아래 절반 유효 비율, IR1(끔이어야) 밝기 · FAST(문턱 20 = 10-19 와 같음 · 문턱 5) · |라플라시안|
  (3) 끈 IR 의 실제 노출 · 게인(IR1 메타데이터) (4) cuVSLAM vo_state 비율 · 자세 이동 (5) 주기
  인자: [측정 s=60] [flash|off] — off = 같은 드라이버 · 같은 장면의 프로젝터 상시 끔 대조: 분리 출력 대신 원시 깊이 · IR 을 같은 지표로 잰다"""
import sys, time, re, json
import numpy as np, cv2
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data as Q
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from realsense2_camera_msgs.msg import Metadata
try:
    from isaac_ros_visual_slam_interfaces.msg import VisualSlamStatus
except Exception:
    VisualSlamStatus = None
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
MODE = sys.argv[2] if len(sys.argv) > 2 else 'flash'
C = '/camera'; SP = '/camera/realsense_splitter_node/output'   # 원시 = 4.51.1 이름(노드 이름 없음)
OUT = {'depth': SP + '/depth', 'i1': SP + '/infra_1', 'i2': SP + '/infra_2'} if MODE == 'flash' else \
    {'depth': C + '/depth/image_rect_raw', 'i1': C + '/infra1/image_rect_raw', 'i2': C + '/infra2/image_rect_raw'}
ns = lambda h: h.stamp.sec * 1000000000 + h.stamp.nanosec
F20 = cv2.FastFeatureDetector_create(threshold=20); F5 = cv2.FastFeatureDetector_create(threshold=5)


def dv(m, lower=False):
    a = np.frombuffer(bytes(m.data), np.uint16).reshape(m.height, m.width)
    if lower: a = a[m.height // 2:]
    return float(np.count_nonzero(a)) / a.size


def ir(m):
    return np.frombuffer(bytes(m.data), np.uint8).reshape(m.height, m.step)[:, :m.width]


def lap(a):
    a = a.astype(np.int16); return float(np.abs(4 * a[1:-1, 1:-1] - a[:-2, 1:-1] - a[2:, 1:-1] - a[1:-1, :-2] - a[1:-1, 2:]).mean())


class M(Node):
    def __init__(self):
        super().__init__('anal_nv_static')
        self.mode = {'depth': {}, 'infra1': {}}; self.meta1 = {}; self.raw = {'depth': [], 'infra1': []}
        self.sd, self.si, self.si2, self.od, self.st = [], [], 0, [], []
        for s in ('depth', 'infra1'):
            self.create_subscription(Metadata, f'{C}/{s}/metadata', lambda m, s=s: self.on_meta(s, m), Q)
            self.create_subscription(Image, f'{C}/{s}/image_rect_raw', lambda m, s=s: self.raw[s].append((ns(m.header), dv(m) if s == 'depth' else lap(ir(m)))), Q)
        self.create_subscription(Image, OUT['depth'], lambda m: self.sd.append((ns(m.header), dv(m), dv(m, True))), Q)
        self.create_subscription(Image, OUT['i1'], self.on_si, Q)
        self.create_subscription(Image, OUT['i2'], self.on_si2, Q)
        self.create_subscription(Odometry, '/visual_slam/tracking/odometry', lambda m: self.od.append((time.time(), m.pose.pose.position.x, m.pose.pose.position.y, m.pose.pose.position.z)), 10)
        if VisualSlamStatus: self.create_subscription(VisualSlamStatus, '/visual_slam/status', lambda m: self.st.append(m.vo_state), 10)

    def on_meta(self, s, m):
        g = re.search(r'"frame_emitter_mode":(\d+)', m.json_data)
        if g: self.mode[s][ns(m.header)] = int(g.group(1))
        if s == 'infra1':
            try:
                d = json.loads(m.json_data); self.meta1[ns(m.header)] = (d.get('actual_exposure'), d.get('gain_level'), d.get('frame_emitter_mode'))
            except Exception:
                pass

    def on_si(self, m):
        a = ir(m); self.si.append((ns(m.header), float(a.mean()), len(F20.detect(a)), len(F5.detect(a)), lap(a)))

    def on_si2(self, m): self.si2 += 1


rclpy.init(); n = M(); t0 = time.time()
while time.time() - t0 < DUR: rclpy.spin_once(n, timeout_sec=0.02)
el = time.time() - t0
print('측정 %.1f s · 모드 %s (출력 = %s)' % (el, MODE, '분리 노드' if MODE == 'flash' else '원시(대조)'))
print('  주기: 원시 깊이 %.1f · 원시 IR1 %.1f · 분리 깊이 %.1f · 분리 IR1 %.1f · 분리 IR2 %.1f · cuVSLAM odom %.1f Hz' % (
    len(n.raw['depth']) / el, len(n.raw['infra1']) / el, len(n.sd) / el, len(n.si) / el, n.si2 / el, len(n.od) / el))
mids = {}
for s, lab in (('depth', '깊이 유효 비율'), ('infra1', 'IR1 |라플라시안|')):
    g = {k: [v for t, v in n.raw[s] if n.mode[s].get(t) == k] for k in (0, 1)}
    unk = sum(1 for t, v in n.raw[s] if t not in n.mode[s])
    if not g[0] or not g[1]:
        print('  원시 %s: 모드0 %d · 모드1 %d — 분류 불가' % (lab, len(g[0]), len(g[1]))); continue
    m0, m1 = np.median(g[0]), np.median(g[1]); mids[s] = (m0 + m1) / 2
    print('  원시 %s: 모드0 중앙 %.3f (n %d, %.3f~%.3f) · 모드1 중앙 %.3f (n %d, %.3f~%.3f) · 메타 없음 %d' % (lab, m0, len(g[0]), min(g[0]), max(g[0]), m1, len(g[1]), min(g[1]), max(g[1]), unk))
    print('    → 실제 프로젝터 켬 = 모드 %d (NVIDIA 분리 노드는 모드 1 = 켬 으로 가정)' % (1 if m1 > m0 else 0))
if n.sd:
    a = np.array([[v, l] for t, v, l in n.sd])
    print('  분리 깊이: n %d · 유효 중앙 %.3f (%.3f~%.3f) · 아래 절반 유효 중앙 %.3f (%.3f~%.3f)%s' % (
        len(a), np.median(a[:, 0]), a[:, 0].min(), a[:, 0].max(), np.median(a[:, 1]), a[:, 1].min(), a[:, 1].max(),
        ' · 원시 가운데(%.3f) 아래 프레임 %d' % (mids['depth'], int(np.sum(a[:, 0] <= mids['depth']))) if 'depth' in mids else ''))
if n.si:
    b = np.array([x[1:] for x in n.si])
    print('  분리 IR1: n %d · 밝기 중앙 %.1f · FAST20 중앙 %.0f (5~95 %% %.0f~%.0f) · FAST5 중앙 %.0f · |라플라시안| 중앙 %.2f%s' % (
        len(b), np.median(b[:, 0]), np.median(b[:, 1]), np.percentile(b[:, 1], 5), np.percentile(b[:, 1], 95), np.median(b[:, 2]), np.median(b[:, 3]),
        ' · 원시 가운데(%.2f) 위 프레임 %d' % (mids['infra1'], int(np.sum(b[:, 3] >= mids['infra1']))) if 'infra1' in mids else ''))
    ex = [n.meta1[x[0]] for x in n.si if x[0] in n.meta1]
    if ex:
        print('  분리 IR1 프레임의 메타: 노출 중앙 %s µs · 게인 중앙 %s · emitter_mode 값 %s' % (
            np.median([e[0] for e in ex if e[0] is not None]), np.median([e[1] for e in ex if e[1] is not None]), sorted(set(e[2] for e in ex))))
if n.od:
    p = np.array([x[1:] for x in n.od]); d = np.linalg.norm(p - p[0], axis=1)
    print('  cuVSLAM: odom %d · 처음 대비 이동 끝 %.2f cm · 최대 %.2f cm' % (len(p), 100 * d[-1], 100 * d.max()))
else:
    print('  cuVSLAM: odom 0 개')
if n.st:
    s = np.array(n.st); print('  cuVSLAM vo_state: n %d · 값별 %s' % (len(s), {int(k): int(np.sum(s == k)) for k in np.unique(s)}))
n.destroy_node(); rclpy.shutdown()
