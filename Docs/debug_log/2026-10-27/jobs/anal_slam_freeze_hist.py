#!/usr/bin/env python3
"""anal_slam_freeze_hist — §23 SLAM map→odom stamp 정체가 예전부터 있었나 (2026-10-27, PC, 로버 안 움직임).
  bag(.tgz) 마다 임시 폴더에 풀어 /tf 만 읽고 지운다:
    map→odom 수 · 새 stamp 간격 중앙 · 99 % · 최대 · > 0.4 s 수 · > 0.5 s 수, 새 stamp 첫 수신 때 미래 여유(stamp − 수신) 중앙
    (= 그때 적용된 transform_timeout 근사), 이동 거리(odom→base_link 경로 길이) · 시간, 거리 1 m 당 > 0.5 s 정체 수,
    params.txt 에서 slam_toolbox mode · transform_timeout · minimum_travel_distance (있으면).
  인자: 출력.tsv tgz…"""
import sys, os, re, math, tarfile, tempfile, shutil, time
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
TS = get_typestore(Stores.ROS2_HUMBLE)
out = open(sys.argv[1], 'w', encoding='utf-8')
cols = ['bag', '시작', '길이s', '이동m', 'mo수', '간격중앙', '간격99', '간격최대', 'gt0.4', 'gt0.5', 'gt0.5_per_m', '여유중앙', 'mode', 'transform_timeout', 'min_travel']
out.write('\t'.join(cols) + '\n'); print('\t'.join(cols))
for f in sys.argv[2:]:
    tmp = tempfile.mkdtemp(dir=os.environ.get('TMPX'))
    try:
        with tarfile.open(f) as tz:
            mem = [m for m in tz.getmembers() if m.name.endswith(('.db3', 'metadata.yaml', 'params.txt', '.mcap'))]
            tz.extractall(tmp, members=mem)
        mds = list(Path(tmp).rglob('metadata.yaml'))
        if not mds: print(Path(f).name, '메타 없음'); continue
        bd = mds[0].parent
        MO, OB = [], []
        with AnyReader([bd], default_typestore=TS) as rd:
            con = [c for c in rd.connections if c.topic == '/tf']
            for c, t, raw in rd.messages(connections=con):
                for tr in rd.deserialize(raw, c.msgtype).transforms:
                    if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((t * 1e-9, tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9))
                    elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((t * 1e-9, tr.transform.translation.x, tr.transform.translation.y))
        par = {}
        pt = list(bd.rglob('params.txt')) or list(Path(tmp).rglob('params.txt'))
        if pt:
            txt = open(pt[0], encoding='utf-8', errors='replace').read()
            blk = re.search(r'slam_toolbox[\s\S]{0,20000}', txt)
            for k in ('mode', 'transform_timeout', 'minimum_travel_distance'):
                m = re.search(r'\b%s\b\s*[:=]\s*([^\s,]+)' % k, blk.group(0) if blk else txt)
                if m: par[k] = m[1].strip("'\"")
        if len(MO) < 50: print(Path(f).name, 'map→odom %d 개 — 건너뜀' % len(MO)); continue
        MO = np.array(sorted(MO)); OB = np.array(sorted(OB))
        new = np.r_[True, np.diff(MO[:, 1]) != 0]; S = MO[new]; gap = np.diff(S[:, 1]); mar = S[:, 1] - S[:, 0]
        dist = float(np.hypot(*np.diff(OB[:, 1:], axis=0).T).sum()) if len(OB) > 1 else 0.0
        row = [Path(f).name.replace('.tgz', ''), time.strftime('%m-%d %H:%M', time.localtime(MO[0, 0])), '%.0f' % (MO[-1, 0] - MO[0, 0]), '%.1f' % dist, str(len(MO)),
               '%.3f' % np.median(gap), '%.3f' % np.percentile(gap, 99), '%.3f' % gap.max(), str(int((gap > 0.4).sum())), str(int((gap > 0.5).sum())),
               '%.2f' % ((gap > 0.5).sum() / dist) if dist > 0.5 else '-', '%.3f' % np.median(mar), par.get('mode', '-'), par.get('transform_timeout', '-'), par.get('minimum_travel_distance', '-')]
        out.write('\t'.join(row) + '\n'); out.flush(); print('\t'.join(row))
    except Exception as e:
        print(Path(f).name, '오류', repr(e)[:150])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
