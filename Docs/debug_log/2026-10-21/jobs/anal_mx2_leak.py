# 10-21 §19.3 끈 프레임 점 새어 듦 — 저장된 한 장씩(설정당 1 장, 참고값): 흰 점(top-hat 5×5 > 20) 연결 성분 수, 전체 · 아래 1/4
import cv2, numpy as np, sys
d = sys.argv[1]
for n in ['Auto_IR_m1', 'A24k248_IR_m1', 'B28k248_IR_m1', 'C32k248_IR_m1', 'D32k128_IR_m1', 'Ctl_IR_m0', 'Auto_IR_m0']:
    a = cv2.imread('%s/%s.png' % (d, n), 0)
    th = cv2.morphologyEx(a, cv2.MORPH_TOPHAT, np.ones((5, 5), np.uint8)) > 20
    c = lambda m: cv2.connectedComponents(m.astype(np.uint8))[0] - 1
    print('%-15s 흰 점 전체 %5d · 아래 1/4 %5d · 밝기 %.1f' % (n, c(th), c(th[360:]), a.mean()))
