#!/usr/bin/env python3
# anal_color_gaps_1113 — 11-13 §1: B 정지 기록의 컬러 4.73 Hz 가 '프레임 손실' 인지 '카메라가 원래 그 주기' 인지 가른다. Jetson, 로버 안 움직임.
#   방법: bag(db3) 의 토픽별 메시지 header.stamp 간격 — 손실이면 간격 ≈ 0.4 s(2 배) 가 섞이고, 원래 주기면 간격이 고르게 ≈ 0.21 s.
#         같은 방법으로 깊이 · cuVSLAM 도 본다(비교용). 기록 시각(수신) 기준 첫 · 끝 메시지 사이 길이로 주기를 다시 계산.
#   인자: $1 = bag 폴더(기본 /tmp/bag_rab_B). 출력: 표준 출력.
import sqlite3, sys, glob, statistics as st
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
B = sys.argv[1] if len(sys.argv) > 1 else '/tmp/bag_rab_B'
db = sqlite3.connect(glob.glob(B + '/*.db3')[0])
topics = {n: (i, t) for i, n, t in db.execute('select id, name, type from topics')}
for name in ('/camera/camera/color/image_raw', '/camera/camera/depth/image_rect_raw', '/visual_slam/tracking/odometry'):
    i, t = topics[name]; M = get_message(t)
    rows = db.execute('select timestamp, data from messages where topic_id=? order by timestamp', (i,)).fetchall()
    hs = [deserialize_message(d, M).header.stamp for _, d in rows]
    h = [s.sec + s.nanosec * 1e-9 for s in hs]; r = [ts * 1e-9 for ts, _ in rows]
    g = [b - a for a, b in zip(h, h[1:])]
    big = [x for x in g if x > 1.5 * st.median(g)]
    print(f'{name}: {len(rows)} 개 · 수신 첫~끝 {r[-1] - r[0]:.2f} s → {(len(rows) - 1) / (r[-1] - r[0]):.3f} Hz · '
          f'stamp 간격 중앙 {st.median(g) * 1000:.1f} ms · 최소 {min(g) * 1000:.1f} · 최대 {max(g) * 1000:.1f} · 중앙의 1.5 배 넘는 간격 {len(big)} 개'
          + (f' (합 {sum(big):.2f} s)' if big else ''))
    if name.endswith('color/image_raw'):
        m = deserialize_message(rows[0][1], M); print(f'  컬러 {m.width}x{m.height} {m.encoding} · {len(m.data)} B/장')
