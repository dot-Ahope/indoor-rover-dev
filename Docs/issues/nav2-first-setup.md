# Nav2 첫 구축과 첫 벤치마크 (RPP · MPPI)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **해결**(기동 · 점대점 · 회전 목표) · 컨트롤러 선택은 **이후 시기로 넘어감** | 09-02 ~ 09-03 (이 카드), 이후 09-07 ~ | [09-02 「Nav2 도입 — 첫 자율주행 성공」(L128)](../debug_log/2026-09-02/SUMMARY.md) | `ros2_ws/src/rover_navigation/`(신규: `config/nav2_params.yaml` · `launch/navigation.launch.py` · `package.xml` · `CMakeLists.txt`) · `config/nav_to_pose_no_spin.xml`(09-03 신규) | [기동 데드밴드](start-deadband.md) · [스톨 래치 × 승격](stall-latch.md) · [라이다 근접 사각](near-wall-blindspot.md) |

**한 줄**: 09-02 에 `rover_navigation` 패키지를 새로 만들어 Nav2(navigation2 1.1.20)를 slam_toolbox 위에 올렸다. 직진 0.5 m 는 첫 시도에 성공했지만, 180° 회전이 필요한 목표에서 로버가 80~100 초 동안 꼼짝 않는 문제가 나왔고, 원인은 두 겹이었다 — ① progress checker 가 제자리 회전을 '진행' 으로 안 봄(Simple → Pose 로 교체) ② RPP 의 각가속 제한이 첫 회전 명령을 0.05 rad/s 로 묶었는데 이 값이 로버의 기동 문턱 아래였음(`max_angular_accel` 1 → 4). 그 뒤 장애물 회피 · 좁은 곳 벤치마크(N1)는 RPP 0/1 · MPPI 0/2 로 실패했고, 공통 원인은 Nav2 설정이 아니라 **펌웨어 쪽 기동 데드밴드**로 판정돼 [데드밴드 카드](start-deadband.md)로 넘어갔다. 09-03 재벤치마크는 데드밴드를 고친 뒤 이번엔 **펌웨어 스톨 래치**에 막혀([스톨 래치 카드](stall-latch.md)) RPP 직진 1 회 성공만 유효 데이터로 남았다.

---

## 1. 증상
- 정면 0.5 m 목표: SUCCEEDED, 잔여 14.5 cm(허용 15 cm) — 실제 이동은 0.362 m 뿐(허용 오차 경계에서 '도달' 판정). 스크립트가 결과를 `UNKNOWN` 으로 찍음. [09-02 L152](../debug_log/2026-09-02/SUMMARY.md) · `outputs/job24b_goal.txt`
- 180° 회전 후 0.5 m 목표: 목표 수락 뒤 **81 초(1 차) · 99 초(재시도) 동안 heading 이 0.1° 도 안 변함**, 그 뒤 갑자기 90° 회전 — 회전시킨 것은 컨트롤러가 아니라 BT 의 `spin` 복구 동작. [09-02 L172](../debug_log/2026-09-02/SUMMARY.md) · `outputs/job25b_goal180.txt` · `job25f_goal180_retry.txt`
- 장애물 너머 1.7 m 목표: 우회 선회는 시작하지만 backup · spin 복구만 반복하다 ABORTED, 104.9 cm 남김. [09-02 L226](../debug_log/2026-09-02/SUMMARY.md) · `outputs/job27c_obstacle.txt`
- N1 벤치마크(장애물 우회): RPP ABORTED · MPPI 두 번 TIMEOUT(목표 23 cm 앞 정체 · 장애물 옆 배회). [09-02 L279](../debug_log/2026-09-02/SUMMARY.md)

## 2. 흐름 (시간순)
옛 SUMMARY 에는 § 번호가 없어 제목 글과 줄 번호(L)로 단다. 출력 파일은 모두 그날 `outputs/`.

| 날짜 · 제목 | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 08-31 (사전) | Nav2 설치 여부 확인 | navigation2 · mppi · rpp 패키지 설치됨, 후보판 1.1.20, `/cmd_vel` 구독자(보드) 1 | 패키지는 있음, `rover_navigation` 은 비어 있음 | `2026-08-31/outputs/job9a_nav2_check.txt`(도구 원본 없음) |
| 09-02 「구성」 L130 | `rover_navigation` 신규, AMCL · map_server 대신 slam_toolbox 가 map→odom · `/map` 제공. `nav2_bringup/navigation_launch.py` 를 우리 params 로 띄움 | — | 파라미터 근거 표(아래 §6.1) | 커밋 `76c08343` |
| 09-02 「기동 검증」 L147 | `job24a_nav2up.sh` | lifecycle 5 개 active · 로컬 코스트맵 1.667 Hz(설정 2.0) · 전역 0.667 Hz(설정 1.0) · load 7.13(6 코어), 상위 python3(=conditioner) 47 % · foxglove 27.5 % · rplidar 18.6 % | 기동 정상, CPU 빠듯 | `job24a_nav2up.txt` |
| 09-02 「첫 자율주행」 L152 | `job24b_goal.sh`(정면 0.5 m) | SUCCEEDED, 잔여 14.5 cm, 이동 0.362 m, heading −4.0° · 출력엔 `결과: UNKNOWN` | 성공. status 매핑 오류(4=SUCCEEDED) 수정 | `job24b_goal.txt` |
| 09-02 「B-1 1 차 시도」 L172 | `job25a_fullreset.sh` → `job25b_goaldir.sh 0.5 180` | 81 초 정지 → spin 으로 +89.6° · nav2.log 에 `Failed to make progress` 가 약 20 s 간격 4 번 | progress checker 가 회전을 진행으로 안 봄(**부분 원인**) | `job25a_fullreset.txt` · `job25b_goal180.txt` · `job25c_navdiag.txt`(도구 원본 없음) |
| 09-02 「원인 ①」 L177 | `SimpleProgressChecker` → `PoseProgressChecker`(`required_movement_angle 0.5`), `job25e_nav2start.sh` 로 재기동 · 확인 | `required_movement_angle` = 0.5 확인, plugin 조회는 타임아웃(load 6.91) | 이것으로 풀릴 것 | `job25e_nav2start.txt` |
| 09-02 같은 곳 | 재시도 `job25b_goaldir.sh`(타임아웃 약 120 s 로 추정) | 99 초 정지 → spin 으로 +89.5° — **안 풀림** | 진짜 원인은 따로 | `job25f_goal180_retry.txt` |
| 09-02 「부수 조치」 L214 | `job25g_diag2.sh` | nav2.log: `Failed to make progress` 4 · `Aborting handle` 4 · spin 1.57 · foxglove 종료 직후 load 4.53 | foxglove 끄면 CPU 확보(SUMMARY 는 6.9 → 3.4 로 적음 — 3.4 출력은 파일에 없음) | `job25g_diag2.txt` |
| 09-02 「원인 ②」 L182 | `job26a_goalmon.sh 0.5 180 70` — `/cmd_vel_nav`(RPP 출력)와 `/cmd_vel`(스무더 출력) 동시 감시 | **RPP w = +0.047~0.053 rad/s 가 68 초 내내 일정, 스무더도 같은 값, heading 176.9 → 176.4°** | RPP `rotateToHeading` 각가속 클램프 × 기동 데드밴드 = 데드락 | `job26a_goalmon.txt` |
| 09-02 「수정 후 결과」 L197 | `max_angular_accel` 1.0 → 4.0, 같은 목표 | t=2 s w=0.243 · t=24 s 에 v 등장 · **SUCCEEDED, 회전 +178.8°, 위치 오차 14.8 cm, 약 28 s** | 해결 | `job26b_goal180_fixed.txt` |
| 09-02 「B-2」 L220 | 정면 108 cm 장애물(폭 ~38 cm) 너머 1.7 m, `job27b_profile.sh` → `job26a_goalmon.sh 1.7 0` | 프로파일: ±10° 108~109 cm, −20~−30° 152 cm, +20° 248 cm. 주행: 우회 선회(−31.9°) → backup(v −0.05) → spin(w 0.6) → 각속도 진동 → **ABORTED, 104.9 cm** | Nav2 회피는 동작, 공간 부족 | `job27a_reset.txt` · `job27b_profile.txt` · `job27c_obstacle.txt` |
| 09-02 「inflation 축소」 L236 | 로컬 · 전역 inflation 0.35 → 0.20 | 치환 스크립트가 한 곳만 바꿈 → 설치본 확인 뒤 두 곳 반영 | 0.35 는 실내에서 과대 | 원천 소실(치환 도구 · 확인 출력 없음) |
| 09-02 「좁은 구석 탈출」 L241 | `job27b_profile.sh`(2 차) · `job21c_where.sh` → 사용자 지적 "뒤는 넓다" → `job26a_goalmon.sh 1.0 180` | 직진 경로 14 cm, 정면 42 · 좌30 41 · **후면 172** · 우90 47 cm(최근접 41 > 스윕 30) → 후방 1.0 m **SUCCEEDED, 회전 +166°, 14.5 cm, 32 s** | 갇힌 게 아님 — **내가 막힌 방향을 목표로 준 것**(§5 실수 ①) | `job27d_profile2.txt` · `job27e_360.txt` · `job27f_escape.txt` |
| 09-02 「마무리」 L256 | `NAV2_EXPLORATION_PLAN.md` 작성(P1~P7 진단 · N1~N5) | — | N1 = 좁은 곳 신뢰성 최우선 | 계획 문서(당시 `Docs/NAV2_EXPLORATION_PLAN.md`) |
| 09-02 「N1 사전 작업」 L261 | RPP `allow_reversing: true` · MPPI 를 `FollowPathMPPI` 로 병렬 구성 | controller_server 에 두 컨트롤러 Created/Configured | 전환은 블록 이름 맞바꿔 재기동 | `job28a_mppi_verify.txt`(도구 원본 없음) |
| 09-02 「N1 벤치마크 1 차」 L279 | `job25a_fullreset.sh` → `job27b_profile.sh` → RPP `job26a_goalmon.sh 1.6 0` | 코스: 정면 97 cm 장애물, 우 136~176 · 좌 275 cm 트임. **RPP ABORTED 56 s, 92.6 cm**(inflation 0.20) | RPP 0/1 | `job29a_reset.txt` · `job29b_course.txt` · `job29c_rpp_run1.txt` |
| 09-02 같은 곳 | MPPI 로 바꿔 `job30_goalabs.sh 0 0 0 150`(복귀) | 후진 v −0.05 로 실사용, 통과 · **t≈93~147 s 동안 0.23 m 남기고 v −0.01 반복, TIMEOUT 23.4 cm** | 목표 근접 미세 명령 정체 | `job30a_mppi_return.txt` |
| 09-02 같은 곳 | MPPI `job30_goalabs.sh 1.6 0 0 150`(전진) | t≈45 s 부터 (0.71~0.76, −0.40~+0.08) 근처에서 heading −75~−110° 를 오가며 배회, **TIMEOUT 87.4 cm**. 사용자: 이 사이 앞 벽에 붙어 회전 · 헛돎 | 미세 명령(±0.01~0.05)이 실행 안 돼 같은 자리 재최적화. 접촉은 [사각 카드](near-wall-blindspot.md) | `job30b_mppi_fwd.txt` |
| 09-02 「판단」 L291 | `xy_goal_tolerance` 0.15 → 0.25(임시) · `footprint_padding` 0.02 → 0.05 · 펌웨어 승격 소스 작성(플래시 대기) | — | **공통 근본 원인 = 기동 데드밴드, 컨트롤러 튜닝으로 해결 불가.** N1 게이트는 펌웨어 보상 뒤에만 | 커밋 `76c08343` |
| 09-02 마감 | `job31_shutdown.sh` | 'agent 종료됨' · 남은 노드 목록에 nav2 · slam 노드가 그대로 찍힘 | 종료 완료로 판단(목록은 데몬 캐시로 **추정**, 미확인) | `job31_shutdown.txt` |
| 09-03 「다음」 L30 · 「오후 세션 경과」 L39 | 펌웨어 승격(0.020) 플래시 뒤 `xy_goal_tolerance` 0.15 복원 · Nav2 재기동(`job25e_nav2start.sh`) | **`inflation radius (0.200) is smaller than the computed inscribed radius (0.215)` ERROR 2 건(로컬 · 전역), bt_navigator 미기동** | 패딩 0.05 로 내접반경이 바뀐 것(§5 실수 ③) → inflation 0.25 | `2026-09-03/outputs/job34b_nav2_space.txt` |
| 09-03 같은 곳 | inflation 0.25 · `job34c_verify.sh` · `job21c_where.sh` · `job27b_profile.sh` | FollowPath = MPPI · tolerance 0.15 · inflation 0.25 · bt_navigator active · 복도 정면 228 cm, 좌우 62~63 cm(중심 기준) | 준비 완료 | `job34c_nav2fix_space.txt` |
| 09-03 같은 곳 | MPPI Run 1 `job30_goalabs.sh 1.6 0 0 150` | 0~30 s v 0.05(최대의 절반) · w +0.04 로 계속 좌회전(직선 목표인데 y 0.38 m 이탈) · t≈48 s 부터 (1.14, 0.38) 에서 v −0.02 · w −0.20 을 100 초 반복, **무반응. TIMEOUT 59.5 cm** | 원인 = 펌웨어 스톨 래치(level 2) — [스톨 카드](stall-latch.md). 좌회전 경향의 원인은 **추정**(복도 우측이 좁아 비용 기울기 · 회전 슬립) | `job34d_mppi_run1.txt` · `job34e_stuckdiag.txt` |
| 09-03 「조치 · 계획」 L53 | RPP 로 전환 + Spin 제거 BT(`nav_to_pose_no_spin.xml`) · 보드 리셋 뒤 `job35a_prep.sh` | FollowPath = RPP · BT = `nav_to_pose_no_spin.xml` · inflation 0.25 · 설정 오류 0 · `/rover/status` OK | 벽 근접 실패 때 spin 이 접촉을 부른 2 건 근거 | `job35a_prep.txt` |
| 09-03 「벤치마크 재개 결과」 L61 | RPP Run 1 `job30_goalabs.sh 1.6 0 0 150` | **SUCCEEDED 20 s, 오차 14.9 cm**, v 0.10 유지, heading ±2° 안 | RPP 직선 우수(유효) | `job35b_rpp_run1.txt` |
| 09-03 같은 곳 | RPP Run 2 `job30_goalabs.sh 0 0 180 150` | 180° 회전 약 21~24 s 로 성공 → 주행 중 선회에서 멈춤, backup 은 `Collision Ahead` 로 거부, **TIMEOUT 122 cm**, `/rover/status` level 2 | 스톨 래치 — 선회 포함 비교는 펌웨어 수정 뒤로 | `job35c_rpp_run2.txt` · `job35d_diag.txt`(도구 원본 없음) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 회전 목표 정지 = progress checker 가 회전을 진행으로 안 봄 | Pose 로 바꾸고 같은 목표 재시도 | 99 초 정지 그대로(`job25f`) | **부분 지지** — 실패 주기(약 20 s 마다 abort)는 이것이 만들었지만 '안 움직임' 은 설명 못 함 |
| 컨트롤러는 명령을 내는데 중간(스무더)에서 사라짐 | `/cmd_vel_nav` 와 `/cmd_vel` 동시 감시 | 두 값이 같음(0.05) | **기각**(`job26a`) |
| 첫 각속도 명령이 기동 문턱 아래 | 클램프 식 1.0 × 0.05 s = 0.05 rad/s 와 관측값 비교, accel 4.0 으로 재시험 | 관측 0.047~0.053 = 예측 0.05. 4.0 에서 첫 명령 0.243 · 즉시 회전 | **지지 · 확인**(`job26a` → `job26b`) |
| 장애물 회피 실패 = inflation 0.35 가 통로를 지움 | 0.20 으로 N1 Run 1 | 여전히 ABORTED(92.6 cm) | **기각(주원인 아님)** — 09-02 SUMMARY 「판단」 L291 |
| 목표 근접 정체 = 허용오차가 너무 좁음 | 0.15 → 0.25 | 근접 정체는 완화, 중간 배회는 그대로 | **부분**(임시 완화로만 유지, 09-03 복원) |
| 좁은 곳 실패의 공통 원인 = 기동 데드밴드(미세 명령 무반응) | RPP · MPPI 출력이 0.01~0.05 급일 때 위치 불변 · 펌웨어 승격 뒤 재시험 | 09-03 승격 뒤 미세 명령 실행 확인(데드밴드 카드) — 그러나 재벤치마크는 스톨 래치로 중단 | **지지**(재벤치마크 결론은 이후 시기) |
| MPPI 가 RPP 보다 좁은 곳에 강하다 | 같은 코스 A/B | 09-02: MPPI 후진 · 통과 확인, 결과는 둘 다 실패. 09-03: 래치로 비교 불가 | **미확인**(09-07 · 09-18 이후 시기) |

## 4. 조치와 효과
| 바꾼 것 | 전 → 후 | 효과(측정) | 한계 · 메모 |
|---|---|---|---|
| progress checker | `SimpleProgressChecker` → `PoseProgressChecker`, `required_movement_angle 0.5` rad | 회전만 하는 동안에도 abort 안 함(26b 성공으로 간접) | `movement_time_allowance` 는 09-02 표에 20 s, 커밋본은 25.0 — 바꾼 시점 · 근거 기록 없음(**미확인**). 09-03 nav2.log 의 abort 간격 ≈ 25 s 로 25 가 적용된 것은 확인(`job34e`) |
| RPP `max_angular_accel` | 1.0 → 4.0 | 첫 명령 0.05 → 0.2 rad/s(계산) · 관측 0.243, 180° 성공 | 데드밴드 자체는 남음 → 펌웨어 승격으로 이어짐 |
| inflation(로컬 · 전역) | 0.35 → 0.20(09-02) → **0.25**(09-03) | 0.20 으로는 N1 Run 1 실패 그대로. 0.25 는 '내접반경 이상' 오류 해소 목적 | 이후 0.35 ↔ 0.22 등 여러 번 오감(09-08 커밋들, 다음 시기) |
| `footprint_padding` | 0.02 → 0.05 | 근접 사각 완화 목적([사각 카드](near-wall-blindspot.md)) | 내접반경 0.165 → 0.215 → inflation 오류 유발(§5 실수 ③). 09-08 0.02, 현재 0.01(다음 시기) |
| RPP `allow_reversing` | false → true | 실효 거의 없음(NavFn 경로에 후진 꺾임이 없음 — 설정 주석 자체가 명기) | 후진 기동은 MPPI(`vx_min −0.08`)가 담당 |
| MPPI 병렬 구성 | 없음 → `FollowPathMPPI` | 두 컨트롤러 로드 확인(`job28a`) · 실제 후진(v −0.05) 사용 확인(`job30a`) | 전환 = 블록 이름 맞바꿔 재기동(BT 의 `controller_id="FollowPath"` 고정이라) |
| `xy_goal_tolerance` | 0.15 → 0.25(09-02 임시) → 0.15(09-03 복원) | 근접 정체만 완화 | — |
| BT | 기본 → `nav_to_pose_no_spin.xml`(Spin 제거, BackUp 0.15 m · 0.05 m/s, Wait 5 s) | RPP Run 1 성공 · Run 2 는 래치로 판단 불가 | 09-11 커밋들에서 BT 를 다시 손봄(다음 시기) |

## 5. 내 실수
### 실수 ① 막힌 방향으로 목표를 주고 '갇혔다' 로 읽음 (09-02 「좁은 구석 탈출」 L241)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 장애물 회피 시험. `job26a_goalmon.sh 1.7 0`(정면 1.7 m)으로 ABORTED 뒤, 로버가 구석에 들어간 상태에서 다음 행동을 정함 |
| 본 것 | `job27d_profile2.txt`: 직진 경로 최근접 **14 cm**, ±10~50° 41~51 cm. 정면만 보는 프로파일이었음 |
| 처음 추론 | 좁은 구석에 갇혔다 — Nav2 가 탈출을 못 한다(기록상 사용자 질문 "갇힌 상태에서 탈출하지 못하는가?" 가 이 추론에 대한 반문) |
| 의심한 이유 | 사용자: "지금 뒤로는 공간이 넓은 상태잖는가." 정면 ±70° 만 재는 `job27b_profile.sh` 는 뒤쪽을 원천적으로 못 봄 |
| 판별 | 전 방위 `job21c_where.sh`(`job27e_360.txt`): 후면 172 cm, 최근접 41 cm > 스윕 30 cm → 회전 가능. 후방 1.0 m 목표(`job27f_escape.txt`) SUCCEEDED |
| 결론 | 실패 원인은 Nav2 가 아니라 **내가 막힌 방향을 목표로 준 것**. 복구 동작 반복 후 포기는 Nav2 의 정상 동작 |
| 다음에 알아보는 법 | 목표를 주기 전에 **전 방위**(`job21c_where.sh` 형) 여유와 목표 방향 통로 폭(로버 폭 33 cm + 양쪽 여유, 기록 권장 50~60 cm)을 먼저 본다. 정면 프로파일만으로 '갇힘' 을 말하지 않는다 |
| 데이터 | `2026-09-02/outputs/job27c_obstacle.txt` · `job27d_profile2.txt` · `job27e_360.txt` · `job27f_escape.txt`, 도구 `jobs/job26a_goalmon.sh` · `job27b_profile.sh` · `job21c_where.sh` |

### 실수 ② 치환 스크립트가 한 곳만 바꿈 (09-02 「inflation_radius 축소」 L236)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | `nav2_params.yaml` 의 `inflation_radius` 0.35 → 0.20 을 로컬 · 전역 두 곳에 적용 |
| 본 것 | 치환 뒤 확인에서 한 곳만 바뀜(어느 쪽이었는지는 기록 없음) |
| 처음 추론 | 치환 한 번으로 두 블록 모두 바뀌었다고 가정 |
| 의심한 이유 | 적용 뒤 확인(SUMMARY: "확인 후 두 곳 모두 반영(설치본까지 검증)") |
| 판별 | 소스 · 설치본(`install/.../nav2_params.yaml`) 양쪽에서 값 확인 |
| 결론 | 1 차 적용 실패 → 두 곳 모두 고침 |
| 다음에 알아보는 법 | 같은 키가 여러 블록에 있는 YAML 은 치환 뒤 `grep -n 키` 로 **개수**를 세고, 실행 중 노드에서 `ros2 param get` 으로 두 노드(`/local_costmap/local_costmap` · `/global_costmap/global_costmap`) 모두 확인한다(09-03 `job34c_verify.sh` 는 로컬만 본다 — 같은 함정). 이후 시기의 'prep 의 sed -i 가 설치본 링크를 끊음' 문제와 같은 계열 |
| 데이터 | **원천 소실** — 치환 도구와 확인 출력은 대화에만 있었음 |

### 실수 ③ 패딩을 키우고 내접반경을 다시 계산하지 않음 (09-02 마감 → 09-03 「경과」 L39)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 근접 사각 완화로 `footprint_padding` 0.02 → 0.05(09-02 저녁) |
| 본 것 | 09-03 기동 로그: `The configured inflation radius (0.200) is smaller than the computed inscribed radius (0.215)` ERROR 2 건, `bt_navigator 미기동` |
| 처음 추론 | (09-02 inflation 절) "로버 내접반경 0.165 보다는 크게" — 패딩을 빼고 계산한 내접반경을 기준으로 삼음 |
| 의심한 이유 | Nav2 가 직접 0.215 를 계산해 경고 |
| 판별 | 0.165(반폭) + 0.05(패딩) = 0.215 > 0.20 — 산술로 바로 확인 |
| 결론 | inflation 0.25 로 올림(`job34c` 에서 bt_navigator active) |
| 다음에 알아보는 법 | 풋프린트 · 패딩을 바꾸면 **내접반경 = 반폭 + 패딩** 을 다시 계산해 inflation 과 견준다. 기동 직후 nav2.log 의 `ERROR` 줄 수를 0 으로 확인(09-03 `job35a_prep.sh` 의 '설정 오류: N건' 이 이 교훈으로 생김) |
| 데이터 | `2026-09-03/outputs/job34b_nav2_space.txt` · `job34c_nav2fix_space.txt`, 도구 `2026-09-02/jobs/job25e_nav2start.sh` · `2026-09-03/jobs/job34c_verify.sh` |

## 6. 남은 것 (09-03 시점)
- 컨트롤러 결정(N1 게이트 5/5) — 스톨 정책 펌웨어 검증 뒤로 미룸. **이후(09-04 ~): 다음 시기에서 채움** — 09-07 RPP 채택(커밋 `c851cb4c` 제목 "RPP 채택 (MPPI 2전 2패)") → 이후 MPPI 로 돌아가 09-21 CostCritic 채택(CLAUDE.md §6).
- MPPI Run 1 의 지속 좌회전(직선 목표에서 y 0.38 m 이탈) — 원인 추정만 있음.
- RPP Run 2 래치 직전 t≈39~75 s: 지령 v 0.06~0.10 · w +0.03~+0.29(반시계)인데 위치는 약 9 cm 만 움직이고 heading 은 +176.6 → +157.7°(**시계 방향**) — 지령과 반대 방향 회전. 기록에 해석 없음, 휠별 텔레메트리가 없던 때라 판별 불가(**미확인**). `job35c_rpp_run2.txt`
- BackUp 의 `Collision Ahead` 거부 이유(뒤 110 cm 여유) — **미확인**. `job35d_diag.txt`
- CPU: 코스트맵 발행률이 설정의 1/2~2/3, `Control loop missed its desired rate of 20.0000Hz` 경고(`job25c_navdiag.txt`). foxglove 끔으로 일부 확보. 계획 §5 는 'MPPI 저속 사양 10 Hz' 를 권했지만 09-03 설정은 20 Hz 그대로.
- velocity_smoother `deadband_velocity: [0,0,0]` — 스무더 단에서 데드밴드를 다룰 수 있는 파라미터였지만 검토한 기록 없음.

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| 첫 주행(정면 0.5 m) | SUCCEEDED 14.5 cm | 09-02 L152, `job24b_goal.txt` |
| B-1 (180° + 0.5 m) | 1 차 · 재시도 실패 → accel 4.0 뒤 성공 | 09-02 L170~, `job25b_goal180.txt` · `job25f_goal180_retry.txt` · `job26a_goalmon.txt` · `job26b_goal180_fixed.txt` |
| B-2 (장애물 너머 1.7 m) · 탈출 | ABORTED · 후방 탈출 성공 | 09-02 L220~, `job27c_obstacle.txt` · `job27f_escape.txt` |
| N1 Run 1~3 (09-02) | RPP ABORTED · MPPI TIMEOUT 2 | 09-02 L279, `job29c_rpp_run1.txt` · `job30a_mppi_return.txt` · `job30b_mppi_fwd.txt` |
| 09-03 MPPI Run 1 · RPP Run 1 · 2 | 래치 · 성공 · 래치 | 09-03 L39 · L61, `job34d_mppi_run1.txt` · `job35b_rpp_run1.txt` · `job35c_rpp_run2.txt` |
| 도구 | `job24a_nav2up.sh` · `job24b_goal.sh` · `job25a_fullreset.sh` · `job25b_goaldir.sh` · `job25e_nav2start.sh` · `job25g_diag2.sh` · `job26a_goalmon.sh` · `job27b_profile.sh` · `job21c_where.sh` · `job30_goalabs.sh` · `job31_shutdown.sh` · `job20a_boot.sh` (09-02 `jobs/`) · `job34c_verify.sh` · `job34e_stuckdiag.sh` · `job35a_prep.sh` · `job33a_reset_noagent.sh` (09-03 `jobs/`) | 아래 §8 |
| 원본 없는 출력 | `job25c_navdiag.txt` · `job28a_mppi_verify.txt` · `job35d_diag.txt` · 08-31 `job9a_nav2_check.txt` | 도구는 원천 소실(대화 안에서 즉석으로 쓰고 저장 안 함) |

---

## 8. 도구 해설
### 8.0 이 시기 도구 공통 사항
- **실행 위치와 부르는 법**: 전부 Jetson 에서 돈다. PC 의 Claude 스크래치패드에 쓴 스크립트를 WSL(`Ubuntu-22.04`) + `sshpass` 로 Jetson `/tmp/` 에 복사하고 `bash /tmp/jobXX.sh 인자` 로 불렀다(08-26 「판단·결정」 에서 확립한 패턴). 복사 · 호출을 하던 감싸개 스크립트는 **저장 안 됨(원천 소실)**. 그 흔적: 출력 첫 줄의 깨진 `wsl: …` 한 줄(WSL 의 localhostForwarding 경고가 인코딩이 깨져 찍힌 것), 09-03 `job34a_boot.txt` 의 `cp: -r not specified; omitting directory '…/82ce61d4-…/scratchpad/'` · '스크립트 재전송 완료' · 'nav2_params 동기화' · colcon `Summary: 1 package finished` 줄. 즉 감싸개가 **스크립트 재전송 → nav2_params 를 Jetson 소스로 복사 → colcon 빌드**까지 했다(SSH 비밀번호는 기록에서 `<PW>`).
- **출력 저장**: 대화에 찍힌 화면 출력을 그대로 `outputs/<job>_<설명>.txt` 로 옮겼다. 그래서 한 출력 파일에 여러 스크립트의 결과가 섞여 있다(예: `job34c_nav2fix_space.txt` = `job25e` + `job34c_verify` + `job21c_where` + `job27b_profile`). 한 스크립트를 여러 번 불렀으면 출력 이름이 다르다(`job26a_goalmon.sh` → `job26a/26b/27c/27f/29c` 출력).
- **공통 결함 ①: '무발행' 대체 문구가 절대 안 찍힘.** `timeout 5 ros2 topic hz T | grep -aoE "average rate…" | head -1 || echo "무발행!"` 형태는 파이프 전체의 종료 코드가 마지막 `head` 의 것(성공 0)이라 `||` 뒤가 실행되지 않는다. **빈칸 = 무발행 · 실패** 로 읽어야 한다. 증거: `job24a_nav2up.txt` 의 `/map` 칸이 비어 있고 다음 줄이 이어 붙음, `job25c_navdiag.txt` 의 `/plan:` · `load:` 빈칸, 09-03 `job32c_min012.txt` 의 '보드 재연결:' 빈칸.
- **공통 결함 ②: 라이다 장착 상수 `LX=0.152, LYAW=π`.** 라이다가 차체 중심 +15.2 cm, 180° 돌려 달린 것을 반영. 09-18 에 데크가 −2.68° 틀어진 것이 발견돼 URDF 는 `π−0.04677` 로 바뀌었지만 이 시기 도구들은 그 전이라 보정이 없다 → 1 m 거리에서 옆으로 약 4.7 cm 어긋남(계산 = tan 2.68° × 1 m). 거리값(중심 기준 최소거리)에는 영향이 작고 방위에만 영향.
- **공통 결함 ③: 노드 생성 직후 주행.** 목표 전송 도구들은 노드를 만들자마자 목표를 보낸다. 지금 운용 규칙(CLAUDE.md §6: 주행 30 s 전 DDS 참여자 생성 금지, 09-21 경)과 맞지 않는다 → 지금 그대로 쓰지 않는다.
- **공통 계산**: 스캔 점 `r` (0.05 < r < 12, 유한값)을 `θ = 각 + π`, `x = 0.152 + r·cosθ`, `y = r·sinθ` 로 base_link 좌표로 옮기고, `dc = hypot(x, y)` = **차체 중심에서의 거리**를 쓴다. 회전 스윕 반경 `SWEEP = hypot(0.25, 0.165) = 0.2995 m`(직사각 0.5 × 0.33 의 반대각선). 5 장의 스캔을 합쳐 한 번에 본다.

### 8.1 `job24a_nav2up.sh` — Nav2 기동 + 검증(주행 없음)
- 위치 · 형태: Jetson, 인자 없음. [`../debug_log/2026-09-02/jobs/job24a_nav2up.sh`](../debug_log/2026-09-02/jobs/job24a_nav2up.sh)
- 왜: 새로 만든 `rover_navigation` 이 실제 로버 스택 위에서 뜨는지 — Nav2 의 전제(odom · scan · map · map→odom)가 다 있는지부터.
- 하는 일: ① `/wheel_odom` · `/odometry/filtered` · `/scan` · `/map` 각각 `ros2 topic hz` 5 s ② `tf2_echo map odom` 의 Translation 한 줄 ③ Nav2 관련 프로세스 9 종 `pkill -f` 후 2 s ④ `setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log` ⑤ 25 s 대기 ⑥ `ros2 node list` 에서 Nav2 노드 ⑦ 5 개 노드 `ros2 lifecycle get`(6 s 제한) ⑧ `/local_costmap/costmap` · `/global_costmap/costmap` hz 8 s ⑨ nav2.log 에서 `error|fail|exception|refus` 마지막 8 줄 ⑩ `/proc/loadavg` + `top -b -n2 -d1 -o %CPU` 두 번째 표본 상위 6.
- 출력: `job24a_nav2up.txt` — 토픽 Hz(50.006 · 30.102 · 9.958 · `/map` 빈칸), map→odom (−0.116, 0.085), 노드 10, active 5, 코스트맵 1.667 · 0.667 Hz, 오류 없음, load 7.13.
- 쓰인 곳: 09-02 「기동 검증」 L147, 「관찰 · 다음 튜닝 후보」 L162(CPU).
- 계보 · 결함: 다음 판이 `job25e_nav2start.sh`(progress checker 확인 추가) → `job25a_fullreset.sh` 안에 흡수 → 09-03 `job35a_prep.sh` 로 묶임 → 이후 `prep_*` · `chk_prep.py` · `chk_drive_gate.py`(10 월). `/map` 은 갱신 때만 발행(0.5 Hz 안팎)이라 5 s 창에서 빈칸이 나올 수 있다 — 빈칸이 고장이라는 뜻은 아님. 지금 다시 쓰기: 기동 구조가 바뀌어(nvblox · 컨테이너 등) 그대로는 안 씀.

### 8.2 `job24b_goal.sh` — 첫 자율주행(정면 D m)
- 위치 · 형태: Jetson, `bash /tmp/job24b_goal.sh [D=0.5] [TMO=60]`. [`jobs/job24b_goal.sh`](../debug_log/2026-09-02/jobs/job24b_goal.sh)
- 왜: Nav2 가 '목표 하나' 를 끝까지 수행하는지 가장 단순한 형태로.
- 하는 일: rclpy 노드 `nav_goal`, TF 버퍼로 `map→base_link` 조회(최대 8 s 대기, 없으면 'slam 확인 필요'). 현재 자세 (x0, y0, θ0) 에서 `gx = x0 + D·cosθ0, gy = y0 + D·sinθ0`, 목표 자세 = 현재 쿼터니언 그대로. `navigate_to_pose` 액션 서버 10 s 대기 → `send_goal_async`(피드백 콜백에서 `distance_remaining` 저장) → 수락 확인 10 s. 결과가 나올 때까지 0.2 s 씩 돌며 **3 s 마다** 위치 · heading · 남은 거리 출력. TMO 넘으면 취소 + `/cmd_vel` 영 10 번(0.05 s 간격). 끝나면 1 s 뒤 자세로 이동 거리 · 목표까지 잔여 · heading 변화 계산, 판정 `err < 0.15` 면 '✅ 목표 도달'.
- 출력: `job24b_goal.txt` — 시작 (−0.117, 0.089) −7.3°, t=3 s 0.43 m · t=6 s 0.25 m 남음, `결과: UNKNOWN`, 잔여 14.5 cm, 이동 0.362 m.
- 쓰인 곳: 09-02 「첫 자율주행」 L152.
- 알려진 결함: ① **status 매핑**: 출력은 `UNKNOWN` 인데 SUMMARY 는 "action_msgs/GoalStatus 는 4=SUCCEEDED. 수정함" 이라 적었다. 저장된 파일에는 이미 `4:'SUCCEEDED'` 가 들어 있어 **저장본은 고친 뒤 판**으로 보인다(추정) — 처음 매핑이 무엇이었는지는 원천 소실. ② 판정이 Nav2 의 허용오차(15 cm)와 같은 문턱이라, '허용오차 경계에서 멈춤'(0.5 m 중 0.362 m 이동)과 '목표 도달' 을 구별 못 한다. ③ 피드백 첫 줄 `남은거리=nan`(피드백 오기 전).
- 계보: → `job25b_goaldir.sh`(방향 지정) → `job26a_goalmon.sh`(+명령 체인) → `job30_goalabs.sh`(절대 좌표). 지금 다시 쓰기: 안 씀(공통 결함 ③).

### 8.3 `job25a_fullreset.sh` — 손으로 옮긴 뒤 전체 재초기화
- 위치 · 형태: Jetson, 인자 없음. [`jobs/job25a_fullreset.sh`](../debug_log/2026-09-02/jobs/job25a_fullreset.sh)
- 왜: 시험마다 로버를 손으로 옮기면 EKF · SLAM 이 그 이동을 모른다 → 지도 · 좌표를 새 출발점에서 다시 시작해야 결과 좌표가 의미 있다. agent(보드 세션)는 건드리면 보드 리셋이 필요하므로 유지.
- 하는 일: ① Nav2 프로세스 종료 3 s ② `sensor_conditioner` · `ekf_node` · `slam_toolbox` 종료 → `ros2 launch rover_bringup ekf.launch.py`(로그 `/tmp/ekf.log`) 16 s(자이로 바이어스 캘리브 ~10 s, **로버 정지 필수**) → 로그의 `gyro bias` 줄 ③ `slam.launch.py` 12 s → `map→base_link` 한 줄(새 지도라 0,0,0 이어야 정상) ④ Nav2 재기동 25 s → lifecycle 5 개 · 로컬 코스트맵 hz ⑤ 공간 판정(파이썬): 중심 기준 최근접이 `SWEEP + 0.05 = 0.35 m` 보다 크면 '회전 OK', 그리고 정면 · 좌 90 · 후면 · 우 −90 의 ±20° 최소거리.
- 출력: `job25a_fullreset.txt`(09-02 오후 첫 회), `job27a_reset.txt`, `job29a_reset.txt` 가 같은 형식 — 예: 정면 204 · 좌 71 · 후면 132 · 우 57 cm.
- 쓰인 곳: B-1 · B-2 · N1 직전 초기화.
- 결함: lifecycle 조회가 부하로 `?` 를 낼 때가 있음(`job25a` 의 behavior_server, `job27a` 의 controller_server) — 실제로 안 떴는지와 구별 안 됨. SLAM 을 새로 시작하므로 **map 원점이 매번 그 자리로 다시 잡힌다** → `job30_goalabs.sh` 의 절대 좌표(0,0)는 '마지막 초기화 지점' 이다.
- 계보: 09-02 `job21a_reset.sh`(EKF+SLAM, Nav2 없음) → 이것(+Nav2) → 09-03 `job33a_reset_noagent.sh`(Nav2 뺌, agent 확인 강화) → 이후 prep 계열. 지금 다시 쓰기: 안 씀(conditioner · ekf.launch 구성이 바뀜).

### 8.4 `job25b_goaldir.sh` — 방향 지정 목표
- 위치 · 형태: Jetson, `bash /tmp/job25b_goaldir.sh [D=0.5] [ANG=180] [TMO=90]`. [`jobs/job25b_goaldir.sh`](../debug_log/2026-09-02/jobs/job25b_goaldir.sh)
- 왜: 회전이 필요한 목표(현재 heading 기준 ANG° 방향으로 D m, 목표 자세 = 진행 방향).
- 하는 일: `gθ = θ0 + ANG`, `gx = x0 + D·cos gθ`, 목표 쿼터니언 `z = sin(gθ/2), w = cos(gθ/2)`. 나머지는 `job24b` 와 같음(3 s 마다 위치 · heading · 남은 거리). 결과 코드 사전 0~6 전부 있음. 판정: 위치 < 15 cm **그리고** |자세 오차| < 14°(= yaw 허용 0.25 rad ≈ 14.3°).
- 출력: `job25b_goal180.txt`(81 s 동안 heading −0.6 → −1.1°, t=84 s 에 +36.5° → spin), `job25f_goal180_retry.txt`(99 s 정지 뒤 +177.7°, 타임아웃이 약 120 s 로 보임 — 인자는 기록 없음).
- 쓰인 곳: 09-02 「B-1 1 차 시도」 L172.
- 결함: 이 도구는 `/cmd_vel` 을 안 봐서 '명령이 0 인가, 명령은 나오는데 안 움직이는가' 를 구별 못 했다 → 그래서 `job26a` 가 생김. 지금 다시 쓰기: 안 씀.

### 8.5 `job25e_nav2start.sh` — Nav2 (재)기동 + progress checker 확인
- 위치 · 형태: Jetson, 인자 없음. [`jobs/job25e_nav2start.sh`](../debug_log/2026-09-02/jobs/job25e_nav2start.sh)
- 왜: progress checker 를 Pose 로 바꾼 뒤 실제로 그 플러그인이 올라왔는지 확인.
- 하는 일: Nav2 프로세스 종료 3 s → launch 25 s → lifecycle 5 개(실패 시 '미기동') → `ros2 param get /controller_server progress_checker.plugin` · `progress_checker.required_movement_angle`(각 8 s) → nav2.log 의 `error|exception|fail` 마지막 5 줄 → load.
- 출력: `job25e_nav2start.txt`(09-02: plugin 조회 실패 · angle 0.5 · load 6.91), 09-03 `job34b_nav2_space.txt`(plugin `nav2_controller::PoseProgressChecker` · **inflation < inscribed ERROR 2 · bt_navigator 미기동**).
- 쓰인 곳: 09-02 원인 ① 확인, 09-03 오후 기동, 09-03 「내일 할 일」 L88 의 정식 절차.
- 결함: 오류 grep 에 `get_state` · `get_parameters` 서비스 타임아웃 경고가 섞여 진짜 오류가 묻힘(09-03 `job34c_verify.sh` · `job35a_prep.sh` 에서 제외 필터 추가). 지금 다시 쓰기: 안 씀(→ `chk_prep.py`).

### 8.6 `job25g_diag2.sh` — 정지 구간 nav2.log 진단 + foxglove 종료
- 위치 · 형태: Jetson, 인자 없음. [`jobs/job25g_diag2.sh`](../debug_log/2026-09-02/jobs/job25g_diag2.sh)
- 왜: Pose 로 바꿔도 정지가 그대로라, 그 사이 Nav2 내부에서 무엇이 반복되는지와 CPU 가 원인인지.
- 하는 일: nav2.log 마지막 30 줄(`process started` 줄 제외) → 패턴 집계(`Failed to make progress` · `Aborting handle` · `missed its desired rate` · `Behavior … running/completed` · `No valid path` · `timed out` 등, `sort | uniq -c`) → `pkill -f foxglove` 3 s → load · top.
- 출력: `job25g_diag2.txt` — `Passing new path to controller` 약 1 s 마다, `Failed to make progress` → `Running spin` → `Turning 1.57` → `spin completed` → 다시 goal. 집계 4 · 4 · 2. foxglove 끈 직후 load 4.53.
- 쓰인 곳: 09-02 「B-1 1 차 시도」(spin 이 회전 주체), 「부수 조치」(foxglove 종료).
- 결함: 패턴 정규식의 `Behavior [A-Za-z]+ (running|completed)` 는 실제 로그 문구(`Running spin`, `spin completed successfully`)와 안 맞아 0 건 — spin 은 원문 30 줄에서만 보임. 지금 다시 쓰기: 안 씀(→ `Docs/tools/anal_navlog.py`, 10-12).

### 8.7 `job26a_goalmon.sh` — 목표 전송 + 명령 체인 감시 ★ 원인 ② 를 확정한 도구
- 위치 · 형태: Jetson, `bash /tmp/job26a_goalmon.sh [D=0.5] [ANG=180] [TMO=70]`. [`jobs/job26a_goalmon.sh`](../debug_log/2026-09-02/jobs/job26a_goalmon.sh)
- 왜: '로버가 안 움직이는 동안 명령은 나오고 있나, 나온다면 어디서 사라지나' — 컨트롤러 출력과 최종 출력을 동시에 봐야 갈린다.
- 하는 일: `/cmd_vel_nav`(컨트롤러 → velocity_smoother 입력)와 `/cmd_vel`(smoother 출력 → 보드)를 둘 다 구독해 마지막 (v, w) 와 받은 개수 n 을 저장. 목표는 `job25b` 와 같은 방식(현재 heading + ANG, D m). **2 s 마다** `hd | RPP(v w n) | OUT(v w n)` 한 줄. 결과 사전은 4 · 5 · 6 만(그 밖은 숫자). 끝에 회전량 · 위치 오차.
- 출력과 읽는 법: `job26a_goalmon.txt` — `RPP(v=+0.000 w=+0.050)` 와 `OUT(… w=+0.050)` 가 68 초 내내 같고 n 이 2 s 에 40 씩(= 20 Hz) 늘어남 → 컨트롤러는 20 Hz 로 0.05 를 내고, 스무더는 그대로 통과, 로버만 안 움직임. t=52~54 s 에 둘 다 0 이고 n 이 멈춘 구간은 progress checker abort 직후 BT 가 다시 경로를 받는 틈으로 보임(추정). `job26b_goal180_fixed.txt` — 첫 줄부터 w 0.243 · heading 변화.
  - 같은 도구의 다른 출력: `job27c_obstacle.txt`(RPP 0 인데 OUT v −0.050 = **BackUp 복구**, OUT w +0.600 = **Spin 복구**. 복구 동작은 behavior_server 가 `/cmd_vel` 에 직접 내므로 `/cmd_vel_nav` 에는 안 보임 — 이 차이로 복구 구간을 가려 읽는다), `job27f_escape.txt`, `job29c_rpp_run1.txt`.
- 쓰인 곳: 09-02 「원인 ②」 L182 · 「수정 후 결과」 L197 · B-2 · N1 Run 1.
- 결함: `p0=pose()` 가 None 이면(TF 없음) 바로 예외. 2 s 표본이라 짧은 명령 변화는 놓침. 감시 중 노드 생성이 주행 직전(공통 결함 ③).
- 계보: `job25b` + 구독 2 개. 다음 판 `job30_goalabs.sh` 는 절대 좌표로 바꾸면서 `/cmd_vel_nav` 감시를 **뺐다**(`/cmd_vel` 만) — 그래서 09-03 MPPI Run 1 에서 컨트롤러 출력과 복구 출력을 구별할 수 없었다. 지금 다시 쓰기: 안 씀. 같은 질문(명령 체인 어디서 사라지나)은 이후 bag 기록(`/cmd_vel_nav` · `/cmd_vel` 함께)으로 답한다.

### 8.8 `job27b_profile.sh` — Nav2 상태 + 전방 형상 프로파일
- 위치 · 형태: Jetson, 인자 없음. [`jobs/job27b_profile.sh`](../debug_log/2026-09-02/jobs/job27b_profile.sh)
- 왜: 장애물 회피 코스를 만들 때 '정면에 무엇이 몇 cm 에 있고 좌우로 돌아갈 틈이 있나' 를 숫자로.
- 하는 일: lifecycle 5 개 · 두 코스트맵 hz → 스캔 5 장 → −70°~+70° 를 10° 간격, 각 ±6° 창의 중심 기준 최소거리와 막대(`#` = 5 cm, 2 m 까지) → **직진 경로상 최근접** = |y| ≤ 0.165 + 0.03 그리고 x > 0.25 인 점의 `min(x) − 0.25`(로버 앞면 기준) → '좌측 우회'(+20~+70°) · '우측 우회'(−70~−20°) 최소거리.
- 출력: `job27b_profile.txt`(B-2 코스), `job27d_profile2.txt`(구석: 직진 14 cm), `job29b_course.txt`(N1 코스: 정면 97, +20° 275 cm), 09-03 `job34c_nav2fix_space.txt`(복도: 직진 203 cm), `job35a_prep.txt`.
- 쓰인 곳: 09-02 「B-2 설정」 L222 · 「N1 코스」 L281 · 09-03 코스 확인.
- 결함: 뒤쪽(±70° 밖)은 안 봄 → 실수 ① 의 원인 중 하나. 직진 띠의 '앞면 기준' 은 x 만 빼서 대각 방향 점은 실제보다 가깝게 나올 수 있음. 지금 다시 쓰기: 데크 yaw 보정 없음(공통 결함 ②), 쓰지 않음.

### 8.9 `job21c_where.sh` — 전 방위 회전 방해물 진단(무동작)
- 위치 · 형태: Jetson, 인자 없음. [`jobs/job21c_where.sh`](../debug_log/2026-09-02/jobs/job21c_where.sh) (09-02 오전 회전 루프 시험용으로 만든 것을 Nav2 시험에도 씀)
- 왜: 제자리 회전이 가능한가 — 직사각 차체는 돌 때 반대각선 반경(약 30 cm)을 쓸고 지나간다.
- 하는 일: 0, ±30, ±60, ±90, ±120, ±150, 180° 의 12 방위, 각 ±15° 창의 중심 기준 최소거리. `SWEEP + 0.05 = 0.35 m` 미만이면 '← 회전 방해!'. 전체 최근접 거리 · 방위, 막힌 방향 목록 또는 '회전 가능'.
- 출력: `job27e_360.txt`(후면 172), 09-03 `job33a_reset.txt` · `job34c_nav2fix_space.txt` · `job34e_stuckdiag.txt`(좌60 30 · 좌90 28 · 좌후120 30 → 회전 방해) · `job35a_prep.txt` · `job35d_diag.txt`.
- 쓰인 곳: 실수 ① 판별, 09-03 MPPI Run 1 정지 위치 확인.
- 결함: 중심 기준 거리라 '벽까지 몇 cm' 를 알려면 반폭(16.5 cm) · 반길이(25 cm)를 빼야 한다(예: 좌90 28 cm → 옆면에서 약 11.5 cm. 사용자는 14 cm 로 잼). 지금 다시 쓰기: 개념은 유효, 데크 yaw 보정 없음.

### 8.10 `job30_goalabs.sh` — 절대 좌표(map) 목표
- 위치 · 형태: Jetson, `bash /tmp/job30_goalabs.sh X Y YAW_DEG [TMO=150]`. 호출 예: `0 0 0 150`(09-02 MPPI 복귀), `1.6 0 0 150`(09-02 MPPI 전진 · 09-03 MPPI Run 1 · RPP Run 1), `0 0 180 150`(09-03 RPP Run 2, 「내일 할 일」 L92 에 명시). [`jobs/job30_goalabs.sh`](../debug_log/2026-09-02/jobs/job30_goalabs.sh)
- 왜: 왕복 벤치마크 — '출발점으로 돌아와라' 를 매번 같은 좌표로 주려면 상대 목표가 아니라 map 절대 좌표가 필요.
- 하는 일: `/cmd_vel` 만 구독(마지막 v, w). 현재 자세 출력 → 목표 `(X, Y)`, 자세 `z = sin(YAW/2), w = cos(YAW/2)` 전송(수락 10 s). **3 s 마다** 위치 · heading · 목표까지 직선거리 · 마지막 명령. TMO 넘으면 취소 → `/cmd_vel` 퍼블리셔를 **그 자리에서 새로 만들어** 영 10 번 → `TIMEOUT`. 끝에 위치 오차 · 자세 오차 · 소요 시간.
- 출력: 09-02 `job30a_mppi_return.txt` · `job30b_mppi_fwd.txt`, 09-03 `job34d_mppi_run1.txt` · `job35b_rpp_run1.txt` · `job35c_rpp_run2.txt`.
- 쓰인 곳: 09-02 N1 Run 2 · 3, 09-03 재벤치마크 전부.
- 결함: ① 취소 뒤 영 명령용 퍼블리셔를 막 만들어 바로 보내므로, 구독자(보드 agent)와 연결이 맺어지기 전에 몇 개가 사라질 수 있다(코드 읽기 추정, 미측정). 실제 정지는 펌웨어 `/cmd_vel` 500 ms watchdog 가 보장한다. ② `/cmd_vel_nav` 를 안 봐 컨트롤러 출력과 복구 동작을 못 가름(§8.7 계보). ③ 펌웨어 상태(`/rover/status`)를 안 봐 09-03 MPPI Run 1 에서 100 초 동안 '배회' 로 보였던 것이 사실은 래치였다 → 09-03 `job35a_prep.sh` 가 상태 확인을 넣음. ④ `p0` 가 None 이면 예외.
- 계보: `job26a` → 이것 → 09-07 이후 러너(`job54` · 이후 `job125_avoid3.py` 등, 다음 시기). 지금 다시 쓰기: 안 씀.

### 8.11 `job31_shutdown.sh` — 안전 종료
- 위치 · 형태: Jetson, 인자 없음. [`jobs/job31_shutdown.sh`](../debug_log/2026-09-02/jobs/job31_shutdown.sh)
- 왜: 배터리 충전 전에 모터 정지 → 노드 → agent 순으로 끄기.
- 하는 일: `ros2 topic pub -1 /cmd_vel geometry_msgs/msg/Twist "{}"` 12 번 → `pkill -9 -f "ros2 launch"` → Nav2 · SLAM · EKF · conditioner · deskew · rplidar · realsense · foxglove · RSP · joy · teleop · component_container 를 `pkill -9` → 3 s → `docker rm -f microros_agent` → `ros2 node list` 로 남은 노드.
- 출력: `job31_shutdown.txt` — 'agent 종료됨', 남은 노드 목록에 Nav2 · slam · camera · rover_jupiter 등이 그대로.
- 결함: 남은 노드 목록은 ros2 데몬이 기억하는 그래프라 `-9` 로 죽인 노드가 남아 보이는 것으로 **추정**(실제 프로세스 확인 `pgrep` 이 없어 미확인). 정지 명령보다 먼저 Nav2 가 다시 명령을 낼 수 있는 순서지만, 곧바로 kill 하고 보드 watchdog(500 ms)가 있어 실해는 없음. '배터리(마지막)' 는 언제나 '측정불가' 를 찍는 자리표시. 지금 다시 쓰기: 안 씀.

### 8.12 `job20a_boot.sh` — 부팅 후 전체 스택 기동 (참고)
- 위치 · 형태: Jetson, 인자 없음. [`jobs/job20a_boot.sh`](../debug_log/2026-09-02/jobs/job20a_boot.sh). 09-03 `job32a_boot.txt`(09:31) · `job34a_boot.txt`(17:23) 가 이 도구 출력.
- 하는 일: 잔여 프로세스 `pkill -9` + agent 컨테이너 삭제 → `base.launch.py`(agent + RSP) 12 s → agent 컨테이너 상태 · `/wheel_odom` hz · `/battery` → `sensors.launch.py`(camera · lidar · deskew · conditioner · EKF · foxglove) 22 s → 자이로 바이어스 줄 → `slam.launch.py` 10 s → 노드 목록 · `/odometry/filtered` · `/scan` hz · conditioner 소스의 `VX_SCALE` 줄 · odom 원점 · map→odom.
- 결함: agent 를 새로 띄우므로 보드가 세션을 다시 맺으려면 **보드 리셋 필요**(08-26 「판단 · 결정」 2: 펌웨어가 부팅 때 한 번만 세션 수립). `/odometry/filtered:` 다음이 빈칸이면 EKF 미발행(`job34a_boot.txt` 에 실제로 빈칸 — 이후 Nav2 기동은 정상이라 일시 지연으로 보임, 미확인).
- 계보: → `job25a` · `job33a`(agent 유지판) → `prep_fast.sh` · `prep_patrol.sh`(10 월).

### 8.13 09-03 도구: `job34c_verify.sh` · `job34e_stuckdiag.sh` · `job35a_prep.sh` · `job33a_reset_noagent.sh`
- **`job34c_verify.sh`**([원본](../debug_log/2026-09-03/jobs/job34c_verify.sh)): `FollowPath.plugin` · `general_goal_checker.xy_goal_tolerance` · **로컬** `inflation_layer.inflation_radius` 를 `ros2 param get`(8 s), nav2.log `ERROR` 중 `get_state|get_parameters` 제외 마지막 3, bt_navigator 상태. 출력 `job34c_nav2fix_space.txt`(MPPI · 0.15 · 0.25 · active). 결함: 전역 inflation 은 안 봄(실수 ② 와 같은 함정).
- **`job34e_stuckdiag.sh`**([원본](../debug_log/2026-09-03/jobs/job34e_stuckdiag.sh)): `/tmp/job21c_where.sh` 의 3~20 줄, nav2.log 에서 `mppi|collision|critic|trajector|Failed|abort|recovery|spin|backup` 마지막 12, `/battery`, `/cmd_vel` 한 장(3 s, 없으면 '정지'). 출력 `job34e_stuckdiag.txt` — 좌측 28~30 cm 로 회전 방해 3 방위, `Failed to make progress` 약 25 s 간격, spin 취소, 12.12 V. **결함: `/rover/status` 를 안 봄** — 그래서 이 진단만으로는 래치를 못 찾았고, level 2 를 확인한 조회 출력은 파일에 없다(대화에만, 원천 소실). `/cmd_vel` 확인 줄이 빈칸 = 3 s 안에 명령이 안 옴(취소 뒤 정지 상태) — '무발행(정지)' 문구는 공통 결함 ① 로 안 찍힘.
- **`job35a_prep.sh`**([원본](../debug_log/2026-09-03/jobs/job35a_prep.sh)): 보드 리셋 뒤 재벤치마크 준비 한 번에 — ① `/tmp/chk_board.sh` + `/rover/status` 의 `message:` ② `/tmp/job33a_reset_noagent.sh`(필터) ③ `/tmp/job25e_nav2start.sh`(필터) + `FollowPath.plugin` · `default_nav_to_pose_bt_xml` · 로컬 inflation · nav2.log ERROR 수 ④ `job21c_where` + `job27b_profile` 의 두 줄. 출력 `job35a_prep.txt`(OK · RPP · `nav_to_pose_no_spin.xml` · 0.25 · 오류 0). 앞 도구들의 결함(상태 미확인 · ERROR 묻힘)을 반영한 첫 '주행 전 검사' — 10-27 `chk_drive_gate.py` 의 먼 조상.
- **`job33a_reset_noagent.sh`**([원본](../debug_log/2026-09-03/jobs/job33a_reset_noagent.sh)): agent 는 절대 안 건드림(그날 오전 디버거가 없어 보드 리셋 불가 — 파일 머리 주석). agent · `/wheel_odom`(없으면 '★RESET 필요' — 공통 결함 ① 로 실제로는 안 찍힘) · `/battery` → EKF 재시작 16 s · SLAM 재시작 10 s → `/odometry/filtered` hz · odom 원점 x · `/scan` hz. 출력 `job33a_reset.txt`(12.09 V). `job25a` 에서 Nav2 부분을 뺀 판.

## 9. 용어
- **Nav2**: ROS 2 자율주행 스택. 전역 계획(planner_server) → 경로 추종(controller_server) → 속도 다듬기(velocity_smoother) → `/cmd_vel`. 행동 순서는 BT(behavior tree)가 정한다.
- **RPP(Regulated Pure Pursuit)**: 경로 위 앞쪽 한 점(lookahead)을 향해 곡률로 조향하는 추종기. 곡률 · 장애물 근접 때 감속(regulated). 경로 시작 방향이 많이 틀리면 먼저 제자리 회전(`use_rotate_to_heading`, 이때 각속도에 `max_angular_accel × 제어주기` 클램프가 걸린다 — 09-02 데드락의 자리).
- **MPPI(Model Predictive Path Integral)**: 속도 명령 열을 수천 개(여기선 batch 1000 × 32 step × 0.05 s = 1.6 s 앞) 무작위로 흔들어 굴려 보고, 비용 함수(critic: 경로 정렬 · 목표 · 장애물 · 전진 선호 …)가 낮은 것들의 가중 평균을 명령으로 낸다. 후진(`vx_min < 0`)도 자연스럽게 고르지만 계산이 무겁다.
- **progress checker**: 컨트롤러가 '진전' 하는지 감시. Simple 은 `required_movement_radius`(여기 0.25 m) 이상 **병진** 이동이 `movement_time_allowance`(20 → 25 s) 안에 없으면 실패. Pose 는 `required_movement_angle`(0.5 rad) 이상 **회전**도 진전으로 인정.
- **goal checker / 허용오차**: `xy_goal_tolerance` 안에 들고 `yaw_goal_tolerance` 안이면 도달. `stateful: True` 면 위치를 한 번 만족한 뒤엔 자세만 본다.
- **inflation · inscribed radius**: 코스트맵이 장애물 둘레에 비용을 퍼뜨리는 반경(inflation_radius)과 비용 감소 기울기(cost_scaling_factor 3.0). 내접반경(inscribed radius) = 풋프린트 안에 들어가는 가장 큰 원의 반지름(직사각형이면 반폭 + 패딩 = 0.165 + 0.05 = 0.215 m). 이 안의 칸은 '확실히 충돌' 비용. inflation 이 내접반경보다 작으면 Nav2 가 오류를 낸다.
- **footprint_padding**: 풋프린트를 사방으로 이만큼 키워 충돌 검사 · 계획을 한다(여기 0.02 → 0.05).
- **BT · 복구(recovery)**: 기본 BT 는 경로 추종이 실패하면 코스트맵 지우기 → Spin(제자리 1.57 rad) → Wait 5 s → BackUp(후진) 을 돌아가며 시도(Humble 기본 BT 구성 — 일반 지식, 이 기록에서 원문 대조는 안 함). 09-03 `nav_to_pose_no_spin.xml` 은 Spin 을 빼고 BackUp 0.15 m · 0.05 m/s 와 Wait 5 s 만 둠. 복구 동작은 behavior_server 가 `/cmd_vel` 에 직접 낸다(`/cmd_vel_nav` 에는 안 보임).
- **velocity_smoother**: 컨트롤러 출력(`/cmd_vel_nav`)을 속도 · 가속 한계로 다듬어 `/cmd_vel` 로. 여기선 `OPEN_LOOP`(측정 속도 대신 직전 명령 기준) · `max_velocity [0.10, 0, 0.60]`.
- **데드밴드 · 정지마찰 · duty · latch · re-arm**: [데드밴드 카드 §9](start-deadband.md) · [스톨 카드 §9](stall-latch.md).
