#!/bin/bash
pkill -9 -f joy_linux 2>/dev/null; pkill -9 -f joy_node 2>/dev/null; pkill -9 -f teleop 2>/dev/null; sleep 1
echo "===장치 재인식 확인==="
lsusb | grep -i "0079" && echo "  DragonRise 연결됨" || echo "  ❌ 없음"
ls -l /dev/input/js* 2>&1
echo "  js0 생성시각(재연결시 갱신): $(stat -c '%y' /dev/input/js0 2>/dev/null | cut -d. -f1)"
echo "======= 클린 원시 읽기 8초 — 스틱 상하좌우 크게 움직여주세요 ======="
python3 - << 'PY'
import struct, os, fcntl, time, sys
try: f=open('/dev/input/js0','rb')
except Exception as e: print("open 실패:",e); sys.exit()
fl=fcntl.fcntl(f,fcntl.F_GETFL); fcntl.fcntl(f,fcntl.F_SETFL,fl|os.O_NONBLOCK)
end=time.time()+8; ax={}; mv=0; init=0
while time.time()<end:
    try: d=f.read(8)
    except: d=None
    if not d or len(d)<8: time.sleep(0.003); continue
    t,val,typ,num=struct.unpack('<IhBB',d)
    if typ&0x80: init+=1; continue
    if typ&0x02: ax[num]=val; mv+=1
sys.stdout.write(f"INIT {init}, 조작이벤트 {mv}, 움직인축 {dict(sorted(ax.items()))}\n")
sys.stdout.write("=> ✅ 장치 정상 — teleop 진행 가능\n" if mv else "=> ❌ 여전히 0\n")
sys.stdout.flush()
PY
echo END
