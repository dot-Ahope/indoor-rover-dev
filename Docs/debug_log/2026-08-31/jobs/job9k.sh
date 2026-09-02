#!/bin/bash
pkill -f joy_linux 2>/dev/null; sleep 1   # 원시 읽기 위해 joy_node 정지
echo "======= 지금부터 10초! 버튼들을 눌러주세요 (스틱 말고 버튼) ======="
python3 - << 'PY'
import struct, os, fcntl, time, sys
f=open('/dev/input/js0','rb')
fl=fcntl.fcntl(f,fcntl.F_GETFL); fcntl.fcntl(f,fcntl.F_SETFL,fl|os.O_NONBLOCK)
end=time.time()+10; btn={}; ax={}; binit=0
while time.time()<end:
    try: d=f.read(8)
    except: d=None
    if not d or len(d)<8: time.sleep(0.003); continue
    t,val,typ,num=struct.unpack('<IhBB',d)
    base=typ & 0x7f
    if typ & 0x80:  # init
        if base==0x01: binit+=1
        continue
    if base==0x01: btn[num]=btn.get(num,0)+1
    elif base==0x02: ax[num]=val
sys.stdout.write(f"버튼 INIT {binit}, 눌림 이벤트: {dict(sorted(btn.items())) if btn else '없음'}\n")
if ax: sys.stdout.write(f"(참고: 움직인 축 {dict(sorted(ax.items()))})\n")
sys.stdout.write("=> ✅ 버튼 정상\n" if btn else "=> ❌ 버튼 이벤트 0 (이 패드는 버튼이 축/hat으로 올 수 있음 — 위 참고 축 확인)\n")
sys.stdout.flush()
PY
echo END
