#!/bin/bash
echo "=== 시리얼 장치 전체 ==="
ls -l /dev/ttyUSB* /dev/ttyACM* /dev/rover /dev/rplidar 2>&1 | sed 's/^/  /'
echo ""
echo "=== by-id ==="
ls -l /dev/serial/by-id/ 2>&1 | sed 's/^/  /'
echo ""
echo "=== 각 ttyUSB 의 드라이버/USB 장치 ==="
for t in /dev/ttyUSB*; do
  [ -e "$t" ] || continue
  b=$(basename $t)
  drv=$(readlink -f /sys/class/tty/$b/device/driver 2>/dev/null | xargs -r basename)
  dev=$(readlink -f /sys/class/tty/$b/device 2>/dev/null)
  vid=$(cat $(dirname $dev)/../idVendor 2>/dev/null); pid=$(cat $(dirname $dev)/../idProduct 2>/dev/null)
  echo "  $b  driver=$drv  usb=$vid:$pid"
  echo "    보유 프로세스: $(fuser -v $t 2>&1 | tail -1)"
done
echo ""
echo "=== CH340 (1a86:7523) 엔드포인트 최대 패킷 크기 ==="
for d in /sys/bus/usb/devices/*/; do
  v=$(cat $d/idVendor 2>/dev/null); p=$(cat $d/idProduct 2>/dev/null)
  if [ "$v" = "1a86" ]; then
    echo "  USB 장치: $d (speed $(cat $d/speed 2>/dev/null) Mbps)"
    for ep in $d*/ep_*; do
      [ -e "$ep/wMaxPacketSize" ] && echo "    $(basename $ep): wMaxPacketSize=$(cat $ep/wMaxPacketSize) type=$(cat $ep/type 2>/dev/null) interval=$(cat $ep/interval 2>/dev/null)"
    done
  fi
done
echo ""
echo "=== 에이전트가 실제로 연 파일 (컨테이너) ==="
docker exec microros_agent sh -c 'for p in $(ls /proc | grep -E "^[0-9]+$"); do if grep -qa micro_ros_agent /proc/$p/cmdline 2>/dev/null; then echo "pid $p:"; ls -l /proc/$p/fd 2>/dev/null | grep -a tty; fi; done' 2>&1 | sed 's/^/  /'
