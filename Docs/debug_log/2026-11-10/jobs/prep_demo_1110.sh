#!/bin/bash
# prep_demo_1110 — 11-10 주행 시연 prep(Jetson). 표준 prep = /tmp/prep_patrol.sh lite(planner navfn · 재계획 0.5 Hz · ODOM=vslam · mppi_viz lite).
#   로버 안 움직임(자이로 캘리브 동안 정지 필수 — 출발 테이프 위). 인자: $1 = 번호(기본 1).
#   출력: 원문은 /tmp/prep_full_<n>.txt(README §5 — 필터 없이 원문 보관), 표준 출력엔 끝 40 줄. PC 에서 outputs/prep_demo_1110_<n>.txt 로 회수.
N=${1:-1}
bash /tmp/prep_patrol.sh lite > /tmp/prep_full_$N.txt 2>&1; echo "rc $?"
tail -40 /tmp/prep_full_$N.txt | cut -c1-200
