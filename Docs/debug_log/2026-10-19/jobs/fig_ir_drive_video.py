#!/usr/bin/env python3
"""fig_ir_drive_video — IR 기록 주행 영상: 위 = IR1 프로젝터 끔(cuVSLAM 입력) | 켬(점 무늬), 아래 = 지도 위 로버 · 지나온 길 · 카메라 시야 | 시간축(회전 속도 · 특징 수). (2026-10-19 §20, PC)
  왜: 4 GB IR bag 을 지우기 전에 사용자가 보고 분석할 구간을 고르도록(§18.1). 시각은 IR 프레임 stamp 기준 t(s) — 사용자가 'tNN 근처' 로 짚을 수 있게 화면 · 시간축에 같은 t.
  입력: fig_ir_extract.py 의 ir_pairs.mp4 · ir_pairs.csv(Jetson), 주행 bag(/map · /tf · /tf_static · /odometry/filtered).
  출력: 영상(mp4, H.264 로 다시 인코딩) + 시간축 그림(png). 인자: 폴더(ir_pairs.* 와 bag_f2y1/) 출력.mp4
  [§21 추가] 아래 가운데 = 출발점 시험 상자 확대(지도 x 0.6~1.8 · y −0.75~0.45): nvblox 조각의 표면 안 칸(빨강, 그 순간의 map→odom 으로 지도에),
        실제 상자(파랑 테두리), 차체(초록). 글 = 그 조각의 북 · 서 면 과장(anal_slice_box 와 같은 정의) — 사용자: 복귀 때 상자 옆 번짐이 있었는지 영상으로 안 보임."""
import sys, math, bisect, csv, subprocess
from pathlib import Path
import numpy as np, cv2, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
D = Path(sys.argv[1]); OUT = sys.argv[2]; FFMPEG = 'C:/ffmpeg/bin/ffmpeg.exe'
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]]); HFOV = math.radians(43); CAMR = 1.4
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
comp = lambda A, B: (A[0] + math.cos(A[2]) * B[0] - math.sin(A[2]) * B[1], A[1] + math.sin(A[2]) * B[0] + math.cos(A[2]) * B[1], A[2] + B[2])

# --- 주행 bag
TS = get_typestore(Stores.ROS2_HUMBLE)
TS.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
BOX = (1.151, 1.261, -0.20, -0.02); ZR = (0.6, 1.8, -0.75, 0.45); REG = (0.95, 1.50, -0.25, 0.25)
MO, OB, OM, SL = [], [], [], []; grid = None
with AnyReader([D / 'bag_f2y1'], default_typestore=TS) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/map', '/odometry/filtered', '/nvblox_node/static_map_slice')]):
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/map': grid = m; continue
        if c.topic == '/nvblox_node/static_map_slice':
            d = np.array(m.data, np.float32).reshape(m.height, m.width); iy, ix = np.nonzero((d <= 0) & (d != m.unknown_value))
            SL.append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, m.origin.x + (ix + 0.5) * m.resolution, m.origin.y + (iy + 0.5) * m.resolution, m.resolution)); continue
        if c.topic == '/odometry/filtered':
            OM.append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, m.twist.twist.angular.z)); continue
        for tr in m.transforms:
            st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9; v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((st, v))
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((st, v))
for L in (MO, OB, OM): L.sort()
MOt, OBt, OMt = [x[0] for x in MO], [x[0] for x in OB], [x[0] for x in OM]
at = lambda L, T, t: L[max(bisect.bisect_right(T, t) - 1, 0)][1]
# 조각 → 지도 좌표(그 조각 시각의 map→odom), 확대 구역 안 칸만 보관 + 북 · 서 면 과장(anal_slice_box 정의)
SL.sort(key=lambda q: q[0]); SLt = [q[0] for q in SL]; SLW = []
for st, lx, ly, r in SL:
    mo = at(MO, MOt, st); gx = mo[0] + math.cos(mo[2]) * lx - math.sin(mo[2]) * ly; gy = mo[1] + math.sin(mo[2]) * lx + math.cos(mo[2]) * ly
    z = (gx > ZR[0]) & (gx < ZR[1]) & (gy > ZR[2]) & (gy < ZR[3]); k = (gx > REG[0]) & (gx < REG[1]) & (gy > REG[2]) & (gy < REG[3])
    nb = 100 * (gy[k].max() + r / 2 - BOX[3]) if k.any() else float('nan'); wb = 100 * (BOX[0] - (gx[k].min() - r / 2)) if k.any() else float('nan')
    SLW.append((gx[z], gy[z], r, mo[2], nb, wb))
pose = lambda t: comp(at(MO, MOt, t), at(OB, OBt, t))

# --- IR 짝
R = list(csv.DictReader(open(D / 'ir_pairs.csv')))
ts = np.array([int(r['stamp_ns']) * 1e-9 for r in R]); tt = np.array([float(r['t']) for r in R])
ofast = np.array([float(r['off_fast']) for r in R]); onfast = np.array([float(r['on_fast']) for r in R]); omean = np.array([float(r['off_mean']) for r in R])
w = np.array([at(OM, OMt, t) for t in ts]); P = np.array([pose(t) for t in ts])

# --- 시간축 그림(배경, 커서는 프레임마다 cv2 로)
TW, TH = 427, 420
fig, ax = plt.subplots(3, 1, figsize=(TW / 100, TH / 100), dpi=100, sharex=True)
ax[0].plot(tt, np.degrees(w), lw=0.8, color='#1f5fa8'); ax[0].set_ylabel('ω °/s'); ax[0].axhline(0, color='0.6', lw=0.5)
ax[1].semilogy(tt, np.maximum(onfast, 1), lw=0.8, color='#c0392b', label='켬(점)'); ax[1].semilogy(tt, np.maximum(ofast, 1), lw=0.8, color='#16a085', label='끔')
ax[1].set_ylabel('FAST 수'); ax[1].legend(fontsize=7, loc='center right', ncol=2)
ax[2].plot(tt, omean, lw=0.8, color='#7f8c8d'); ax[2].set_ylabel('끔 밝기'); ax[2].set_xlabel('t (s, IR 시각)')
for a in ax: a.tick_params(labelsize=7); a.yaxis.label.set_size(8); a.grid(alpha=0.3)
fig.tight_layout(pad=0.4); fig.canvas.draw()
tl = cv2.cvtColor(np.asarray(fig.canvas.buffer_rgba())[:, :, :3], cv2.COLOR_RGB2BGR).copy()
x0px = ax[2].transData.transform((tt[0], 0))[0]; x1px = ax[2].transData.transform((tt[-1], 0))[0]
fig.savefig(OUT.replace('.mp4', '_timeline.png'), dpi=150); plt.close(fig)
y_top = int(TH - ax[0].get_window_extent().y1); y_bot = int(TH - ax[2].get_window_extent().y0)

# --- 지도 판
MW, MH = 427, 420
ZW = 1280 - MW - tl.shape[1]; zs = ZW / (ZR[1] - ZR[0]); z2p = lambda x, y: (int((x - ZR[0]) * zs), int((ZR[3] - y) * zs))
g = np.array(grid.data, np.int8).reshape(grid.info.height, grid.info.width); res = grid.info.resolution; ox, oy = grid.info.origin.position.x, grid.info.origin.position.y
xmin, xmax = P[:, 0].min() - 1.0, P[:, 0].max() + 1.0; ymin, ymax = P[:, 1].min() - 1.0, P[:, 1].max() + 1.0
s = min(MW / (xmax - xmin), MH / (ymax - ymin))
cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
w2p = lambda x, y: (int(MW / 2 + (x - cx) * s), int(MH / 2 - (y - cy) * s))
base = np.full((MH, MW, 3), 235, np.uint8)
iy, ix = np.nonzero(g >= 65)
for gx, gy in zip(ox + (ix + 0.5) * res, oy + (iy + 0.5) * res):
    p = w2p(gx, gy)
    if 0 <= p[0] < MW and 0 <= p[1] < MH: cv2.circle(base, p, max(1, int(res * s / 2)), (60, 60, 60), -1)
iy, ix = np.nonzero(g == -1)
for gx, gy in zip(ox + (ix + 0.5) * res, oy + (iy + 0.5) * res):
    p = w2p(gx, gy)
    if 0 <= p[0] < MW and 0 <= p[1] < MH: base[p[1], p[0]] = (200, 200, 200)
for k in range(1, len(P)): cv2.line(base, w2p(*P[k - 1, :2]), w2p(*P[k, :2]), (200, 215, 245), 1)
cv2.putText(base, '1 m', (MW - 70, MH - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1); cv2.line(base, (MW - 70, MH - 24), (MW - 70 + int(s), MH - 24), (0, 0, 0), 2)

# --- 프레임 합성
cap = cv2.VideoCapture(str(D / 'ir_pairs.mp4')); tmp = OUT.replace('.mp4', '_raw.mp4'); vw = None
for i in range(len(R)):
    ok, top = cap.read()
    if not ok: break
    x, y, th = P[i]
    mp = base.copy()
    for k in range(max(1, i - 2000), i + 1): cv2.line(mp, w2p(*P[k - 1, :2]), w2p(*P[k, :2]), (60, 140, 40), 2)
    pts = np.array([w2p(x + math.cos(th) * a - math.sin(th) * b, y + math.sin(th) * a + math.cos(th) * b) for a, b in FP], np.int32)
    fov = [w2p(x, y)] + [w2p(x + CAMR * math.cos(th + a), y + CAMR * math.sin(th + a)) for a in np.linspace(-HFOV, HFOV, 9)]
    ov = mp.copy(); cv2.fillPoly(ov, [np.array(fov, np.int32)], (80, 220, 255)); mp = cv2.addWeighted(ov, 0.35, mp, 0.65, 0)
    cv2.polylines(mp, [pts], True, (20, 110, 20), 2)
    cv2.putText(mp, 't=%.1f  (%.2f, %.2f) %.0fdeg  w=%+.0f' % (tt[i], x, y, math.degrees(th), math.degrees(w[i])), (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 1)
    cv2.rectangle(mp, w2p(ZR[0], ZR[3]), w2p(ZR[1], ZR[2]), (200, 80, 0), 1)
    tlc = tl.copy(); cx_ = int(x0px + (tt[i] - tt[0]) / (tt[-1] - tt[0]) * (x1px - x0px)); cv2.line(tlc, (cx_, y_top), (cx_, y_bot), (0, 0, 255), 1)
    zp = np.full((MH, ZW, 3), 245, np.uint8); j = bisect.bisect_right(SLt, ts[i]) - 1
    if j >= 0:
        gx, gy, r, myaw, nb, wb = SLW[j]; hs = r * zs / 2
        for a_, b_ in zip(gx, gy):
            p = z2p(a_, b_); cv2.rectangle(zp, (int(p[0] - hs), int(p[1] - hs)), (int(p[0] + hs), int(p[1] + hs)), (90, 90, 230), -1)
        cv2.putText(zp, 'nvblox N %+.1f  W %+.1f cm' % (nb, wb), (8, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 160), 1)
    cv2.rectangle(zp, z2p(BOX[0], BOX[3]), z2p(BOX[1], BOX[2]), (200, 80, 0), 2)
    pz = np.array([z2p(x + math.cos(th) * a - math.sin(th) * b, y + math.sin(th) * a + math.cos(th) * b) for a, b in FP], np.int32); cv2.polylines(zp, [pz], True, (20, 110, 20), 2)
    cv2.putText(zp, 'box zoom  t=%.1f' % tt[i], (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    cv2.line(zp, (ZW - 10 - int(0.2 * zs), MH - 14), (ZW - 10, MH - 14), (0, 0, 0), 2); cv2.putText(zp, '20 cm', (ZW - 10 - int(0.2 * zs), MH - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    frame = np.vstack([top, np.hstack([mp, zp, tlc])])
    if vw is None: vw = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*'mp4v'), 15, (frame.shape[1], frame.shape[0]))
    vw.write(frame)
    if i in (len(R) // 4, len(R) // 2, 3 * len(R) // 4): cv2.imwrite(OUT.replace('.mp4', '_t%03d.png' % int(tt[i])), frame)
vw.release()
subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-i', tmp, '-c:v', 'libx264', '-crf', '23', '-pix_fmt', 'yuv420p', OUT], check=True)
Path(tmp).unlink()
print('영상 %s (%d 프레임, %.0f s)' % (OUT, i + 1, tt[-1] - tt[0]))
