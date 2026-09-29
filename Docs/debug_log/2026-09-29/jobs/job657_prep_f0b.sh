#!/bin/bash
# 09-29 §12.1 F0-b prep: nvblox 컨테이너 확인 → job240(기본 스택, B2·B3 끔) → 컨디셔너 파라미터 확인
set +u
echo "########## 0. nvblox 컨테이너 ##########"
bash /tmp/job499_container_up.sh 2>&1 | grep -a "컨테이너\|nvblox 패키지"
bash /tmp/job240_clean.sh 15
echo "########## 10. 컨디셔너 B2·B3 (끔이어야) · 배터리 ##########"
for p in icr_enable rot_cov_enable; do echo "  $p = $(timeout 6 ros2 param get /sensor_conditioner $p 2>/dev/null)"; done
echo "  배터리 $(timeout 5 ros2 topic echo /battery --once --field voltage 2>/dev/null | head -1) V"
