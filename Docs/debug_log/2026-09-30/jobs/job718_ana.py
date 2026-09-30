#!/usr/bin/env python3
"""09-30 §16: 매핑 bag 에서 map→odom(SLAM 보정) 시계열의 점프 찾기 + 그 시각의 로버 운동.
   - map→odom 연속 표본 사이 변화 > 5 cm 또는 > 2° 를 점프로 표시(정상 보정은 스캔마다 mm~cm)
   - 각 점프 직전 3 s 의 휠 ω·자이로 ω·선속도(무엇을 하던 중인지), odom 위치
   - 10 s 간격 요약: map→odom, odom 자세, 회전/직진 속도 최대
   인자: BAG"""
import sys, math
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

r = rosbag2_py.SequentialReader()
r.open(rosbag2_py.StorageOptions(uri=sys.argv[1], storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
mo, ob, wh, gy, sc = [], [], [], [], []


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if tp == '/tf':
        m = deserialize_message(data, get_message(types[tp]))
        for tr in m.transforms:
            a, c = tr.header.frame_id, tr.child_frame_id
            v = (t, tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))
            if a == 'map' and c == 'odom': mo.append(v)
            elif a == 'odom' and c == 'base_link': ob.append(v)
    elif tp == '/wheel_odom':
        m = deserialize_message(data, get_message(types[tp])); wh.append((t, m.twist.twist.linear.x, m.twist.twist.angular.z))
    elif tp == '/imu/data':
        m = deserialize_message(data, get_message(types[tp])); gy.append((t, -m.angular_velocity.y))
    elif tp == '/scan':
        sc.append(t)
mo, ob, wh, gy = map(np.array, (mo, ob, wh, gy))
t0 = ob[0, 0]
print('표본: map→odom %d, odom→base %d, 휠 %d, 자이로 %d, scan %d, 길이 %.0f s' % (len(mo), len(ob), len(wh), len(gy), len(sc), ob[-1, 0] - t0))
# 같은 stamp 두 번 발행 → 시간 중복 제거(마지막 값)
_, idx = np.unique(mo[:, 0][::-1], return_index=True); mo = mo[::-1][idx]; mo = mo[np.argsort(mo[:, 0])]
d = np.hypot(np.diff(mo[:, 1]), np.diff(mo[:, 2])); da = np.degrees(np.abs((np.diff(mo[:, 3]) + np.pi) % (2 * np.pi) - np.pi))
J = np.where((d > 0.05) | (da > 2.0))[0]
print('\n== map→odom 점프(>5 cm 또는 >2°): %d 건' % len(J))
import time as _t
for k in J[:40]:
    t = mo[k + 1, 0]; w = (wh[:, 0] > t - 3) & (wh[:, 0] < t); g = (gy[:, 0] > t - 3) & (gy[:, 0] < t)
    i = np.searchsorted(ob[:, 0], t); i = min(i, len(ob) - 1)
    print('%s (+%5.1f s) 점프 %.2f m %+.1f° | map→odom (%+.2f,%+.2f,%+.1f°)→(%+.2f,%+.2f,%+.1f°) | 직전3s 휠v최대 %.3f 휠ω최대 %.2f 자이로ω최대 %.2f | odom (%+.2f,%+.2f,%+.0f°)' % (
        _t.strftime('%H:%M:%S', _t.localtime(t)), t - t0, d[k], math.degrees(((mo[k + 1, 3] - mo[k, 3]) + math.pi) % (2 * math.pi) - math.pi),
        mo[k, 1], mo[k, 2], math.degrees(mo[k, 3]), mo[k + 1, 1], mo[k + 1, 2], math.degrees(mo[k + 1, 3]),
        np.abs(wh[w, 1]).max() if w.any() else 0, np.abs(wh[w, 2]).max() if w.any() else 0, np.abs(gy[g, 1]).max() if g.any() else 0,
        ob[i, 1], ob[i, 2], math.degrees(ob[i, 3])))
print('\n== 10 s 요약: 시각 | map→odom | odom 자세 | 휠 v 최대·휠 ω 최대·자이로 ω 최대 | 휠ω−자이로ω 평균차')
for ts in np.arange(t0, ob[-1, 0], 10.0):
    k = min(np.searchsorted(mo[:, 0], ts + 10), len(mo) - 1); i = min(np.searchsorted(ob[:, 0], ts + 10), len(ob) - 1)
    w = (wh[:, 0] >= ts) & (wh[:, 0] < ts + 10); g = (gy[:, 0] >= ts) & (gy[:, 0] < ts + 10)
    gi = np.interp(wh[w, 0], gy[:, 0], gy[:, 1]) if w.any() else np.array([0])
    print('%s (+%4.0f) | (%+.2f,%+.2f,%+5.1f°) | (%+.2f,%+.2f,%+4.0f°) | %.3f %.2f %.2f | %+.3f' % (
        _t.strftime('%H:%M:%S', _t.localtime(ts + 10)), ts + 10 - t0, mo[k, 1], mo[k, 2], math.degrees(mo[k, 3]),
        ob[i, 1], ob[i, 2], math.degrees(ob[i, 3]),
        np.abs(wh[w, 1]).max() if w.any() else 0, np.abs(wh[w, 2]).max() if w.any() else 0, np.abs(gy[g, 1]).max() if g.any() else 0,
        (wh[w, 2] - gi).mean() if w.any() else 0))
