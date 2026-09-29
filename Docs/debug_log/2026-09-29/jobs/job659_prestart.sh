#!/bin/bash
# 09-29 §12.1 출발 전: 컨디셔너 파라미터(긴 대기) + 경로 점검
for p in icr_enable rot_cov_enable; do echo "  $p = $(timeout 15 ros2 param get /sensor_conditioner $p 2>&1 | tail -1)"; done
python3 /tmp/job658_pathcheck.py 2>&1 | grep -av "^\["
