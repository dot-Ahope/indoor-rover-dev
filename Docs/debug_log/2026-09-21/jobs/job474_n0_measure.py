#!/usr/bin/env python3
"""N0 정지 측정 (2026-09-21, 계획서 §5.1). 컨테이너 안에서 실행(nvblox_msgs 필요). 인자: NAME SEC [BOX_FRONT_X BOX_CY]  (base_link 기준 상자 전면 x·중심 y, 게이트 감사값)
  구독: nvblox ESDF 2D 슬라이스(nvblox_msgs/DistanceMapSlice, 기본 토픽 /nvblox_node/static_map_slice — 실제 이름은 실행 후 확인) 를 SEC 초.
  (i) 상자 가장자리: 슬라이스에서 거리 ≤ 0(장애물 안) 셀 중 로버 진행 방향 앞·상자 y 띠 안의 최소 x → 물리 전면 x 와 차(셀 단위)
  (ii) 근거리 자취: 카메라 0.45 m 안(앞단 기준 0.43) 구역의 장애물 셀 수 프레임별 → 0 이어야
  (iii) 슬라이스 수신 주기·지연(header stamp − 수신), 프레임 수
  좌표: 슬라이스는 global_frame(odom). base_link 자세는 TF(odom→base_link)로 매 프레임 조회.
"""
import sys, time, math
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
import tf2_ros
from nvblox_msgs.msg import DistanceMapSlice
NAME, SEC = sys.argv[1], float(sys.argv[2])
BX = float(sys.argv[3]) if len(sys.argv) > 3 else float('nan'); BY = float(sys.argv[4]) if len(sys.argv) > 4 else float('nan')
HL, HW, CAMX = 0.25, 0.165, 0.234
rclpy.init(); n = Node('n0measure474'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
FR = []; TOPIC = sys.argv[5] if len(sys.argv) > 5 else '/nvblox_node/static_map_slice'


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def cb(m):
    trecv = time.time(); st = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
    try:
        t = buf.lookup_transform(m.header.frame_id, 'base_link', rclpy.time.Time()).transform
    except Exception:
        FR.append(None); return
    px, py, pth = t.translation.x, t.translation.y, yaw_of(t.rotation)
    d = np.asarray(m.data, dtype=np.float32).reshape(m.height, m.width)
    known = d != m.unknown_value
    jj, ii = np.where(known)
    X = m.origin.x + (ii + 0.5) * m.resolution - px; Y = m.origin.y + (jj + 0.5) * m.resolution - py
    c, s = math.cos(-pth), math.sin(-pth); rx = X * c - Y * s; ry = X * s + Y * c   # base_link 좌표
    dist = d[jj, ii]
    obst = dist <= 0.0
    # (i) 상자 띠: y ∈ [BY−0.14, BY+0.14], x ∈ [0.5, 2.0]
    band = obst & (np.abs(ry - BY) < 0.14) & (rx > 0.5) & (rx < 2.0) if not math.isnan(BY) else obst & (rx > 0.5) & (rx < 2.0) & (np.abs(ry) < 0.3)
    front = float(rx[band].min()) if band.any() else float('nan')
    nb = int(band.sum())
    # (ii) 근거리: 카메라에서 0.45 m 안, 앞쪽 x > 0.25(앞단), |y| < 0.5
    near = obst & (np.hypot(rx - CAMX, ry) < 0.45) & (rx > 0.25) & (np.abs(ry) < 0.5)
    # 자유 공간 최소 거리(로버 중심 기준, 정보용)
    FR.append((trecv, st, front, nb, int(near.sum()), int(obst.sum()), int(known.sum()), m.resolution, m.width, m.height))


n.create_subscription(DistanceMapSlice, TOPIC, cb, qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < SEC + 3.0:
    rclpy.spin_once(n, timeout_sec=0.05)
rclpy.shutdown()
fr = [f for f in FR if f is not None]; notf = sum(1 for f in FR if f is None)
print('==== %s: 슬라이스 %d 프레임 (%.1f s, TF 실패 %d) 토픽 %s' % (NAME, len(fr), SEC, notf, TOPIC))
if not fr:
    sys.exit(1)
tr = np.array([f[0] for f in fr]); lag = np.array([f[0] - f[1] for f in fr]); fx = np.array([f[2] for f in fr]); nb = np.array([f[3] for f in fr]); near = np.array([f[4] for f in fr]); ob = np.array([f[5] for f in fr])
dtr = np.diff(tr)
print('  (iii) 수신 %.2f Hz, 간격 중앙 %.3f 최대 %.3f s | stamp 지연 중앙 %.3f 최대 %.3f s | 해상도 %.3f m, %dx%d' % ((len(tr) - 1) / (tr[-1] - tr[0]), np.median(dtr), dtr.max(), np.median(lag), lag.max(), fr[0][7], fr[0][8], fr[0][9]))
print('  (i) 상자 띠 장애물 셀 최소 x(base): 중앙 %.3f 최소 %.3f 최대 %.3f (프레임당 셀 %.0f) | 물리 전면 %.3f → 차 %+.3f m = %+.1f 셀' % (
    np.nanmedian(fx), np.nanmin(fx), np.nanmax(fx), np.median(nb), BX, np.nanmedian(fx) - BX, (np.nanmedian(fx) - BX) / fr[0][7]))
print('  (ii) 카메라 0.45 m 안 장애물 셀: 프레임당 중앙 %.0f 최대 %d, 0 이 아닌 프레임 %d/%d | 전체 장애물 셀 중앙 %.0f' % (np.median(near), near.max(), (near > 0).sum(), len(near), np.median(ob)))
