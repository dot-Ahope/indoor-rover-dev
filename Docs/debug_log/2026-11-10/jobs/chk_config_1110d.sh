#!/bin/bash
# chk_config_1110d — 11-10 §0 이어서(읽기만 · 로버 안 움직임 · DDS 참여자 안 만듦).
#   왜: 1110 에서 설치된 BT 플러그인 .so 시각(PathBlockedAhead 10-01 · CopyPath 10-14)이 그 뒤 포트를 더한 소스 변경
#       (only_new 10-23 커밋 0a6e5f73 · step 10-26 커밋 36e59493)보다 앞섬 → 옛 빌드가 깔렸는지 판별.
#   판정: .so 안에 포트 이름 문자열(only_new · step 의 설명문)이 있으면 새 빌드, 없으면 옛 빌드. 시각만으로 판단하지 않는다.
#   보는 것: install · build 두 곳의 .so 시각 · 크기 · md5 와 문자열 검색. 인자: 없음. 출력: 표준 출력.
for lib in librover_path_blocked_ahead_bt_node.so librover_copy_path_bt_node.so; do
  for d in ~/ros2_ws/install/rover_navigation/lib ~/ros2_ws/build/rover_navigation; do
    f=$d/$lib; [ -e "$f" ] || { echo "없음 $f"; continue; }
    echo "$(stat -c '%y %s' $f | cut -c1-16,36-) $(md5sum < $f | cut -c1-12) ${f#$HOME/ros2_ws/}"
  done
done
echo "== 포트 문자열"
P=~/ros2_ws/install/rover_navigation/lib
echo "  PathBlockedAhead only_new: $(strings $P/librover_path_blocked_ahead_bt_node.so | grep -c 'only_new')"
echo "  CopyPath step 설명: $(strings $P/librover_copy_path_bt_node.so | grep -c '호 길이 간격')"
echo "  CopyPath input_path: $(strings $P/librover_copy_path_bt_node.so | grep -c 'input_path')"
# 1차 실행 뒤 덧붙임: 한글 설명문은 strings(기본 ASCII)가 못 뽑음 → 영문 포트 이름 'step' 을 낱말 단위로. 링크 여부도 찍음
echo "  CopyPath 'step' 낱말: $(strings $P/librover_copy_path_bt_node.so | grep -cx 'step')"
ls -l $P/librover_path_blocked_ahead_bt_node.so $P/librover_copy_path_bt_node.so | awk '{print "  " $1, $9, $10, $11}' | sed "s|$HOME/ros2_ws/||g"
