#!/bin/bash
# (오늘만) run_jn.sh 는 인자를 넘기지만 여기서는 f2m1 용으로 고정: 캡처 권한 확인 + 순회 prep(궤적 발행 원래대로, 벌점 15). 로버 안 움직임
echo "  tcpdump 권한: $(getcap /usr/bin/tcpdump 2>/dev/null || echo 없음)"
bash /tmp/prep_patrol.sh ${1:-true} ${2:-15.0}
