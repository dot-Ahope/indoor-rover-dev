#!/usr/bin/env python3
"""주행 중 새로 생기는 LETHAL 셀의 통계 (2026-09-11) — '유령 셀' 이 어디서 생기는가.

  job304: v5 정체를 만든 셀은 (+1.19,+0.17) 1셀·라이다 근거 0%·정체 3.7 s 전 출현. 같은 종류의 1~2셀 군집이
  전역 (+0.80,+0.69) (+14.6 s), 로컬 (+0.88,+0.77) (+16.3 s) 에도 있었다. 이들이 우연인지 체계적인지 본다.
  연속한 로컬 코스트맵 프레임을 비교해 '이번 프레임에서 처음 LETHAL 이 된 셀' 을 모으고,
    - 그 시각 /scan 점 0.10 m 안에 있는가(라이다 근거)
    - base_link 로부터 거리·방위, 카메라(camera_link)로부터 거리
    - 같은 프레임에서 붙어 있는 신규 셀 수(군집 크기)
  를 기록해 라이다 근거 없는 신규 셀의 카메라 거리 히스토그램을 낸다. 로버는 움직이지 않는다(bag 재생).
  또 첫 프레임 시각의 라이다 점만으로 지도를 그려 좌측에 무엇이 있는지 코스트맵 없이 본다.
"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan

BAG = sys.argv[1]
TOPIC = sys.argv[2] if len(sys.argv) > 2 else '/local_costmap/costmap'
LIDAR_MAP = len(sys.argv) > 3 and sys.argv[3] == 'map'


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


r = rosbag2_py.SequentialReader()
r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
mo, ob, grids, scans = [], [], [], []
static = {}
while r.has_next():
    topic, data, ts = r.read_next()
    t = ts * 1e-9
    if topic == '/tf':
        for tr in deserialize_message(data, TFMessage).transforms:
            tt = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                mo.append((tt, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                ob.append((tt, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
    elif topic == '/tf_static':
        for tr in deserialize_message(data, TFMessage).transforms:
            static[(tr.header.frame_id, tr.child_frame_id)] = (tr.transform.translation.x, tr.transform.translation.y, tr.transform.translation.z, yaw_of(tr.transform.rotation))
    elif topic == TOPIC:
        grids.append((t, deserialize_message(data, OccupancyGrid)))
    elif topic == '/scan':
        scans.append((t, deserialize_message(data, LaserScan)))
mo.sort(); ob.sort()
mo_t = [s[0] for s in mo]; ob_t = [s[0] for s in ob]; sc_t = [s[0] for s in scans]


def latest(seq, ts, t):
    i = bisect.bisect_right(ts, t) - 1
    return seq[i] if i >= 0 else None


def chain(child, root='base_link'):
    x = y = z = yaw = 0.0
    cur = child; hops = 0
    while cur != root and hops < 8:
        found = None
        for (p, c), tr in static.items():
            if c == cur:
                found = (p, tr); break
        if not found:
            return None
        p, (tx, ty, tz, tyaw) = found
        x, y = tx + x * math.cos(tyaw) - y * math.sin(tyaw), ty + x * math.sin(tyaw) + y * math.cos(tyaw)
        z += tz; yaw += tyaw; cur = p; hops += 1
    return (x, y, z, yaw) if cur == root else None


print('정적 프레임:', ', '.join('%s->%s' % k for k in sorted(static)))
cam = None
for cf in ('camera_link', 'camera_depth_frame', 'camera_depth_optical_frame', 'd455_link'):
    cam = chain(cf)
    if cam:
        print('카메라 %s -> base_link: (%.3f, %.3f, z %.3f)' % (cf, cam[0], cam[1], cam[2])); break
if not cam:
    cam = (0.15, 0.0, 0.0, 0.0); print('카메라 정적 TF 없음 → base_link 앞 0.15 m 가정')
l2b = chain(scans[0][1].header.frame_id) if scans else None
if l2b:
    print('라이다 -> base_link: (%.3f, %.3f, z %.3f, yaw %.0f°)' % l2b[:3] + (math.degrees(l2b[3]),) if False else '라이다 -> base_link: (%.3f, %.3f, z %.3f, yaw %.0f°)' % (l2b[0], l2b[1], l2b[2], math.degrees(l2b[3])))
else:
    l2b = (0, 0, 0, 0)


def pose_in(frame, t):
    b = latest(ob, ob_t, t)
    if frame == 'odom' or not mo:
        return (b[1], b[2], b[3])
    a = latest(mo, mo_t, t)
    _, mx, my, myaw = a
    return (mx + b[1] * math.cos(myaw) - b[2] * math.sin(myaw), my + b[1] * math.sin(myaw) + b[2] * math.cos(myaw), myaw + b[3])


def scan_points(frame, t):
    sc = latest(scans, sc_t, t)
    if not sc:
        return np.zeros((0, 2))
    s = sc[1]; rr = np.array(s.ranges); ang = s.angle_min + np.arange(len(rr)) * s.angle_increment
    ok = np.isfinite(rr) & (rr > s.range_min) & (rr < s.range_max)
    rr, ang = rr[ok], ang[ok]
    lx = rr * np.cos(ang); ly = rr * np.sin(ang)
    bx = l2b[0] + lx * math.cos(l2b[3]) - ly * math.sin(l2b[3]); by = l2b[1] + lx * math.sin(l2b[3]) + ly * math.cos(l2b[3])
    px, py, pyaw = pose_in(frame, sc[0])
    return np.column_stack([px + bx * math.cos(pyaw) - by * math.sin(pyaw), py + bx * math.sin(pyaw) + by * math.cos(pyaw)])


frame = grids[0][1].header.frame_id
print('%s (%s): %d 프레임, %.1f s' % (TOPIC, frame, len(grids), grids[-1][0] - grids[0][0]))
prev = None
new_cells = []   # (t, x, y, lidar_supported, dist_base, bearing_deg, dist_cam, cluster_size)
for tg, gg in grids:
    res = gg.info.resolution; ox0, oy0 = gg.info.origin.position.x, gg.info.origin.position.y
    dd = np.array(gg.data, dtype=np.int16).reshape(gg.info.height, gg.info.width)
    jj, ii = np.where(dd >= 100)
    cur = set(zip(((ox0 + (ii + 0.5) * res) / res).round().astype(int).tolist(), ((oy0 + (jj + 0.5) * res) / res).round().astype(int).tolist()))
    if prev is not None:
        new = cur - prev
        if new:
            sp = scan_points(frame, tg)
            px, py, pyaw = pose_in(frame, tg)
            cxg = px + cam[0] * math.cos(pyaw) - cam[1] * math.sin(pyaw); cyg = py + cam[0] * math.sin(pyaw) + cam[1] * math.cos(pyaw)
            # 신규 셀끼리 8-연결 군집 크기
            newset = set(new); seen = set(); size = {}
            for c in newset:
                if c in seen:
                    continue
                q = [c]; seen.add(c); comp = [c]
                while q:
                    a = q.pop()
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            b = (a[0] + dx, a[1] + dy)
                            if b in newset and b not in seen:
                                seen.add(b); q.append(b); comp.append(b)
                for c2 in comp:
                    size[c2] = len(comp)
            for (i, j) in new:
                x = i * res; y = j * res
                sup = bool(len(sp)) and np.hypot(sp[:, 0] - x, sp[:, 1] - y).min() < 0.10
                dxb, dyb = x - px, y - py
                bx = dxb * math.cos(pyaw) + dyb * math.sin(pyaw); by = -dxb * math.sin(pyaw) + dyb * math.cos(pyaw)
                new_cells.append((tg - grids[0][0], x, y, sup, math.hypot(bx, by), math.degrees(math.atan2(by, bx)), math.hypot(x - cxg, y - cyg), size[(i, j)], bx, by))
    prev = cur
nc = new_cells
print('신규 LETHAL 셀 %d개 (첫 프레임 제외). 라이다 근거 있음 %d, 없음 %d'
      % (len(nc), sum(1 for c in nc if c[3]), sum(1 for c in nc if not c[3])))
ghost = [c for c in nc if not c[3]]
small = [c for c in ghost if c[7] <= 2]
print('라이다 근거 없는 신규 셀 중 군집 ≤2셀(고립): %d개' % len(small))
print('  카메라 거리 히스토그램 (고립 유령 셀):')
edges = [0, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.5, 2.0, 9]
for lo, hi in zip(edges[:-1], edges[1:]):
    k = [c for c in small if lo <= c[6] < hi]
    print('    %.1f~%.1f m: %3d개  %s' % (lo, hi, len(k), '#' * len(k)))
print('  base_link 기준 방위 히스토그램 (고립 유령 셀):')
for lo, hi in ((-180, -90), (-90, -45), (-45, -15), (-15, 15), (15, 45), (45, 90), (90, 180)):
    k = [c for c in small if lo <= c[5] < hi]
    print('    %+4d~%+4d°: %3d개' % (lo, hi, len(k)))
print('  전방 시야(±45°) 고립 유령 셀의 base_link 거리 분포: ', end='')
fwd = sorted(c[4] for c in small if abs(c[5]) < 45)
if fwd:
    print('n=%d, 최소 %.2f, 25%% %.2f, 중앙 %.2f, 75%% %.2f, 최대 %.2f' % (len(fwd), fwd[0], fwd[len(fwd) // 4], fwd[len(fwd) // 2], fwd[3 * len(fwd) // 4], fwd[-1]))
else:
    print('없음')
print('  라이다 근거 있는 신규 셀의 base_link 거리: ', end='')
sup_d = sorted(c[4] for c in nc if c[3])
if sup_d:
    print('n=%d, 최소 %.2f, 중앙 %.2f, 최대 %.2f' % (len(sup_d), sup_d[0], sup_d[len(sup_d) // 2], sup_d[-1]))
else:
    print('없음')
print('  고립 유령 셀 목록 (시각 s, 차체좌표 전방/횡, 카메라거리):')
for c in small[:40]:
    print('    t=%5.1f  전방 %+.2f 횡 %+.2f  카메라 %.2f m' % (c[0], c[8], c[9], c[6]))

if LIDAR_MAP:
    t = grids[0][0]
    sp = scan_points(frame, t)
    px, py, pyaw = pose_in(frame, t)
    print()
    print('첫 프레임 라이다 점 지도 (로버 첫 자세 기준, 0.05 m; 행=전방, 열=횡, 왼쪽이 +좌측; R 로버)')
    step = 0.05
    fw = np.arange(2.2, -0.3, -step); lat = np.arange(1.5, -0.8, -step)
    canvas = [[' '] * len(lat) for _ in fw]
    for x, y in sp:
        dx, dy = x - px, y - py
        f = dx * math.cos(pyaw) + dy * math.sin(pyaw); l = -dx * math.sin(pyaw) + dy * math.cos(pyaw)
        a = int(round((2.2 - f) / step)); b = int(round((1.5 - l) / step))
        if 0 <= a < len(fw) and 0 <= b < len(lat):
            canvas[a][b] = '.'
    a = int(round(2.2 / step)); b = int(round(1.5 / step)); canvas[a][b] = 'R'
    hdr = ''.join(('|' if abs(l - round(l * 2) / 2) < 1e-6 else ' ') for l in lat)
    print('        횡: ' + hdr + '   (| = +1.5 +1.0 +0.5 0 -0.5)')
    for a, f in enumerate(fw):
        print('  %+5.2f  ' % f + ''.join(canvas[a]))
    # 좌측(횡 +0.5~+1.3) 전방 0~1.6 라이다 점의 횡 분포 (0.1 m 전방 띠별 최소 횡)
    print('  좌측 라이다 점: 전방 띠별 가장 안쪽(작은 횡) 점')
    for lo in np.arange(-0.2, 1.6, 0.2):
        pts = []
        for x, y in sp:
            dx, dy = x - px, y - py
            f = dx * math.cos(pyaw) + dy * math.sin(pyaw); l = -dx * math.sin(pyaw) + dy * math.cos(pyaw)
            if lo <= f < lo + 0.2 and 0.3 < l < 1.6:
                pts.append(l)
        print('    전방 %+.1f~%+.1f: %s' % (lo, lo + 0.2, ('최소 횡 %+.2f (점 %d)' % (min(pts), len(pts))) if pts else '점 없음'))
