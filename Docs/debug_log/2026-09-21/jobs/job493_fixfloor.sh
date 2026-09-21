#!/bin/bash
# N3 결함 수정 (2026-09-21 §10.4~10.5): nvblox_nav2 층 lookupInSlice() 의 슬라이스 인덱스 round → floor.
#   근거: DistanceMapSlice.msg 의 origin 은 첫 픽셀의 모서리(esdf_slice_conversions.cu: origin = aabb.min()) → 셀 k 는 [origin+k·res, origin+(k+1)·res) 이므로 floor 가 맞다.
#   round 는 소수부 ≥ 0.5 일 때 옆 픽셀을 읽어 층 그림이 −1 셀 평행이동(§10.3 관찰: 두 축 −0.05). 되돌리기: git -C $R checkout -- nvblox_nav2/src/nvblox_costmap_layer.cpp 후 재빌드.
set +u
R=/home/jetson/workspaces/isaac_ros-dev/src/isaac_ros_nvblox
F=$R/nvblox_nav2/src/nvblox_costmap_layer.cpp
echo "== 수정 전: $(grep -n 'scaled_position.array()' $F | cut -c1-120)"
if grep -q 'scaled_position.array().round()' $F; then
  sed -i 's|scaled_position.array().round().cast<int>();|scaled_position.array().floor().cast<int>();  // 2026-09-21 수정: origin 은 픽셀 모서리(DistanceMapSlice.msg) → floor 가 맞음. round 는 −1 셀 평행이동을 일으킴(rover §10.4)|' $F
fi
echo "== 수정 후: $(grep -n 'scaled_position.array()' $F | cut -c1-120)"
echo "== git diff ($R)"; git -C $R --no-pager diff --stat | tail -2; git -C $R --no-pager diff -U1 -- nvblox_nav2/src/nvblox_costmap_layer.cpp | grep -aE '^[-+] ' | cut -c1-150
source /opt/ros/humble/setup.bash; cd ~/ros2_ws
SO=~/ros2_ws/install/nvblox_nav2/lib/libnvblox_costmap_layer.so; B0=$(stat -c %Y $SO 2>/dev/null || echo 0)
T0=$(date +%s); colcon build --symlink-install --packages-select nvblox_nav2 --cmake-args -DCMAKE_BUILD_TYPE=Release 2>&1 | grep -aE "Starting|Finished|Failed|error:|Error|Summary" | tail -6 | cut -c1-160; echo "빌드 소요 $(( $(date +%s) - T0 )) s"
B1=$(stat -c %Y $SO 2>/dev/null || echo 0); echo ".so 갱신: $([ "$B1" -gt "$B0" ] && echo yes || echo NO) ($(date -d @$B1 '+%H:%M:%S' 2>/dev/null))"
echo "== 실행 중 Nav2 는 아직 옛 .so — job488 재기동 때 반영"
