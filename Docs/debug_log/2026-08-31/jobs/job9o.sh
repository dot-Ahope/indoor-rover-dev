#!/bin/bash
echo "===모든 joy 프로세스 종료==="
pkill -9 -f joy_linux 2>/dev/null; pkill -9 -f joy_node 2>/dev/null; pkill -9 -f teleop 2>/dev/null; sleep 2
echo "잔존 joy: $(pgrep -af 'joy_linux|joy_node' | wc -l)개"
echo "===장치 상태==="
lsusb | grep -i "0079:181c" && echo "  DragonRise 연결됨" || echo "  ❌ DragonRise USB 없음(분리?)"
ls -l /dev/input/js0 2>&1
echo '<PW>' | sudo -S -p '' fuser -v /dev/input/js0 2>&1 | tail -2
echo "======= 클린 원시 읽기 8초 — 스틱 움직여주세요 ======="
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
sys.stdout.write("=> ✅ 장치 정상\n" if mv else "=> ❌ 이벤트 0 (장치/케이블/모드 점검 — 조이스틱 USB 재연결 권장)\n")
sys.stdout.flush()
PY
echo END
