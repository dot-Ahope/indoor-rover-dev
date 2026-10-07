#!/bin/bash
# 10-07 §9.2: 영상 6 개 전부 — 실제 영상(4K 세로) → 406×720·30 fps 로 먼저 줄이고(한 그래프로 하면 hstack 입력 높이 0 오류), RViz 풍 데이터(720×720) 와 좌우 결합
V=Docs/debug_log/2026-10-07/videos; O=$V/fused
for n in 130300 131145 131400 131424 131646 131823; do
  ffmpeg -loglevel error -y -i $V/20261007_$n.mp4 -vf "fps=30,scale=406:720,setsar=1" -an -c:v libx264 -crf 20 -pix_fmt yuv420p real_$n.mp4
  ffmpeg -loglevel error -y -i real_$n.mp4 -i rv_$n.mp4 -i lab_real.png -filter_complex "[0:v][2:v]overlay=0:0[a];[1:v]fps=30[b];[a][b]hstack=inputs=2[v]" -map "[v]" -an -shortest -c:v libx264 -crf 23 -pix_fmt yuv420p -movflags +faststart $O/fused_$n.mp4
done
