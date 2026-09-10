#!/usr/bin/env python3
"""정지 상태 깊이 지속성 측정 (2026-09-10).

  왜: job205 CSV 에서 로버가 **전혀 움직이지 않은** t=0~1.5 구간에 상자 깊이점이
      84→54→64→32→42→105→228→146→27→2→0 으로 요동치다 사라졌다.
      거리가 안 변했으므로 '가까워져서 화각을 벗어났다' 로는 설명되지 않는다.
      (A) 카메라(자동노출/레이저 수렴)  vs  (B) 계측(map 고정 사각형이 SLAM 보정으로 어긋남)
      을 가른다. 로버를 세워 두고 **base_link 기준** 고정 영역을 보면 SLAM 과 무관해진다.

  사용: python3 job209_static.py [초=60] [간격=0.5]
"""
import sys, time, math
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from geometry_msgs.msg import Twist
from rclpy.qos import qos_profile_sensor_data

DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
STEP = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5

rclpy.init(); n = Node('static209')
S = {}
n.create_subscription(PointCloud2, '/camera/camera/depth/color/points',
                      lambda m: S.__setitem__('pc', m), qos_profile_sensor_data)
pub = n.create_publisher(Twist, '/cmd_vel', 10)


def xyz():
    """base_link 기준 점군. 카메라 광학축 → base_link 변환은 TF 로 하지 않고
       URDF 고정값을 쓴다(정지 상태이므로 TF 지연·보정의 영향을 배제)."""
    if 'pc' not in S:
        return None
    m = S['pc']
    off = {f.name: f.offset for f in m.fields}
    if not {'x', 'y', 'z'} <= set(off):
        return None
    buf = np.frombuffer(m.data, dtype=np.uint8)
    stride = m.point_step
    cnt = len(buf) // stride
    arr = buf[:cnt*stride].reshape(cnt, stride)

    def col(name):
        o = off[name]
        return arr[:, o:o+4].copy().view(np.float32).reshape(-1)
    X, Y, Z = col('x'), col('y'), col('z')
    ok = np.isfinite(X) & np.isfinite(Y) & np.isfinite(Z) & (Z > 0.01)
    X, Y, Z = X[ok], Y[ok], Z[ok]
    # optical(x우 y하 z전) → base_link(x전 y좌 z상), URDF camera_link 오프셋
    bx = Z + 0.232
    by = -X + 0.0475
    bz = -Y + 0.143
    return np.stack([bx, by, bz], axis=1)


print('카메라 대기...')
t0 = time.time()
while time.time() - t0 < 10 and 'pc' not in S:
    rclpy.spin_once(n, timeout_sec=0.1)
if 'pc' not in S:
    print('포인트클라우드 없음 — 중단'); sys.exit(1)

# 초기 3초: 낮은 물체(상자) 후보 위치 확정
print('상자 후보 탐색 3초...')
cand = []
t0 = time.time()
while time.time() - t0 < 3.0:
    rclpy.spin_once(n, timeout_sec=0.05)
    P = xyz()
    if P is None:
        continue
    sel = P[(P[:, 0] > 0.5) & (P[:, 0] < 1.4) & (np.abs(P[:, 1]) < 0.35)
            & (P[:, 2] > 0.06) & (P[:, 2] < 0.30)]
    if len(sel) >= 20:
        cand.append(np.median(sel, axis=0))
if not cand:
    print('낮은 물체 후보 없음 — 상자가 처음부터 안 보인다'); sys.exit(2)
C = np.median(np.array(cand), axis=0)
print('상자 후보 중심 (base_link) x=%.3f y=%.3f z=%.3f  (샘플 %d)' % (C[0], C[1], C[2], len(cand)))
HX, HY = 0.14, 0.14      # 상자 반폭 0.09 + 여유
print('추적 창: x %.2f~%.2f, y %.2f~%.2f, z 0.04~0.35'
      % (C[0]-HX, C[0]+HX, C[1]-HY, C[1]+HY))
print()
print('   t   전체점  장애물층  상자창  상자z중앙  상자x중앙   비고')

zero_from = None
rows = []
t0 = time.time(); nxt = 0.0
while time.time() - t0 < DUR:
    rclpy.spin_once(n, timeout_sec=0.05)
    el = time.time() - t0
    if el < nxt:
        continue
    nxt += STEP
    P = xyz()
    if P is None:
        continue
    tot = len(P)
    obs = P[(P[:, 0] > 0.3) & (P[:, 0] < 1.45) & (P[:, 2] > 0.06) & (P[:, 2] < 0.40)]
    box = P[(np.abs(P[:, 0]-C[0]) < HX) & (np.abs(P[:, 1]-C[1]) < HY)
            & (P[:, 2] > 0.04) & (P[:, 2] < 0.35)]
    zc = np.median(box[:, 2]) if len(box) else float('nan')
    xc = np.median(box[:, 0]) if len(box) else float('nan')
    rows.append((el, tot, len(obs), len(box)))
    if len(box) == 0 and zero_from is None:
        zero_from = el
    if len(box) > 0:
        zero_from = None
    print('%6.1f  %6d   %6d   %5d    %6.3f    %6.3f' % (el, tot, len(obs), len(box), zc, xc))

print()
b = np.array([r[3] for r in rows])
o = np.array([r[2] for r in rows])
t = np.array([r[0] for r in rows])
print('=== 요약 (%d 샘플, %.0f초) ===' % (len(rows), DUR))
print('  상자창 점수 : 최소 %d  최대 %d  중앙 %.0f  평균 %.1f' % (b.min(), b.max(), np.median(b), b.mean()))
print('  0 인 샘플   : %d / %d (%.0f%%)' % ((b == 0).sum(), len(b), 100.0*(b == 0).sum()/len(b)))
print('  장애물층    : 최소 %d  최대 %d  중앙 %.0f' % (o.min(), o.max(), np.median(o)))
if (b == 0).any():
    print('  최초 0 시각 : %.1f s' % t[b == 0][0])
    # 연속 0 최장 구간
    best = cur = 0; s = None; bs = None
    for i, v in enumerate(b):
        if v == 0:
            if s is None: s = t[i]
            cur += 1
            if cur > best: best, bs = cur, s
        else:
            cur = 0; s = None
    print('  연속 0 최장 : %.1f 초 (t=%.1f 부터)' % (best*STEP, bs))
print()
if (b > 0).mean() > 0.9:
    print('판정 → (B) 계측 문제. 정지 상태에서 깊이는 계속 나온다.')
elif (b == 0).mean() > 0.9:
    print('판정 → 상자가 이 창에 거의 안 잡힌다. 창 위치나 상자 배치를 다시 본다.')
else:
    print('판정 → (A) 카메라 쪽. 정지·같은 거리인데 깊이가 들락거린다.')
