#!/usr/bin/env python3
"""/cmd_vel 명령 충돌 검증 (2026-09-11 저녁, 사용자 질문).
  1) 지금 그래프에서 /cmd_vel, /cmd_vel_nav 의 발행자 노드
  2) velocity_smoother / behavior_server 의 관련 파라미터
  3) bag_s4r2 의 /cmd_vel 시계열: 0.3 s 창 안에서 linear.x 부호가 뒤섞이는 구간(전진↔후진↔0),
     같은 창에서 서로 다른 발행자가 섞였을 개연성(연속 메시지 간격이 비정상적으로 짧은 곳)"""
import subprocess, sys, math
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True, executable='/bin/bash').stdout
SRC="source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; "
print("=== 1) 발행자 ===")
for t in ('/cmd_vel','/cmd_vel_nav','/cmd_vel_smoothed'):
    out=sh(SRC+f"timeout 8 ros2 topic info {t} --verbose 2>/dev/null")
    pubs=[]; sec=None
    for l in out.splitlines():
        if l.startswith('Publishers:'): sec='p'
        elif l.startswith('Subscribers:'): sec='s'
        elif 'Node name:' in l and sec=='p': pubs.append(l.split(':',1)[1].strip())
    print(f"  {t:18s} 발행자 {len(pubs)}: {pubs}")
print("=== 2) 파라미터 ===")
for n,p in (('/velocity_smoother','velocity_timeout'),('/velocity_smoother','max_decel'),('/velocity_smoother','max_accel'),
            ('/velocity_smoother','smoothing_frequency'),('/velocity_smoother','feedback'),('/velocity_smoother','deadband_velocity'),
            ('/controller_server','FollowPath.max_allowed_time_to_collision_up_to_carrot')):
    v=sh(SRC+f"timeout 6 ros2 param get {n} {p} 2>/dev/null").strip().replace('\n',' ')
    print(f"  {n} {p}: {v.split('is:')[-1].strip() if 'is:' in v else v or '?'}")
print("=== 3) bag_s4r2 /cmd_vel 시계열 ===")
try:
    import rosbag2_py
    from rclpy.serialization import deserialize_message
    from geometry_msgs.msg import Twist
except Exception as e:
    print("  rosbag2_py 없음:", e); sys.exit(0)
import glob
bags=sorted(glob.glob('/tmp/bag_s4r2'))
if not bags: print("  bag 없음"); sys.exit(0)
r=rosbag2_py.SequentialReader()
r.open(rosbag2_py.StorageOptions(uri=bags[0], storage_id='sqlite3'), rosbag2_py.ConverterOptions('',''))
msgs=[]
while r.has_next():
    topic,data,ts=r.read_next()
    if topic=='/cmd_vel':
        m=deserialize_message(data,Twist); msgs.append((ts*1e-9, m.linear.x, m.angular.z))
if not msgs: print("  /cmd_vel 메시지 없음"); sys.exit(0)
t0=msgs[0][0]; msgs=[(t-t0,v,w) for t,v,w in msgs]
print(f"  메시지 {len(msgs)}개, {msgs[-1][0]:.1f}s, 평균 간격 {(msgs[-1][0]-msgs[0][0])/max(len(msgs)-1,1)*1000:.0f} ms")
# 간격 분포
gaps=[msgs[i][0]-msgs[i-1][0] for i in range(1,len(msgs))]
import statistics
print(f"  간격 중앙 {statistics.median(gaps)*1000:.0f} ms, 10ms 미만 {sum(1 for g in gaps if g<0.010)}개, 1s 초과 {sum(1 for g in gaps if g>1.0)}개")
# 부호 뒤섞임: 0.3s 창 안에 +v, -v, 0 이 함께
def sgn(v): return 1 if v>0.005 else (-1 if v<-0.005 else 0)
mix=[]
W=0.3
for i in range(len(msgs)):
    win=[m for m in msgs[i:] if m[0]-msgs[i][0]<=W]
    s=set(sgn(m[1]) for m in win)
    if 1 in s and -1 in s: mix.append((msgs[i][0], [(round(m[0]-msgs[i][0],2), round(m[1],3)) for m in win[:8]]))
# 중복 제거(연속 창)
uniq=[]; last=-9
for t,w in mix:
    if t-last>W: uniq.append((t,w)); last=t
print(f"  0.3s 창 안에 전진(+)과 후진(−)이 같이 있는 구간: {len(uniq)}곳")
for t,w in uniq[:8]:
    print(f"    t={t:6.1f}s  {w}")
# 후진 구간 목록과 그 직전 명령
back=[i for i,m in enumerate(msgs) if m[1]<-0.005]
if back:
    starts=[back[0]]+[back[k] for k in range(1,len(back)) if msgs[back[k]][0]-msgs[back[k-1]][0]>0.5]
    print(f"  후진 시작 {len(starts)}회:")
    for i in starts[:6]:
        pre=[(round(m[0]-msgs[i][0],2), round(m[1],3)) for m in msgs[max(0,i-5):i+3]]
        print(f"    t={msgs[i][0]:6.1f}s  직전~직후: {pre}")
