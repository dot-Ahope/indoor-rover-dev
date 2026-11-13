#!/usr/bin/env python3
# anal_color_frames_1113 — 11-13 §3: f2rd1 bag 의 컬러 원본(640x480 rgb8)에서 지정 시각에 가장 가까운 장면을 JPEG(base64)로 표준 출력에 낸다.
#   왜: 서쪽 통로 동쪽 가장자리에 저장 지도에 없는 비용 ≥ 99 칸이 생김 — 실제 물체인지 카메라로 확인. Jetson, 로버 안 움직임 · DDS 참여자 안 만듦.
#   인자: bag 폴더 날짜 시각… . 출력: 시각마다 'JPG <HHMMSS> <base64>' 한 줄.
import sqlite3, sys, glob, io, base64, datetime, numpy as np
from PIL import Image
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import Image as Img
B, D, T = sys.argv[1], sys.argv[2], sys.argv[3:]
KST = datetime.timezone(datetime.timedelta(hours=9))
db = sqlite3.connect(glob.glob(B + '/*.db3')[0])
tid = dict(db.execute('select name, id from topics'))['/camera/camera/color/image_raw']
for hms in T:
    t = datetime.datetime.fromisoformat(f'{D}T{hms}').replace(tzinfo=KST).timestamp() * 1e9
    ts, data = db.execute('select timestamp, data from messages where topic_id=? order by abs(timestamp-?) limit 1', (tid, int(t))).fetchone()
    m = deserialize_message(data, Img)
    a = np.frombuffer(bytes(m.data), np.uint8).reshape(m.height, m.width, 3)
    bio = io.BytesIO(); Image.fromarray(a).save(bio, 'JPEG', quality=80)
    print(f'JPG {hms.replace(":", "")} {datetime.datetime.fromtimestamp(ts / 1e9, KST):%H:%M:%S.%f}'[:-4].replace(' ', '_', 0) + ' ' + base64.b64encode(bio.getvalue()).decode())
