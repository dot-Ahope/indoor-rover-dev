# 8 기 묶음 보고의 '관련 문제' 링크를 머리 표 값 줄 마지막 칸에 덧붙임 — 그 줄에 이미 있으면 건너뜀
import sys
sys.stdout.reconfigure(encoding='utf-8')
D = 'F:/6_Indoor_Rover/Rover/Docs/issues/'
BE,BR,PI,CV,CS,GH,PT,PB,DO,RC = ('box-exaggeration-source','box-return-cells','projector-ir-alternation','cuvslam-velocity-fusion',
 'camera-container-shm','ghost-cells-depth-preset','path-tracking-replan-b0','pathblocked-only-new','drive-ops-1019-1023','record-conventions-evolution')
NAME = {BE:'상자 칸 과장의 근원',BR:'복귀 상자 칸',PI:'프로젝터 번갈이 · IR',CV:'cuVSLAM 속도 융합',CS:'카메라 ↔ 컨테이너 공유메모리',
 GH:'유령 칸 · 깊이 프리셋',PT:'경로 추종 · B0',PB:'PathBlockedAhead only_new',DO:'주행 전 검사 · 운용(8 기)',RC:'기록 규칙의 진화'}
M = {
 'nvblox-n6-global-ghosts':[GH,BE], 'depth-obstacle-costmap':[GH,BE], 'low-box-global-memory':[GH,BR,PT],
 'box-side-stall-cause':[BE,BR,GH,PT,CV], 'box-side-stall-remedies':[BE,BR,GH,PT], 'nvblox-migration-n0-n4':[GH],
 'depth-relay-artifacts':[GH,BE,PI], 'dds-shm-incident':[CS,PI,CV,DO], 'storage-housekeeping':[RC,PI],
 'cpu-load-stalls':[PT,DO,PI], 'network-saturation-mppi-viz':[CS], 'pre-drive-dds-participants':[DO,CS],
 'prep-fast-startup':[DO,CS], 'slam-stamp-freeze':[CS,DO], 'isaac-cuvslam-evaluation':[PI,CV,CS],
 'icr-b2-b3':[CV], 'sensor-conditioner':[CV], 'stuck-monitor':[CV], 'tf-lag-w3-wobble':[CV,PT],
 'stationary-yaw-drift':[CV,DO], 'wheel-odom-scale-slip':[CV], 'rf2o-gates-people':[CV], 'rf2o-introduction':[CV,BE],
 'f0-rotation-side-slip':[CV], 'rotation-obstacle-smear':[CV,BE], 'sensor-deck-yaw':[BE],
 'mppi-offline-simulator':[PT], 'bt-copypath-end-yaw':[PT], 'f2-patrol-loc-jump':[PB], 'f2-baseline-no5':[PT,PB],
 'global-planner-choice':[PT], 'mppi-passage-tuning':[PT], 'onboard-stop-nav-guard':[PT],
 'repo-public-ops':[RC], 'jetson-wifi-link':[DO], 'board-link-microros-session':[DO], 'cable-step-over':[DO],
}
for card, links in M.items():
    p = D + card + '.md'; L = open(p, encoding='utf-8').read().split('\n')
    i = next(k for k, l in enumerate(L) if l.startswith('|') and '관련 문제' in l)
    j = i + 2
    assert L[j].startswith('|'), card
    add = [l for l in links if '(%s.md)' % l not in L[j]]
    if not add: print('skip', card); continue
    row = L[j].rstrip(); assert row.endswith('|'), card
    L[j] = row[:-1].rstrip() + ' · ' + ' · '.join('[%s](%s.md)' % (NAME[l], l) for l in add) + ' (8 기) |'
    open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(L))
    print('add', card, len(add))
