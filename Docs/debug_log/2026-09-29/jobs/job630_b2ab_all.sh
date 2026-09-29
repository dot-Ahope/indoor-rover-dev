#!/bin/bash
# B2·B3 오프라인 A/B 일괄(Jetson, 09-28 §27): 네트워크가 끊겨도 계속 돌도록 setsid nohup 으로 띄워 /tmp/b2ab_all.txt 에 쓴다.
#   bag(09-29 확대): s1·r1·r1b(시계 0.38), r2(부분), r2b(시계 0.20 ×4), r3(반시계 0.20 ×4), s2(반시계 0.38 ×1) × 설정 off / b2 / b23
: > /tmp/b2ab_all.txt
for B in s1 r1 r1b r2 r2b r3 s2; do for V in off b2 b23; do bash /tmp/job628_b2ab.sh /tmp/bag_$B $V >> /tmp/b2ab_all.txt 2>&1; done; done
echo "=== 끝 $(date +%T)" >> /tmp/b2ab_all.txt
