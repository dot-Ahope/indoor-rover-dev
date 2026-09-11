#!/usr/bin/env python3
import subprocess, sys, glob
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True, executable='/bin/bash').stdout
SRC="source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; "
print("=== 1) /cmd_vel 계열 발행자 (Humble 형식: 'Publisher count') ===")
for t in ('/cmd_vel','/cmd_vel_nav'):
    out=sh(SRC+f"timeout 8 ros2 topic info {t} --verbose 2>/dev/null")
    sec=None; pubs=[]; subs=[]
    for l in out.splitlines():
        if l.startswith('Publisher count'): sec='p'
        elif l.startswith('Subscription count'): sec='s'
        elif 'Node name:' in l: (pubs if sec=='p' else subs).append(l.split(':',1)[1].strip())
    print(f"  {t:14s} 발행자 {pubs}   구독자 {subs}")
print("  stuck_monitor 발행 토픽:", [l.strip() for l in sh(SRC+"timeout 8 ros2 node info /stuck_monitor 2>/dev/null").split('Publishers:')[-1].split('Service Servers')[0].splitlines() if l.strip().startswith('/')][:6])
print("=== 2) 더듬거림: 전진(+)→0→전진(+) 이 1 s 안에 반복되는 구간 (bag_s4r2) ===")
import rosbag2_py
from rclpy.serialization import deserialize_message
from geometry_msgs.msg import Twist
r=rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri='/tmp/bag_s4r2',storage_id='sqlite3'),rosbag2_py.ConverterOptions('',''))
msgs=[]
while r.has_next():
    t,d,ts=r.read_next()
    if t=='/cmd_vel': m=deserialize_message(d,Twist); msgs.append((ts*1e-9,m.linear.x))
t0=msgs[0][0]; msgs=[(t-t0,v) for t,v in msgs]
sg=[1 if v>0.005 else (-1 if v<-0.005 else 0) for _,v in msgs]
runs=[]; i=0
while i<len(sg):
    j=i
    while j<len(sg) and sg[j]==sg[i]: j+=1
    runs.append((sg[i], msgs[i][0], msgs[j-1][0]-msgs[i][0]+0.05, j-i)); i=j
short_stop=[(s,t,d,n) for s,t,d,n in runs if s==0 and d<1.0]
print(f"  구간(run) {len(runs)}개: 전진 {sum(1 for x in runs if x[0]==1)}, 정지 {sum(1 for x in runs if x[0]==0)}, 후진 {sum(1 for x in runs if x[0]==-1)}")
print(f"  1 s 미만의 짧은 정지 {len(short_stop)}개 → 앞뒤가 전진인 것(더듬거림): {sum(1 for k,(s,t,d,n) in enumerate(runs) if s==0 and d<1.0 and 0<k<len(runs)-1 and runs[k-1][0]==1 and runs[k+1][0]==1)}개")
for s,t,d,n in runs[:40]:
    if d>=0.15 or s!=0: print(f"    {'전진' if s==1 else ('후진' if s==-1 else '정지')} t={t:5.1f}s {d:4.2f}s")
print("=== 3) N1 사실: JetPack / L4T / CUDA / Isaac ROS 흔적 ===")
print("  L4T:", sh("head -1 /etc/nv_tegra_release 2>/dev/null").strip() or '?')
print("  JetPack:", sh("dpkg -l 2>/dev/null | grep -E 'nvidia-jetpack ' | awk '{print $3}'").strip() or '?', "| CUDA:", sh("ls /usr/local | grep -E '^cuda-[0-9]' | tr '\n' ' '").strip() or '?')
print("  isaac_ros apt 소스:", sh("grep -rl isaac /etc/apt/sources.list.d/ 2>/dev/null | tr '\n' ' '").strip() or '없음', "| isaac 패키지:", sh("dpkg -l 2>/dev/null | grep -ci isaac").strip())
print("  nvblox 워크스페이스 흔적:", sh("ls ~/ros2_ws/src 2>/dev/null | grep -i -E 'isaac|nvblox' | tr '\n' ' '").strip() or '없음')
print("  GPU 사용률(tegrastats 1회):", sh("timeout 3 tegrastats --interval 1000 2>/dev/null | head -1 | grep -oE 'GR3D_FREQ [0-9]+%'").strip() or '?')
print("  free -m:", sh("free -m | awk 'NR==2{print $2\"MB 총, \"$7\"MB 가용\"}'").strip())
