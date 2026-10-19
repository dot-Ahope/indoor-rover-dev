#!/usr/bin/env python3
"""mk_vslam_bag — IR bag(§17 프로세스 안 기록)을 cuVSLAM 오프라인 입력 bag 으로: 프로젝터 끔 / 켬 프레임을 다른 토픽으로 나누고 IMU · tf_static 을 붙인다. (2026-10-19 §23, Jetson 호스트)
  출력 토픽: /off/infra{1,2}/image_rect_raw · camera_info, /on/infra{1,2}/… (영상과 같은 stamp 의 camera_info), /camera/imu, /tf_static(주행 bag 에서).
  판정 = 각 영상의 메타데이터 frame_emitter_mode == on_mode(0, §15 S1)면 켬. 시각(bag 기록 시각)은 원래 그대로.
  인자: IRbag 주행bag 출력bag [all_off — §25 프로젝터 상시 끔 기록: 메타데이터와 무관하게 모두 /off 로]"""
import sys, re
import rosbag2_py
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import Image, CameraInfo
from realsense2_camera_msgs.msg import Metadata

IN, DRIVE, OUT = sys.argv[1:4]; ON_MODE = 0; ALL_OFF = len(sys.argv) > 4 and sys.argv[4] == 'all_off'
opt = lambda u: (rosbag2_py.StorageOptions(uri=u, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
ns = lambda h: h.stamp.sec * 1000000000 + h.stamp.nanosec
r = rosbag2_py.SequentialReader(); r.open(*opt(IN)); types = {t.name: t.type for t in r.get_all_topics_and_types()}
mode = {}; info = {}
r.set_filter(rosbag2_py.StorageFilter(topics=['/camera/camera/infra1/metadata', '/camera/camera/infra2/metadata', '/camera/camera/infra1/camera_info', '/camera/camera/infra2/camera_info']))
while r.has_next():
    topic, data, _ = r.read_next(); s = topic.split('/')[3]
    if topic.endswith('metadata'):
        m = deserialize_message(data, Metadata); g = re.search(r'"frame_emitter_mode":(\d+)', m.json_data)
        if g: mode[(s, ns(m.header))] = int(g.group(1))
    else:
        info[(s, ns(deserialize_message(data, CameraInfo).header))] = data
print('메타데이터 %d · camera_info %d' % (len(mode), len(info)))
w = rosbag2_py.SequentialWriter(); w.open(*opt(OUT))
for k in ('off', 'on'):
    for s in ('infra1', 'infra2'):
        w.create_topic(rosbag2_py.TopicMetadata(name='/%s/%s/image_rect_raw' % (k, s), type='sensor_msgs/msg/Image', serialization_format='cdr'))
        w.create_topic(rosbag2_py.TopicMetadata(name='/%s/%s/camera_info' % (k, s), type='sensor_msgs/msg/CameraInfo', serialization_format='cdr'))
w.create_topic(rosbag2_py.TopicMetadata(name='/camera/imu', type='sensor_msgs/msg/Imu', serialization_format='cdr'))
# tf_static: 주행 bag 의 것 — 뒤에 늦게 붙는 구독자도 받게 transient_local 로
tfq = '- history: 3\n  depth: 0\n  reliability: 1\n  durability: 1\n  deadline:\n    sec: 9223372036\n    nsec: 854775807\n  lifespan:\n    sec: 9223372036\n    nsec: 854775807\n  liveliness: 1\n  liveliness_lease_duration:\n    sec: 9223372036\n    nsec: 854775807\n  avoid_ros_namespace_conventions: false'
w.create_topic(rosbag2_py.TopicMetadata(name='/tf_static', type='tf2_msgs/msg/TFMessage', serialization_format='cdr', offered_qos_profiles=tfq))
d = rosbag2_py.SequentialReader(); d.open(*opt(DRIVE)); d.set_filter(rosbag2_py.StorageFilter(topics=['/tf_static'])); first_tf = []
while d.has_next():
    _, data, t = d.read_next(); first_tf.append(data)
r = rosbag2_py.SequentialReader(); r.open(*opt(IN))
r.set_filter(rosbag2_py.StorageFilter(topics=['/camera/raw/infra1/image_rect_raw', '/camera/raw/infra2/image_rect_raw', '/camera/camera/imu']))
n = {'off': 0, 'on': 0, 'nometa': 0, 'noinfo': 0}; wrote_tf = False
while r.has_next():
    topic, data, t = r.read_next()
    if not wrote_tf:
        for x in first_tf: w.write('/tf_static', x, t)
        wrote_tf = True
    if topic == '/camera/camera/imu':
        w.write('/camera/imu', data, t); continue
    s = topic.split('/')[3]; st = ns(deserialize_message(data, Image).header); md = mode.get((s, st))
    if md is None: n['nometa'] += 1; continue
    k = 'off' if ALL_OFF else ('on' if md == ON_MODE else 'off'); ci = info.get((s, st))
    if ci is None: n['noinfo'] += 1; continue
    w.write('/%s/%s/image_rect_raw' % (k, s), data, t); w.write('/%s/%s/camera_info' % (k, s), ci, t); n[k] += 1
del w
print('tf_static %d 묶음 · 끔 %d · 켬 %d · 메타 없음 %d · camera_info 없음 %d → %s' % (len(first_tf), n['off'], n['on'], n['nometa'], n['noinfo'], OUT))
