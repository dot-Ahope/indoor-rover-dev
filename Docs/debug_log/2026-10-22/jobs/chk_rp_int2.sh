#!/bin/bash
# 10-22 §14 재생 출력 확인(러너 출력 스트림이 첫 재생 머리말 뒤 끊김 — 작업은 계속됨): 적용 파라미터 · 재생 시간 · 조각 수
source /opt/ros/humble/setup.bash
for t in i14 i20; do echo "== $t"; grep -a "projective_integrator_max_integration_distance_m:" /tmp/nvblox_replay_f2lp1_$t.log | head -1 | cut -c1-140; grep -a "depth_image_callback" /tmp/nvblox_replay_f2lp1_$t.log | tail -1; ros2 bag info ~/bags/replay_f2lp1_$t 2>/dev/null | grep -aE "Duration|Count" | cut -c1-140; done
