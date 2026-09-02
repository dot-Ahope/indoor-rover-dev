#!/bin/bash
source /opt/ros/humble/setup.bash 2>/dev/null
echo "===모든 joy/teleop 종료==="
pkill -9 -f teleop 2>/dev/null; pkill -9 -f joy_linux 2>/dev/null; pkill -9 -f joy_node 2>/dev/null; sleep 2
echo "  ros2 node에 joy 남았나: $(source ~/ros2_ws/install/setup.bash 2>/dev/null; ros2 node list 2>/dev/null | grep -c joy)"
echo "  프로세스(ros2 run 래퍼 포함 카운트): $(pgrep -af 'joy_linux' | cut -c1-60)"
echo "===원시 js0 중립값 (스틱 놓은 상태, 5초) — 1.00이면 장치 latch 문제==="
timeout 6 python3 - << 'PY'
import struct, os, fcntl, time, sys
f=open('/dev/input/js0','rb'); fl=fcntl.fcntl(f,fcntl.F_GETFL); fcntl.fcntl(f,fcntl.F_SETFL,fl|os.O_NONBLOCK)
end=time.time()+5; ax={}; last={}; mv=0
while time.time()<end:
    try: d=f.read(8)
    except: d=None
    if not d or len(d)<8: time.sleep(0.005); continue
    t,val,typ,num=struct.unpack('<IhBB',d)
    base=typ&0x7f
    if base==0x02:
        last[num]=val
        if not (typ&0x80): mv+=1
sys.stdout.write(f"중립 시 각 축 마지막값(정규화): {({k:round(v/32767,2) for k,v in sorted(last.items())})}\n")
sys.stdout.write(f"조작(비INIT) 이벤트 {mv}개 (손 뗐으면 0이어야)\n")
big=[k for k,v in last.items() if abs(v)>16000]
sys.stdout.write(f"=> 중립인데 |값|>0.5인 축: {big} {'← ⚠ 장치가 풀값 latch(패드 문제)' if big else '(없음 = 정상 중립)'}\n")
sys.stdout.flush()
PY
echo END
