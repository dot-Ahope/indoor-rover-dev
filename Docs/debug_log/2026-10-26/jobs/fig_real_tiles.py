#!/usr/bin/env python3
"""fig_real_tiles — 실제 촬영 작업본에서 지정 시각 장면을 뽑아 시각 글씨를 붙여 격자 한 장으로(토큰 절약: 6 장 = 그림 1 장) (2026-10-26 §16, PC).
  인자: 작업본.mp4 작업본시작HH:MM:SS 출력.png 열수 HH:MM:SS.s=설명 ..."""
import sys, subprocess, time, io
from PIL import Image, ImageDraw, ImageFont
vid, t0s, out, ncol = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
ep = lambda s: sum(float(x) * k for x, k in zip(s.split(':'), (3600, 60, 1)))
T0 = ep(t0s); W, H = 640, 360
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 22)
tiles = []
for a in sys.argv[5:]:
    ts, _, lab = a.partition('=')
    off = ep(ts) - T0
    png = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', '%.2f' % off, '-i', vid, '-frames:v', '1', '-vf', 'scale=%d:%d' % (W, H), '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
    im = Image.open(io.BytesIO(png)).convert('RGB'); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 30], fill=(0, 0, 0)); d.text((6, 3), '%s  %s' % (ts, lab), fill=(255, 255, 0), font=font)
    tiles.append(im)
nrow = (len(tiles) + ncol - 1) // ncol; G = Image.new('RGB', (ncol * W, nrow * H), (40, 40, 40))
for i, im in enumerate(tiles): G.paste(im, ((i % ncol) * W, (i // ncol) * H))
G.save(out); print('저장', out, len(tiles), '장')
