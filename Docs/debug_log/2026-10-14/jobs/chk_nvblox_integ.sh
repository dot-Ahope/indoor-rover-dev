#!/bin/bash
# (10-14 §7) 실행 중 nvblox 가 읽은 통합 거리 확인 — 로버 안 움직임
grep -a "projective_integrator_max_integration_distance_m\|max_integration_distance" /tmp/nvblox_node.log | head -4 | cut -c1-160
ls -la /tmp/nvblox*.yaml 2>/dev/null | head -3; grep -h "max_integration_distance_m" /tmp/nvblox*.yaml 2>/dev/null | head -2
