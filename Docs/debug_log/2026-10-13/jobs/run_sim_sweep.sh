#!/bin/bash
# (10-13 §9) MPPI 시뮬 묶음: 장면 5 개 × cost_w 3 개 × 씨앗 10 개, fpchk=1, 3 개씩 병렬 — 계산만, 로버 안 움직임. 결과 /tmp/sweep/*.txt, 끝에 요약표.
source /opt/ros/humble/setup.bash; cd /tmp; mkdir -p /tmp/sweep; rm -f /tmp/sweep/*.txt
[ -d /tmp/bag_f2a10 ] || tar xzf /tmp/bag_f2a10.tgz -C /tmp
T3=$(python3 -c "
import rosbag2_py
r=rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri='/tmp/bag_f2a10',storage_id='sqlite3'),rosbag2_py.ConverterOptions('cdr','cdr'))
print(r.read_next()[2]*1e-9+75.3)" 2>/dev/null | tail -1)
COM="vx_std=0.08 wz_std=0.4 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2 lag_steps=1 w_gain=0.7 w_acc=1.2 humble=1 temperature=0.15 near_thr=0.5 dyn_path=2 dyn_cost=1 obst=1 vx_min=-0.06 fwd_w=15 fpchk=1"
{ for sc in "box_f2o1 bag_f2o1 $(date -d 13:32:59 +%s) 300" "box_f2p1 bag_f2p1 $(date -d 14:14:22 +%s) 350" "door_f2a10 bag_f2a10 $T3 200" "out_f2o1 bag_f2o1 $(date -d 13:30:24 +%s) 280" "out_f2p1 bag_f2p1 $(date -d 14:11:47 +%s) 280"; do set -- $sc
    for w in 3.81 7.62 11.43; do for sd in 1 2 3 4 5 6 7 8 9 10; do echo "$1 $2 $3 $4 $w $sd"; done; done; done; } > /tmp/sweep/jobs.lst
echo "작업 $(wc -l < /tmp/sweep/jobs.lst) 개 시작 $(date +%T)"
xargs -P 3 -L 1 bash -c 'python3 /tmp/anal_mppi_sim.py /tmp/$1 0 label=$0_w$4_s$5 t_abs=$2 cycles=$3 seed=$5 cost_w=$4 '"$COM"' 2>&1 | grep -av "Opened database" > /tmp/sweep/$0_$4_$5.txt' < /tmp/sweep/jobs.lst
echo "끝 $(date +%T)"
python3 - <<'PY'
import glob, re, numpy as np, collections
R = collections.defaultdict(list)
for f in sorted(glob.glob('/tmp/sweep/*_*_*.txt')):
    sc, w, sd = re.match(r'.*/(\w+)_([0-9.]+)_(\d+)\.txt', f).groups(); s = open(f, errors='replace').read()
    m1 = re.search(r'LETHAL 여유.*?최소 (-?[0-9.]+|nan)', s); m2 = re.search(r'실패\) 주기 (\d+) 회', s); m3 = re.search(r'후: 전진 ([+-][0-9.]+)', s); m4 = re.search(r'끝 3 s 이동 ([0-9.]+)', s)
    if not (m1 and m2 and m3): print('해석 실패', f, s[-300:]); continue
    R[(sc, float(w))].append((int(sd), float(m1.group(1)) * 100, int(m2.group(1)), float(m3.group(1)), float(m4.group(1)) if m4 else float('nan')))
print('장면         cost_w   최소 여유(cm) 중앙 · 최악 · 씨앗별(오름차순)                         멈춘 씨앗(실패≥10)   전진 거리 중앙(m)')
for (sc, w), v in sorted(R.items()):
    c = sorted(x[1] for x in v); st = [x[0] for x in v if x[2] >= 10]
    print('%-12s %5.2f    %5.1f · %5.1f · %s   %d / %d %s   %.2f' % (sc, w, np.median(c), c[0], ' '.join('%.1f' % x for x in c), len(st), len(v), ('(씨앗 %s)' % ','.join(map(str, st))) if st else '', np.median([x[3] for x in v])))
PY
