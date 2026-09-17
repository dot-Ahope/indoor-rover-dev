#!/bin/bash
FW=/mnt/f/6_Indoor_Rover/Rover/firmware/rover_jupiter_fw
cd $FW/build
ls -la --time-style=+%T speed_controller.o safety_monitor.o microros_task.o main.o 2>/dev/null | awk '{print $6, $7}'
# 0.005f = 0x3ba3d70a, 0.010f = 0x3c23d70a, 0.008f = 0x3c23d70a? (0.008f = 0x3c03126f)
for o in speed_controller.o safety_monitor.o microros_task.o; do
  D=$(arm-none-eabi-objdump -s $o 2>/dev/null | tr -s ' ')
  printf "%-20s 0.005f(0ad7a33b):%s 0.010f(0ad7233c):%s 0.008f(6f12033c):%s 0.003f(a69bc43b):%s\n" $o \
    "$(echo "$D" | grep -ac '0ad7a33b')" "$(echo "$D" | grep -ac '0ad7233c')" "$(echo "$D" | grep -ac '6f12033c')" "$(echo "$D" | grep -ac 'a69bc43b')"
done
