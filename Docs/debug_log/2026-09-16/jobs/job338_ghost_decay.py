#!/usr/bin/env python3
"""voxel_decay 를 60→120 s(로컬)·90→180 s(전역) 로 늘리면 잡음 셀이 누적돼 통로를 막는가 — 주행 bag 실데이터로 검토 (2026-09-16 §C).

  로컬/전역 코스트맵의 LETHAL 셀을 프레임마다 분류한다:
    lidar  : 최근 10 s 의 /scan 점(odom/map 으로 변환) 0.12 m 이내 → 라이다가 지지(2D 장애물층 담당, decay 무관)
    box    : 상자 영역(BX−0.05~BX+0.35, BY−0.30~BY+0.30) → 깊이 기억이 담당하는 진짜 낮은 장애물
    other  : 그 밖의 깊이 전용 셀 = 잡음·유령 후보(낮은 실물일 수도 있으므로 위치를 같이 찍는다)
  각 'other' 셀의 생존구간(첫 LETHAL ~ 마지막 LETHAL)을 구해
    - 시간대별 개수, 통로 띠(x 0.3~1.6, y −0.10~+0.50, 출발프레임 기준) 안의 개수, 로버 궤적과의 최소거리
    - decay 를 D2 로 늘렸을 때의 상한 시뮬레이션: 모든 소멸을 decay 소멸로 보고 생존을 (D2−D1) 만큼 연장 → 동시 생존 최대 수·통로 띠 안 최대 수
  인자: BAG BX BY [D1_local=60] [D2_local=120] [D1_global=90] [D2_global=180]
"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan

BAG = sys.argv[1]; BX = float(sys.argv[2]); BY = float(sys.argv[3])
D1L = float(sys.argv[4]) if len(sys.argv) > 4 else 60.0; D2L = float(sys.argv[5]) if len(sys.argv) > 5 else 120.0
D1G = float(sys.argv[6]) if len(sys.argv) > 6 else 90.0; D2G = float(sys.argv[7]) if len(sys.argv) > 7 else 180.0
BAND = (0.3, 1.6, -0.10, 0.50)


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


r = rosbag2_py.SequentialReader()
r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
mo, ob, lcs, gcs, scans, static = [], [], [], [], [], {}
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
            static[tr.child_frame_id] = (tr.header.frame_id, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation))
    elif topic == '/local_costmap/costmap':
        lcs.append((t, deserialize_message(data, OccupancyGrid)))
    elif topic == '/global_costmap/costmap':
        gcs.append((t, deserialize_message(data, OccupancyGrid)))
    elif topic == '/scan':
        m = deserialize_message(data, LaserScan)
        scans.append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, m.header.frame_id, m))
mo.sort(); ob.sort()
mo_t = [s[0] for s in mo]; ob_t = [s[0] for s in ob]; sc_t = [s[0] for s in scans]
T0 = ob[0][0]


def latest(seq, ts, t):
    i = bisect.bisect_right(ts, t) - 1
    return seq[i] if i >= 0 else None


def chain_to_base(frame):
    """정적 TF 체인으로 frame → base_link 의 (x, y, yaw)"""
    x, y, yaw = 0.0, 0.0, 0.0
    f = frame; hops = 0
    while f != 'base_link' and f in static and hops < 8:
        parent, tx, ty, tyaw = static[f]
        # 현재 (x,y,yaw) 는 f 기준 → parent 기준으로
        x, y = tx + x * math.cos(tyaw) - y * math.sin(tyaw), ty + x * math.sin(tyaw) + y * math.cos(tyaw)
        yaw += tyaw; f = parent; hops += 1
    return (x, y, yaw, f == 'base_link')


def base_in_frame(t, frame):
    """t 시각 base_link → frame('odom' 또는 'map') 의 (x, y, yaw)"""
    b = latest(ob, ob_t, t)
    if b is None:
        return None
    if frame == 'odom':
        return (b[1], b[2], b[3])
    a = latest(mo, mo_t, t)
    if a is None:
        return None
    X = a[1] + b[1] * math.cos(a[3]) - b[2] * math.sin(a[3]); Y = a[2] + b[1] * math.sin(a[3]) + b[2] * math.cos(a[3])
    return (X, Y, a[3] + b[3])


scan_cache = {}


def scan_points(frame, t, window=10.0):
    """t 이전 window 초의 스캔 점을 frame 좌표로 (캐시)"""
    key = (frame, round(t, 1))
    if key in scan_cache:
        return scan_cache[key]
    i1 = bisect.bisect_right(sc_t, t); i0 = bisect.bisect_left(sc_t, t - window)
    pts = []
    for k in range(i0, i1, 3):      # 3 스캔에 1개 (10 Hz → 3.3 Hz) 로 충분
        st, fid, m = scans[k]
        lx, ly, lyaw, ok = chain_to_base(fid)
        pose = base_in_frame(st, frame)
        if pose is None:
            continue
        rng = np.array(m.ranges, dtype=np.float64)
        ang = m.angle_min + np.arange(rng.size) * m.angle_increment
        good = np.isfinite(rng) & (rng > 0.05) & (rng < 8.0)
        px = rng[good] * np.cos(ang[good]); py = rng[good] * np.sin(ang[good])
        # laser → base
        bx = lx + px * math.cos(lyaw) - py * math.sin(lyaw); by = ly + px * math.sin(lyaw) + py * math.cos(lyaw)
        # base → frame
        X = pose[0] + bx * math.cos(pose[2]) - by * math.sin(pose[2]); Y = pose[1] + bx * math.sin(pose[2]) + by * math.cos(pose[2])
        pts.append(np.stack([X, Y], axis=1))
    out = np.concatenate(pts) if pts else np.zeros((0, 2))
    scan_cache[key] = out
    return out


def classify(frames, frame_name, label, D1, D2):
    print('\n===== %s 코스트맵 (%s, %d 프레임, decay %.0f → %.0f s 시뮬레이션) =====' % (label, frame_name, len(frames), D1, D2))
    first, last, pos = {}, {}, {}
    series = []
    for (t, G) in frames:
        res = G.info.resolution; ox, oy = G.info.origin.position.x, G.info.origin.position.y
        d = np.array(G.data, dtype=np.int16).reshape(G.info.height, G.info.width)
        jj, ii = np.where(d >= 100)
        if ii.size == 0:
            series.append((t - T0, 0, 0, 0, 0)); continue
        X = ox + (ii + 0.5) * res; Y = oy + (jj + 0.5) * res
        # 프레임 → map (로컬은 odom 이므로 map->odom 적용)
        if frame_name == 'odom':
            a = latest(mo, mo_t, t) or mo[0]     # 첫 map->odom 이전 프레임은 첫 TF 로
            MX = a[1] + X * math.cos(a[3]) - Y * math.sin(a[3]); MY = a[2] + X * math.sin(a[3]) + Y * math.cos(a[3])
        else:
            MX, MY = X, Y
        sp = scan_points(frame_name, t)
        if sp.shape[0]:
            # 최근접 스캔점 거리 (셀 수 ≤ 수천, 스캔점 수천 → 블록 계산)
            dmin = np.full(ii.size, 9.0)
            for s0 in range(0, ii.size, 500):
                blk = np.hypot(X[s0:s0 + 500, None] - sp[None, :, 0], Y[s0:s0 + 500, None] - sp[None, :, 1])
                dmin[s0:s0 + 500] = blk.min(axis=1)
        else:
            dmin = np.full(ii.size, 9.0)
        lidar = dmin <= 0.12
        box = (MX >= BX - 0.05) & (MX <= BX + 0.35) & (MY >= BY - 0.30) & (MY <= BY + 0.30)
        other = ~lidar & ~box
        band = other & (MX > BAND[0]) & (MX < BAND[1]) & (MY > BAND[2]) & (MY < BAND[3])
        series.append((t - T0, int(lidar.sum()), int(box.sum()), int(other.sum()), int(band.sum())))
        for k in np.where(other)[0]:
            key = (int(round(MX[k] / res)), int(round(MY[k] / res)))
            first.setdefault(key, t - T0); last[key] = t - T0; pos[key] = (MX[k], MY[k])
    print('  t(s)  lidar  box  other  other@통로띠   (5 s 간격)')
    lastp = -99
    for s in series:
        if s[0] - lastp >= 5.0:
            print('  %5.1f  %5d %4d  %5d  %5d' % s); lastp = s[0]
    if not first:
        print('  깊이 전용(other) 셀 없음'); return
    # 생존 구간
    lives = [(first[k], last[k], pos[k]) for k in first]
    L = np.array([b - a for a, b, _ in lives])
    print('  깊이 전용 셀 총 %d개: 생존 중앙값 %.1f s, 최대 %.1f s, ≥%.0f s(=decay 소멸 후보) %d개' % (len(lives), np.median(L), L.max(), D1 - 5, int((L >= D1 - 5).sum())))
    # 로버 궤적과의 최소거리 (map)
    traj = np.array([[*base_in_frame(t, 'map')[:2]] for t in np.arange(T0, ob[-1][0], 0.5) if base_in_frame(t, 'map')]) if mo else np.zeros((0, 2))
    near = []
    for a, b, (x, y) in lives:
        dd = np.hypot(traj[:, 0] - x, traj[:, 1] - y).min() if traj.size else 9
        near.append(dd)
    near = np.array(near)
    print('  로버 궤적과 최소거리: <0.25 m %d개, 0.25~0.5 %d개, >0.5 %d개' % (int((near < 0.25).sum()), int(((near >= 0.25) & (near < 0.5)).sum()), int((near >= 0.5).sum())))
    inband = [(a, b, p) for a, b, p in lives if BAND[0] < p[0] < BAND[1] and BAND[2] < p[1] < BAND[3]]
    print('  통로 띠 안 깊이 전용 셀 %d개:' % len(inband))
    for a, b, p in sorted(inband)[:12]:
        print('     (%.2f, %.2f) t %.1f~%.1f (%.0f s)' % (p[0], p[1], a, b, b - a))
    # 군집 요약 (0.15 m)
    P = np.array([p for _, _, p in lives])
    used = np.zeros(len(P), bool); clusters = []
    for i in range(len(P)):
        if used[i]:
            continue
        m = np.hypot(P[:, 0] - P[i, 0], P[:, 1] - P[i, 1]) < 0.15
        used |= m; clusters.append((int(m.sum()), P[m].mean(axis=0), np.mean([lives[k][1] - lives[k][0] for k in np.where(m)[0]])))
    clusters.sort(key=lambda c: -c[0])
    print('  군집(0.15 m) 상위: ' + '; '.join('%d셀@(%.2f,%.2f) 평균생존 %.0fs' % (n, c[0], c[1], l) for n, c, l in clusters[:8]))
    # decay 연장 시뮬레이션 (상한): 모든 소멸을 decay 소멸로 간주 → last + (D2 − D1)
    ext = D2 - D1
    tt = np.arange(0, ob[-1][0] - T0 + ext, 1.0)
    alive1 = np.array([sum(1 for a, b, _ in lives if a <= x <= b) for x in tt])
    alive2 = np.array([sum(1 for a, b, _ in lives if a <= x <= b + ext) for x in tt])
    band1 = np.array([sum(1 for a, b, _ in inband if a <= x <= b) for x in tt])
    band2 = np.array([sum(1 for a, b, _ in inband if a <= x <= b + ext) for x in tt])
    print('  동시 생존 깊이 전용 셀: decay %.0f 최대 %d개 → %.0f(상한) 최대 %d개 | 통로 띠: %d → %d개' % (D1, alive1.max(), D2, alive2.max(), band1.max(), band2.max()))


print('bag %s: T0 %.2f, 길이 %.1f s, 스캔 %d, 로컬 %d, 전역 %d, 정적TF %s' % (BAG, T0, ob[-1][0] - T0, len(scans), len(lcs), len(gcs), list(static.keys())[:6]))
if scans:
    lx, ly, lyaw, ok = chain_to_base(scans[0][1])
    print('스캔 프레임 %s → base_link: (%.3f, %.3f, %.1f°) 체인 %s' % (scans[0][1], lx, ly, math.degrees(lyaw), 'OK' if ok else '불완전'))
classify(lcs, 'odom', '로컬', D1L, D2L)
classify(gcs, 'map', '전역', D1G, D2G)
