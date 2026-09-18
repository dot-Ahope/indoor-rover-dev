#!/usr/bin/env python3
"""SLAM(map) 자세로 본 '진행 방향 − 몸체 방향'(게걸음 각) 통계 (2026-09-18). 인자: BAG GOAL_EPOCH [...]
  SLAM 보정 시각마다 map 자세 = map->odom ∘ odom->base_link. 연속 보정 사이 변위의 몸체(중간 heading) 기준 옆/앞 비 → 각.
  같은 구간 odom 자세로도 계산(EKF 가 vy=0 이므로 ≈0 이 기준선).
  - 각이 회전 방향·속도와 무관하게 일정 → 센서 장착 yaw 오차 또는 일정한 기구적 게걸음
  - 회전 방향에 따라 부호가 바뀜 → 옆미끄럼
"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def load(bag, G):
    r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
    mo, ob = [], []; k = 0
    while r.has_next():
        topic, data, ts = r.read_next(); k += 1
        if topic != '/tf':
            continue
        for tr in deserialize_message(data, TFMessage).transforms:
            st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9 - G
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                mo.append((st, k, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                ob.append((st, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
    # 09-18 버그 수정: slam_toolbox 는 같은 stamp 로 map->odom 을 두 번 보내고, 보정 순간엔 두 값이 다르다(보정 전·후).
    #   stamp 로만 정렬하면 두 값 순서가 뒤바뀌어 한 보정을 두 번 셌다(되돌림은 길이 0 구간이라 버려짐). → 같은 stamp 는 마지막 수신값만.
    mo.sort(key=lambda m: (m[0], m[1])); ded = {}
    for m in mo: ded[m[0]] = (m[0], m[2], m[3], m[4])
    mo = sorted(ded.values()); ob.sort()
    return np.array(mo), np.array(ob)


def odom_at(ob, t):
    ts = ob[:, 0]; k = min(max(bisect.bisect_left(ts, t), 1), len(ts) - 1)
    a, b = ob[k - 1], ob[k]; w = 0.0 if b[0] == a[0] else min(max((t - a[0]) / (b[0] - a[0]), 0), 1)
    return np.array([a[1] + w * (b[1] - a[1]), a[2] + w * (b[2] - a[2]), a[3] + w * wrap(b[3] - a[3])])


def compose(M, p):
    c, s = math.cos(M[3]), math.sin(M[3])
    return np.array([M[1] + c * p[0] - s * p[1], M[2] + s * p[0] + c * p[1], wrap(M[3] + p[2])])


def crab(P0, P1):
    d = P1[:2] - P0[:2]; h = P0[2] + wrap(P1[2] - P0[2]) / 2
    f = d[0] * math.cos(h) + d[1] * math.sin(h); l = -d[0] * math.sin(h) + d[1] * math.cos(h)
    return f, l, wrap(P1[2] - P0[2])


allr = []
print('%-5s | 구간 | SLAM 게걸음 각(거리가중) 평균 / 중앙 / IQR | odom 기준선 | 왼회전 / 오른회전 / 직선 (각, 거리)' % 'run')
args = sys.argv[1:]
for k in range(0, len(args), 2):
    bag, G = args[k], float(args[k + 1]); name = bag.split('_')[-1]
    mo, ob = load(bag, G)
    tend = ob[-1, 0]
    idx = [0]
    for i in range(1, len(mo)):
        j = idx[-1]
        if math.hypot(mo[i, 1] - mo[j, 1], mo[i, 2] - mo[j, 2]) > 0.0005 or abs(wrap(mo[i, 3] - mo[j, 3])) > math.radians(0.01):
            idx.append(i)
    rows = []
    for a, b in zip(idx, idx[1:]):
        t0, t1 = mo[a, 0], mo[b, 0]
        if t0 < 0 or t1 > tend:
            continue
        # 보정 직후 자세끼리: 구간 시작 = 새 보정(a) 적용된 map 자세, 끝 = 다음 보정(b) 적용된 map 자세
        p0o, p1o = odom_at(ob, t0), odom_at(ob, t1)
        P0, P1 = compose(mo[a], p0o), compose(mo[b], p1o)
        f, l, dpsi = crab(P0, P1)
        fo, lo, _ = crab(p0o, p1o)
        if f < 0.02:          # 전진 2 cm 미만(정지·제자리 회전)은 각이 불안정 → 제외
            continue
        rows.append((f, l, dpsi, fo, lo, P0[2] + wrap(P1[2] - P0[2]) / 2))   # 마지막 = 구간 중간 map heading
    R = np.array(rows); allr.append(R)
    ang = np.degrees(np.arctan2(R[:, 1], R[:, 0])); w = R[:, 0]
    ango = np.degrees(np.arctan2(R[:, 4], R[:, 3]))
    def cat(sel):
        return '%+.2f° (%.2f m)' % (np.degrees(math.atan2(R[sel, 1].sum(), R[sel, 0].sum())), R[sel, 0].sum()) if sel.any() else '-'
    L = R[:, 2] > math.radians(2); Rr = R[:, 2] < -math.radians(2); S = ~(L | Rr)
    q1, q3 = np.percentile(ang, [25, 75])
    print('%-5s | %3d | %+.2f° / %+.2f° / %.2f° | %+.2f° | %s / %s / %s' % (name, len(R), np.degrees(math.atan2(R[:, 1].sum(), R[:, 0].sum())), np.median(ang), q3 - q1,
          np.degrees(math.atan2(R[:, 4].sum(), R[:, 3].sum())), cat(L), cat(Rr), cat(S)))
R = np.concatenate(allr)
ang = np.degrees(np.arctan2(R[:, 1], R[:, 0]))
print('통합 %d 구간 %.2f m: SLAM 게걸음 각 %+.2f° (거리가중), 중앙 %+.2f°, odom 기준선 %+.2f°' % (len(R), R[:, 0].sum(), np.degrees(math.atan2(R[:, 1].sum(), R[:, 0].sum())), np.median(ang),
      np.degrees(math.atan2(R[:, 4].sum(), R[:, 3].sum()))))
# 회전율과의 관계: 구간 회전량/거리(곡률)별
k = R[:, 2] / R[:, 0]
for lo_, hi_ in ((-9, -1.0), (-1.0, -0.3), (-0.3, 0.3), (0.3, 1.0), (1.0, 9)):
    s = (k >= lo_) & (k < hi_)
    if s.any():
        print('  곡률 %+.1f~%+.1f rad/m: %3d 구간 %.2f m → 각 %+.2f°' % (lo_, hi_, s.sum(), R[s, 0].sum(), np.degrees(math.atan2(R[s, 1].sum(), R[s, 0].sum()))))

# 바닥 기울기 점검: 기울기로 옆으로 흐르면 게걸음 각이 map heading 에 따라 바뀐다(장착 오차면 일정)
hd = np.degrees(R[:, 5])
for lo_, hi_ in ((-90, -20), (-20, -5), (-5, 5), (5, 20), (20, 90)):
    sel = (hd >= lo_) & (hd < hi_)
    if sel.any():
        print('  heading %+3d~%+3d°: %3d 구간 %.2f m → 각 %+.2f°' % (lo_, hi_, sel.sum(), R[sel, 0].sum(), np.degrees(math.atan2(R[sel, 1].sum(), R[sel, 0].sum()))))
