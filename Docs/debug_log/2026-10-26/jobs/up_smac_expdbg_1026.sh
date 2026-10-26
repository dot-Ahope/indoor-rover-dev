#!/bin/bash
# 10-26 §22 Smac 탐색 기록 진단 빌드(Jetson ~/smac_dbg_ws 오버레이, 로버 안 움직임): nav2_smac_planner 1.1.20 원본(설치판과 같은 태그) + Docs/06_planner/smac_fork/nav2_smac_planner_rover_expdump.patch(기록만, 동작 그대로)
#   비용 상한 포크(~/smac_ws)는 경로가 설치판과 달라질 수 있어(§5.2 rp2) 쓰지 않음. 실행본 = 패치 base64(/tmp/smac_expdbg.patch) + 이 머리. 오프라인 시험에서만 source.
set -e
W=~/smac_dbg_ws; mkdir -p $W/src; cd $W/src
if [ ! -d navigation2 ]; then git clone -q --depth 1 --branch 1.1.20 --filter=blob:none --sparse https://github.com/ros-navigation/navigation2.git 2>/dev/null && (cd navigation2 && git sparse-checkout set nav2_smac_planner); fi
cd navigation2; git checkout -q -- . ; echo "소스 $(git log -1 --format='%h %cd' --date=short)"
git apply --check /tmp/smac_expdbg.patch && git apply /tmp/smac_expdbg.patch && git diff --stat | tail -1
source /opt/ros/humble/setup.bash; cd $W
colcon build --packages-select nav2_smac_planner --cmake-args -DCMAKE_BUILD_TYPE=Release 2>&1 | tail -4
ls -la install/nav2_smac_planner/lib/libnav2_smac_planner.so && echo "SMAC_EXP_DIR 문자열 $(strings install/nav2_smac_planner/lib/libnav2_smac_planner.so | grep -c SMAC_EXP_DIR)"
