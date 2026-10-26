# Smac 실패 · 성공 순간의 출발(로버) · 목표 자세가 전역 코스트맵에서 어떤 칸인가: 중심 칸 비용, 차체 직사각형(+패딩 0.01) 안 최대 비용 · 치명(100 = 비용 254) · 내접(99 = 253) 칸 수(OccupancyGrid 0~100 눈금, 차체 안을 칸 절반 간격 표본)
import sys, math, bisect, time, numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag = Path(sys.argv[1])
# (시각, 결과, 목표 x, y, 목표 yaw°) — nav2 로그 · 러너 yaw
EV = [('16:11:56.85', '실패', -1.60, -5.50, -100), ('16:12:15.53', '실패', -1.60, -5.50, -100), ('16:12:22.02', '실패', -1.60, -5.50, -100),
      ('16:12:35.21', '실패', -1.65, -3.70, 82), ('16:12:59.54', '실패(출발 치명)', -1.65, -3.70, 82), ('16:13:08.65', '성공', -1.65, -3.70, 82)]
FP = (0.262 + 0.01, -0.248 - 0.01, 0.165 + 0.01)
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
MO, OB, CM = [], [], []
with AnyReader([bag], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    cs = [c for c in rd.connections if c.topic in ('/tf', '/global_costmap/costmap')]
    for c, t, raw in rd.messages(connections=cs):
        m = rd.deserialize(raw, c.msgtype); ts = t * 1e-9
        if c.topic == '/tf':
            for tr in m.transforms:
                v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((ts, v))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((ts, v))
        else:
            i = m.info; CM.append((ts, i.resolution, i.origin.position.x, i.origin.position.y, np.array(m.data, dtype=np.int16).reshape(i.height, i.width)))
MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]; CMt = [q[0] for q in CM]
at = lambda L, T, t: L[max(bisect.bisect_right(T, t) - 1, 0)]
print('전역 코스트맵 메시지', len(CM))
def cells(cm, x, y, yaw):
    _, r, ox, oy, G = cm; g = G.copy(); g[g < 0] = 0   # 미지(-1) → 0 으로 봄(unknown 통과 허용 설정)
    k = lambda px, py: G[int((py - oy) / r), int((px - ox) / r)]
    c, s = math.cos(yaw), math.sin(yaw); vals = []
    for u in np.arange(FP[1], FP[0] + 1e-9, r / 2):
        for w in np.arange(-FP[2], FP[2] + 1e-9, r / 2):
            vals.append(k(x + c * u - s * w, y + s * u + c * w))
    v = np.array(vals); return k(x, y), v.max(), int((v == 100).sum()), int((v == 99).sum())
day = time.strftime('%Y-%m-%d', time.localtime(OB[0][0]))
for hm, res, gx, gy, gyaw in EV:
    t = time.mktime(time.strptime(day + ' ' + hm[:8], '%Y-%m-%d %H:%M:%S')) + float('0' + hm[8:])
    p = comp(at(MO, MOt, t)[1], at(OB, OBt, t)[1]); cm = at(CM, CMt, t)
    sc = cells(cm, *p); gc = cells(cm, gx, gy, math.radians(gyaw))
    print('%s %-14s 출발 (%.2f,%.2f,%4.0f°) 중심 %3d · 차체 최대 %3d · 치명 %2d · 내접 %2d | 목표 (%.2f,%.2f,%4d°) 중심 %3d · 차체 최대 %3d · 치명 %2d · 내접 %2d | 지도 %.1f s 전' % (
        hm, res, p[0], p[1], math.degrees(p[2]), *sc, gx, gy, gyaw, *gc, t - cm[0]))
