#!/usr/bin/env python3
"""depth_turn_filter — 깊이 bag 에서 로버가 빨리 돌던 순간의 깊이 프레임을 뺀 새 bag. (2026-10-19 §13, Jetson 에서 실행)
  왜: §11~12 — 복귀 길 상자는 회전(156 → 108°) 중에만 보였고 그 관측 자체가 지도에서 약 8 cm 어긋남(원시 점), 기억은 그 뒤 오도메트리 오차로 더 밀림.
      회전 중 관측을 빼면 과장이 줄어드는지(가설 확인) · 상자를 잊지 않는지(쓸 수 있는지).
  규칙(시험 전 선언): 깊이 시각 ±0.25 s 의 odom→base_link yaw 변화율 |ω| > thr(기본 0.10 rad/s)이면 그 깊이 · camera_info 를 뺀다. tf · tf_static 은 그대로.
  인자: 입력bag 출력bag [thr]"""
import sys, math, bisect
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
from sensor_msgs.msg import Image, CameraInfo

IN, OUT = sys.argv[1], sys.argv[2]; THR = float(sys.argv[3]) if len(sys.argv) > 3 else 0.10
D = '/camera/camera/depth/image_rect_raw'; CI = '/camera/camera/depth/camera_info'; KEEP = {D, CI, '/tf', '/tf_static'}
opt = lambda u: (rosbag2_py.StorageOptions(uri=u, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
# 1 차: odom→base_link yaw 시계열
r = rosbag2_py.SequentialReader(); r.open(*opt(IN)); Y = []
while r.has_next():
    topic, data, ts = r.read_next()
    if topic != '/tf': continue
    for tr in deserialize_message(data, TFMessage).transforms:
        if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
            q = tr.transform.rotation; Y.append((tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9, math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))))
Y.sort(); Yt = [y[0] for y in Y]


def yaw_at(t):
    i = min(max(bisect.bisect_left(Yt, t), 0), len(Y) - 1); return Y[i][1]


def omega(t):
    a, b = yaw_at(t - 0.25), yaw_at(t + 0.25); return abs(math.atan2(math.sin(b - a), math.cos(b - a))) / 0.5


# 2 차: 쓰기
r = rosbag2_py.SequentialReader(); r.open(*opt(IN)); w = rosbag2_py.SequentialWriter(); w.open(*opt(OUT))
for t in r.get_all_topics_and_types():
    if t.name in KEEP: w.create_topic(t)
n = dropped = 0
while r.has_next():
    topic, data, ts = r.read_next()
    if topic not in KEEP: continue
    if topic in (D, CI):
        m = deserialize_message(data, Image if topic == D else CameraInfo); st = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
        if topic == D: n += 1
        if omega(st) > THR:
            dropped += topic == D; continue
    w.write(topic, data, ts)
print('깊이 %d 장 중 회전 |ω| > %.2f rad/s 로 뺀 것 %d (%.1f %%) → %s' % (n, THR, dropped, 100.0 * dropped / max(n, 1), OUT))
