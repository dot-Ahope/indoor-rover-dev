#!/usr/bin/env python3
"""chk_tf_lag — §16 nvblox 전역 층 TF 실패가 부하 탓인가 (2026-10-27, PC).
  · map→odom(/tf) 발행: 수신 간격 · stamp 간격 분포, 수신 − stamp 지연
  · 슬라이스마다 '그 슬라이스 수신 시점까지 받은 map→odom 의 최신 stamp' 와 슬라이스 stamp 차(앞섬이면 조회 실패 조건)
  · nav2 경고(Can't transform) 시각 vs controller 'Control loop missed' 시각 겹침
  인자: bag폴더 nav2.log"""
import sys, re, time, math
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
ts_ = get_typestore(Stores.ROS2_HUMBLE)
ts_.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
hs = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + '.%02d' % int((t % 1) * 100)
MO, SL = [], []
with AnyReader([Path(sys.argv[1])], default_typestore=ts_) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/nvblox_node/static_map_slice')]):
        m = rd.deserialize(raw, c.msgtype); ts = t * 1e-9
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((ts, tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9))
        else: SL.append((ts, m.header.stamp.sec + m.header.stamp.nanosec * 1e-9))
MO = np.array(MO); SL = np.array(SL)
rx = np.diff(MO[:, 0]); st = np.diff(MO[:, 1]); lag = MO[:, 0] - MO[:, 1]
print('map→odom %d 개 · 수신 간격 중앙 %.3f s · 95%% %.3f · 최대 %.3f s · stamp 간격 0 인 것(같은 stamp 재발행) %d' % (len(MO), np.median(rx), np.percentile(rx, 95), rx.max(), (st == 0).sum()))
print('  stamp 새로 바뀌는 간격: 중앙 %.3f · 95%% %.3f · 최대 %.3f s' % (np.median(st[st > 0]), np.percentile(st[st > 0], 95), st[st > 0].max()))
print('  수신 − stamp 지연: 중앙 %.3f · 95%% %.3f · 최대 %.3f s' % (np.median(lag), np.percentile(lag, 95), lag.max()))
# 슬라이스 stamp − (그때까지 받은 map→odom 최신 stamp)
lead = []
for ts, s in SL:
    k = np.searchsorted(MO[:, 0], ts) - 1
    if k >= 0: lead.append((ts, s - MO[:k + 1, 1].max()))
lead = np.array(lead)
print('슬라이스 %d 개 · 슬라이스 stamp − 최신 map→odom stamp: 중앙 %+.3f · 95%% %+.3f · 최대 %+.3f s · 앞선(>0) 비율 %.1f %%' % (
    len(lead), np.median(lead[:, 1]), np.percentile(lead[:, 1], 95), lead[:, 1].max(), 100 * (lead[:, 1] > 0).mean()))
# 로그
def lt(l):
    m = re.search(r'\[(\d{10}\.\d+)\]', l); return float(m[1]) if m else None
W, C = [], []
for l in open(sys.argv[2], encoding='utf-8', errors='replace'):
    if "Can't transform" in l and 'global_costmap' in l: W.append(lt(l))
    elif 'Control loop missed' in l: C.append(lt(l))
W = [w for w in W if w]; C = np.array([c for c in C if c])
t0, t1 = MO[0, 0], MO[-1, 0]; W = [w for w in W if t0 <= w <= t1]; Cw = C[(C >= t0) & (C <= t1)]
near = [np.abs(Cw - w).min() if len(Cw) else 99 for w in W]
print('주행 창 경고 %d 번 · Control loop missed %d 번(창 %.0f s) · 경고 ±0.5 s 안에 missed 있음 %d/%d' % (len(W), len(Cw), t1 - t0, sum(n <= 0.5 for n in near), len(W)))
# 우연 기준: 무작위 시각에서 ±0.5 s 안에 missed 있을 확률
rs = np.random.default_rng(0).uniform(t0, t1, 2000); p = np.mean([np.abs(Cw - r).min() <= 0.5 for r in rs])
print('  우연 기준(무작위 시각 ±0.5 s 안 missed 확률) %.0f %%' % (100 * p))
print('경고 시각별: 경고 · 직전 map→odom 수신 간격(그 시각을 포함한 공백) · 그 슬라이스의 앞섬')
for w in W:
    k = np.searchsorted(MO[:, 0], w); gap = MO[k, 0] - MO[k - 1, 0] if 0 < k < len(MO) else -1
    j = np.searchsorted(lead[:, 0], w) - 1
    print('  %s 공백 %.3f s (%s → %s) · 앞섬 %+.3f s · missed ±%.2f s' % (hs(w), gap, hs(MO[k - 1, 0]), hs(MO[k, 0]), lead[j, 1] if j >= 0 else float('nan'), np.abs(Cw - w).min()))
