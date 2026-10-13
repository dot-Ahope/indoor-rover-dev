#!/bin/bash
# (10-13 §9) 시뮬 묶음 진행 확인 — 로버 안 움직임
date +%T; echo "결과 파일 $(ls /tmp/sweep/*_*_*.txt 2>/dev/null | wc -l) / 150 · 내용 있는 것 $(grep -al "LETHAL 여유" /tmp/sweep/*_*_*.txt 2>/dev/null | wc -l)"; echo "실행 중: xargs $(pgrep -fc "xargs -P 3") · 시뮬 $(pgrep -fc anal_mppi_sim.py)"; ls -t /tmp/sweep/*.txt | head -3; uptime; tail -3 /tmp/live/current.log | cut -c1-160
