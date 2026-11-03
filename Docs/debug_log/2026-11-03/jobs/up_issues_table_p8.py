import sys
sys.stdout.reconfigure(encoding='utf-8')
p = 'F:/6_Indoor_Rover/Rover/Docs/issues/ISSUES.md'
s = open(p, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in s else '\n'
T = '''### 8 기 10-19 ~ 10-23 (상자 칸 과장 · 프로젝터 · cuVSLAM · 공유메모리 · 유령 칸 · 경로 추종 · B0) — 11-03 작성 · 앞 카드 26 장도 이어 채움
| 카드 | 상태 | 한 줄 |
|---|---|---|
| [카메라 상자 칸 과장의 근원](box-exaggeration-source.md) | 조사 중 | 출발점 상자 로버 쪽 면 +5.3 cm(f2x1)를 원시 깊이 점으로 나누면 관측 오차 3~5 + odom 기억 밀림 +2.7~6.1 + 칸 반올림(최대 5) cm. nvblox 설정 · 깊이 필터 · map 기억 · 깊이 해상도는 대책 아님(5 cm 척도 한계 주의) |
| [복귀 길 상자 칸](box-return-cells.md) | 우회(통합 거리 2.0, 1 회 검증) · 기억 밀림 남음 | 복귀 때 상자는 차체 옆 시야 밖이라 odom 기억이고 SLAM 보정마다 밀린다. 프리셋 3 · 프로젝터 끔에선 다시 봐도 깊이 0 → f2lp1 이 세 지도 0 칸인 채 접촉, 통합 2.0 뒤 f2pi1 실제 여유 1.1 cm |
| [프로젝터 번갈이 · IR](projector-ir-alternation.md) | 우회(10-21 §20 상시 끔 결정) | 번갈이는 우리 분리 노드 · NVIDIA 권장 구성 모두 자동 노출이 켠 프레임에 맞춰져 끈 IR 이 어두워 cuVSLAM 이 못 따라감(f2y1 469~483 cm). 상시 끔이면 따라감(f2z1 25.7 cm · yaw 0.8°) — 대가는 맨바닥 유령 칸 |
| [cuVSLAM 병진 속도 융합](cuvslam-velocity-fusion.md) | 부분 해결(운용 채택) | 오프라인(번갈이) 실패 → 상시 끔에서 따라감 → 같은 주행 그림자 비교 W3 회전 창 −20 %(UDP) · −31~−41 %(SHM) → 10-23 기본. 상자 옆 여유에는 효과 없음, yaw 는 휠 · 자이로가 정함 |
| [카메라 ↔ 컨테이너 공유메모리](camera-container-shm.md) | 해결(카메라 ↔ cuVSLAM 경로) | IR 307 kB 가 UDP 수신 버퍼 208 kB 를 넘어 정지 13 · 주행 9.5 Hz → 카메라 ↔ cuVSLAM 만 SHM+UDP 로 15.0 Hz(정지 A/B · 재기동 10/10 · f2sm1). 소켓 버림 감소의 직접 근거는 측정 결함으로 판정 불가 |
| [프로젝터 끔의 유령 칸 · 깊이 프리셋 3 · 통합 거리 2.0](ghost-cells-depth-preset.md) | 우회 | 상시 끔 뒤 맨바닥 유령 칸이 f2dr1 을 끊어 프리셋 3 기본(유령 0, 대가 낮은 상자 칸 절반 · min_weight · 프리셋 5 기각). 프리셋 3 + 1.4 m 는 f2lp1 접촉 → 2.0(f2pi1 3/3). 기전(무늬 없는 바닥 스테레오 오정합)은 추정 |
| [경로 추종 · 재계획 → B0](path-tracking-replan-b0.md) | 조사 중 | 상자 옆 근접은 계획기가 아니라 MPPI 굽은 곳 안쪽 깎기와 로버 자리 재계획 누적(경로 11~16 cm, 실제 0.3~6.7 cm). 재계획 0.01 Hz 도 b910 15.2 · 5.5 · 3.1 cm → B0 결함 기준선 고정. 10-23 Smac 오프라인 비교는 10-26 에 무효 |
| [PathBlockedAhead 99/100 · only_new](pathblocked-only-new.md) | 조사 중(조치 적용 · 실주행 효과 미확인) | 서쪽 통로 막힘 오판은 경로 받은 같은 틱에 99. 문턱 100 안은 상자 막힘도 끄는 내 오류 → '받을 때보다 커진 점만' 세는 only_new, bag 재생 9 사건 확인. ⚠ 표준 prep 0.5 Hz 와의 조합은 미시험 |
| [주행 전 검사 · 운용 사고(8 기)](drive-ops-1019-1023.md) | 우회 | 출발 위치 검사 PREP_POSE 가 prep 26 회 중 실제 오류 3 회를 주행 전에 거름, 게이트 P 65 % 완화는 판정을 바꾼 적 없음. prep 실패 3 유형 · 스크래치패드 소실 2 회 · 밤사이 재부팅 3 회의 원인은 미확인 |
| [기록 규칙의 진화](record-conventions-evolution.md) | 해결(규칙) · 보류(큰 bag 정리) | 큰 bag 수명 · 실수 칸 형식 · 추론별 데이터 위치 · 영상 기본 도구가 README §2.3 · §6 에 자리잡음. 남은 결함: TOOLS.md 3 일 누락 · 'git 제외' 라던 mp4 2 개가 실제로는 추적됨 |
| 이어 채움 | — | [상자 옆 정지 기전](box-side-stall-cause.md) · [대책](box-side-stall-remedies.md)(MonotoneEscape 실주행 첫 작동 f2sm2h) · [Isaac · cuVSLAM 평가](isaac-cuvslam-evaluation.md) · [DDS 공유메모리](dds-shm-incident.md)(10-20 재점검 표 검증) · [rf2o 도입](rf2o-introduction.md) · [rf2o 게이트 · 사람](rf2o-gates-people.md) · [제자리 회전 미끄러짐](f0-rotation-side-slip.md)(W3 창 9 주행) · [회전 중 번짐](rotation-obstacle-smear.md) · [N6 유령](nvblox-n6-global-ghosts.md) · [깊이 장애물](depth-obstacle-costmap.md) · [F2 기준선 no5](f2-baseline-no5.md) · [계획기](global-planner-choice.md) · [nav_guard](onboard-stop-nav-guard.md) · [CPU](cpu-load-stalls.md) · [MPPI 통로](mppi-passage-tuning.md) · [빠른 prep](prep-fast-startup.md) · [Wi-Fi](jetson-wifi-link.md) · [보드 연결](board-link-microros-session.md) · [전선](cable-step-over.md) · [보관](storage-housekeeping.md) · [DDS 참여자](pre-drive-dds-participants.md) |

'''.replace('\n', nl)
k = s.index('### 10 월 (형식 시범)')
assert '### 8 기' not in s
s = s[:k] + T + s[k:]
open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
