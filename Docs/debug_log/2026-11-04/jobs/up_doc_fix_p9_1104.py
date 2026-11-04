# up_doc_fix_p9_1104 — 11-04 §5: 9 기 문제 대장이 찾은 낡은 주석 · 문서 정정(동작 변경 없음). PC 한 번, 로버 안 움직임, 출력 'ok'.
R = 'F:/6_Indoor_Rover/Rover/'
def sub(p, o, n):
    s = open(R + p, encoding='utf-8', newline='').read()
    assert s.count(o) == 1, (p, o[:60], s.count(o))
    open(R + p, 'w', encoding='utf-8', newline='').write(s.replace(o, n))
N = 'ros2_ws/src/rover_navigation/config/nav2_params.yaml'
sub(N, '#   10-23 NavFn 판 28 단독은 f2pa2 에서 5.5 s 정지 1 회(목표 · 경로 방향 57° 어긋남) — Smac 판 2 회엔 없음.',
       '#   10-23 NavFn 판 28 단독은 f2pa2 에서 5.5 s 정지 1 회(목표 · 경로 방향 57° 어긋남) — Smac 판 2 회엔 없음.\n'
       '#   (11-04 추가) 채택 뒤 f2sa3(no5): 서쪽 통로 NavFn 대체 경로에서 최소 여유 0.8 cm · 정지 15.3 s(10-26 §15). ⚠ 28 · 5 로 달린 7 회는 모두 planner:=smac · 재계획 0.01 —\n'
       '#   기본 구성(NavFn · 0.5 Hz) + 28 · 5 조합은 아직 달린 적 없음(문제 대장 mppi-corner-cut-pathalign).')
o = [l for l in open(R + N, encoding='utf-8').read().split('\n') if l.lstrip().startswith('motion_model_for_search: "REEDS_SHEPP"')][0]
tail = o[o.index('이전 DUBIN'):]
sub(N, tail, '이전 DUBIN(전진만) 의 옛 설명(후진 cusp 을 넣지 않음)은 RS 에선 맞지 않음 — RS 는 후진 구간을 낼 수 있다(11-04 주석 정정)')
sub(N, '      # 2026-09-14 정지 A/B(09-14 §2.19): R 0.20/cost 2.0',
       '      # (아래 3 줄은 09-14 첫 비교 당시 이야기 — 지금 값의 근거는 10-26 §6.3 · 10-27 §8, 11-04 표시)\n      # 2026-09-14 정지 A/B(09-14 §2.19): R 0.20/cost 2.0')
sub('ros2_ws/src/rover_navigation/config/places.yaml', '(미검증 자리 — f2pl3 에서 첫 도착)', '(첫 도착 f2pl4 — f2pl3 은 움직이지 않음, 11-04 정정)')
P = 'Docs/06_planner/SMAC_HYBRID_PLAN.md'
s = open(R + P, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in s else '\n'
add = (nl + '## 11. 2026-11-04 정정 · 상태 (문제 대장 9 기 smac-hybrid-adoption 카드 대조)' + nl +
 '- §8 · §10 의 10-23 판정(Hybrid 기준 미달 · Phase P 멈춤 · Lattice cp · 회전 벌점 효과 없음)은 10-26 §6.1 에서 무효 — 한 planner_server 의 Smac 변형들이 정적 동작 표를 공유해 변형 차이가 적용되지 않았다. 변형마다 따로 다시 잰 결과(10-26 §6.3)는 RS + 해석 1.0 m 가 최선.' + nl +
 '- 10-26 §4 ~ 10-27 의 결과(포크 analytic_expansion_max_cost · cost_penalty 원인 · tolerance 0.35 · 실주행 f2sh · f2sa · f2st · f2tf · f2tt)는 이 계획서에 없다 → `Docs/issues/smac-hybrid-adoption.md` 가 정리본.' + nl +
 '- §6 \'REEDS_SHEPP 는 이 Phase 밖\' 은 지금 채택값(`nav2_params.yaml` motion_model_for_search REEDS_SHEPP)과 어긋남. §7 의 `PHASE_P_RESULTS.md` 는 만들지 않았다.' + nl +
 '- 지금 상태: `planner:=smac` 은 시험 구성(launch 기본 navfn · prep 재계획 0.5 Hz). 러너 목표 방향은 여전히 NavFn 에 묻는다(`path_end_yaw.py` 22 행 planner_id GridBased — P2 미해결).' + nl)
open(R + P, 'w', encoding='utf-8', newline='').write(s.rstrip('\r\n') + nl + add)
T = 'Docs/04_navigation/TEST_COURSE_AND_GATES.md'
sub(T, '| C | SLAM 생존 | map→odom ≥ 수십 개/5 s, 최대 간격 ≤0.2 s | `job386_slamalive.py` |',
       '| C | SLAM 생존 | map→odom ≥ 수십 개/5 s, 최대 간격 ≤0.2 s — ⚠ 11-04 정정: 코드는 09-17 job386 부터 **수신 간격 최대 < 0.5 s · stamp 지연 최대 < 1.0 s**, 10-27 부터 `Docs/tools/chk_drive_gate.py`(B · C · G2 한 노드) | `job386_slamalive.py` → `chk_drive_gate.py` |')
sub(T, '| 게이트 | A·B·J·C·G2(`job551` 내장) + prep 게이트(§2)',
       '| 게이트 | A·B·J·C·G2(`job551` 내장 — 10-27 부터 B · C · G2 는 `chk_drive_gate.py` 한 노드, 그리고 정지 부하 **P**: 30 s 대기의 마지막 10 s 코어 평균 ≤ `LOAD_MAX`(기본 60 %), 11-04 표시) + prep 게이트(§2)')
D = 'Docs/tools/README.md'
sub(D, '| `up_tools.sh` | 위 Jetson 쪽 도구와 주행 보조 스크립트를 /tmp 로 전송 | `up950.sh` 등 |',
       '| `chk_drive_gate.py` | (Jetson) 주행 직전 게이트 B(/wheel_odom) · C(map→odom 간격 < 0.5 s · stamp 지연 < 1.0 s) · G2(출발 자세 여유) 를 한 노드로, 마지막 줄 `GATE …` 를 러너가 읽음(10-27) | job254 · job386 · job440 |\n'
       '| `run_slam_replay.sh` · `slam_replay_feed.py` | (Jetson) SLAM 위치 추정 재생 A/B — 도메인 42 · sim time 으로 bag 을 먹여 설정별 map→odom 정체 비교(10-27). ⚠ 설정값을 스크립트에 손으로 다시 적어 둠 — slam.launch.py 를 바꾸면 같이 | — |\n'
       '| `up_tools.sh` | (PC) 저장소 판 Jetson 쪽 도구(prep_fast · prep_patrol · chk_prep · chk_drive_gate · anal_rtps_*)를 /tmp 로 전송(11-04 고침 — 예전엔 스크래치패드 tools/ 를 읽음) | `up950.sh` 등 |')
print('ok')
