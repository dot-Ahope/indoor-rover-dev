#!/bin/bash
# (10-13 §11) 패딩 0 시뮬 진행 확인 — 로버 안 움직임
date +%T; echo "결과 파일 $(ls /tmp/sweep_pad0/*_*_*.txt 2>/dev/null | wc -l) / 40 · 끝난 것 $(grep -al "LETHAL 여유" /tmp/sweep_pad0/*_*_*.txt 2>/dev/null | wc -l) · 실행 중 시뮬 $(pgrep -fc anal_mppi_sim.py)"
