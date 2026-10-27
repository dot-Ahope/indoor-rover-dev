#!/bin/bash
# §24 정지 상태 SLAM stamp 지연 20 s 관찰(새 게이트 SEC=20) + slam 로그 최근 줄. 로버 안 움직임
python3 /tmp/chk_drive_gate.py 20 2>&1 | grep -av "^\[" | grep -a "C \|GATE"
echo "slam 스캔 버림(전체) $(grep -ac "Message Filter dropping" /tmp/slam.log) · 최근: $(grep -a "dropping\|WARN\|ERROR" /tmp/slam.log | tail -3 | cut -c1-160)"
