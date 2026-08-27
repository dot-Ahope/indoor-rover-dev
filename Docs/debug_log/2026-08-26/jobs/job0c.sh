#!/bin/bash
# udev 규칙: CH340(1a86:7523) -> /dev/rover 심볼릭 링크 고정
echo '<PW>' | sudo -S bash -c 'cat > /etc/udev/rules.d/99-rover.rules << "EOF"
# ALOPS Jupiter R1.4 (STM32F405) - CH340N USB-serial
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="rover", GROUP="dialout", MODE="0660"
EOF
udevadm control --reload-rules && udevadm trigger --subsystem-match=tty'
sleep 1
echo "===VERIFY==="
ls -l /dev/rover 2>/dev/null || echo NO_ROVER_LINK
