#!/bin/bash
# 10-01 §6 F1-2(office_v2): 출발 테이프에서 office_v2 불러오기 → 복원 확인. 판정(선언): 원점에서 ≤ 5 cm, 5 s 안 안정(연속 변화 ≤ 1 cm), /map 333×227·원점 (−5.29, −6.96).
#   전체 스택(Nav2 포함, MAPPING=0) — 다음 단계 F1-4·F2 를 바로 이어갈 수 있게.
set +u
MAP=office_v2 MAPPING=0 bash /tmp/job726_prep_map.sh 2>&1 | grep -aE "지도|wheel_odom|gyro bias|odometry/filtered|slam 인자|map->odom|_server|배터리|EKF 위반|불러오기|프로세스|  [a-z_\" ]+ +[0-9]+$"
echo "== slam.log 불러오기"; grep -aiE "deserializ|loading|posegraph|Failed|error" /tmp/slam.log | cut -c1-200 | head -6
python3 /tmp/job697_restore_chk.py 2>&1 | grep -av "^\["
