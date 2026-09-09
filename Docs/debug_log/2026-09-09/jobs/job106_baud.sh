#!/bin/bash
echo "=== agent 실행 인자 ==="
docker inspect -f '{{join .Config.Cmd " "}}' microros_agent 2>/dev/null | sed 's/^/  Cmd: /'
docker inspect -f '{{join .Config.Entrypoint " "}}' microros_agent 2>/dev/null | sed 's/^/  Entrypoint: /'
echo ""
echo "=== /dev/ttyUSB0 실제 termios (호스트) ==="
stty -F /dev/ttyUSB0 2>&1 | head -4 | sed 's/^/  /'
echo ""
echo "=== io 카운터 접근 시도 ==="
docker exec microros_agent cat /proc/1/io 2>&1 | head -8 | sed 's/^/  /'
echo ""
echo "=== 컨테이너 내 프로세스 ==="
docker top microros_agent 2>/dev/null | head -4 | sed 's/^/  /'
echo ""
echo "=== USB 컨트롤러/장치 ==="
lsusb 2>/dev/null | grep -aiE "ch340|1a86|serial" | sed 's/^/  /'
echo "  드라이버: $(readlink -f /sys/class/tty/ttyUSB0/device/driver 2>/dev/null | xargs -r basename)"
echo "  bulk 엔드포인트 크기:"
for f in /sys/bus/usb/devices/*/bInterfaceNumber; do :; done
find /sys/bus/usb/devices -name "ep_8*" -o -name "ep_0*" 2>/dev/null | head -0
udevadm info -a -n /dev/ttyUSB0 2>/dev/null | grep -aE "bMaxPacketSize|idVendor|idProduct|speed" | head -6 | sed 's/^/    /'
echo ""
echo "=== 재시도: 10초 바이트 유입 (호스트에서 컨테이너 pid 경유) ==="
CPID=$(docker inspect -f '{{.State.Pid}}' microros_agent 2>/dev/null)
echo "  호스트 기준 agent pid = ${CPID:-?}"
if [ -n "$CPID" ] && [ -r /proc/$CPID/io ]; then
  A=$(awk '/^rchar/{print $2}' /proc/$CPID/io)
  sleep 10
  B=$(awk '/^rchar/{print $2}' /proc/$CPID/io)
  echo "  보드->젯슨 $(( (B-A)/10 )) B/s"
else
  echo "  /proc/$CPID/io 읽기 불가 (권한)"
fi
