#!/usr/bin/env python3
"""10-07 §9.2 RViz 풍 bag 시각화(사용자 지정 스타일) — 720×720, 10 fps(실제 속도), 로버 진행 방향이 위(RViz 고정 프레임 base_link 처럼).
   지도: 미지 회색 · 빈 곳 흰색 · 벽 검정(RViz map). 로컬 코스트맵: RViz costmap 색(1~98 파랑→빨강, 99 내접 청록, 100 치명 자홍, 알파 0.7).
   라이다 점(빨강), 전역 경로(초록 선), 차체 외곽(초록 테두리 = Nav2 footprint), 라이다 원통(보라), 1 m 격자(옅은 파랑), TF 이름(base_link·odom·lidar_link·camera_link).
   인자: npz out.mp4 시작KST 길이s 라벨 [global]
   §10 추가: 경로는 로버 앞 남은 부분만, 새 경로가 오면 3 s 강조('새 경로 계획 HH:MM:SS')·직전 경로 흐린 회색, 지나온 궤적(파랑).
     global 이면 전역 코스트맵(계획기가 보는 지도) 내접·치명 칸을 주황 테두리로 겹침 — 로컬(MPPI)과 전역(계획기) 지도 차이 디버깅용.
   시각: Jetson epoch 1791346297 = 13:11:37 KST. 좌표·치수: 차체 x −0.248~+0.262·y ±0.165, 라이다 x 0.152(yaw π−0.04677), 카메라 x 0.232(URDF)."""
import sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

E0, K0 = 1791346297.0, 13 * 3600 + 11 * 60 + 37
def kst2e(s): h, m, x = map(int, s.split(':')); return E0 + h * 3600 + m * 60 + x - K0
def e2kst(e): s = int(e - E0 + K0); return '%02d:%02d:%02d' % (s // 3600, s // 60 % 60, s % 60)
Z = np.load(sys.argv[1]); OUT = sys.argv[2]; TA = kst2e(sys.argv[3]); DUR = float(sys.argv[4]); LAB = sys.argv[5]; GLB = len(sys.argv) > 6 and sys.argv[6] == 'global'
W = 720; SPAN = 4.0; PX = SPAN / W                       # 4 m × 4 m, 1 px = 5.6 mm
XF, XB, HW, LX, LY, CX = 0.262, -0.248, 0.165, 0.152, math.pi - 0.04677, 0.232
tr, mo, cmd = Z['traj'], Z['mo'], Z['cmd']; pt, pn, pxy = Z['plan_t'], Z['plan_n'], Z['plan_xy']; off = np.r_[0, np.cumsum(pn)]
M = Z['map']; mres, mox, moy = Z['map_meta']
MAPC = np.zeros(M.shape + (3,), np.uint8); MAPC[:] = (160, 160, 160); MAPC[(M >= 0) & (M < 50)] = (255, 255, 255); MAPC[M >= 50] = (0, 0, 0)
PAL = np.zeros((256, 4), np.float32)                     # RViz costmap 팔레트(근사): 0 투명, 1~98 파랑→빨강, 99 청록, 100 자홍
for c in range(1, 99): f = c / 98.0; PAL[c] = (255 * f, 0, 255 * (1 - f), 0.7)
PAL[99] = (0, 255, 255, 0.7); PAL[100] = (255, 0, 255, 0.7)
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 15); fsm = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 15)
u = (np.arange(W) + 0.5) - W / 2; UU, VV = np.meshgrid(u, u)
RX, RY = -VV * PX, -UU * PX                              # 화면 위 = 로버 앞(+x), 왼쪽 = 로버 왼쪽(+y)
def last(ts, t): i = np.searchsorted(ts, t) - 1; return i if i >= 0 else None
def at(X, t): i = min(max(np.searchsorted(X[:, 0], t), 0), len(X) - 1); return X[i, 1:4]
trail, TRW = [], []
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, W), '-r', '10', '-i', '-',
                       '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', OUT], stdin=subprocess.PIPE)
for k in range(int(DUR * 10)):
    t = TA + k / 10.0; x, y, th = at(tr, t); c, s = math.cos(th), math.sin(th)
    WX, WY = x + c * RX - s * RY, y + s * RX + c * RY    # 화면 픽셀 → map 좌표
    ix = ((WX - mox) / mres).astype(int); iy = ((WY - moy) / mres).astype(int); ok = (ix >= 0) & (ix < M.shape[1]) & (iy >= 0) & (iy < M.shape[0])
    img = np.full((W, W, 3), 160, np.float32); img[ok] = MAPC[iy[ok], ix[ok]]
    i = last(Z['lcm_t'], t)
    if i is not None:                                    # 로컬 코스트맵(odom 격자) → map→odom 역변환으로 픽셀마다 조회
        g = Z['lcm'][i].astype(np.int16) & 0xFF; r, ox, oy = Z['lcm_meta'][i]; mx, my, mth = at(mo, Z['lcm_t'][i]); cm, sm = math.cos(mth), math.sin(mth)
        OX, OY = cm * (WX - mx) + sm * (WY - my), -sm * (WX - mx) + cm * (WY - my)
        jx = ((OX - ox) / r).astype(int); jy = ((OY - oy) / r).astype(int); okc = (jx >= 0) & (jx < g.shape[1]) & (jy >= 0) & (jy < g.shape[0])
        val = np.zeros((W, W), np.int16); val[okc] = g[jy[okc], jx[okc]]; p = PAL[val]; a = p[..., 3:4]
        img = img * (1 - a) + p[..., :3] * a
    img[(np.abs(np.mod(WX + 1e-3, 1.0)) < PX * 0.9) | (np.abs(np.mod(WY + 1e-3, 1.0)) < PX * 0.9)] = (150, 190, 230)   # 1 m 격자
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    def scr(px, py):                                     # map → 화면 픽셀
        dx, dy = px - x, py - y; bx, by = c * dx + s * dy, -s * dx + c * dy; return W / 2 - by / PX, W / 2 - bx / PX
    if GLB:                                              # 전역 코스트맵(계획기) 내접·치명 칸 = 주황 테두리
        gi = last(Z['gcm_t'], t)
        if gi is not None:
            G = Z['gcm'][gi].astype(np.int16); gr, gox, goy = Z['gcm_meta'][gi]; gy_, gx_ = np.nonzero(G >= 99)
            for cx_, cy_ in zip(gox + (gx_ + .5) * gr, goy + (gy_ + .5) * gr):
                if abs(cx_ - x) < 2.9 and abs(cy_ - y) < 2.9:
                    u_, v_ = scr(cx_, cy_); h = gr / PX / 2 - 1; d.rectangle([u_ - h, v_ - h, u_ + h, v_ + h], outline=(255, 140, 0), width=1)
    trail.append(scr(x, y)); TRW.append((x, y)); d.line([scr(a_, b_) for a_, b_ in TRW[::3]] + [scr(x, y)], fill=(40, 90, 220), width=2)
    i = last(pt, t)
    if i is not None:
        if i > 0 and t - pt[i] < 6:                      # 직전 경로(흐린 회색) — 바뀐 것을 비교
            Q = pxy[off[i - 1]:off[i]]; jq = np.argmin(np.hypot(Q[:, 0] - x, Q[:, 1] - y)); d.line([scr(a_, b_) for a_, b_ in Q[jq:]], fill=(150, 150, 150), width=2)
        P = pxy[off[i]:off[i + 1]]; jp = np.argmin(np.hypot(P[:, 0] - x, P[:, 1] - y)); fresh = t - pt[i] < 3
        d.line([scr(a_, b_) for a_, b_ in P[jp:]], fill=(0, 230, 0) if fresh else (0, 150, 0), width=6 if fresh else 3)
        # 목표 깃발은 그리지 않음(10-07 §11 사용자)
        if fresh: d.rectangle([W - 250, 32, W - 6, 56], fill=(0, 120, 0)); d.text((W - 244, 34), '새 경로 계획 %s' % e2kst(pt[i]), fill=(255, 255, 255), font=font)
    i = last(Z['scan_t'], t)
    if i is not None:
        rr = Z['scan_r'][i]; a0, da = Z['scan_a'][i]; aa = a0 + da * np.arange(len(rr)) + LY; okk = np.isfinite(rr) & (rr > .05) & (rr < 5)
        px_, py_, pth = at(tr, Z['scan_t'][i]); bx, by = LX + rr[okk] * np.cos(aa[okk]), rr[okk] * np.sin(aa[okk]); cc, ss = math.cos(pth), math.sin(pth)
        for qx, qy in zip(px_ + cc * bx - ss * by, py_ + ss * bx + cc * by):
            u_, v_ = scr(qx, qy); d.rectangle([u_ - 1.5, v_ - 1.5, u_ + 1.5, v_ + 1.5], fill=(230, 0, 0))
    C = [(XF, HW), (XF, -HW), (XB, -HW), (XB, HW), (XF, HW)]
    d.line([(W / 2 - py / PX, W / 2 - px / PX) for px, py in C], fill=(0, 200, 0), width=3)                     # footprint
    lu, lv = W / 2, W / 2 - LX / PX; d.ellipse([lu - 13, lv - 22, lu + 13, lv + 22], fill=(110, 110, 230))       # 라이다(보라 원통)
    mx, my, mth = at(mo, t); ou, ov = scr(mx, my)
    for name, (uu_, vv_) in (('odom', (ou, ov)), ('base_link', (W / 2, W / 2 + 8)), ('lidar_link', (lu, lv - 8)), ('camera_link', (W / 2, W / 2 - CX / PX - 16))):
        if 0 < uu_ < W and 0 < vv_ < W:
            tw = d.textlength(name, font=fsm); d.rectangle([uu_ - tw / 2 - 3, vv_ - 9, uu_ + tw / 2 + 3, vv_ + 9], fill=(255, 255, 255)); d.text((uu_ - tw / 2, vv_ - 9), name, fill=(0, 0, 0), font=fsm)
    j = last(cmd[:, 0], t); v, w = (cmd[j, 1], cmd[j, 2]) if j is not None and t - cmd[j, 0] < 0.5 else (0.0, 0.0)
    d.rectangle([0, 0, W, 26], fill=(40, 40, 40)); d.text((8, 3), '%s   %s KST' % (LAB, e2kst(t)), fill=(240, 240, 240), font=font)
    d.rectangle([0, W - 24, W, W], fill=(40, 40, 40)); d.text((8, W - 22), '지령 v %+.3f m/s   ω %+.2f rad/s     map (%.2f, %.2f, %+.0f°)' % (v, w, x, y, math.degrees(th)), fill=(240, 240, 240), font=font)
    ff.stdin.write(np.asarray(im).tobytes())
ff.stdin.close(); ff.wait(); print('ok', OUT, int(DUR * 10))
