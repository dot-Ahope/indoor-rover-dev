#!/bin/bash
# 09-30 §7: 실제 촬영(세로) + 데이터 영상(가로) 좌우 결합. 동기 = 문 통과 순간(영상에서 읽음 ↔ bag 계산).
#   인자: 실제영상 데이터영상 데이터시작초(T) 출력 [라벨]
#   T = bag 경과(출발 기준) + 3.0(데이터 영상은 출발 3 s 전부터) — 실제 영상 0 s 에 해당하는 데이터 영상 시각.
REAL=$1; DATA=$2; TS=$3; OUT=$4; LAB=${5:-}
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$REAL")
ffmpeg -loglevel error -y -i "$REAL" -ss "$TS" -i "$DATA" -filter_complex "\
[0:v]fps=30,scale=-2:720,setsar=1[a];\
[1:v]fps=30,tpad=stop_mode=clone:stop_duration=30,setsar=1[b];\
[a][b]hstack=inputs=2,pad=ceil(iw/2)*2:ih,drawtext=fontfile=/Windows/Fonts/malgun.ttf:text='${LAB}':x=12:y=h-34:fontsize=20:fontcolor=white:box=1:boxcolor=black@0.6[v]" \
 -map "[v]" -an -t "$DUR" -c:v libx264 -crf 21 -pix_fmt yuv420p "$OUT" && ls -la "$OUT"
