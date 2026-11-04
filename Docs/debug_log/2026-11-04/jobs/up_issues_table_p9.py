# up_issues_table_p9 — ISSUES.md 에 9 기 카드 표를 넣고 '10 월 (형식 시범)' 두 줄을 9 기 표로 옮김(11-04 §4). PC 한 번 · 로버 안 움직임 · 인자 없음 · 출력 'ok'.
p = 'F:/6_Indoor_Rover/Rover/Docs/issues/ISSUES.md'
s = open(p, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in s else '\n'
assert '### 9 기' not in s
T = '''### 9 기 10-26 ~ 10-29 (Smac 채택 · MPPI 굽은 곳 · nvblox 층 TF · SLAM stamp · 주행 전 검사 · F2.5 · 정지 드리프트) — 11-04 작성 · 시범 2 장 확장 · 앞 카드 약 25 장 이어 채움
| 카드 | 상태 | 한 줄 |
|---|---|---|
| [Smac Hybrid 채택](smac-hybrid-adoption.md) | 부분 해결(시험 구성 채택 · 기본 아님) | 오프라인 변형 비교는 1.1.20 Smac 의 static 설정 공유로 대부분 무효 → 변형마다 다시 재 RS + 해석 1.0 m. 실주행 b910 상자 옆 18.4 · 10.8 cm(MPPI 14 · 10, B0 15.2 · 5.5 · 3.1), 통로 남행은 tolerance 0.35 로 Smac 이 받아 0.8 → 4.1 cm. 북행 · 좁은 곳 출발은 출발 자세에 따라 NavFn 대체. launch 기본은 navfn |
| [MPPI 굽은 곳 안쪽 깎기 · PathAlign 28 / PathFollow 5](mppi-corner-cut-pathalign.md) | 우회(설정 채택 · 기전 미확인) | Smac 경로에서도 MPPI 가 굽은 곳 안쪽을 +10.7 · +15.7 cm 깎음(odom 좌표, 위치 보정 몫 ≤ 5 cm). 시뮬은 차를 못 가름, 실주행 A/B +4.6 · +1.6 cm 로 28 · 5 채택. ⚠ 기본 구성(NavFn · 0.5 Hz) + 28 · 5 조합은 달린 적 없음 |
| [nvblox 층 TF 조회 실패 처리](nvblox-layer-tf-drop.md) | 해결 | 전역 nvblox 층이 map→odom 조회 실패 순간 odom 슬라이스를 단위 변환으로 map 에 적어 0.55 m · 7.5° 틀어진 장(f2st1 3 장, 가짜 막힘 2). catch 에 return 뒤 f2tf1 틀어진 장 0, 방아쇠(SLAM stamp 정체)는 timeout 1.5 로 f2tt1 · f2tt2 경고 0. 영향 가능 기간 10-08 ~ 10-27 |
| [SLAM map→odom 시각 정체](slam-stamp-freeze.md) | 우회 | 위치 추정 정합(LinkNearChains 64 %) 동안 stamp 가 0.4~1.3 s 멈춰 nav2 TF 실패 → transform_timeout 1.5 로 f2tt1 · f2tt2 실패 0. 정체 자체(주행당 > 0.5 s 30 번 안팎)와 비용은 남음. 10-07 이후 위치 추정 순회 전부(회귀 아님) |
| [주행 전 검사 정리](drive-gate-consolidation.md) | 해결(정리) · 남은 결함 3 | 게이트 B · C · G2 를 한 노드(chk_drive_gate)로, P 를 30 s 대기 안으로 → 게이트 23.6 → 6.7 s, 출발까지 66 → 40 s(2 주행). 게이트 C 실제 관찰 창 1~5 s 흔들림 · timeout 1.5 뒤 C 문턱 1.0 s 의 뜻이 바뀜 · TEST_COURSE 게이트 표 낡음 |
| [F2.5 장소 이름 이동](f25-place-navigation.md) | 조사 중 | 등록부 좌표만 쓰는 place_server 로 실주행 5 회 — 앞 3 회는 설계대로 거절 · 멈춤(비스듬한 명목 자세 · 치우친 좌표 · 첫 메시지 유실), f2pl4 6/6(stop → /cmd_vel 0 0.29 s) · f2pl5 2/2. T1 미실행 · 모델 미실행 · launch 에 없음 · 휴대폰 창구는 휴대폰에서 미시험 |
| [세워 둔 로버의 방향 드리프트](stationary-yaw-drift.md) | 조사 중 | 주행 뒤 정지에서만 odom yaw 가 돌고(43 분 +16.6°) SLAM 은 고치지 않아 경로 없음 · 7° 틀린 출발. 출발 전 검사 ⓐ 는 저장소에만(Jetson 판 미확인), d2 미실행. '정지 중 SLAM 이 안 고침' 은 위치 추정 문턱(0.15 rad)과 어긋나 기전 미확인 |
| 이어 채움 | — | [계획기](global-planner-choice.md) · [F2 기준선 no5](f2-baseline-no5.md)(9 기 no5 4 주행) · [BT CopyPath](bt-copypath-end-yaw.md) · [경로 추종 · B0](path-tracking-replan-b0.md) · [only_new](pathblocked-only-new.md)(f2sa3 첫 실작동) · [MPPI 통로](mppi-passage-tuning.md) · [MPPI 시뮬](mppi-offline-simulator.md) · [nvblox 층 반올림](nvblox-layer-round-floor.md) · [복귀 길 상자 칸](box-return-cells.md)(잊기 = 기능 · 시야 = 센서 한계, 사용자) · [상자 옆 정지 기전](box-side-stall-cause.md) · [낮은 상자 기억](low-box-global-memory.md) · [DDS 참여자](pre-drive-dds-participants.md) · [운용(8 기)](drive-ops-1019-1023.md) · [CPU](cpu-load-stalls.md) · [SLAM 포크](slam-fork-rotation.md) · [nav_guard](onboard-stop-nav-guard.md) · [휠 오도](wheel-odom-scale-slip.md)(반전 순간 FG 부호) · [트랙 비대칭](track-asymmetry.md) · [stuck_monitor](stuck-monitor.md)(자이로 우선 켜지 않음, 사용자) · [데크 yaw](sensor-deck-yaw.md)(xacro ↔ urdf) · [기록 규칙](record-conventions-evolution.md) |

'''.replace('\n', nl)
k = s.index('### 10 월 (형식 시범)')
e = s.index('## 카드 형식')
old = s[k:e]
new = '### 10 월 (형식 시범)' + nl + '10-29 시범 2 장(SLAM stamp 정체 · 정지 중 방향 드리프트)은 11-04 9 기에서 전체 형식으로 넓혀 위 9 기 표로 옮겼다.' + nl + nl
s = s[:k] + T + new + s[e:]
open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
