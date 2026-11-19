#!/usr/bin/env python3
"""lib_rover — Docs/tools 의 그림 · 분석 도구가 함께 쓰는 공통 부품(직접 실행하지 않음, import 전용). (2026-11-19 §2)
  왜: 사용자 — "tools 의 도구들이 겹치는 것들이 많을 텐데, 이제 그렇지 않게 만들자". 11-19 점검에서 같은 코드(좌표 변환 · tf 사슬 ·
      차체 풋프린트 · 저장 지도 읽기 · 코스트맵 색표 · nav2 사건 읽기 · bag 읽기)가 도구 약 15 개에 손으로 복사돼 있었다 → 여기 한 곳에 둔다.
      앞머리 lib_ = 'import 만 하는 부품'(11-19 사용자 확인으로 README §3.1 에 7 번째로 넣음).
  로버 움직임: 없음. 인자: 없음(모듈). 출력: 없음.
  쓰는 법: sys.path.insert(0, str(Path(__file__).resolve().parent)); import lib_rover as L
  값의 출처: FP = nav2_params.yaml footprint(패딩 없는 차체), 카메라 반각 43° · 1.4 m = 11-18 까지 그림 도구들의 값(nvblox 통합 거리 1.4 — 10-22 부터 실제 설정은 2.0,
            그림의 부채꼴은 '대략의 시야' 표시일 뿐), 지도 = Docs/04_navigation/maps/<이름>.yaml."""
import math, re, time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]          # Docs/tools → Docs → 저장소
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]])   # base_link 기준 차체 외곽(m)
HFOV, CAMR, CAMX = math.radians(43), 1.4, 0.2       # 카메라 시야 반각 · 그릴 거리 · base_link 앞 거리(그림용)


# ── 좌표 변환(전부 4 × 4 동차 행렬, 평면 그림은 [:2] 만 씀) ──
def q2yaw(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def T4(tr):
    """geometry_msgs/Transform(translation · rotation) 또는 Pose(position · orientation) → 4 × 4."""
    t = getattr(tr, 'translation', None) or tr.position
    q = getattr(tr, 'rotation', None) or tr.orientation
    x, y, z, w = q.x, q.y, q.z, q.w; M = np.eye(4)
    M[:3, :3] = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                 [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                 [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    M[:3, 3] = [t.x, t.y, t.z]; return M


def yaw_of(M): return math.atan2(M[1, 0], M[0, 0])
def xyyaw(M): return M[0, 3], M[1, 3], yaw_of(M)
def w2(M, P):
    """평면 점 P(N × 2)를 M 으로 옮긴 N × 2."""
    P = np.asarray(P, float).reshape(-1, 2)
    return (M @ np.c_[P, np.zeros(len(P)), np.ones(len(P))].T).T[:, :2]


def chain(static, frame, root='base_link'):
    """/tf_static 로 frame → root 고정 변환. 사슬이 끊기면 None."""
    M = np.eye(4)
    while frame != root:
        if frame not in static: return None
        par, Mp = static[frame]; M = Mp @ M; frame = par
    return M


def last(seq, t):
    """시각순 (t, …) 목록에서 t 이전 마지막 것(없으면 첫 것). 빈 목록이면 None."""
    if not seq: return None
    i = np.searchsorted([s[0] for s in seq], t, side='right') - 1
    return seq[max(i, 0)]


# 11-19 §3: 도구마다 '어느 표본을 고르나' 규칙이 달랐다 — 결과를 바꾸지 않으려고 셋 다 둔다(새 도구는 last 를 쓴다)
def after(seq, t):
    """t 이상인 첫 것(없으면 마지막) — 옛 anal_box_history.near · anal_odom_drift.at 의 규칙."""
    return seq[min(np.searchsorted([s[0] for s in seq], t), len(seq) - 1)]


def nearest(seq, t):
    """시각이 가장 가까운 것 — 옛 fig_stop_costmap.pose 의 규칙."""
    return seq[int(np.argmin(np.abs(np.array([s[0] for s in seq]) - t)))]


# ── 차체 여유 · 상자(10-13 정의) ──
def rect_clear(P, fp=FP):
    """차체 기준 점들(N × 2 이상, 앞 두 열만 씀)에서 풋프린트 사각형(축 정렬) 바깥까지의 거리 N 개(안이면 0)."""
    x, y = P[:, 0], P[:, 1]; z = np.zeros(len(P))
    return np.hypot(np.maximum.reduce([fp[:, 0].min() - x, z, x - fp[:, 0].max()]), np.maximum.reduce([fp[:, 1].min() - y, z, y - fp[:, 1].max()]))


def box_cells(g, Mob, Mmo):
    """'상자' = 정지 때 로컬 코스트맵(g = (t, ox, oy, res, 격자), odom)에서 차체에 가장 가까운 치명 칸이 속한 8 연결 덩어리(10-13 §4.6 정의,
    옛 anal_box_history · anal_box_layers · anal_plan_keepout 가 각자 같은 줄을 가짐). 돌려줌: 지도 좌표 칸 중심 N × 2."""
    from scipy import ndimage
    _, ox, oy, res, G = g; Lc = np.argwhere(G >= 100); Lo = np.c_[ox + (Lc[:, 1] + 0.5) * res, oy + (Lc[:, 0] + 0.5) * res]
    d = rect_clear(w2(np.linalg.inv(Mob), Lo)); lab, _ = ndimage.label(G >= 100, structure=np.ones((3, 3))); k = int(np.argmin(d))
    return w2(Mmo, Lo[lab[Lc[:, 0], Lc[:, 1]] == lab[Lc[k, 0], Lc[k, 1]]])


# ── 시각 ──
def hms_epoch(day, hms):
    """day = 'YYYY-MM-DD ' (bag 첫 메시지의 지역 날짜), hms = 'HH:MM:SS[.cc]' → epoch 초."""
    h = hms.split('.')[0]; frac = float('0.' + hms.split('.')[1]) if '.' in hms else 0.0
    return time.mktime(time.strptime(day + h, '%Y-%m-%d %H:%M:%S')) + frac
def hms(t, digits=0):
    s = time.strftime('%H:%M:%S', time.localtime(t))
    return s + ('.%0*d' % (digits, int((t % 1) * 10 ** digits)) if digits else '')


# ── bag 읽기 ──
TOPIC_KEY = {'/local_costmap/costmap': 'loc', '/global_costmap/costmap': 'glo', '/plan': 'raws', '/plan_smoothed': 'plans',
             '/transformed_global_plan': 'tplan', '/trajectories': 'traj', '/scan': 'scan', '/cmd_vel': 'cmd',
             '/wheel_odom': 'wheel', '/odometry/filtered': 'ekf', '/odom_rf2o': 'rf2o', '/odom_rf2o/gated': 'rf2o_gated',
             '/nvblox_node/static_map_slice': 'slice'}
EARLY = ('glo', 'raws', 'plans')      # 구간 앞 오래된 것도 '마지막 것' 으로 필요(전역 코스트맵 · 경로는 드물게 옴)
ODOM_KEYS = ('wheel', 'rf2o', 'rf2o_gated')


def typestore():
    """ROS 2 Humble 타입 + nvblox DistanceMapSlice(bag 에 정의가 없음 — 옛 anal_box_layers · anal_plan_keepout 의 등록 줄)."""
    from rosbags.typesys import Stores, get_typestore, get_types_from_msg
    ts = get_typestore(Stores.ROS2_HUMBLE)
    ts.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n',
                                   'nvblox_msgs/msg/DistanceMapSlice'))
    return ts


def open_bag(bag):
    """with open_bag(경로) as r: … — 타입 정의 없는 .db3 도 읽게 typestore() 를 붙인 AnyReader."""
    from rosbags.highlevel import AnyReader
    return AnyReader([Path(bag)], default_typestore=typestore())


def read_bag(bag, topics, h0=None, h1=None, pre=30.0, post=2.0, scan_max=6.0):
    """bag 에서 topics 만 읽어 키별 시각순 목록으로. h0 · h1 = 'HH:MM:SS'(bag 날짜 기준) — 주면 [h0 − pre, h1 + post] 만(EARLY · /tf_static 은 앞쪽 전부).
    돌려줌: dict — 't0' · 'day' · 'tA' · 'tB' · 'static'{child: (parent, M)} · 'ob'(odom→base_link) · 'mo'(map→odom) 와
      loc · glo = (t, ox, oy, res, 격자 int16[h, w]) (+ 'loc_frame') / raws · plans = (t, 점 N×2, 끝 yaw — 점 1 개 이하 경로도 그대로, yaw nan) /
      tplan = (t, 점) / traj = (t, 후보 n×8×2, 최적 N×2) / scan = (t, frame, 점 N×2) / cmd = (t, v, ω) /
      wheel · rf2o · rf2o_gated = (t, M, vx, ω, vy) / ekf = (t, M) / slice = (t, frame, ox, oy, res, 미관측 값, float32[h, w])."""
    D = {k: [] for k in ('ob', 'mo', *TOPIC_KEY.values())}; D['static'] = {}
    with open_bag(bag) as r:
        t0 = r.start_time / 1e9; day = time.strftime('%Y-%m-%d ', time.localtime(t0))
        tA = hms_epoch(day, h0) if h0 else -1e18; tB = hms_epoch(day, h1) if h1 else 1e18
        D.update(t0=t0, day=day, tA=tA if h0 else t0, tB=tB if h1 else r.end_time / 1e9)
        want = set(topics) | {'/tf_static'}
        for c, t, raw in r.messages(connections=[c for c in r.connections if c.topic in want]):
            ts = t / 1e9; key = TOPIC_KEY.get(c.topic)
            if c.topic != '/tf_static' and (ts > tB + post or (ts < tA - pre and key not in EARLY)): continue
            m = r.deserialize(raw, c.msgtype)
            if c.topic in ('/tf', '/tf_static'):
                for tr in m.transforms:
                    if c.topic == '/tf_static': D['static'][tr.child_frame_id] = (tr.header.frame_id, T4(tr.transform))
                    elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': D['ob'].append((ts, T4(tr.transform)))
                    elif tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': D['mo'].append((ts, T4(tr.transform)))
            elif key in ('loc', 'glo'):
                i = m.info; D[key].append((ts, i.origin.position.x, i.origin.position.y, i.resolution, np.array(m.data, np.int16).reshape(i.height, i.width)))
                D[key + '_frame'] = m.header.frame_id
            elif key in ('raws', 'plans'):   # 빈 경로도 남김(옛 anal_box_history 는 '마지막 경로가 비었으면 nan' 으로 셈) — 고르는 쪽(bt_plans)이 점 2 개 이상만 씀
                D[key].append((ts, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses]).reshape(-1, 2),
                               q2yaw(m.poses[-1].pose.orientation) if m.poses else float('nan')))
            elif key == 'slice':
                D[key].append((ts, m.header.frame_id, m.origin.x, m.origin.y, m.resolution, m.unknown_value, np.asarray(m.data, np.float32).reshape(m.height, m.width)))
            elif key == 'tplan':
                D[key].append((ts, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses]).reshape(-1, 2)))
            elif key == 'traj':   # MPPI lite 발행: 'Candidate Trajectories' 10 × 8 점 · 'Optimal Trajectory' 32 점(11-18 §2)
                cand = np.array([[k.pose.position.x, k.pose.position.y] for k in m.markers if k.ns.startswith('Candidate')])
                opt = np.array([[k.pose.position.x, k.pose.position.y] for k in m.markers if k.ns.startswith('Optimal')])
                D[key].append((ts, cand.reshape(-1, 8, 2) if len(cand) and len(cand) % 8 == 0 else np.zeros((0, 8, 2)), opt.reshape(-1, 2)))
            elif key == 'scan':
                ang = m.angle_min + m.angle_increment * np.arange(len(m.ranges)); rg = np.array(m.ranges, float)
                ok = np.isfinite(rg) & (rg > m.range_min) & (rg < scan_max)
                D[key].append((ts, m.header.frame_id, np.c_[rg[ok] * np.cos(ang[ok]), rg[ok] * np.sin(ang[ok])]))
            elif key == 'cmd': D[key].append((ts, m.linear.x, m.angular.z))
            elif key in ODOM_KEYS: D[key].append((ts, T4(m.pose.pose), m.twist.twist.linear.x, m.twist.twist.angular.z, m.twist.twist.linear.y))
            elif key == 'ekf': D[key].append((ts, T4(m.pose.pose)))
    for k, v in D.items():
        if isinstance(v, list): v.sort(key=lambda q: q[0])
    return D


# ── nav2 사건(nav2.log 의 '[epoch]' 줄 · nav_events.txt 의 'HH:MM:SS.cc …' 줄 둘 다) ──
# (찾을 말 1, 찾을 말 2, 이름) — 위에서부터 처음 맞는 것 하나. 이름은 D 스타일 규칙대로 짧은 영문(ROS 쪽 이름 그대로 둘 수 있는 것은 그대로).
EVENTS = [('PathBlockedAhead', '2.0 s 지속되면', 'PathBlockedAhead'), ('', '주행 중단', 'blocked 2 s -> stop'),
          ('monotone_escape', '시작', 'MonotoneEscape'), ('', 'Optimizer fail', 'MPPI: no feasible trajectory'),
          ('', 'SmacHybrid failed', 'Smac failed -> NavFn'), ('', 'extrapolation into the future', 'TF extrapolation'),
          ('', 'Received a path to smooth', 'new global plan'), ('', 'Goal succeeded', 'goal reached')]
_EPOCH = re.compile(r'\[(\d{10}\.\d+)\]'); _HMS = re.compile(r'^(\d\d:\d\d:\d\d\.\d+)')
_BLK = re.compile(r'PathBlockedAhead: 앞 경로 \(([-\d.]+), ([-\d.]+)\)')


def line_time(line, day):
    m = _EPOCH.search(line)
    if m: return float(m.group(1))
    m = _HMS.match(line)
    return hms_epoch(day, m.group(1)) if m else None


def nav_events(path, day, tA, tB, merge=1.0):
    """돌려줌: (사건 [(t, 이름)], BT 계획 [[t, 스무딩 성공?]], 막힘 판정 점 [(t, x, y)] — map 좌표)."""
    ev, bt, blk = [], [], []
    if not path: return ev, bt, blk
    for line in open(path, encoding='utf-8', errors='replace'):
        te = line_time(line, day)
        if te is None: continue
        if 'Received a path to smooth' in line: bt.append([te, True])
        elif 'Smoothed path leads to a collision' in line and bt: bt[-1][1] = False
        if not (tA - 3 <= te <= tB + 1): continue
        mb = _BLK.search(line)
        if mb: blk.append((te, float(mb.group(1)), float(mb.group(2))))
        # 11-19 §2: nav2.log 원문에는 nvblox 층의 'Can't transform … extrapolation' 경고(주행 중단 아님)가 f2sa3 한 주행에 17 줄 —
        #   옛 fig_drive_video 의 이름 'TF 외삽 → 중단' 을 그대로 쓰면 과장이라 이름에서 '중단' 을 빼고 층 경고 줄은 사건으로 안 셈
        if 'NvbloxCostmapLayer' in line: continue
        for k1, k2, lab in EVENTS:
            if (not k1 or k1 in line) and k2 in line:
                if not (ev and ev[-1][1] == lab and te - ev[-1][0] < merge): ev.append((te, lab))
                break
    return ev, bt, blk


def bt_plans(D, bt):
    """BT 가 컨트롤러에 준 전역 경로 목록 [(t, 점, 끝 yaw, 출처)] — fig_drive_video(10-23 §20.7) · fig_rviz_video(10-26 §8) 의 규칙:
    스무딩 성공 = 그 직후 /plan_smoothed, 실패 = 그 직전 /plan(CopyPath), 그리고 /plan 중 점 간격 중앙 > 0.04 m = Smac(러너 조회 NavFn 은 0.025).
    사건 파일이 없으면 /plan_smoothed 전부를 NavFn 경로로 본다."""
    sel = []; plans = [q for q in D['plans'] if len(q[1]) > 1]; raws = [q for q in D['raws'] if len(q[1]) > 1]
    if bt:
        for te, ok in bt:
            c = [q for q in plans if 0 <= q[0] - te + 0.05 < 1.5] if ok else []
            if c: sel.append((c[0][0], c[0][1], c[0][2], 'NavFn')); continue
            c = [q for q in raws if 0 <= te + 0.05 - q[0] < 1.5]
            if c: sel.append((te, c[-1][1], c[-1][2], 'NavFn'))
    else: sel = [(q[0], q[1], q[2], 'NavFn') for q in plans]
    sel += [(q[0], q[1], q[2], 'Smac') for q in raws if len(q[1]) > 3 and np.median(np.hypot(*np.diff(q[1], axis=0).T)) > 0.04]
    return sorted(sel, key=lambda q: q[0])


# ── 저장 지도 ──
def load_map(name='office_v3'):
    """Docs/04_navigation/maps/<name>.yaml · .pgm → (회색 값 0~1 배열(위가 북), extent). 벽 0.25 · 빈 곳 1.0 · 미지 0.88(스타일 D 와 같은 값)."""
    import yaml
    d = ROOT / 'Docs/04_navigation/maps'; Y = yaml.safe_load(open(d / f'{name}.yaml', encoding='utf-8'))
    raw = (d / Y['image']).read_bytes()
    m = re.match(rb'P5\s+(?:#.*\s+)*(\d+)\s+(\d+)\s+(\d+)\s', raw); W, H = int(m.group(1)), int(m.group(2))
    img = np.frombuffer(raw[m.end():m.end() + W * H], np.uint8).reshape(H, W)
    res, (ox, oy) = Y['resolution'], Y['origin'][:2]
    return np.where(img < 100, 0.25, np.where(img > 250, 1.0, 0.88)), [ox, ox + W * res, oy, oy + H * res]


def draw_map(ax, name='office_v3'):
    g, ext = load_map(name)
    ax.imshow(g, cmap='gray', vmin=0, vmax=1, extent=ext, origin='upper', interpolation='nearest', zorder=0)


# ── 코스트맵 색표(값 → 칸 번호: np.clip(값, −1, 100) + 1 → −1 미지 0 · 0 빈 칸 1 · 1~98 감쇠 · 99 내접 100 · 100 치명 101) ──
def cm_index(g): return np.clip(g, -1, 100) + 1


def costmap_cmap(style='d'):
    from matplotlib.colors import ListedColormap
    if style == 'd':       # 11-19 견본 D: 미지 #e0e0e0 · 빈 칸 흰색 · 감쇠 250 → 170 회색 · 내접 #a0a0a0 · 치명 #404040
        return ListedColormap(['#e0e0e0', '#ffffff'] + ['#%02x%02x%02x' % ((int(250 - 80 * i / 97),) * 3) for i in range(98)] + ['#a0a0a0', '#404040'])
    if style == 'light':   # 10-27 §13 fig_rviz_video FIG_STYLE=light · fig_smac_expansion 과 같은 색
        return ListedColormap(np.r_[[[0.98, 0.95, 0.80]], np.linspace([1, 1, 1], [0.78, 0.80, 0.84], 99), [[0.45, 0.47, 0.52]], [[0.08, 0.09, 0.11]]])
    if style == 'rviz':    # RViz2 'costmap' 색표 손 근사(원본 화면과 대조 안 함, 11-19 §0): 미지 회청 · 빈 칸 투명 · 파랑 → 빨강 · 내접 하늘 · 치명 자홍
        cols = [(0.44, 0.54, 0.53, 0.85), (0, 0, 0, 0)] + [((i - 1) / 97, 0.0, 1 - (i - 1) / 97, 0.18 + 0.27 * (i - 1) / 97) for i in range(1, 99)]
        return ListedColormap(cols + [(0.0, 1.0, 1.0, 0.45), (1.0, 0.0, 1.0, 0.85)])
    raise ValueError(style)


def grid_extent(g): return [g[1], g[1] + g[4].shape[1] * g[3], g[2], g[2] + g[4].shape[0] * g[3]]


def lethal_cells(g, thr=100):
    """코스트맵 (t, ox, oy, res, 격자) 의 값 ≥ thr 칸 중심(격자 프레임) N × 2."""
    _, ox, oy, res, G = g; L = np.argwhere(G >= thr)
    return np.c_[ox + (L[:, 1] + 0.5) * res, oy + (L[:, 0] + 0.5) * res]


# ── 스타일 D(11-19 사용자 선택) 공통 설정 · 저장기 ──
def style_d():
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8})


def axes_d(ax, xlabel='x (m)', ylabel='y (m)'):
    ax.set_aspect('equal'); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.grid(alpha=0.3)


def writer(out, fps):
    """확장자 .gif → PillowWriter, 그 밖(.mp4) → FFMpegWriter(C:/ffmpeg/bin/ffmpeg.exe 가 있으면 그것)."""
    import matplotlib.pyplot as plt
    from matplotlib.animation import PillowWriter, FFMpegWriter
    if str(out).lower().endswith('.gif'): return PillowWriter(fps=fps)
    if Path('C:/ffmpeg/bin/ffmpeg.exe').exists(): plt.rcParams['animation.ffmpeg_path'] = 'C:/ffmpeg/bin/ffmpeg.exe'
    return FFMpegWriter(fps=fps, bitrate=4000)
