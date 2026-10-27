#!/bin/bash
# §24 옛 게이트(B · C · G2 따로) vs 새 게이트(chk_drive_gate 한 노드) — 같은 정지 상태에서 값 · 소요 시간. 로버 안 움직임
T=$(date +%s.%N); BR=$(timeout 12 ros2 topic hz /wheel_odom 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1); echo "옛 B: $BR · $(echo "$(date +%s.%N) - $T" | bc | cut -c1-5) s"
T=$(date +%s.%N); python3 /tmp/job386_slamalive.py 2>&1 | grep -av "^\[" | tail -2 | sed 's/^/옛 C: /'; echo "   $(echo "$(date +%s.%N) - $T" | bc | cut -c1-5) s"
T=$(date +%s.%N); timeout 60 python3 /tmp/job440_startclear.py 2>&1 | grep -av "^\[" | tail -3 | sed 's/^/옛 G2: /'; echo "   $(echo "$(date +%s.%N) - $T" | bc | cut -c1-5) s"
T=$(date +%s.%N); python3 /tmp/chk_drive_gate.py 2>&1 | grep -av "^\["; echo "새 게이트 전체 $(echo "$(date +%s.%N) - $T" | bc | cut -c1-5) s"
