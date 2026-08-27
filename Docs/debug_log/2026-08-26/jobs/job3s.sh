#!/bin/bash
# 손 회전 녹화 분석: gyro z 통계 + 파형 요약
python3 - << 'EOF'
vals = []
with open('/tmp/gyro_rec.txt') as f:
    for line in f:
        line = line.strip()
        if line and line != '---':
            try:
                vals.append(float(line))
            except ValueError:
                pass

n = len(vals)
print(f"samples: {n}  ({n/50:.1f}s)")
if n == 0:
    print("EMPTY — no data recorded")
    raise SystemExit

mn, mx = min(vals), max(vals)
mean = sum(vals) / n
std = (sum((v - mean) ** 2 for v in vals) / n) ** 0.5
print(f"min: {mn:+.4f}  max: {mx:+.4f}  mean: {mean:+.5f}  std: {std:.5f} rad/s")
big = sum(1 for v in vals if abs(v) > 0.1)
huge = sum(1 for v in vals if abs(v) > 0.5)
print(f"|z|>0.1 rad/s: {big} samples ({big/n*100:.1f}%)")
print(f"|z|>0.5 rad/s: {huge} samples ({huge/n*100:.1f}%)")

# 2초 구간별 피크 요약 (파형 확인)
print("--- 2s-window peak |z| trace ---")
w = 100
for i in range(0, n, w):
    seg = vals[i:i+w]
    peak = max(abs(v) for v in seg)
    bar = '#' * min(int(peak * 20), 40)
    print(f"t={i/50:5.1f}s  peak={peak:6.3f}  {bar}")
EOF
