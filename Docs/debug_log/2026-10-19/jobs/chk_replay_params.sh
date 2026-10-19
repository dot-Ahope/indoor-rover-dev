#!/bin/bash
# (10-19 §6) 재생 nvblox 로그에서 실제 적용된 파라미터 확인 — 인자: 꼬리표 ... 로버 안 움직임
for t in "$@"; do echo "== $t"; grep -aoE "(voxel_size|projective_integrator_max_integration_distance_m|esdf_integrator_max_site_distance_vox|projective_integrator_truncation_distance_vox)[^,]{0,30}" /tmp/nvblox_replay_$t.log | sort -u | head -6; done
