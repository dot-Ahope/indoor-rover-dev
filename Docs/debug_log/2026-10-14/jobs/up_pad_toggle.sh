#!/bin/bash
# (10-14 §21 A/B 시험 B 조건) 로버가 서 있는 상태에서 로컬 코스트맵 footprint_padding 을 pad_relief 가 f2t1 에서 한 것과 같은 값·간격으로 바꿨다 되돌린다.
#   f2t1: 15:23:24 0.010 → 0.000, 15:23:33 0.000 → 0.010(9 s). pad_relief 도 같은 /local_costmap/local_costmap SetParameters 서비스를 쓴다.
#   로버 안 움직임. 끝난 뒤 30 s 넘게 기다렸다 주행(주행 30 s 전 DDS 참여자 생성 금지 규칙).
P=/local_costmap/local_costmap
echo "$(date +%T.%N | cut -c1-12) 시작 패딩 $(timeout 12 ros2 param get $P footprint_padding 2>&1 | tail -1)"
echo "$(date +%T.%N | cut -c1-12) → 0.0 : $(timeout 12 ros2 param set $P footprint_padding 0.0 2>&1 | tail -1)"
sleep 9
echo "$(date +%T.%N | cut -c1-12) → 0.01: $(timeout 12 ros2 param set $P footprint_padding 0.01 2>&1 | tail -1)"
echo "$(date +%T.%N | cut -c1-12) 끝 패딩 $(timeout 12 ros2 param get $P footprint_padding 2>&1 | tail -1)"
