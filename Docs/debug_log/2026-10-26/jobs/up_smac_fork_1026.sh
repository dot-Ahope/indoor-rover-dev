#!/bin/bash
# 10-26 §5 Smac 포크 빌드(Jetson ~/smac_ws 오버레이, 로버 안 움직임): nav2_smac_planner 1.1.20(= apt 판과 같은 태그) + Docs/06_planner/smac_fork/nav2_smac_planner_rover_maxcost.patch
#   실행본 = 이 머리 + 스크래치패드가 붙인 패치 base64(/tmp/smac_fork.patch). 주행 스택은 /opt/ros 판을 그대로 씀 — 오버레이는 오프라인 시험 · planner:=smac 때만 source.
set -e
W=~/smac_ws; mkdir -p $W/src; cd $W/src
if [ ! -d navigation2 ]; then git clone -q --depth 1 --branch 1.1.20 --filter=blob:none --sparse https://github.com/ros-navigation/navigation2.git && (cd navigation2 && git sparse-checkout set nav2_smac_planner); fi
cd navigation2; git checkout -q -- . ; echo "소스 $(git log -1 --format='%h %cd' --date=short)"
git apply --check /tmp/smac_fork.patch && git apply /tmp/smac_fork.patch && git diff --stat | tail -1
source /opt/ros/humble/setup.bash; cd $W
colcon build --packages-select nav2_smac_planner --cmake-args -DCMAKE_BUILD_TYPE=Release 2>&1 | tail -5
ls -la install/nav2_smac_planner/lib/libnav2_smac_planner.so && strings install/nav2_smac_planner/lib/libnav2_smac_planner.so | grep -c "analytic_expansion_max_cost"
