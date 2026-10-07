#!/bin/bash
# 10-07 §3.3: f2c2 W3 구간(러너 t 176~240 ≈ epoch 1791339070~1791339135) nav2 로그 전부(Message Filter 제외, 읽기만)
awk 'match($0, /\[(17913390[7-9][0-9]|1791339[01][0-9][0-9])\.[0-9]+\]/) && !/Message Filter|tick rate/' /tmp/nav2.log | grep -av "^\s*$" | sed -E 's/^\[[a-z_.]+-[0-9]+\] //' | cut -c1-200 | awk '{c[$0]++} c[$0]<=2' | head -60
