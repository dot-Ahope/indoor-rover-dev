#!/usr/bin/env python3
"""anal_split_s1 — 분리 노드 S1 판정 측정(10-19 §15). 로버 안 움직임.
  원시 깊이 · IR1 을 각자 메타데이터로 켬/끔 분류해 지표 분포를 만들고, 분리 출력(/camera/split/...)의 지표가 맞는 쪽인지 본다.
  지표: 깊이 = 유효 화소(0 아님) 비율, IR = |라플라시안| 평균(프로젝터 점 무늬 세기). 주기 · 해상도 · 도착 지연(수신 − stamp)도.
  인자: [측정 s=20]"""
import sys, time, re
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, PointCloud2
from realsense2_camera_msgs.msg import Metadata

DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 20.0
RAW = '/camera/camera'; SPL = '/camera/split'
ns = lambda h: h.stamp.sec * 1000000000 + h.stamp.nanosec


def depth_valid(m):
    return float(np.count_nonzero(np.frombuffer(bytes(m.data), np.uint16))) / (m.width * m.height)


def ir_lap(m):
    a = np.frombuffer(bytes(m.data), np.uint8).reshape(m.height, m.step)[:, :m.width].astype(np.int16)
    return float(np.abs(4 * a[1:-1, 1:-1] - a[:-2, 1:-1] - a[2:, 1:-1] - a[1:-1, :-2] - a[1:-1, 2:]).mean())


class M(Node):
    def __init__(self):
        super().__init__('anal_split_s1')
        self.mode = {'depth': {}, 'infra1': {}}; self.raw = {'depth': [], 'infra1': []}; self.out = {}; self.size = {}; self.lat = {}
        q = qos_profile_sensor_data
        for s in ('depth', 'infra1'):
            self.create_subscription(Metadata, f'{RAW}/{s}/metadata', lambda m, s=s: self.on_meta(s, m), q)
            self.create_subscription(Image, f'{RAW}/{s}/image_rect_raw', lambda m, s=s: self.on_raw(s, m), q)
        for k, t, ty in (('depth', f'{SPL}/depth/image_rect_raw', Image), ('infra1', f'{SPL}/infra1/image_rect_raw', Image),
                         ('infra2', f'{SPL}/infra2/image_rect_raw', Image), ('points', f'{SPL}/depth/color/points', PointCloud2)):
            self.out[k] = []
            self.create_subscription(ty, t, lambda m, k=k: self.on_out(k, m), q)

    def on_meta(self, s, m):
        g = re.search(r'"frame_emitter_mode":(\d+)', m.json_data)
        if g: self.mode[s][ns(m.header)] = int(g.group(1))

    def lat_of(self, key, h):
        self.lat.setdefault(key, []).append(time.time() - (h.stamp.sec + h.stamp.nanosec * 1e-9))

    def on_raw(self, s, m):
        self.size['raw ' + s] = (m.width, m.height, m.encoding); self.lat_of('raw ' + s, m.header)
        self.raw[s].append((ns(m.header), depth_valid(m) if s == 'depth' else ir_lap(m)))

    def on_out(self, k, m):
        self.size['split ' + k] = (m.width, m.height, getattr(m, 'encoding', 'pc2')); self.lat_of('split ' + k, m.header)
        v = depth_valid(m) if k == 'depth' else ir_lap(m) if k.startswith('infra') else 0.0
        self.out[k].append((ns(m.header), v, time.time()))


rclpy.init(); n = M(); t0 = time.time()
while time.time() - t0 < DUR: rclpy.spin_once(n, timeout_sec=0.05)
el = time.time() - t0
print('측정 %.1f s' % el)
for k, v in n.size.items(): print('  해상도 %-14s %s' % (k, v))
for k, L in n.out.items(): print('  주기 split %-7s %5.1f Hz (%d)' % (k, len(L) / el, len(L)))
for k in ('raw depth', 'raw infra1'): print('  주기 %-13s %5.1f Hz' % (k, len(n.raw[k.split()[1]]) / el))
for k, L in sorted(n.lat.items()): print('  도착 지연 %-14s 중앙 %5.1f ms · 95 %% %5.1f ms' % (k, 1e3 * np.median(L), 1e3 * np.percentile(L, 95)))
for s, lab in (('depth', '깊이 유효 비율'), ('infra1', 'IR1 |라플라시안|')):
    on = [v for t, v in n.raw[s] if n.mode[s].get(t) == 1]; off = [v for t, v in n.raw[s] if n.mode[s].get(t) == 0]
    unk = sum(1 for t, v in n.raw[s] if t not in n.mode[s])
    if not on or not off: print('  %s: 켬 %d · 끔 %d — 분류 불가' % (lab, len(on), len(off))); continue
    mon, moff = np.median(on), np.median(off); mid = (mon + moff) / 2
    sp = np.array([v for t, v, _ in n.out[s]])
    print('  원시 %s: 켬 중앙 %.3f (n %d, %.3f~%.3f) · 끔 중앙 %.3f (n %d, %.3f~%.3f) · 메타 없음 %d · 비 %.2f'
          % (lab, mon, len(on), min(on), max(on), moff, len(off), min(off), max(off), unk, max(mon, moff) / max(min(mon, moff), 1e-9)))
    want_on = s == 'depth'
    bad = int(np.sum(sp <= mid)) if want_on else int(np.sum(sp >= mid))
    print('  분리 %s: n %d, 중앙 %.3f, 범위 %.3f~%.3f, 가운데(%.3f) %s 쪽 프레임 %d' % (lab, len(sp), np.median(sp), sp.min(), sp.max(), mid, '아래' if want_on else '위', bad))
n.destroy_node(); rclpy.shutdown()
