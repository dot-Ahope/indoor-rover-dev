#!/bin/bash
# 10-23 §20.2 PathBlockedAhead '처음 막힘' 이 경로를 받은 뒤 몇 초에 나왔나(PC, 로버 안 움직임).
#   경로 받음 = smoother_server 'Received a path to smooth'(BT 가 새 경로를 만들 때마다 한 번). 0.0x s = 계획기가 이미 99 칸을 지나는 경로를 냄, 수십 s = 주행 중 새로 생김.
# 인자: nav2 로그들(outputs/nav2_<run>.log)
for f in "$@"; do echo "== $(basename $f)"
  awk 'match($0,/\[(17927[0-9]+\.[0-9]+)\]/,m){t=m[1]}
       /Received a path to smooth/{p=t}
       /PathBlockedAhead: 앞 경로/ && /지속되면 재계획/ { match($0,/\(([^)]*)\) 비용 ([0-9]+)/,q); printf "  처음 막힘 (%s) 비용 %s · 경로 받고 %.2f s 뒤\n", q[1], q[2], t-p }' "$f"
done
