# 9 기 묶음 보고의 '관련 문제' 링크를 머리 표 값 줄 마지막 칸에 덧붙임 — 그 줄에 이미 있으면 건너뜀
import sys
sys.stdout.reconfigure(encoding='utf-8')
D = 'F:/6_Indoor_Rover/Rover/Docs/issues/'
SH,MC,NT,DG,F25,SS,YD = ('smac-hybrid-adoption','mppi-corner-cut-pathalign','nvblox-layer-tf-drop','drive-gate-consolidation','f25-place-navigation','slam-stamp-freeze','stationary-yaw-drift')
NAME = {SH:'Smac Hybrid 채택',MC:'MPPI 굽은 곳 · PathAlign 28/5',NT:'nvblox 층 TF 실패',DG:'주행 전 검사 정리',F25:'F2.5 장소 이름 이동',SS:'SLAM stamp 정체',YD:'정지 중 방향 드리프트'}
M = {
 'f2-baseline-no5':[SH,F25], 'southwest-orient-stall':[F25], 'bt-copypath-end-yaw':[SH,F25], YD:[F25,DG],
 'pre-drive-dds-participants':[DG,F25], 'jetson-wifi-link':[F25], 'pathblocked-only-new':[MC,NT,F25], DG:[F25,SS],
 SH:[MC,F25,NT], 'path-tracking-replan-b0':[SH,MC], 'passage-width-analysis':[SH], 'prep-fast-startup':[DG,SH],
 MC:[SH,NT], 'global-planner-choice':[SH,MC,NT], 'box-return-cells':[NT,MC], 'rotation-method-track-ratio':[MC],
 'box-side-stall-cause':[MC,NT], NT:[SS,MC], 'mppi-wobble-temperature':[MC], SS:[NT,DG,YD],
 'nvblox-n6-global-ghosts':[NT], 'onboard-stop-nav-guard':[F25,NT], 'tf-lag-w3-wobble':[NT,DG], 'slam-fork-rotation':[YD,SS],
 'sensor-conditioner':[YD], F25:[YD,DG,SH], 'mppi-passage-tuning':[MC], 'mppi-offline-simulator':[MC],
 'low-box-global-memory':[NT], 'nvblox-layer-round-floor':[NT], 'cpu-load-stalls':[SS,DG], 'drive-ops-1019-1023':[DG],
}
for card, links in M.items():
    p = D + card + '.md'; L = open(p, encoding='utf-8').read().split('\n')
    i = next(k for k, l in enumerate(L) if l.startswith('|') and '관련 문제' in l)
    j = i + 2
    assert L[j].startswith('|'), card
    add = [l for l in links if '(%s.md)' % l not in L[j]]
    if not add: print('skip', card); continue
    row = L[j].rstrip(); assert row.endswith('|'), card
    L[j] = row[:-1].rstrip() + ' · ' + ' · '.join('[%s](%s.md)' % (NAME[l], l) for l in add) + ' (9 기) |'
    open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(L))
    print('add', card, len(add))
