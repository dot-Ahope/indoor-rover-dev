#!/usr/bin/env python3
"""10-01 §8.32: 주행 중 위치 추정 노드가 낸 /map(전역 정적 층의 입력)이 저장 지도 office_v2.pgm 과 같은가 — 특히 서쪽 통로.
   bag 의 /map 마다: 크기·원점, 저장본 대비 점유 추가/삭제 셀 수(전체·서쪽 통로 띠 x −1.8~−1.4, y −4.5~−3.0)"""
import sys, numpy as np, rosbag2_py
from PIL import Image
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
im = np.array(Image.open('/home/jetson/maps/office/office_v2.pgm')); H, W = im.shape; r0 = 0.05; ox0, oy0 = -5.29, -6.96
occ0 = np.flipud(im == 0)   # 행 0 = 아래(y 작음), OccupancyGrid 와 같은 방향
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=sys.argv[1], storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}; t0 = None; n = 0
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if t0 is None: t0 = t
    if tp != '/map': continue
    m = deserialize_message(data, get_message(types[tp])); g = np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width)
    gox, goy, res = m.info.origin.position.x, m.info.origin.position.y, m.info.resolution
    # 저장본 격자로 맞춤(같은 해상도 가정)
    di, dj = int(round((oy0 - goy) / res)), int(round((ox0 - gox) / res))
    sub = np.full((H, W), -1, np.int16); ii0, jj0 = max(0, -di), max(0, -dj)
    for_i = slice(max(0, di), min(g.shape[0], di + H)); for_j = slice(max(0, dj), min(g.shape[1], dj + W))
    blk = g[for_i, for_j]; sub[ii0:ii0 + blk.shape[0], jj0:jj0 + blk.shape[1]] = blk
    occ = sub >= 65
    add, rem = occ & ~occ0, occ0 & ~occ & (sub >= 0)
    c0, c1 = int((-1.8 - ox0) / r0), int((-1.4 - ox0) / r0); y0_, y1_ = int((-4.5 - oy0) / r0), int((-3.0 - oy0) / r0)
    print('%6.1f s /map %d×%d 원점 (%.2f, %.2f) | 저장본 대비 점유 추가 %d · 삭제 %d | 서쪽 통로 띠 추가 %d · 저장본 점유 %d' % (
        t - t0, m.info.width, m.info.height, gox, goy, add.sum(), rem.sum(), add[y0_:y1_, c0:c1].sum(), occ0[y0_:y1_, c0:c1].sum()))
    n += 1
print('/map %d 개' % n)
