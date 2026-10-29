# anal_scan_align_sum — outputs/scan_align/*.txt(anal_scan_align_bag 출력) 분포 요약 (10-29 §2, PC)
import numpy as np, glob
R=[l.split() for f in sorted(glob.glob('outputs/scan_align/*.txt')) for l in open(f)]
A=np.array([[float(x) for x in r[1:]] for r in R]); s0,sb,db,v=A[:,5],A[:,6],A[:,7],A[:,4]
print('판 %d · 정지(v<0.02) %d'%(len(A),(v<0.02).sum()))
for nm,m in (('전체',v>=0),('정지',v<0.02),('주행',v>=0.02)):
    print('%s s0 최소 %.3f · 5%% %.3f · 중앙 %.3f | |db| 중앙 %.1f · 95%% %.1f · 최대 %.1f | sb-s0 95%% %.3f 최대 %.3f'%(nm,s0[m].min(),np.percentile(s0[m],5),np.median(s0[m]),np.median(abs(db[m])),np.percentile(abs(db[m]),95),abs(db[m]).max(),np.percentile((sb-s0)[m],95),(sb-s0)[m].max()))
print('낮은 s0 8 판 (이름 t x y yaw v s0 sb db)')
for j in np.argsort(s0)[:8]: print('  '+' '.join(R[j]))
print('큰 |db| 8 판')
for j in np.argsort(-abs(db))[:8]: print('  '+' '.join(R[j]))
