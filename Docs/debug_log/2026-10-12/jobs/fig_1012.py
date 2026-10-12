# 10-12 §15 그림 4 장: (1) 주행 10 회의 /tf 수신 추이 (2) 계측 4 회의 UDP 수신·손실 (3) 포화 전후 프로세스 부하 (4) W3 출발 후진 거리·prep 시간
#   색: 포화 = 녹슨 주황, 정상 = 청록 계열(구성 이름은 글로 병기 — 색만으로 구분하지 않음)
import re, time, glob, collections, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
S = 'C:/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad/'
OUT = 'F:/6_Indoor_Rover/Rover/Docs/04_navigation/figures/2026-10-12_'
BAD, OK, INK, MUT = '#c05621', '#2b7a78', '#1d2329', '#6b7680'
RUNS = [('f2f1', '벌점 15 · 궤적 206 kB · 그림자 EKF 켬', True, '3/3 성공(상자 옆 멈칫)'), ('f2f3', '벌점 15 · 궤적 206 kB · 그림자 켬', True, '목표 3 중단'),
        ('f2g1', '벌점 5 · 궤적 206 kB · 그림자 켬', False, '3/3 성공(후진 2.93 m)'), ('f2g2', '벌점 15 · 궤적 206 kB · 그림자 켬', True, '목표 3 중단'),
        ('f2h1', '벌점 15 · 궤적 발행 끔 · 그림자 끔', False, '3/3 성공'), ('f2i1', '벌점 15 · 궤적 206 kB · 그림자 끔', True, '목표 3 중단'),
        ('f2j1', '벌점 15 · 궤적 206 kB · 그림자 끔(계측)', True, '목표 3 중단'), ('f2k1', '벌점 15 · 궤적 206 kB · 기록기 손실 허용', True, '목표 2 중단'),
        ('f2l1', '벌점 15 · 궤적 lite 28 kB · 그림자 끔', False, '3/3 성공'), ('f2l2', '벌점 15 · 궤적 lite 28 kB · 그림자 끔', False, '3/3 성공')]

def tfrate(nm):
    v = []
    for l in open(S + 'tf_rate_%s.txt' % nm, encoding='utf-8', errors='replace'):
        m = re.match(r'(\d\d:\d\d:\d\d)\s+([\d.]+)', l)
        if m: v.append(float(m.group(2)))
    return np.array(v[:-1])   # 끝 칸은 기록 종료 구간이라 뺌

# (1) /tf 수신 추이
fig, axs = plt.subplots(5, 2, figsize=(13, 10.5), sharex=True, sharey=True)
for a, (nm, cfg, sat, res) in zip(axs.T.flat, RUNS):
    y = tfrate(nm); x = np.arange(len(y)) * 10 + 5; c = BAD if sat else OK
    a.fill_between(x, 0, y, color=c, alpha=.18, step='mid'); a.step(x, y, where='mid', color=c, lw=2)
    a.axhline(25, color=MUT, lw=.8, ls='--'); a.set_ylim(0, 56); a.set_xlim(0, 235)
    a.set_title('%s  %s' % (nm, cfg), loc='left', fontsize=9.5, color=INK, weight='bold', pad=3)
    a.set_title(('포화 · ' if sat else '정상 · ') + res, loc='right', fontsize=9.5, color=c, weight='bold', pad=3)
    a.grid(axis='y', color='#e3e6e5', lw=.6); a.spines[['top', 'right']].set_visible(False)
for a in axs[-1]: a.set_xlabel('출발 뒤 경과 [s]')
for a in axs[:, 0]: a.set_ylabel('/tf 수신 [Hz]')
fig.suptitle('주행 10 회의 좌표 변환(/tf) 수신 주기 — 정상은 50 Hz, 점선(25 Hz) 아래로 떨어져 유지되면 포화', fontsize=12.5, y=0.998)
fig.tight_layout(); fig.savefig(OUT + 'tf_rate_runs.png', dpi=110); plt.close(fig)

# (2) UDP 수신·손실
fig, axs = plt.subplots(4, 1, figsize=(12, 9.5), sharex=True)
for a, nm in zip(axs, ['f2j1', 'f2k1', 'f2l1', 'f2l2']):
    s = []
    for l in open(S + 'f0_%s/net_%s.log' % (nm, nm), errors='replace'):
        f = l.split()
        if len(f) > 3 and f[1] == 'SNMP': s.append((int(f[0]), int(f[3]), int(f[7])))
    s = np.array(s, float); t = s[1:, 0] - s[0, 0]; rin = np.diff(s[:, 1]) / np.diff(s[:, 0]); drp = np.diff(s[:, 2]) / np.diff(s[:, 0])
    sat = dict(RUNS_ := [(r[0], r[2]) for r in RUNS])[nm]; c = BAD if sat else OK
    a.fill_between(t, 0, rin / 1000, color=c, alpha=.25, step='pre', label='수신'); a.step(t, rin / 1000, color=c, lw=1.5)
    a.step(t, drp / 1000, color=INK, lw=1.3, label='수신 버퍼 부족 손실')
    cfg = [r[1] for r in RUNS if r[0] == nm][0]; res = [r[3] for r in RUNS if r[0] == nm][0]
    a.text(0.01, 0.86, '%s  %s → %s' % (nm, cfg, res), transform=a.transAxes, fontsize=10, weight='bold', color=INK)
    a.set_ylim(0, 95); a.set_ylabel('천 개 / s'); a.grid(axis='y', color='#e3e6e5', lw=.6); a.spines[['top', 'right']].set_visible(False)
    if nm == 'f2j1': a.legend(loc='upper right', fontsize=9, frameon=False)
axs[-1].set_xlabel('계측 시작 뒤 경과 [s]  (짧은 뾰족한 봉우리 = 목표가 바뀔 때의 탐색 통신, 스스로 회복)')
fig.suptitle('UDP 통신량과 손실(2 s 간격) — 포화는 수신량이 평상 5,300 개/s 에서 6~8 만 개/s 로 뛰어 유지되는 상태', fontsize=12.5, y=0.995)
fig.tight_layout(); fig.savefig(OUT + 'udp_storm.png', dpi=110); plt.close(fig)

# (3) 프로세스 부하(§3.3·§5.2·§7.3 측정값, 코어 1 개 = 100)
names = ['EKF', '위치 추정', 'nvblox', '계획기', 'behavior', 'smoother', 'rf2o', '컨트롤러', 'BT']
# f2f3 한 주행의 측정값(outputs/f2f1_f2f3_proc.txt: 'f2f3앞' → 'f2f3포화')
pre = {'f2f3': [21.7, 21.4, 17.0, 9.9, 8.0, 6.9, 4.0, 29.6, 17.8]}
post = {'f2f3': [54.1, 50.6, 28.9, 19.4, 16.4, 15.0, 12.6, 31.6, 27.3]}
fig, a = plt.subplots(figsize=(11, 4.8)); x = np.arange(len(names)); w = 0.36
p0 = np.array(pre['f2f3']); p1 = np.array(post['f2f3'])
a.bar(x - w / 2 - 0.01, p0, w, color=OK, label='포화 전'); a.bar(x + w / 2 + 0.01, p1, w, color=BAD, label='포화 중')
for i in range(len(names)): a.text(x[i] + w / 2 + 0.01, p1[i] + 1, '×%.1f' % (p1[i] / p0[i]), ha='center', fontsize=9, color=INK)
a.set_xticks(x, names); a.set_ylabel('CPU (코어 1 개 = 100)'); a.legend(frameon=False); a.spines[['top', 'right']].set_visible(False); a.grid(axis='y', color='#e3e6e5', lw=.6)
a.set_title('포화 전후 프로세스 부하(f2f3) — 좌표 변환을 주고받는 프로세스가 함께 무거워짐. 카메라·라이다 드라이버는 변화 없음', fontsize=11, loc='left')
fig.tight_layout(); fig.savefig(OUT + 'cpu_saturation.png', dpi=110); plt.close(fig)

# (4) 후진 거리 + prep 시간
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.6), gridspec_kw={'width_ratios': [1.5, 1]})
rv = [('f2e2\n(10-08)', 2.93, 5), ('f2g1', 2.93, 5), ('f2f1', 0.41, 15), ('f2h1', 0.24, 15), ('f2l1', 0.23, 15), ('f2l2', 0.20, 15)]
bars = a1.bar([r[0] for r in rv], [r[1] for r in rv], color=[MUT if r[2] == 5 else OK for r in rv], width=0.62)
for b, r in zip(bars, rv): a1.text(b.get_x() + b.get_width() / 2, r[1] + 0.05, '%.2f m' % r[1], ha='center', fontsize=10, color=INK)
a1.axhline(0.5, color=BAD, lw=1, ls='--'); a1.text(1.5, 0.55, '판정 기준 0.5 m', color=BAD, fontsize=9, ha='center')
a1.text(0.5, 3.13, '후진 벌점 5', ha='center', color=MUT, fontsize=10, weight='bold'); a1.text(3.5, 0.75, '후진 벌점 15', ha='center', color=OK, fontsize=10, weight='bold')
a1.set_ylabel('W3 출발 뒤 후진 거리 [m]'); a1.set_ylim(0, 3.3); a1.spines[['top', 'right']].set_visible(False); a1.set_title('앞 회전 우선: 끝까지 주행한 6 회의 목표 3 후진 거리', fontsize=11, loc='left')
pt = [('기존 prep\n(3 회)', [288, 281, 317], MUT), ('빠른 prep\n(1 회)', [70], OK)]
for i, (lab, v, c) in enumerate(pt):
    a2.bar(i, np.mean(v), color=c, width=0.55); a2.scatter([i] * len(v), v, color=INK, s=18, zorder=3)
    a2.text(i, max(v) + 14, '%d 분 %02d 초' % divmod(int(round(np.mean(v))), 60) if np.mean(v) >= 60 else '%d 초' % np.mean(v), ha='center', fontsize=10.5, color=INK)
a2.set_xticks([0, 1], [p[0] for p in pt]); a2.set_ylabel('prep 소요 [s] (PC 기준)'); a2.set_ylim(0, 360); a2.spines[['top', 'right']].set_visible(False)
a2.set_title('prep 시간: 조회를 한 프로세스로 · 고정 대기 → 폴링', fontsize=11, loc='left')
fig.tight_layout(); fig.savefig(OUT + 'reverse_prep.png', dpi=110); plt.close(fig); print('ok')
