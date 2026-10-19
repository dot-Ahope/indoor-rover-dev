#!/usr/bin/env python3
"""depth_edge_filter — 깊이 bag 의 깊이 영상에서 가장자리(깊이 불연속) 화소를 지운 새 bag 을 만든다. (2026-10-19 §8, Jetson 에서 실행)
  왜: 통합 거리 · site · 복셀을 바꿔도 상자 로버 쪽 면 과장(+5.3 cm)이 그대로 → 입력 깊이 자체(물체 가장자리에서 앞 · 뒤 깊이가 섞인 화소, 09-14 '실루엣 비산점')를 의심.
       nvblox 의 깊이 전처리(do_depth_preprocessing)는 3.2.5 에서 켜면 중단(§7)이라 bag 단계에서 거른다.
  규칙(시험 전 선언): 유효 화소(0 아님) 중 3×3 이웃의 유효 화소와 깊이 차가 max(abs_m, rel × 깊이) 보다 큰 것이 하나라도 있으면 0(무효)으로.
  인자: 입력bag 출력bag [abs_m=0.05] [rel=0.04]. 입력 토픽 중 깊이 · camera_info · tf · tf_static 만 옮긴다. 출력 = sqlite3."""
import sys
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message, serialize_message
from sensor_msgs.msg import Image

IN, OUT = sys.argv[1], sys.argv[2]; ABS = float(sys.argv[3]) if len(sys.argv) > 3 else 0.05; REL = float(sys.argv[4]) if len(sys.argv) > 4 else 0.04
D = '/camera/camera/depth/image_rect_raw'; KEEP = {D, '/camera/camera/depth/camera_info', '/tf', '/tf_static'}
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=IN, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
w = rosbag2_py.SequentialWriter(); w.open(rosbag2_py.StorageOptions(uri=OUT, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
for t in r.get_all_topics_and_types():
    if t.name in KEEP: w.create_topic(t)
n = rem = val = 0
while r.has_next():
    topic, data, ts = r.read_next()
    if topic not in KEEP: continue
    if topic == D:
        m = deserialize_message(data, Image)
        a = np.frombuffer(bytes(m.data), np.uint16).reshape(m.height, m.width).astype(np.float32) / 1000.0
        v = a > 0; bad = np.zeros_like(v); P = np.pad(a, 1); PV = np.pad(v, 1)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0: continue
                nb = P[1 + dy:1 + dy + a.shape[0], 1 + dx:1 + dx + a.shape[1]]; nv = PV[1 + dy:1 + dy + a.shape[0], 1 + dx:1 + dx + a.shape[1]]
                bad |= v & nv & (np.abs(a - nb) > np.maximum(ABS, REL * a))
        out = (a * 1000.0).round().astype(np.uint16); out[bad] = 0
        m.data = out.tobytes(); data = serialize_message(m); n += 1; rem += int(bad.sum()); val += int(v.sum())
    w.write(topic, data, ts)
print('깊이 %d 장 · 유효 화소 중 지운 비율 %.2f %% (abs %.3f m, rel %.3f) → %s' % (n, 100.0 * rem / max(val, 1), ABS, REL, OUT))
