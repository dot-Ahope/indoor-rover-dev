#!/bin/bash
# 설치된 nav2_mppi_controller(Humble 1.1.20) 헤더에서 시뮬레이터 충실도 관련 동작 확인 (읽기 전용)
I=/opt/ros/humble/include/nav2_mppi_controller
[ -d "$I" ] || I=$(dirname $(find /opt/ros/humble/include -name optimizer.hpp -path '*mppi*' | head -1))/..
echo "헤더 경로: $I"; find $I -name '*.hpp' | sed "s#$I/##" | sort | tr '\n' ' '; echo
echo "== regenerate / noise"; grep -rn "regenerate\|generateNoisedControls\|noise_thread\|ready_" $I --include=*.hpp | cut -c1-200
echo "== savitsky / history / smoothing"; grep -rn -i "savitsky\|control_history\|smooth" $I --include=*.hpp | cut -c1-200
echo "== softmax / temperature / gamma"; grep -rn "temperature\|gamma\|softmax\|exp(" $I --include=*.hpp | cut -c1-200
echo "== initial state velocities"; grep -rn "updateInitialStateVelocities\|propagateStateVelocities\|state.speed\|speed.linear\|speed.angular" $I --include=*.hpp | cut -c1-220
echo "== shift"; grep -rn "shift" $I --include=*.hpp | cut -c1-200
