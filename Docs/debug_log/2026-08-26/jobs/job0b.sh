#!/bin/bash
# CH340이 ttyUSB로 안 잡히는 원인 조사: 커널 로그 + brltty 여부
echo "===SUDO_DMESG==="
echo '<PW>' | sudo -S dmesg 2>/dev/null | grep -iE "ch34|ttyUSB|1a86|brltty" | tail -15
echo "===BRLTTY_PKG==="
dpkg -l | grep -i brltty || echo NO_BRLTTY_PKG
echo "===BRLTTY_PROC==="
ps aux | grep -i [b]rltty || echo NO_BRLTTY_PROC
echo "===UDEV_INFO==="
udevadm info -q all -p /sys/bus/usb/devices/1-2.2 2>/dev/null | head -20
for d in /sys/bus/usb/devices/*; do
  if [ -f "$d/idVendor" ] && [ "$(cat $d/idVendor)" = "1a86" ]; then
    echo "CH340 at: $d"
    echo "  driver binds:"
    ls "$d":*/ -d 2>/dev/null
    for intf in "$d":*; do
      [ -e "$intf/driver" ] && echo "  $intf -> $(readlink -f $intf/driver)"
    done
  fi
done
