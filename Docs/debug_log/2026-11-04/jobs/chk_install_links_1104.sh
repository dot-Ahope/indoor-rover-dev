#!/bin/bash
# 11-04: 설치본 설정 파일이 src 를 가리키는 링크인지(prep 옛 sed -i 가 끊었는지) 확인 — 읽기만, 로버 안 움직임
I=~/ros2_ws/install/rover_navigation/share/rover_navigation/config
for f in $I/*.yaml $I/*.xml; do
  if [ -L "$f" ]; then echo "링크  $(basename $f) -> $(readlink -f $f)"; else
    s=~/ros2_ws/src/rover_navigation/config/$(basename $f)
    if cmp -s "$f" "$s"; then d="src 와 같음"; else d="src 와 다름($(diff "$s" "$f" | grep -c '^[<>]') 줄)"; fi
    echo "파일  $(basename $f)  $d  $(stat -c %y $f | cut -c1-19)"; fi
done
echo "== PreferForward 값(src · 설치본)"; grep -ho 'PreferForwardCritic: {[^}]*}' ~/ros2_ws/src/rover_navigation/config/nav2_params.yaml $I/nav2_params.yaml
echo "== 저장소 커밋(Jetson src)"; git -C ~/ros2_ws log -1 --format='%h %cd' 2>/dev/null || echo "(src 는 git 아님)"
