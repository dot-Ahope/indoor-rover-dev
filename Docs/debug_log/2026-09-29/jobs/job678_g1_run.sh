#!/bin/bash
# 09-29 §13 G1 실행
python3 /tmp/job677_g1.py 2>&1 | grep -av "^\["
echo "  nav2.log nav_guard:"; grep -a "nav_guard" /tmp/nav2.log | tail -4 | cut -c1-220
