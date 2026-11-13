#!/usr/bin/env python3
# anal_costmap_crop_1113 — 11-13 §3: bag(db3) 의 /global_costmap/costmap 에서 지정 시각에 가장 가까운 메시지를 골라 서쪽 통로 창(map x −2.8~−0.8, y −6.0~−1.6)만
#   잘라 npz(base64)로 표준 출력에 낸다(Jetson 의 2.9 GB bag 을 옮기지 않고 그림 재료만 PC 로). 로버 안 움직임 · DDS 참여자 안 만듦.
#   인자: bag 폴더 날짜(YYYY-MM-DD) 시각HH:MM:SS.ss … . 출력: 'NPZ <base64>' 한 줄 + 사람이 읽는 요약.
import sqlite3, sys, glob, io, base64, datetime, numpy as np
from rclpy.serialization import deserialize_message
from nav_msgs.msg import OccupancyGrid
B, D, T = sys.argv[1], sys.argv[2], sys.argv[3:]
KST = datetime.timezone(datetime.timedelta(hours=9))
db = sqlite3.connect(glob.glob(B + '/*.db3')[0])
tid = dict(db.execute('select name, id from topics'))['/global_costmap/costmap']
X0, X1, Y0, Y1 = -2.8, -0.8, -6.0, -1.6
out = {}
for hms in T:
    t = datetime.datetime.fromisoformat(f'{D}T{hms}').replace(tzinfo=KST).timestamp() * 1e9
    ts, data = db.execute('select timestamp, data from messages where topic_id=? order by abs(timestamp-?) limit 1', (tid, int(t))).fetchone()
    m = deserialize_message(data, OccupancyGrid); i = m.info
    g = np.array(m.data, dtype=np.int16).reshape(i.height, i.width)
    c0 = int((X0 - i.origin.position.x) / i.resolution); c1 = int((X1 - i.origin.position.x) / i.resolution)
    r0 = int((Y0 - i.origin.position.y) / i.resolution); r1 = int((Y1 - i.origin.position.y) / i.resolution)
    crop = g[r0:r1, c0:c1]
    k = hms.replace(':', '').replace('.', '_'); out['g' + k] = crop
    out['meta' + k] = np.array([ts / 1e9, i.resolution, i.origin.position.x + c0 * i.resolution, i.origin.position.y + r0 * i.resolution])
    print(f'{hms}: 메시지 {datetime.datetime.fromtimestamp(ts / 1e9, KST):%H:%M:%S.%f}'[:-4] + f' · 해상도 {i.resolution} · 창 {crop.shape} · 99 이상 {int((crop >= 99).sum())} 칸 · 253 이상 {int((crop >= 253).sum())} 칸')
bio = io.BytesIO(); np.savez_compressed(bio, **out)
print('NPZ ' + base64.b64encode(bio.getvalue()).decode())
