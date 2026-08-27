#!/bin/bash
# 손 회전 녹화 분석: D455f 자이로(광학 y) vs EKF vyaw
python3 - << 'PY'
def load(p):
    v=[]
    for line in open(p):
        line=line.strip()
        if line and line!='---':
            try: v.append(float(line))
            except: pass
    return v
for name,p,hz in (("D455f gyro (optical y = -robot yaw)","/tmp/gyro_rec.txt",200),("EKF filtered vyaw","/tmp/yaw_rec.txt",30)):
    v=load(p); n=len(v)
    print(f"== {name}: samples={n} ({n/hz:.1f}s)")
    if not v: continue
    mean=sum(v)/n; std=(sum((x-mean)**2 for x in v)/n)**0.5
    print(f"   min={min(v):+.3f} max={max(v):+.3f} std={std:.4f} rad/s | |v|>0.3: {sum(1 for x in v if abs(x)>0.3)} | |v|>1.0: {sum(1 for x in v if abs(x)>1.0)}")
    w=hz*2
    print("   2s-window peak:", " ".join(f"{max(abs(x) for x in v[i:i+w]):.2f}" for i in range(0,n,w)))
PY
