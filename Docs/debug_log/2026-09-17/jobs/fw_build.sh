#!/bin/bash
mkdir -p /mnt/f; mountpoint -q /mnt/f || mount -t drvfs F: /mnt/f || { echo "F: 마운트 실패"; exit 1; }
FW=/mnt/f/6_Indoor_Rover/Rover/firmware/rover_jupiter_fw
echo "=== 불변식 검사가 실제로 걸리는지 (MIN 을 4 mm/s 로 바꾼 사본 전처리) ==="
T=/tmp/fwcheck; rm -rf $T; mkdir -p $T; cp $FW/App/app/rover_platform.h $T/; cp $FW/App/app/motor_config.h $T/ 2>/dev/null || find $FW -name motor_config.h -exec cp {} $T/ \;
sed -i 's/#define MIN_WHEEL_SPEED_UMPS          8000/#define MIN_WHEEL_SPEED_UMPS          4000/' $T/rover_platform.h
echo '#include "rover_platform.h"' > $T/t.c
arm-none-eabi-gcc -E -I$T $T/t.c -o /dev/null 2>&1 | grep -a "error" | head -2
echo "=== 정상 헤더 전처리 ==="; cp $FW/App/app/rover_platform.h $T/rover_platform.h; arm-none-eabi-gcc -E -I$T $T/t.c -o /dev/null 2>&1 | grep -ac error | sed 's/^/  error 줄 수: /'
echo "=== 빌드 ==="; cd $FW && make -j8 2>&1 | grep -aE "error|warning: .*(speed_controller|safety_monitor|rover_platform|microros_task)|arm-none-eabi-size|text|rover_jupiter_fw.elf" | tail -12
ls -la --time-style=+%F\ %T $FW/build/rover_jupiter_fw.elf | awk '{print $6, $7, $5, $8}'
