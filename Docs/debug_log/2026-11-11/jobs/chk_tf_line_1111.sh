#!/bin/bash
# chk_tf_line_1111 — 11-11 §5: nav2.log 의 TF 외삽 줄 원문과 앞뒤 3 줄(읽기만 · 로버 안 움직임 · DDS 참여자 안 만듦). 판정 ③ 이 '주행 중 실패' 인지 확인.
#   인자: 없음. 출력: 표준 출력.
grep -an -B3 -A3 'xtrapolat' /tmp/nav2.log | cut -c1-260
echo "== 첫 목표 시각"; grep -a 'Begin navigating' /tmp/nav2.log | head -1 | cut -c1-120
