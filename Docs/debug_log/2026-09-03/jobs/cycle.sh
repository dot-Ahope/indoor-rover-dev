#!/bin/bash
# 펌웨어 MIN 값 변경 → 빌드 → 플래시 → ST-Link 리셋 → EKF 재시작 → 데드밴드 측정
MIN=$1
cd /f/6_Indoor_Rover/Rover
sed -i "s|^#define MIN_WHEEL_SPEED_MPS       [0-9.]*f|#define MIN_WHEEL_SPEED_MPS       ${MIN}f|" firmware/rover_jupiter_fw/App/app/rover_platform.h
echo "MIN 설정: $(grep -oE 'MIN_WHEEL_SPEED_MPS *[0-9.]+f' firmware/rover_jupiter_fw/App/app/rover_platform.h)"
export PATH="/c/ST/STM32CubeCLT_1.21.0/GNU-tools-for-STM32/bin:/c/Program Files (x86)/GnuWin32/bin:$PATH"
make -C firmware/rover_jupiter_fw -j8 2>&1 | grep -aE "^ *[0-9]+\s+[0-9]+|error" | tail -1
CLI="/c/ST/STM32CubeCLT_1.21.0/STM32CubeProgrammer/bin/STM32_Programmer_CLI.exe"
"$CLI" -c port=SWD reset=HWrst -w "F:\6_Indoor_Rover\Rover\firmware\rover_jupiter_fw\build\rover_jupiter_fw.elf" -v -rst 2>&1 | grep -aE "Download verified|error" | head -1
sleep 3
"$CLI" -c port=SWD reset=HWrst -rst 2>&1 | grep -aE "^MCU Reset" | head -1
sleep 12
