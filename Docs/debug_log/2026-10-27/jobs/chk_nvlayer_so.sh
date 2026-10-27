#!/bin/bash
# 읽기 전용: nvblox_nav2 설치 라이브러리 위치 · 갱신 시각 · 새 문자열(10-27 §17)
for f in $(find ~/ros2_ws/install/nvblox_nav2 -name "*.so*" 2>/dev/null); do echo "$f $(stat -c '%y' $(readlink -f $f) | cut -c1-19) sha $(sha256sum $(readlink -f $f) | cut -c1-12) 링크→ $(readlink -f $f)"; done
grep -rn "library path\|<library" ~/ros2_ws/install/nvblox_nav2/share/nvblox_nav2/*.xml 2>/dev/null | head -3
