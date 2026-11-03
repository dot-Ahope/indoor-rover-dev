# 6 기 묶음 보고의 '다른 카드에 넣을 링크' 를 머리 표 '관련 문제' 칸(마지막 칸)에 덧붙임 — 이미 링크가 있으면 건너뜀
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
D = 'F:/6_Indoor_Rover/Rover/Docs/issues/'
NAME = {'pad-relief-runtime-padding':'pad_relief · 실행 중 패딩','box-side-stall-cause':'상자 옆 정지 기전','box-side-stall-remedies':'상자 옆 정지 대책',
 'bt-copypath-end-yaw':'BT 끝 방향 CopyPath','f2-baseline-no5':'F2 기준선 no5','prep-fast-startup':'빠른 prep','network-saturation-mppi-viz':'통신 포화',
 'dds-shm-incident':'DDS 공유메모리','rotation-method-track-ratio':'회전 방식 · 앞 회전 우선'}
P,C,R,B,F,Q,N='pad-relief-runtime-padding','box-side-stall-cause','box-side-stall-remedies','bt-copypath-end-yaw','f2-baseline-no5','prep-fast-startup','network-saturation-mppi-viz'
M = {
 C:[P,R,F,B,N], R:[C,P,F,B,Q], B:[P,C,R], F:[P,C,R], 'jetson-wifi-link':[P], Q:[P,N], 'tf-lag-w3-wobble':[P],
 'mppi-wobble-temperature':[P], 'mppi-offline-simulator':[P,C,R], 'inflation-padding-roles':[P,R], 'stuck-monitor':[P],
 P:[C,R,B,F,Q], 'southwest-orient-stall':[C], N:['dds-shm-incident','rotation-method-track-ratio',Q], 'f0-rotation-side-slip':[C],
 'rotation-obstacle-smear':[C], 'low-box-global-memory':[R,Q,B], 'pre-drive-dds-participants':[Q,N], 'dds-shm-incident':[N],
 'rotation-method-track-ratio':[N], 'slam-stamp-freeze':[N], 'foxglove-snap-cpu':[N], 'mppi-passage-tuning':[B],
 'f2-patrol-loc-jump':[F], 'costmap-clear-recovery':[B], 'global-planner-choice':[B],
}
for card, links in M.items():
    p = D + card + '.md'; L = open(p, encoding='utf-8').read().split('\n')
    i = next(k for k, l in enumerate(L) if l.startswith('|') and '관련 문제' in l)
    j = i + 2                      # 머리줄 · 구분줄 다음 = 값 줄
    assert L[j].startswith('|'), card
    whole = '\n'.join(L)
    add = [l for l in links if '(%s.md)' % l not in whole]
    if not add: print('skip', card); continue
    row = L[j].rstrip()
    assert row.endswith('|'), card
    ins = ' · '.join('[%s](%s.md)' % (NAME[l], l) for l in add)
    L[j] = row[:-1].rstrip() + ' · ' + ins + ' (7 기) |'
    open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(L))
    print('add', card, add)
