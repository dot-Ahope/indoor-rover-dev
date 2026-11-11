#!/bin/bash
# prep_smac_1110 — 11-10 §10: 마지막 검증 구성 prep(Jetson) = f2tt1 · f2tt2(10-27 · 10-28)와 같음:
#   prep_patrol(vslam · 프로젝터 끔 · SHM · mppi_viz lite · PreferForward 15) + NAV_ADD="planner:=smac" + REPLAN_HZ=0.01.
#   본보기 2026-10-28/jobs/prep_smac_1028.sh. 로버 안 움직임(자이로 캘리브 동안 정지 — 출발 테이프 위, 처음 방향).
#   인자: $1 = 번호(기본 1). 출력: 원문 /tmp/prep_full_smac_<n>.txt, 표준 출력엔 끝 40 줄(PC 에서 outputs/ 로 tee).
N=${1:-1}
NAV_ADD="planner:=smac" REPLAN_HZ=0.01 bash /tmp/prep_patrol.sh lite > /tmp/prep_full_smac_$N.txt 2>&1; echo "rc $?"
tail -40 /tmp/prep_full_smac_$N.txt | cut -c1-200
