#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "joy_node PID: $(pgrep -f joy_linux | tr '\n' ' ')  (여러개면 충돌)"
echo "======= 20초 내내 스틱을 계속 움직여주세요 (멈추지 마세요) ======="
python3 - << 'PY'
import time, struct, os, fcntl, threading, rclpy, sys
from rclpy.node import Node
from sensor_msgs.msg import Joy
# 원시 js0 (별도 fd)
raw={'move':0,'ax':{}}
def rawread(stop):
    try:
        f=open('/dev/input/js0','rb'); fl=fcntl.fcntl(f,fcntl.F_GETFL); fcntl.fcntl(f,fcntl.F_SETFL,fl|os.O_NONBLOCK)
    except Exception as e:
        raw['err']=str(e); return
    while not stop.is_set():
        try: d=f.read(8)
        except: d=None
        if not d or len(d)<8: time.sleep(0.003); continue
        t,val,typ,num=struct.unpack('<IhBB',d)
        if typ&0x80: continue
        if typ&0x02: raw['ax'][num]=val; raw['move']+=1
stop=threading.Event(); th=threading.Thread(target=rawread,args=(stop,)); th.start()
class A(Node):
    def __init__(s): super().__init__('m'); s.jc=0; s.a={}; s.create_subscription(Joy,'/joy',s.cb,10)
    def cb(s,m):
        s.jc+=1
        for i,v in enumerate(m.axes):
            if abs(v)>0.2: s.a[i]=round(v,2)
rclpy.init(); n=A(); e=time.time()+20
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.05)
stop.set(); th.join(timeout=1)
o=[f"원시 js0 조작이벤트 {raw['move']}개, 움직인축 {raw.get('ax',{})} {('ERR:'+raw['err']) if 'err' in raw else ''}"]
o.append(f"/joy 수신 {n.jc}개, |값|>0.2 축 {n.a}")
if raw['move']>0 and not n.a: o.append("=> 원시는 움직이나 /joy는 0 → joy_node가 js0 못읽음/멈춤 (재기동/설정 필요)")
elif raw['move']==0: o.append("=> 원시도 0 → 스틱 조작 안됨(타이밍) 또는 장치 이슈")
else: o.append(f"=> ✅ 둘 다 움직임 — /joy 정상 (이전 0은 타이밍)")
sys.stdout.write("\n".join(o)+"\n"); sys.stdout.flush()
PY
echo END
