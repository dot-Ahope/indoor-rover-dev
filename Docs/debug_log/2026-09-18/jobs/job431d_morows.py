#!/usr/bin/env python3
"""map->odom 원시 기록 점검(2026-09-18): 한 보정이 두 번 세어지는지. 인자: BAG GOAL_EPOCH T0 T1
  bag 수신 순서 그대로(헤더 stamp 로 정렬하지 않고) 헤더 stamp·수신 시각·값을 출력.
"""
import sys, math
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
bag, G, T0, T1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
prev = None
while r.has_next():
    topic, data, ts = r.read_next()
    if topic != '/tf':
        continue
    rt = ts * 1e-9 - G
    for tr in deserialize_message(data, TFMessage).transforms:
        if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
            st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9 - G
            q = tr.transform.rotation; yaw = math.degrees(math.atan2(2 * q.w * q.z, 1 - 2 * q.z * q.z))
            v = (round(tr.transform.translation.x, 5), round(tr.transform.translation.y, 5), round(yaw, 3))
            if T0 <= rt <= T1:
                print('수신 %7.3f  stamp %7.3f (차 %+.3f)  x %+.5f y %+.5f yaw %+.3f°%s' % (rt, st, st - rt, v[0], v[1], v[2], '' if v == prev else '   ← 값 변경'))
            prev = v
