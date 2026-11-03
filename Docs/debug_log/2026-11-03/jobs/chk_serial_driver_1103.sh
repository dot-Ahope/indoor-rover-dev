#!/bin/bash
# 보드 CH340 장치 이름(ttyCH341USB0 vs ttyUSB*)과 ch341 드라이버 출처(커널 기본 vs WCH 벤더) 확인 — 11-03 §11
# Jetson 에서 읽기만(sudo 없음 · 설정 변경 없음 · 로버 안 움직임). 인자 없음. 출력은 화면(PC 가 outputs/ 로 저장).
echo "== 커널 · L4T"
uname -r
head -1 /etc/nv_tegra_release 2>/dev/null
echo "== 별칭 · 실장치"
ls -l /dev/rover /dev/rplidar 2>&1
ls -l /dev/ttyUSB* /dev/ttyCH341USB* 2>&1
echo "== 실린 모듈"
lsmod | grep -iE 'ch34|cp210|usbserial|ftdi' || echo "(없음)"
echo "== modinfo ch341"
modinfo ch341 2>&1 | grep -iE '^(filename|version|author|description|vermagic|srcversion)'
echo "== 모듈 파일 위치 (커널 기본 자리 · updates · extra)"
K=/lib/modules/$(uname -r)
ls -l $K/kernel/drivers/usb/serial/ch341.ko* 2>&1
find $K -name 'ch34*.ko*' 2>/dev/null | while read f; do echo "$f  $(stat -c '%y %s' "$f" | cut -c1-19)"; done
echo "== 커널 기본 모듈 목록에 ch341 이 있는가 (modules.builtin · 패키지 소유)"
grep -c ch341 $K/modules.builtin 2>/dev/null
dpkg -S "$K/kernel/drivers/usb/serial/ch341.ko" 2>&1 | head -2
echo "== 장치에 붙은 드라이버 (sysfs)"
for d in /sys/bus/usb/devices/*; do
  [ -f "$d/idVendor" ] || continue
  v=$(cat $d/idVendor); p=$(cat $d/idProduct)
  case "$v:$p" in 1a86:*|10c4:*)
    echo "$(basename $d) $v:$p"
    for i in "$d":*; do [ -e "$i/driver" ] && echo "   $(basename $i) -> $(basename $(readlink -f $i/driver))  tty: $(ls $i 2>/dev/null | grep -E 'tty' | tr '\n' ' ')"; done ;;
  esac
done
echo "== ~/ch341_build"
ls -la ~/ch341_build 2>&1 | head -20
grep -rIl 'ttyCH341USB' ~/ch341_build 2>/dev/null | head -5
grep -rIhoE 'DRIVER_VERSION[^;]*|#define VERSION[^;]*' ~/ch341_build 2>/dev/null | head -3
echo "== 부팅 뒤 커널 로그 (sudo 없이 읽히면)"
dmesg 2>&1 | grep -iE 'ch34|ttyCH341|cp210x' | tail -8
echo "== udev 규칙 파일"
ls -l /etc/udev/rules.d/ 2>&1 | grep -iE 'rover|rplidar|serial'
