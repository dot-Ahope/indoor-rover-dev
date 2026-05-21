#!/bin/bash
# F5a — WSL Ubuntu-22.04 에서 micro-ROS 정적 라이브러리 빌드.
# Docker 없이 colcon 으로 직접 빌드.
# 결과: $UTILS/libmicroros/{libmicroros.a, include/*}
set -e
set -o pipefail

UTILS=/mnt/c/Project/Rover/Rover/firmware/rover_jupiter_fw/Middlewares/Third_Party/micro_ros_stm32cubemx_utils
LIBDIR=$UTILS/microros_static_library_ide

WSL_BUILD=$HOME/microros_build
mkdir -p $WSL_BUILD/src
cd $WSL_BUILD

echo "===== Step 0: rosdep init ====="
if [ ! -d /etc/ros/rosdep ]; then
    rosdep init
fi

echo "===== Step 1: clone micro_ros_setup ====="
if [ ! -d src/micro_ros_setup ]; then
    git clone -b humble https://github.com/micro-ROS/micro_ros_setup.git src/micro_ros_setup
fi

source /opt/ros/humble/setup.bash

echo "===== Step 2: rosdep update + install ====="
rosdep update 2>&1 | tail -3
rosdep install --from-paths src --ignore-src -y -r 2>&1 | tail -5

echo "===== Step 3: colcon build (micro_ros_setup) ====="
colcon build 2>&1 | tail -5
source install/local_setup.bash

echo "===== Step 4: create_firmware_ws (generate_lib) ====="
# 이전 partial 실패 정리: firmware/ 가 있는데 mcu_ws 가 없으면 partial state.
if [ -d firmware ] && [ ! -d firmware/mcu_ws ]; then
    echo "Removing partial firmware/ from previous failed run"
    rm -rf firmware
fi
if [ ! -d firmware/mcu_ws ]; then
    ros2 run micro_ros_setup create_firmware_ws.sh generate_lib 2>&1 | tail -10
fi

echo "===== Step 5: add tf2_msgs (workaround) ====="
pushd firmware/mcu_ws > /dev/null
if [ ! -d ros2/tf2_msgs ]; then
    git clone -b ros2 https://github.com/ros2/geometry2 /tmp/geometry2
    cp -R /tmp/geometry2/tf2_msgs ros2/tf2_msgs
    rm -rf /tmp/geometry2
fi
popd > /dev/null

echo "===== Step 6: build firmware (libmicroros.a) ====="
export TOOLCHAIN_PREFIX=/usr/bin/arm-none-eabi-
# F405 cross-compile flags — 우리 Makefile 과 동일 (Og→O0 으로 라이브러리는 디버그 무관)
export RET_CFLAGS="-ffunction-sections -fdata-sections -DSTM32CUBEIDE \
-DENOTSUP=1 -DECANCELED=1 -DEOWNERDEAD=1 -DENOTRECOVERABLE=1 \
-mcpu=cortex-m4 -mfloat-abi=hard -mthumb -mfpu=fpv4-sp-d16 \
-O2 -DSTM32F405xx -DUSE_HAL_DRIVER"

ros2 run micro_ros_setup build_firmware.sh \
    $LIBDIR/library_generation/toolchain.cmake \
    $LIBDIR/library_generation/colcon.meta 2>&1 | tail -20

echo "===== Step 7: copy output to project ====="
find firmware/build/include/ -name "*.c" -delete 2>/dev/null || true
DEST=$UTILS/libmicroros
rm -rf $DEST
mkdir -p $DEST/include
cp -R firmware/build/include/* $DEST/include/
cp firmware/build/libmicroros.a $DEST/libmicroros.a

# include path 정리 (script line 86-94 와 동일)
pushd firmware/mcu_ws > /dev/null
INCLUDE_PACKAGES=$(colcon list 2>/dev/null | awk '{print $1}')
popd > /dev/null

for var in $INCLUDE_PACKAGES; do
    if [ -d "$DEST/include/${var}/${var}" ]; then
        cp -r $DEST/include/${var}/${var}/* $DEST/include/${var}/ 2>/dev/null || true
        rm -rf $DEST/include/${var}/${var}
    fi
done

echo ""
echo "===== DONE ====="
ls -la $DEST/libmicroros.a
echo "Headers: $(find $DEST/include -name '*.h' | wc -l) files"
