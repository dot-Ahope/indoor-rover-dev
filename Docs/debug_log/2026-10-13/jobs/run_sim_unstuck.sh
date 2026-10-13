#!/bin/bash
# (10-13 §14.2) 실제 정지 자세 3 곳에서 시뮬 시작: pad=0.01 대 pad=0, 씨앗 1~5, 150 주기, fpchk=1 — 계산만, 로버 안 움직임
source /opt/ros/humble/setup.bash; cd /tmp; rm -rf /tmp/unstuck; mkdir -p /tmp/unstuck
COM="vx_std=0.08 wz_std=0.4 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2 lag_steps=1 w_gain=0.7 w_acc=1.2 humble=1 temperature=0.15 near_thr=0.5 dyn_path=2 dyn_cost=1 obst=1 vx_min=-0.06 fwd_w=15 cost_w=3.81 fpchk=1 cycles=150"
{ for sc in "f2o1 13:33:27" "f2p1 14:14:56" "f2q1 17:51:40"; do set -- $sc; for pd in 0.01 0; do for sd in 1 2 3 4 5; do echo "$1 $(date -d $2 +%s) $pd $sd"; done; done; done; } > /tmp/unstuck/jobs.lst
xargs -P 3 -L 1 bash -c 'python3 /tmp/anal_mppi_sim.py /tmp/bag_$0 0 label=$0_p$2_s$3 t_abs=$1 seed=$3 pad=$2 '"$COM"' 2>&1 | grep -av "Opened database" > /tmp/unstuck/$0_$2_$3.txt' < /tmp/unstuck/jobs.lst
python3 - <<'PY'
import glob, re, numpy as np, collections
R = collections.defaultdict(list)
for f in sorted(glob.glob('/tmp/unstuck/*_*_*.txt')):
    sc, pd, sd = re.match(r'.*/(\w+?)_([0-9.]+)_(\d+)\.txt', f).groups(); s = open(f, errors='replace').read()
    m1 = re.search(r'LETHAL 여유.*?최소 (-?[0-9.]+|nan)', s); m2 = re.search(r'실패\) 주기 (\d+) 회', s); m3 = re.search(r'후: 전진 ([+-][0-9.]+) 횡 ([+-][0-9.]+) 회전 ([+-][0-9.]+)', s); m4 = re.search(r'후진 거리 ([0-9.]+)', s)
    if not (m1 and m2 and m3): print('해석 실패', f, s[-200:].replace('\n', ' | ')); continue
    R[(sc, pd)].append((int(sd), float(m3.group(1)), float(m1.group(1)) * 100, int(m2.group(1)), float(m4.group(1)), float(m3.group(3))))
print('정지 자세   패딩    15 s 뒤 전진(m, 씨앗 1~5)            나온 씨앗(≥0.30 m)   최소 여유(cm) 최악   실패 주기(/150, 씨앗별)        후진 거리(m) 중앙')
for (sc, pd), v in sorted(R.items()):
    v.sort(); print('%-8s %-5s   %s   %d / %d             %5.1f            %s     %.2f' % (sc, pd, ' '.join('%+.2f' % x[1] for x in v), sum(x[1] >= 0.30 for x in v), len(v), min(x[2] for x in v), ' '.join('%3d' % x[3] for x in v), np.median([x[4] for x in v])))
PY
