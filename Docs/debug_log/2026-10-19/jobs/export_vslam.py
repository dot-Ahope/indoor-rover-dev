#!/usr/bin/env python3
"""export_vslam — 오프라인 cuVSLAM 출력 bag → 변형별 오도메트리 csv + vo_state 요약. (2026-10-19 §23, 컨테이너 안 — VisualSlamStatus 메시지 정의가 거기 있음)
  vo_state: 0 미상 · 1 성공 · 2 실패(09-29 §9.1 메시지 파일 확인). 인자: 출력bag 접두사"""
import sys, csv, collections
import rosbag2_py
from rclpy.serialization import deserialize_message
from nav_msgs.msg import Odometry
from isaac_ros_visual_slam_interfaces.msg import VisualSlamStatus

IN, PRE = sys.argv[1:3]
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=IN, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
od = collections.defaultdict(list); vs = collections.defaultdict(collections.Counter); vt = collections.defaultdict(list)
while r.has_next():
    topic, data, t = r.read_next(); k = topic.split('/')[1]
    if topic.endswith('odometry'):
        m = deserialize_message(data, Odometry); p = m.pose.pose.position; q = m.pose.pose.orientation
        od[k].append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, p.x, p.y, p.z, q.x, q.y, q.z, q.w))
    else:
        m = deserialize_message(data, VisualSlamStatus); vs[k][m.vo_state] += 1; vt[k].append((t * 1e-9, m.vo_state))
for k in sorted(set(od) | set(vs)):
    with open('%s_%s.csv' % (PRE, k), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['t', 'x', 'y', 'z', 'qx', 'qy', 'qz', 'qw']); w.writerows(od[k])
    with open('%s_%s_state.csv' % (PRE, k), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['t_rx', 'vo_state']); w.writerows(vt[k])
    tot = sum(vs[k].values())
    print('  %s: 오도메트리 %d · 상태 %d (성공 %.1f %% · 실패 %d · 미상 %d)' % (k, len(od[k]), tot, 100.0 * vs[k][1] / max(tot, 1), vs[k][2], vs[k][0]))
