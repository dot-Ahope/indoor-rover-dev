# 시험 코스·게이트·주행 절차 — v3.0 (F2 순회 no5, 표준 prep), 2026-11-19

**적용 범위**: 표준 prep 구성(`Docs/04_navigation/CURRENT_STACK.md` §1 — Smac → NavFn · 재계획 0.01 Hz · cuVSLAM 병진 속도 · 전역/로컬 nvblox · MPPI)으로 저장 지도 `office_v3` 위 **8 목표 순회(no5)** 를 도는 주행. 지금 구성을 바꾸고 확인하는 주 시험이다.
- **상자 코스(Phase S/N 층 비교, v1.0~v2.2)와 F0-a 왕복(v2.3 §7)은 이 판에서 뺐다.** 그 코스를 다시 돌릴 때는 v2.3 원문(커밋 `8c225597` 의 이 파일)을 연다 — 게이트 D·E·F·K·L·M·N · 러너 `job125` 재고정 · 모드 S/N 짝 주행 규칙이 거기 있다. 기준선은 `Docs/debug_log/2026-09-21/BASELINE_STVL.md` · `Docs/05_nvblox/PHASE_N_RESULTS.md`.
- 근거 날짜의 `Docs/debug_log/<날짜>/SUMMARY.md` 가 원문이다. 값이 이 문서와 다르면 코드(`config/` · launch · `Docs/tools/prep_*.sh` · 러너)가 맞다.
- **Phase 전환 규칙**(유지): Phase 가 바뀌면 이 문서를 그대로 따르지 말고 절 단위로 검토해 새 판을 쓴다. 검토 항목에 **bag 토픽(§6)** 을 반드시 넣는다(09-21 사용자 질의).

## 0. v2.3 → v3.0 절 단위 검토 결과
v2.3 은 09-28(F0-a)까지의 판이라 09-29 이후 주 시험이 된 F2 순회(10-01~)의 코스 · 러너 · 게이트가 없었다(11-19 SUMMARY §4 에서 발견).

| v2.3 절 | 판정 | 이유 |
|---|---|---|
| §1 배치(상자 코스) | **교체** | 순회는 저장 지도 좌표로 목표를 준다(`GOAL_FRAME=map`). 물리 배치는 출발 테이프와 출발 상자뿐 → §1 |
| §2 절차 | **교체** | `run_mp9prep.sh`(job240) · `run_drive_nohup.sh` · `job488` 모드 전환은 지금 쓰지 않음. 지금 = `prep_patrol.sh` → `run_f2c.sh` → `run_f0.sh` → Jetson `job551` → `job550` → §2 |
| §3 게이트 A · B · C · G2 · J | 유지(도구 갱신) | `job551` 이 그대로 검사. B · C · G2 는 10-27 부터 `chk_drive_gate.py` 한 노드. C 문턱은 v2.3 표의 '≤0.2 s' 가 아니라 코드 값(< 0.5 s · 지연 < 1.0 s, 11-04 정정) |
| §3 게이트 D · E · F · L · M · N | **뺌** | 상자 코스 전용(카메라 점군 상자 검출 · 통로 띠). `job551` 머리 주석 "상자 코스 게이트는 쓰지 않는다"(09-23) |
| §3 게이트 G1(목표 여유) | **대체** | 순회 러너에는 없음 — Nav2 가 목표 칸을 거부하면 러너가 멈춘다(`job551` 머리 주석). 장소 이동(F2.5)은 `place_server` 의 `min_clear` |
| §3 게이트 H · K(파라미터 · 층 실효값) | **대체** | `chk_prep.py` 가 prep 안에서 실행 값을 읽어 기록(10-12 §13). 층은 launch 인자로 고정돼 전환 단계가 없다 |
| §3 게이트 I(배터리) | 유지 | 문턱 없음, prep 기록 |
| (없음) | **추가** | 정지 부하 **P**(10-01 §8.9, 10-27 §24 부터 30 s 대기 끝 10 s) · 출발 위치 검사 **PREP_POSE**(10-21) |
| §4 운영 규칙 | **수정** | 1 · 4 · 6 · 7 · 8 · 13 · 14 유지. 2 · 3 · 5 · 9 · 10 · 11 · 12 · 15 는 상자 코스 · 모드 비교 전용이라 뺌(9 · 11 의 내용은 CURRENT_STACK 으로 옮겨 감). 10-12 이후 규칙 추가 → §5 |
| §5 산출물 | **수정** | `job551` 의 기록 토픽 · 회수 파일로 → §6 |
| §7 F0-a 왕복 | **뺌** | v2.3 원문에 둠(위 적용 범위) |
| (없음) | **추가** | 판정 기본값(§4) · 알려진 미해결(§7) |

## 1. 코스 (no5)
- **지도** `office_v3`(10-02, `f2-patrol-loc-jump`). 좌표는 전부 map 프레임, **출발 테이프 = 지도 원점 (0, 0, yaw 0)**(F1-2, 09-30). 지도를 바꾸면 이 표와 등록부 `places.yaml` 이 무효다.
- **목표 8 개** — 러너 래퍼 `Docs/debug_log/2026-10-22/jobs/run_f2c.sh` 의 `NO5` 문자열(10-14 §13: 10 목표에서 D 와 남서 두 번째를 뺌). 그림 `Docs/04_navigation/figures/2026-10-14_patrol_goals.png`(10 목표 판 — no5 는 그중 5 · 6 을 뺀 것).

| # | 이름(`places.yaml`) | map (x, y) | 방향 | 메모 |
|---|---|---|---|---|
| 1 | B | 2.25, −1.6 | p | |
| 2 | C | −1.6, −2.0 | p | |
| 3 | 통로 북쪽(서쪽 통로) | −1.65, −3.7 | p | 등록부는 10-28 §9 에 −1.78(통로 가운데)로 옮겼지만 **순회 비교는 no5 값 −1.65 를 유지** |
| 4 | 남서 | −1.6, −5.5 | **f** | 좁은 구석 — 위치(0.15 m)만 맞추면 끝, 결과 `SUCCEEDED_XY`(10-07 §7) |
| 5 | 통로 북쪽 | −1.65, −3.7 | p | 통로 남쪽 끝에서 반바퀴 돌아 북쪽으로 나옴 — 11-13 교착 자리(§7) |
| 6 | 위 복도 | −1.6, −2.1 | p | |
| 7 | W3(동쪽 끝) | 5.5, −2.2 | p | 바닥 전선 자리 |
| 8 | 출발점 | 0, 0 | p | 돌아오는 길에 출발 상자 옆을 지남 |

- 방향 `p` = 목표를 보내기 직전 계획 경로 끝 0.3 m 의 진행 방향(09-28 §16), `f` = 같되 위치 안에 들면 방향 맞춤 없이 끝. 목표 판정기 xy **0.15 m** · yaw **0.35 rad** · stateful(`nav2_params.yaml` 102 · 108 · 115, 09-28).
- 속도 0.07(러너 인자), 목표 사이 정지 0 s.
- **출발 상자**: 출발점 근처 복귀 길(map x ≈ 1.0~1.3, y ≈ −0.1~0.07)의 라이다보다 낮은 작은 상자 — **라이다 아래 물체 감지 · 회피를 매번 시험하려고 사용자가 일부러 둔 것**(10-14). 치우거나 우회 대상으로 보지 않는다. 라이다 점 0 · nvblox 카메라 칸만 생기며(주행마다 6~14 칸), 이 자리의 막힘 정지 · 여유는 낮은 물체 성능의 측정값으로 읽는다(`box-side-stall-cause` 카드). 크기 실측 기록은 없음(미확인).
- 나머지 사무실 배치(가구 · 가방 · 상자)는 고정하지 않는다. 서쪽 통로 남쪽은 배치가 5~10 cm 좁아지면 교착이 났다(11-13 §6.2 · §7) — **배치가 평소와 달라 보이면 주행 전 SUMMARY 에 적는다**.

## 2. 절차 (한 회차)
| 단계 | 할 일 | 확인 | 근거 |
|---|---|---|---|
| 0 | (하루 시작) PC 러너 존재 확인 + `touch`(스크래치패드 7 일 자동 삭제, README §4) — `run_jn.sh` · `run_f0.sh` · `job550_f0run.py` · `job551_f0drive.sh` · `job613_pathyaw.py` · `chk_drive_gate.py`. 사라졌으면 저장소 사본(`Docs/debug_log/2026-11-13/jobs/` 등, `<PW>` 가림)에서 복구 | 파일 6 개 | 11-13 §1(사본 소실 → 복구) |
| 1 | (재부팅 뒤) `bash Docs/tools/up_tools.sh` — Jetson `/tmp` 에 prep 도구 재전송. 보드 세션 확인(rover-base active · 발행자 생성) | `up_tools` 출력 · 보드 세션 1 | 11-04 §1 · 11-11 §5 `chk_ready_1111.sh` |
| 2 | 사용자가 로버를 **출발 테이프 위 · 처음 방향(yaw 0)** 으로, 출발 상자를 테이프 자리에 둔다. 관찰자는 로버 · 카메라 시야에서 떨어진다 | — | 11-11 §5 |
| 3 | prep: `run_jn.sh` 로 Jetson `bash /tmp/prep_patrol.sh lite`(인자 없이 = 표준). **출력은 거르지 말고 원문 파일로**(`outputs/prep_<이름>.txt`) | `PREP_OK` · 위치 차 ≤ 0.10 m · yaw ±2° · `BT RateController hz="0.01"` · Smac tol 0.35 | 11-11 §7 · README §5 |
| 4 | 판정 기준을 SUMMARY 새 § 로 **주행 전에** 선언(§4 기본값에서 바꾼 것 · STAGE · NOTE) | 선언 § | README §2.2 |
| 5 | **주행 30 s 전부터 DDS 참여자를 만들거나 없애지 않는다**(`ros2 topic/param` · 임시 노드). 대화 쪽에서 따로 대기 · top 을 켜지 않는다 — 러너가 한다 | — | 09-21 cc1 · 10-27 §24 |
| 6 | 사용자 **"시작"** 뒤에만: `STAGE='<구성 표기>' bash Docs/debug_log/2026-10-22/jobs/run_f2c.sh <이름> '<NOTE>' $(git rev-parse --short HEAD) no5`(WSL). 래퍼가 `BAG_PROFILE=nvblox` · `GOAL_FRAME=map` · `LONG_REC=1` · 추가 토픽을 넣고 `run_f0.sh` 를 부른다. 게이트(§3) → 30 s 대기 → 출발은 **약 40~50 s 뒤** | 러너 줄 `SUCCEEDED` × 8(4 번째 `SUCCEEDED_XY`) | 10-22 · 11-11 §5 |
| 7 | 회수: `run_f0.sh` 가 끝에 `f0_<이름>/` 로 가져온다(§6). **러너가 '회수' 줄을 찍기 전에는 Jetson 전원을 끄지 않는다.** 그날 `Docs/debug_log/<날짜>/bags/f0_<이름>/` 로 옮기고, Nav2 로그(Jetson `/tmp/nav2.log`)도 회수 — 재부팅 · prep 이 `/tmp` 를 지움 | `회수 …` 줄 | 11-10 f2dm2 bag 소실 · README §5 |
| 8 | 분석: 러너 원문 → `Docs/tools/anal_drive_results.py`(목표별 결과 · 시간), Nav2 로그 → `anal_navlog.py` · 사건 파일(`2026-11-11/jobs/chk_nav2_run_1111.sh` · `chk_tf_line_1111.sh` · `up_nav_events_1111.sh` 꼴), 그림 → `fig_patrol_run.py` · `fig_scene.py` · `fig_odom.py`(`Docs/tools/README.md`) | SUMMARY 표 | 11-10 · 11-11 · 11-19 |
| 9 | 기록 · 커밋: README §2 · §8(커밋 전 `python Docs/tools/chk_record_rules.py`, 비밀번호 게이트 0) | — | README §8 |

- 이어 가기: 중간에 멈춘 회차는 래퍼 마지막 인자로 남은 목표만 줄 수 있다(`home` · `homew` 등, `run_f2c.sh` 안 문자열). 이어 간 회차는 '연속 완주' 에 넣지 않는다.

## 3. 게이트 (전부 통과해야 주행; 실패 시 러너가 "주행하지 않음" 으로 멈춘다)
| # | 게이트 | 문턱 | 측정 도구 | 실패 시 | 근거 |
|---|---|---|---|---|---|
| prep | 스택 준비 | Nav2 수명 주기 active(controller · planner · bt_navigator · behavior · nav_map_server) · map→base_link TF · `/wheel_odom` ≥ 20 Hz · `/odometry/filtered` ≥ 20 Hz · 전역 코스트맵에 저장 지도 → `PREP_OK` | `Docs/tools/chk_prep.py`(prep 안, 참여자 1 개) | prep 다시 | 10-12 §13 |
| 위치 | 출발 위치 추정 | map→base 가 `PREP_POSE`(기본 `0,0,0` = 출발 테이프)에서 위치 ±0.10 m · yaw ±2° 안 | `chk_prep.py` | prep 다시(SLAM 이 출발 위치를 틀림). 테이프 밖에서 시작하면 `PREP_POSE='x,y,yaw°'` | 10-21(prep 직후 21° · −41° 틀림 2 회) |
| A | 프로세스 중복 · 누락 | 14 종 각 1 개(EKF 는 그림자 EKF 수만큼 더) | `job551`(pgrep) | prep 다시 | 09-11 · 10-07 · 10-20 |
| B | 보드 세션 | `/wheel_odom` 5 s 동안 ≥ 1 Hz | `chk_drive_gate.py` | 에이전트가 살아 있으면 두고 보드 리셋 요청 | 09-11 · 10-27 §24 |
| J | nvblox 노드 | 노드 1 개 · 깊이 콜백 ≥ 10 Hz | `job551`(nvblox 통계 로그) | prep 다시 | 09-21 §9 |
| C | SLAM 생존 | map→odom 5 s 동안 수신 간격 최대 < 0.5 s · stamp 지연 최대 < 1.0 s | `chk_drive_gate.py` | prep 다시 | 09-17 · 10-27 §24 · 11-04 정정 |
| G2 | 출발 자세 여유 | 로컬 LETHAL 칸 · 라이다 점(2 m 안) ↔ 차체 외곽 ≥ 0.10 m(`G2_SKIP=1` 이면 건너뜀 — 쓰면 SUMMARY 에 적음) | `chk_drive_gate.py` | 로버 주변 물체 · 사람 치움 | 09-18 |
| P | 정지 부하 | 30 s 대기의 마지막 10 s 코어 평균 ≤ `LOAD_MAX`(기본 60 %, 정지 기준선 36 %) | `job551`(`/proc/stat`) | 원인 프로세스 확인 · prep | 10-01 §8.9 · 10-27 §24 |
| I | 배터리 | 기록만(문턱 없음) | prep 출력 | — | — |

- 목표 여유는 게이트가 아니다: Nav2 가 목표 칸을 거부하면 러너가 멈춘다(`job551` 머리 주석).

## 4. 판정 기본값 (회차마다 주행 전에 선언 — 11-11 §5 판)
- ① 8 목표 `SUCCEEDED`(4 번째는 `SUCCEEDED_XY`) · ABORT 0 · nav_guard 취소 0 — 러너 원문.
- ② 접촉 0 — **사용자 관찰**(bag 의 접촉 분석은 출발 상자만 보는 보조).
- ③ 주행 중 TF 외삽 실패 0 — 회수한 Nav2 로그의 `extrapolation` · `Extrapolation` 줄. 첫 목표 시각 전(Nav2 설정 중) 줄은 따로 적고 세지 않는다(11-11 §5.1).
- ④ 사람 개입 0(밀기 · 들기 · 수동 정지 · 경로 막기) — 있으면 그 회차는 '반복 완주' 에서 빼고 따로 적는다(실패로 세지 않음).
- 참고(합불 아님): 총 시간(f2tt1 412.2 · f2tt2 413.7 · f2rr1 434.4 s) · 막힘 정지 · 탈출 동작 횟수 · 1 s 넘는 정지 · 출발 상자 옆 최소 여유.
- **표준 갱신 규칙**: 구성을 바꾸면 그 조합으로 ① ~ ④ 를 통과한 주행 이름이 생길 때까지 '미검증'. CURRENT_STACK 의 '표준' 은 같은 구성 연속 3 회 뒤에 바꾼다(README §2.2, 11-10 §9 · 11-11 §5.2).
- 지금 기준선: **f2tt1(10-27) · f2tt2(10-28) · f2rr1(11-11)** — 표준 구성 연속 3 회, 전부 8/8 · 주행 중 TF 실패 0 · 접촉 0. B0(NavFn) 대조 = 태그 `navfn-baseline-20261023` · `PLANNER=navfn`.

## 5. 운영 규칙 (게이트가 못 잡는 것)
1. **주행은 사용자의 "시작" 지시로만.** 게이트 통과 = 준비 완료이지 주행 허가가 아니다.
2. 손으로 로버를 옮겼으면 반드시 prep. **오래 세워 둔 스택(정지 수십 분)도 출발 전 prep** — 정지 중 odom yaw 가 돌아간다(10-28 §16.1, 43 분에 +16.6°).
3. 주행 30 s 전 DDS 참여자 생성 · 소멸 금지(§2-5).
4. **Wi-Fi 재연결 뒤엔 스택 전체 재기동**(prep) — 떠 있던 DDS 노드가 CPU 를 2~3 배 쓴다(09-23 n62b).
5. 카메라 설정(프로젝터 상시 끔 · 깊이 프리셋 3 · 점군 `camera_pointcloud:=keep`)은 표준 prep 값 그대로 둔다 — 바꾸면 그 조합은 '미검증'(§4). 점군은 지금 순회의 장애물 층 입력이 아니다(nvblox 는 깊이 영상, 점군은 상자 코스 게이트 · STVL 용, `navigation.launch.py` 176~178 행).
6. **`mppi_viz:=true` 쓰지 않는다** — 궤적 발행 206 kB 로 통신이 포화돼 Nav2 가 멈춘다(10-12, 6/6). 표준은 `lite`.
7. **실행 중 코스트맵 풋프린트 · 패딩을 바꾸지 않는다**(`pad_relief` 켜지 않음). 바꿨다면 주행 전 prep 으로 재기동(10-14, 멈칫 A/B 확정).
8. 판정 기준은 주행 **전에** SUMMARY 에 선언. 사후 변경은 새 § 로 남긴다.
9. 러너 인자 `STAGE` · `NOTE` · `GIT_HEAD` 필수 — 개선 전후를 같은 코스 · 같은 토픽으로 비교하기 위해. 기본 기록 토픽은 줄이지 않고 더할 것만 `EXTRA_TOPICS_ADD` · `BAG_COLOR` 등으로(§6).
10. 거리 기준(차체 외곽 / base_link / 칸 가장자리)을 문장마다 적는다. 위치 비교는 map 좌표로 하되, map 은 SLAM 보정으로 회차마다 몇 cm 다를 수 있다.
11. GB 급 bag(컬러 기록 등)은 바로 지우지 않는다: 시각화 → 사용자가 짚는 부분 분석 → 기록 → 사용자 확인 뒤 삭제(README §6).

## 6. 산출물 (회차당)
| 파일(PC `bags/f0_<이름>/` → 그날 폴더로) | 내용 | 생성 |
|---|---|---|
| `bag_<이름>.tgz` | 기본 토픽: `/tf` · `/tf_static` · `/map` · `/scan` · `/plan` · `/plan_smoothed` · 로컬/전역 코스트맵 · `/odometry/filtered` · `/wheel_odom` · `/cmd_vel` · `/rover/status` · `/battery` · `/rover/stuck` · `/imu/data` + `BAG_PROFILE=nvblox` 의 `/nvblox_node/static_map_slice` + `LONG_REC=1` 의 `/trajectories` · `/transformed_global_plan` + 래퍼 추가 `/odometry/ekf_a` · `/odom_rf2o` · `/odom_rf2o/gated`. 선택: `BAG_DEPTH=1` 깊이 · `BAG_COLOR=1` 컬러(+깊이, 11-13 — GB 급). bag 안에 `run_meta.txt`(인자 · 토픽 · 배포 sha256) · `params.txt`(실행 파라미터) | `job551` · `job453` · `job451` |
| `f0_<이름>.log` | 러너 원문(게이트 · 목표별 결과 · 시간) | `job551` · `job550` |
| `<이름>.csv` | 10 Hz: map · odom · 휠 yaw · 지령 · map→odom | `job550` |
| `tegra_<이름>.log` · `top_<이름>.log` · `proc_<이름>.log` · `rss_<이름>.txt` · `net_<이름>.log` | GPU/전력/온도 · CPU · 프로세스별 · 메모리 · 네트워크 | `job551` |
| Nav2 로그(Jetson `/tmp/nav2.log`) | 막힘 정지 · 탈출 · 계획 실패 · TF 줄 — §4 ③ 의 근거, 직접 회수 | prep 이 띄운 Nav2 |
- 기록 토픽을 바꾸면 bag 만으로 판정 지표를 다시 낼 수 있는지 먼저 묻고, 용량 증가 · STAGE 표기를 함께 적는다(Phase 전환 체크리스트, 유지).

## 7. 알려진 미해결 (이 판을 쓸 때 열려 있는 것)
- **서쪽 통로 남쪽 교착(11-13 f2rd2, 목표 5 에서 nav_guard 취소)**: 남쪽 끝 반바퀴 중 막힘 정지 → Smac 실패(`Starting point in lethal space`) → NavFn 원경로가 꺾임을 따라가지 않음 → 탈출 동작은 외곽 여유 13.9 cm 를 보고 '괜찮음' → 진행 검사(25 s) 재시도 중 nav_guard(45 s) 취소. 수정 계획 `Docs/debug_log/2026-11-13/SUMMARY.md` §9(미구현). 배치가 좁을 때 재현될 수 있다 — 그 회차는 ① 불합격으로 센다.
- 러너 본체(`run_f0.sh` 등)는 PC 스크래치패드에 있고 저장소에는 날짜별 사본만 있다(§2-0). TODO(improve): 러너를 `Docs/tools/` 상시 도구(`run_` 앞머리)로 옮길지 결정.
- 러너 목표 방향은 NavFn 경로 끝에서 구한다(`path_end_yaw.py`, `planner_id GridBased`) — Smac 표준과 어긋남(`smac-hybrid-adoption` P2 미해결).

## 8. 변경 이력
- v3.0.1 2026-11-23: §5-11 의 '사람이 찍힌 영상 · 사진은 git 제외 폴더에만' 삭제 — 사용자 결정(사람 노출은 고려사항에 두지 않음). 근거 `Docs/debug_log/2026-11-23/SUMMARY.md` §2.
- **v3.0 2026-11-19**: F2 순회(no5) · 표준 prep 판. §0 검토표, §1 코스(office_v3 · 목표 8 · 출발 상자), §2 절차(prep_patrol → run_f2c → run_f0 → job551), §3 게이트(prep · 위치 · A · B · J · C · G2 · P · I), §4 판정 기본값(11-11 §5), §5 운영 규칙, §6 산출물, §7 미해결. 상자 코스 · F0-a 는 v2.3 원문(커밋 `8c225597`)으로. 근거 `Docs/debug_log/2026-11-19/SUMMARY.md` §4 · §5.
- v2.3 2026-09-28: §7 F0-a 왕복 절차 추가(목표 `p`, 판정기 xy 0.15·yaw 0.35, 포크 SLAM·C++ 컨디셔너, 원래 방향 복귀 제외). 근거 `Docs/debug_log/2026-09-28/SUMMARY.md §13~21`.
- v2.2 2026-09-23(N6-2): 게이트 M·N 추가, 운영 규칙 13(Wi-Fi 재연결 뒤 재기동)·14(점군 유지)·15(러너 재고정 0.06). 근거 `Docs/debug_log/2026-09-23/SUMMARY.md §1~13`.
- v2.1 2026-09-22 저녁(N6-0): 모드 선택을 launch 인자 `camera_layer`(기본 nvblox)로, nvblox 기동·정리를 `nvblox.launch.py`/`nvblox_up.sh` 로 자동화. 근거 `2026-09-22/SUMMARY.md §4`.
- v2.0.1 2026-09-22 저녁: N5 결정(로컬 층 nvblox 채택) 반영, 게이트 L 문턱 ≥ 8 정정. 결과 요약 `Docs/05_nvblox/PHASE_N_RESULTS.md`.
- v2.0 2026-09-22: Phase N 판(게이트 J·K·L, bag 프로파일). 근거 `Docs/debug_log/2026-09-21/SUMMARY.md §9~10`, `2026-09-22/SUMMARY.md §0~1`.
- v1.0 2026-09-21: 09-11~09-21 규칙 통합. 기준선 `Docs/debug_log/2026-09-21/BASELINE_STVL.md`, 러너 원본 `Docs/debug_log/2026-09-21/jobs/`.
