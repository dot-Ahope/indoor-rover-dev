#!/usr/bin/env python3
# anal_series_1113 — 11-13 §6: bag(db3)에서 지정 창의 시계열을 csv(gzip+base64)로 표준 출력에 낸다(큰 컬러 bag 을 옮기지 않고 분석 재료만 PC 로).
#   왜: f2rd2 목표 5 에서 '회전 지령은 있는데 회전이 안 됨'(stuck_monitor) — 지령 · 바퀴 · 보드 상태(듀티 · 스톨)를 나란히, 그리고 목표 3 · 4 진입 때 방향 전환을 경로와 함께 본다.
#   Jetson, 로버 안 움직임 · DDS 참여자 안 만듦. 인자: bag 폴더 날짜 시작HH:MM:SS 끝HH:MM:SS
#   출력: 'CSV <base64(gzip(text))>' 한 줄. 텍스트 줄 형식: 토픽약칭,수신시각(epoch s),값…
#     cmd,t,v,w | wod,t,v,w(/wheel_odom twist) | ekf,t,x,y,yaw,v,w(/odometry/filtered, odom 프레임) | st,t,key=val;…(/rover/status 첫 상태)
#     plan,t,n,x0,y0,xe,ye,yawe(/plan, map) | bt,t,node,prev,cur(/behavior_tree_log, IDLE 로 가는 줄 제외) | tf,t,mo_x,mo_y,mo_yaw(map→odom)
import sqlite3, sys, glob, io, gzip, base64, datetime, math
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
B, D, S, E = sys.argv[1:5]
KST = datetime.timezone(datetime.timedelta(hours=9))
ep = lambda h: int(datetime.datetime.fromisoformat(f'{D}T{h}').replace(tzinfo=KST).timestamp() * 1e9)
t0, t1 = ep(S), ep(E)
db = sqlite3.connect(glob.glob(B + '/*.db3')[0])
tp = {n: (i, t) for i, n, t in db.execute('select id, name, type from topics')}
yaw = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
out = []
def rows(name):
    if name not in tp: return
    i, t = tp[name]; M = get_message(t)
    for ts, d in db.execute('select timestamp, data from messages where topic_id=? and timestamp between ? and ? order by timestamp', (i, t0, t1)):
        yield ts / 1e9, deserialize_message(d, M)
for t, m in rows('/cmd_vel'): out.append(f'cmd,{t:.3f},{m.linear.x:.4f},{m.angular.z:.4f}')
for t, m in rows('/wheel_odom'): out.append(f'wod,{t:.3f},{m.twist.twist.linear.x:.4f},{m.twist.twist.angular.z:.4f}')
for t, m in rows('/odometry/filtered'):
    p = m.pose.pose; out.append(f'ekf,{t:.3f},{p.position.x:.4f},{p.position.y:.4f},{yaw(p.orientation):.4f},{m.twist.twist.linear.x:.4f},{m.twist.twist.angular.z:.4f}')
for t, m in rows('/rover/status'):
    if m.status: out.append(f'st,{t:.3f},' + ';'.join(f'{kv.key}={kv.value}' for kv in m.status[0].values) + f';level={m.status[0].level};msg={m.status[0].message}')
for t, m in rows('/plan'):
    ps = m.poses
    if ps: out.append(f'plan,{t:.3f},{len(ps)},{ps[0].pose.position.x:.3f},{ps[0].pose.position.y:.3f},{ps[-1].pose.position.x:.3f},{ps[-1].pose.position.y:.3f},{yaw(ps[-1].pose.orientation):.3f}')
for t, m in rows('/behavior_tree_log'):
    for ev in m.event_log:
        if ev.current_status != 'IDLE': out.append(f'bt,{t:.3f},{ev.node_name},{ev.previous_status},{ev.current_status}')
for t, m in rows('/tf'):
    for tr in m.transforms:
        if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
            q = tr.transform; out.append(f'tf,{t:.3f},{q.translation.x:.4f},{q.translation.y:.4f},{yaw(q.rotation):.4f}')
out.sort(key=lambda s: float(s.split(',')[1]))
print(f'줄 {len(out)} · 종류별 ' + ' '.join(f'{k}={sum(1 for s in out if s.startswith(k + ","))}' for k in ('cmd', 'wod', 'ekf', 'st', 'plan', 'bt', 'tf')))
print('CSV ' + base64.b64encode(gzip.compress('\n'.join(out).encode())).decode())
