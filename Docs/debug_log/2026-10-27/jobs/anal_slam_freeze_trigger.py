#!/usr/bin/env python3
"""anal_slam_freeze_trigger — §26 SLAM map→odom stamp 정체가 무엇에 맞춰 나나 (2026-10-27, PC).
  가설 ① 스캔 처리 조건(위치 추정: 이동 0.30 m 또는 회전 0.15 rad 마다 정합) — 처리할 때마다 오래 걸림
       → 정체 직전 '마지막 처리 뒤 누적 이동 · 회전' 이 문턱에 걸쳐 있어야 하고, 정체 간 이동/회전이 문턱 근처로 모여야 함.
  가설 ② 지도 갱신 주기(map_update_interval 10 s) → 정체 간격이 10 s 배수로 모여야 함.
  가설 ③ 회전 · 정지 등 운동 상태와 무관한 무작위.
  정체 = 새 stamp 간격 > 0.4 s. odom→base_link(EKF) 로 이동 · 회전을 잰다. 로버가 서 있을 때(1 s 이동 < 1 cm · 회전 < 1°)의 정체 수도.
  인자: bag폴더"""
import sys, math, time
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
hs = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + '.%02d' % int((t % 1) * 100)
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
MO, OB = [], []
with AnyReader([Path(sys.argv[1])], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/tf']):
        for tr in rd.deserialize(raw, c.msgtype).transforms:
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((t * 1e-9, tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9))
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((t * 1e-9, tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation)))
MO = np.array(sorted(MO)); OB = np.array(sorted(OB))
ob_t = OB[:, 0]; seg = np.r_[0, np.cumsum(np.hypot(*np.diff(OB[:, 1:3], axis=0).T))]
dyaw = np.r_[0, np.cumsum(np.abs((np.diff(OB[:, 3]) + np.pi) % (2 * np.pi) - np.pi))]
at = lambda t: int(np.clip(np.searchsorted(ob_t, t), 0, len(ob_t) - 1))
new = np.r_[True, np.diff(MO[:, 1]) != 0]; S = MO[new]
F = [(S[i, 0], S[i + 1, 0], S[i + 1, 1] - S[i, 1]) for i in range(len(S) - 1) if S[i + 1, 1] - S[i, 1] > 0.4]   # (정체 시작 수신, 끝 수신, 길이)
print('정체(> 0.4 s) %d 번' % len(F))
st = np.array([f[0] for f in F])
gaps = np.diff(st); print('정체 사이 시간: 중앙 %.1f s · 10 s 배수(±1 s) 비율 %.0f %% (무작위면 약 20 %%)' % (np.median(gaps), 100 * np.mean(np.abs(gaps / 10 - np.round(gaps / 10)) * 10 <= 1.0)))
dd = np.array([seg[at(st[k + 1])] - seg[at(st[k])] for k in range(len(st) - 1)]); da = np.array([dyaw[at(st[k + 1])] - dyaw[at(st[k])] for k in range(len(st) - 1)])
print('정체 사이 이동: 중앙 %.2f m · 10%% %.2f · 90%% %.2f | 회전: 중앙 %.2f rad · 10%% %.2f · 90%% %.2f' % (np.median(dd), np.percentile(dd, 10), np.percentile(dd, 90), np.median(da), np.percentile(da, 10), np.percentile(da, 90)))
print('  (이동 ≥ 0.30 m 또는 회전 ≥ 0.15 rad 인 정체 사이 %d/%d)' % (int(((dd >= 0.30) | (da >= 0.15)).sum()), len(dd)))
mov = []
for a, b, L in F:
    i = at(a - 1.0); j = at(a)
    v = (seg[j] - seg[i]); w = (dyaw[j] - dyaw[i])
    mov.append((v, w))
mov = np.array(mov); still = (mov[:, 0] < 0.01) & (mov[:, 1] < math.radians(1))
print('정체 직전 1 s 운동: 서 있음 %d · 직진 위주(회전 < 3°) %d · 회전 포함 %d' % (still.sum(), int(((~still) & (mov[:, 1] < math.radians(3))).sum()), int((mov[:, 1] >= math.radians(3)).sum())))
# 주행 전체에서 서 있던 시간 비율(비교)
tt = np.arange(ob_t[0] + 1, ob_t[-1], 0.5); sv = np.array([(seg[at(t)] - seg[at(t - 1)] < 0.01) and (dyaw[at(t)] - dyaw[at(t - 1)] < math.radians(1)) for t in tt])
print('주행 창에서 서 있는 시각 비율 %.0f %% (정체 중 서 있음 %.0f %%)' % (100 * sv.mean(), 100 * still.mean()))
# 처리 간격: stamp 가 바뀐 간격 분포(정상 처리 주기 확인)
g = np.diff(S[:, 1]); print('새 stamp 간격 분포: < 0.15 s %.0f %% · 0.15~0.4 %.0f %% · > 0.4 %.0f %%' % (100 * np.mean(g < 0.15), 100 * np.mean((g >= 0.15) & (g <= 0.4)), 100 * np.mean(g > 0.4)))
print('정체 길이: 중앙 %.2f · 최대 %.2f s' % (np.median([f[2] for f in F]), max(f[2] for f in F)))
