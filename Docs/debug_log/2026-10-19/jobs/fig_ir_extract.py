#!/usr/bin/env python3
"""fig_ir_extract — IR bag(프로세스 안 기록, §17)에서 IR1 의 프로젝터 끔 · 켬 프레임을 짝지어 나란히 놓은 작은 영상 + 프레임별 지표 csv. (2026-10-19 §20, Jetson 에서 실행)
  왜: 4 GB IR bag 을 PC 로 옮기지 않고, 사용자가 볼 영상(끔 = cuVSLAM 입력 | 켬 = 점 무늬)과 비교 지표만 뽑는다.
  판정: 메타데이터 frame_emitter_mode == on_mode(0, §15 S1 실측)면 켬.
  지표(프레임마다): 평균 밝기, |라플라시안| 평균(질감), FAST 모서리 수(문턱 20 — 추적 가능한 특징 수의 대리값; cuVSLAM 의 실제 특징 검출기와는 다름).
  짝: 끔 프레임마다 직전 켬 프레임(33 ms 앞)을 붙인다. 출력 프레임 = 끔 프레임 시각(약 15 Hz).
  인자: IRbag 출력폴더 [축소 배율=1.0]"""
import sys, csv, re, time
import numpy as np, cv2
import rosbag2_py
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import Image
from realsense2_camera_msgs.msg import Metadata

IN, OUT = sys.argv[1], sys.argv[2]; SC = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0; ON_MODE = 0
IMG = '/camera/raw/infra1/image_rect_raw'; META = '/camera/camera/infra1/metadata'
fast = cv2.FastFeatureDetector_create(threshold=20)


def opt(u):
    return rosbag2_py.StorageOptions(uri=u, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr')


ns = lambda h: h.stamp.sec * 1000000000 + h.stamp.nanosec
# 1 차: 메타데이터만
r = rosbag2_py.SequentialReader(); r.open(*opt(IN)); r.set_filter(rosbag2_py.StorageFilter(topics=[META])); mode = {}
while r.has_next():
    _, data, _ = r.read_next(); m = deserialize_message(data, Metadata); g = re.search(r'"frame_emitter_mode":(\d+)', m.json_data)
    if g: mode[ns(m.header)] = int(g.group(1))
print('메타데이터 %d' % len(mode))
# 2 차: 영상
r = rosbag2_py.SequentialReader(); r.open(*opt(IN)); r.set_filter(rosbag2_py.StorageFilter(topics=[IMG]))
vw = None; last_on = None; rows = []; n = {'on': 0, 'off': 0, 'nometa': 0}; t0 = None; tic = time.time()


def stats(a):
    lap = np.abs(cv2.Laplacian(a, cv2.CV_16S)).mean()
    return float(a.mean()), float(lap), len(fast.detect(a, None))


def label(a, txt):
    b = cv2.cvtColor(a, cv2.COLOR_GRAY2BGR); cv2.putText(b, txt, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2); return b


while r.has_next():
    _, data, _ = r.read_next(); m = deserialize_message(data, Image); t = ns(m.header)
    if t0 is None: t0 = t
    md = mode.get(t)
    if md is None: n['nometa'] += 1; continue
    a = np.frombuffer(bytes(m.data), np.uint8).reshape(m.height, m.step)[:, :m.width]
    if SC != 1.0: a = cv2.resize(a, None, fx=SC, fy=SC, interpolation=cv2.INTER_AREA)
    if md == ON_MODE:
        n['on'] += 1; last_on = (t, a, stats(a)); continue
    n['off'] += 1
    if last_on is None or t - last_on[0] > 80_000_000: continue   # 짝 켬 프레임이 80 ms 안에 없으면 건너뜀
    so = stats(a); son = last_on[2]
    rows.append(dict(t=round((t - t0) * 1e-9, 3), stamp_ns=t, off_mean=so[0], off_lap=so[1], off_fast=so[2], on_mean=son[0], on_lap=son[1], on_fast=son[2]))
    frame = np.hstack([label(a, 'OFF (cuVSLAM) t=%.1f  FAST %d' % (rows[-1]['t'], so[2])), label(last_on[1], 'ON (dots)  FAST %d' % son[2])])
    if vw is None:
        vw = cv2.VideoWriter(OUT + '/ir_pairs.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 15, (frame.shape[1], frame.shape[0]))
    vw.write(frame)
vw.release()
with open(OUT + '/ir_pairs.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(x) for x in rows]
A = lambda k: np.array([x[k] for x in rows])
print('IR1 켬 %d · 끔 %d · 메타 없음 %d → 짝 %d (%.0f s 처리)' % (n['on'], n['off'], n['nometa'], len(rows), time.time() - tic))
for k in ('mean', 'lap', 'fast'):
    print('  %-5s 끔 중앙 %8.2f (5~95 %% %.2f~%.2f) · 켬 중앙 %8.2f (5~95 %% %.2f~%.2f)' % (k, np.median(A('off_' + k)), *np.percentile(A('off_' + k), [5, 95]), np.median(A('on_' + k)), *np.percentile(A('on_' + k), [5, 95])))
