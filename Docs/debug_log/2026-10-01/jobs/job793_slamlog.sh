#!/bin/bash
# 10-01 §8.41: f2a12 +283.5 s(epoch ≈ 1790841826) map→odom 1.37 m 점프 — slam_toolbox 로그에 루프 클로저/매칭 기록이 있나
ls -la /tmp/slam.log; wc -l /tmp/slam.log
grep -anE "1790841(7[89]|8[0-4])[0-9]\." /tmp/slam.log | cut -c1-220 | tail -40
echo "== 전체에서 loop/closure/Match 단어"; grep -aciE "loop|closure|matched" /tmp/slam.log; grep -aiE "loop|closure|matched" /tmp/slam.log | tail -8 | cut -c1-220
