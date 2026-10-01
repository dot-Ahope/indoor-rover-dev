#!/usr/bin/env python3
"""10-01 §8.11: STUCK 판정(14:02:52.67) 때 stuck_monitor 와 같은 방식으로 앞(0°)·뒤(180°) ±20° 섹터를 재현 — 2 s 전 스캔 A vs 마지막 B.
   섹터별 유효 점 수(<3 m), A·B 중앙 range, median(A−B). 자이로 회전 보정은 bag 의 /imu/data 적분으로."""
import sys, math, datetime, numpy as np, rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
LIDAR_YAW = math.pi - 0.04677; BINS = 360
def profile(m):
    r = np.asarray(m.ranges, dtype=np.float32); a = m.angle_min + m.angle_increment * np.arange(len(r)) + LIDAR_YAW
    ok = np.isfinite(r) & (r > m.range_min) & (r < min(m.range_max, 12.0)); p = np.full(BINS, np.inf, np.float32)
    np.minimum.at(p, (np.degrees(a[ok]) % 360).astype(int) % BINS, r[ok]); p[np.isinf(p)] = np.nan; return p
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=sys.argv[1], storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
T = datetime.datetime.now().replace(hour=14, minute=2, second=52, microsecond=670000).timestamp()
sc, gy = [], []
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if not (T - 3 <= t <= T + 0.2): continue
    if tp == '/scan': sc.append((t, profile(deserialize_message(data, get_message(types[tp])))))
    elif tp == '/imu/data': gy.append((t, -deserialize_message(data, get_message(types[tp])).angular_velocity.y))
B = [s for s in sc if s[0] <= T][-1]; A = [s for s in sc if s[0] <= B[0] - 2.0][-1]
g = np.array(gy); m = (g[:, 0] >= A[0]) & (g[:, 0] <= B[0]); roll = math.degrees(np.sum(g[m][1:, 1] * np.diff(g[m][:, 0])))
Br = np.roll(B[1], int(round(roll)))
print('A %.2f s 전, 자이로 회전 %+.1f°' % (B[0] - A[0], roll))
for c in (0, 180):
    idx = [(c + k) % 360 for k in range(-20, 21)]; a, b = A[1][idx], Br[idx]
    ok = np.isfinite(a) & np.isfinite(b) & (a < 3) & (b < 3)
    print('섹터 %3d°: 3 m 안 유효 %2d 개 | A 중앙 %.2f · B 중앙 %.2f m | median(A−B) %+.3f m | 그 섹터 전체(제한 없음) A 중앙 %.2f m' % (
        c, ok.sum(), np.nanmedian(a[ok]) if ok.any() else np.nan, np.nanmedian(b[ok]) if ok.any() else np.nan,
        np.median(a[ok] - b[ok]) if ok.sum() >= 8 else np.nan, np.nanmedian(a)))
    if ok.any(): print('   유효 빈(각도: A→B): ' + ' '.join('%d:%.2f→%.2f' % ((c + k) % 360, A[1][(c + k) % 360], Br[(c + k) % 360]) for k in range(-20, 21) if ok[k + 20])[:600])
# 비교: 자이로 대신 스캔 상관 회전(use_gyro=false 일 때 실제 경로)으로 roll
sys.path.insert(0, '/home/jetson/ros2_ws/install/rover_bringup/lib/rover_bringup')
import importlib.util
spec = importlib.util.spec_from_file_location('sm', '/home/jetson/ros2_ws/install/rover_bringup/lib/rover_bringup/stuck_monitor.py'); sm = importlib.util.module_from_spec(spec); spec.loader.exec_module(sm)
rs = sm.rot_shift_deg(A[1], B[1]); Br2 = np.roll(B[1], int(round(rs))) if rs is not None else B[1]
f, b = sm.sector_delta(A[1], Br2, 0), sm.sector_delta(A[1], Br2, 180)
print('스캔 상관 회전 %s° → 앞 %s · 뒤 %s m (실시간 판정 "관측 0.1cm/8.9°" 재현 여부)' % (rs, f, b))
fg, bg = sm.sector_delta(A[1], Br, 0), sm.sector_delta(A[1], Br, 180)
print('자이로 회전 %+.1f° → 앞 %s · 뒤 %s m' % (roll, fg, bg))
