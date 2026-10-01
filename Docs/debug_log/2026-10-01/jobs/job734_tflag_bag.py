#!/usr/bin/env python3
"""10-01 §8.2: bag 의 /tf 로 map→odom(slam) 스탬프가 odom→base_link(EKF) 최신 스탬프보다 뒤처진 시간 — 컨트롤러는 로봇 자세(EKF 최신 스탬프)를
   map 으로 바꿀 때 그 시각의 map→odom 이 있어야 하고, 없으면 transform_tolerance(0.2 s)까지 기다린다.
   출력: map→odom 고유 스탬프 간격, (EKF 최신 스탬프 − map→odom 최신 스탬프) 분포, 그 값이 0.2 s 를 넘은 구간. 인자: BAG [시작 s] [끝 s]"""
import sys, numpy as np, rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=sys.argv[1], storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
mo, ob = [], []
while r.has_next():
    tp, data, ts = r.read_next()
    if tp != '/tf': continue
    for t in deserialize_message(data, TFMessage).transforms:
        s = t.header.stamp.sec + t.header.stamp.nanosec * 1e-9; k = (t.header.frame_id, t.child_frame_id)
        if k == ('map', 'odom'): mo.append((ts * 1e-9, s))
        elif k == ('odom', 'base_link'): ob.append((ts * 1e-9, s))
mo, ob = np.array(mo), np.array(ob); t0 = ob[0, 0]
a = float(sys.argv[2]) if len(sys.argv) > 2 else 0; b = float(sys.argv[3]) if len(sys.argv) > 3 else 1e9
print('map→odom %d (%.1f Hz), odom→base %d, 길이 %.0f s' % (len(mo), len(mo) / (mo[-1, 0] - mo[0, 0]), len(ob), ob[-1, 0] - t0))
u = np.unique(mo[:, 1]); du = np.diff(u)
print('map→odom 고유 스탬프 %d 개, 간격 중앙 %.3f · 95%% %.3f · 최대 %.3f s' % (len(u), np.median(du), np.percentile(du, 95), du.max()))
print('map→odom 스탬프 − 수신 시각: 중앙 %+.3f · 최소 %+.3f · 최대 %+.3f s (양수 = 미래 날짜)' % tuple(np.percentile(mo[:, 1] - mo[:, 0], [50, 0, 100])))
# EKF 수신마다: 그때까지 받은 map→odom 최신 스탬프와 EKF 스탬프 차
j = np.searchsorted(mo[:, 0], ob[:, 0], side='right') - 1; ok = j >= 0
latest = np.maximum.accumulate(mo[:, 1])[j[ok]]; deficit = ob[ok, 1] - latest; tt = ob[ok, 0] - t0
m = (tt >= a) & (tt <= b); d = deficit[m]
print('구간 %.0f~%.0f s: (EKF 스탬프 − map→odom 최신 스탬프) 중앙 %+.3f · 95%% %+.3f · 최대 %+.3f s, >0 인 비율 %.1f %%, >0.2 s 인 비율 %.2f %%' % (
    a, min(b, tt[-1]), np.median(d), np.percentile(d, 95), d.max(), (d > 0).mean() * 100, (d > 0.2).mean() * 100))
big = tt[m][d > 0.2]
if len(big):
    seg = np.split(big, np.where(np.diff(big) > 0.5)[0] + 1)
    print('>0.2 s 구간: ' + ', '.join('%.1f~%.1f s(최대 %.2f)' % (s[0], s[-1], deficit[m][(tt[m] >= s[0]) & (tt[m] <= s[-1])].max()) for s in seg[:20]))
