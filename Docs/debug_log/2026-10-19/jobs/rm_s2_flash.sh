#!/bin/bash
# 10-19 §18: 큰 bag 정리 — s2_flash30rec(§16 ③ IR 8 Hz, 수치는 §16.1 기록) 삭제. 삭제 전 대상 확인
B=/home/jetson/bags/s2_flash30rec
[ -d "$B" ] || { echo "없음: $B"; exit 1; }
echo "== 삭제 전"; du -sh $B; ls $B; grep -aE "duration|message_count: [0-9]{3,}" $B/metadata.yaml | head -4
rm -rf "$B" && echo "== 삭제함 $B"
echo "== 남은 bag"; du -sh /home/jetson/bags/* 2>/dev/null | sort -h | tail -8; df -h /home/jetson | tail -1
