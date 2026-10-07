#!/bin/bash
# 10-07 §9: 실제 영상(세로 4K) 구간 → 406×720·30 fps, 데이터 영상(720×720·10 fps) 과 좌우 결합. (Git Bash ffmpeg 의 drawtext 는 fontconfig 로 죽어 라벨은 PNG 오버레이)
V=Docs/debug_log/2026-10-07/videos
real() { ffmpeg -loglevel error -y -ss $2 -t $3 -i $V/$1.mp4 -vf "fps=30,scale=406:720,setsar=1" -an -c:v libx264 -crf 20 -pix_fmt yuv420p $4; }
real 20261007_130300 130 75 real_corner.mp4      # 13:05:10~13:06:25 (휴대폰 파일 이름 시각 = 시작)
real 20261007_131424 0 72 real_corridor.mp4      # 13:14:24~13:15:36
real 20261007_131646 44 40 real_box1.mp4         # 13:17:30~13:18:10, 이어서 촬영 없음 13 s(gap.png), 131823 0~25 s
for c in corner corridor box; do ffmpeg -loglevel error -y -i real_$c.mp4 -i data_$c.mp4 -i lab_real.png -filter_complex "[0:v][2:v]overlay=0:0[a];[1:v]fps=30[b];[a][b]hstack=inputs=2[v]" -map "[v]" -an -shortest -c:v libx264 -crf 26 -preset slow -pix_fmt yuv420p -movflags +faststart sbs_$c.mp4; done
