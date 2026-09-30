#!/bin/bash
# 09-30 F1: 현재 자세 → 지도 저장(office_v1) → 매핑 통계
python3 /tmp/job692_posenow.py 2>&1 | grep -av "^\["
bash /tmp/job684_map_save.sh office_v1
echo "slam 노드 수(그래프): $(grep -ac "Adding node" /tmp/slam.log) 건 로그, 루프 폐합 로그: $(grep -aci "loop closure\|closure" /tmp/slam.log) 건"
