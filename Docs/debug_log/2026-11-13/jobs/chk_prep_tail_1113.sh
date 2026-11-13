#!/bin/bash
# chk_prep_tail_1113 — prep 원문(/tmp/prep_full_color_$1.txt) 끝 45 줄과 prep 프로세스 생존을 본다(읽기만, 로버 안 움직임). 인자: $1 회차 이름.
echo "== prep 실행 중: $(pgrep -fc 'prep_fast.sh|prep_patrol.sh') · 원문 $(stat -c '%s B %y' /tmp/prep_full_color_$1.txt 2>&1 | cut -c1-40)"
tail -45 /tmp/prep_full_color_$1.txt | tr -cd '\11\12\15\40-\176\200-\377'
