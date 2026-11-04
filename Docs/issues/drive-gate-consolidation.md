# 주행 전 검사 정리 — 게이트 B · C · G2 한 노드(chk_drive_gate) · prep 파라미터 조회 한 노드(chk_prep) · 대화 쪽 대기 없앰

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **해결**(정리 자체 — 판정 기준은 그대로, 같은 정지 상태에서 B · G2 값 같음, 게이트 23.6 → 6.7 s · 게이트 → 출발 66 → 40 s, f2tt1 · f2tt2 · 10-28 장소 이동 5 회에서 정상 동작, **측정**) · 남은 결함 3: ① 게이트 C 의 실제 관찰 창이 5 s 가 아닐 수 있음(f2tt1 map→odom 20 개/5 s) ② C 문턱이 timeout 1.5 에서 '≈ 2.5 s 정체' 를 뜻하게 됨 ③ 단일 출처 `TEST_COURSE_AND_GATES.md` 가 옛 도구 · 옛 문턱을 적고 있음 | 10-27 §24 ~ 10-28 §4 (11-04 코드 대조) | [10-27 §24](../debug_log/2026-10-27/SUMMARY.md) 사용자 "테스트 주행 전 여러 검사 중 중복 · 불필요한 것 없애자" | 새 [`Docs/tools/chk_drive_gate.py`](../tools/chk_drive_gate.py)(커밋 `a813ac8a`) · [`Docs/tools/chk_prep.py`](../tools/chk_prep.py) PARAMS 확장(같은 커밋) · 러너 `job551_f0drive.sh`(실행본 = PC 스크래치패드, 사본 [`2026-10-27/jobs/job551_f0drive.sh`](../debug_log/2026-10-27/jobs/job551_f0drive.sh)) · `run_f0.sh`(전송 목록, 사본 [`2026-10-27/jobs/run_f0.sh`](../debug_log/2026-10-27/jobs/run_f0.sh)) · prep 래퍼 `prep_smac_1027b.sh` → `prep_smac_1028.sh` | [주행 직전 DDS 참여자](pre-drive-dds-participants.md)(이 정리의 배경 규칙) · [주행 전 검사 · 운용(8 기)](drive-ops-1019-1023.md)(바로 앞 판) · [빠른 prep](prep-fast-startup.md)(`chk_prep.py` 계보) · [SLAM map→odom 시각 정체](slam-stamp-freeze.md)(게이트 C 의 뜻) · [장소 이름 이동](f25-place-navigation.md)(같은 게이트를 쓰는 러너) · [정지 중 방향 드리프트](stationary-yaw-drift.md)(f2pl1 게이트 C 0.92 s) |

**한 줄**: 러너가 주행 직전에 게이트 B(`ros2 topic hz` 12 s) · C(`job386` 5 s) · G2(`job440`)를 따로 띄워 DDS 참여자 3 개 · 약 24 s 를 쓰고, 그 뒤 30 s 대기 다음에 부하 게이트 P 10 s 를 또 쟀으며, prep 래퍼는 `ros2 param get` 을 약 11 번 불렀다. 10-27 에 B · C · G2 를 같은 기준 그대로 한 노드(`chk_drive_gate.py`)로, P 를 30 s 대기의 마지막 10 s 로, 파라미터 조회를 `chk_prep.py` 한 노드로 옮기고, 대화 쪽에서 따로 두던 30 s 대기 · 1 s top 을 없앴다. 같은 정지 상태 비교에서 B · G2 값이 같았고, 실주행 f2tt1 · f2tt2 에서 게이트 → 출발이 40 s(f2tf1 66 s)로 줄었다. 정리 중 새 C 가 한 번 FAIL(stamp 지연 1.14 s)했는데 로버가 출발 위치를 틀린 상태의 SLAM 정체로 봤다(추정). 카드 작성 중 원문을 다시 보니 C 는 관찰 창 안 수신 수가 20~101 개로 흔들려(새 참여자 발견 지연 추정) 실제 관찰 시간이 1~5 s 이고, timeout 1.5 이후 C 문턱 1.0 s 는 2.5 s 정체에서야 걸린다.

## 1. 증상
- 사용자(10-27 §24): "테스트 주행 전 여러 검사 중 중복 · 불필요한 것 없애자".
- 정리 전 한 주행의 주행 전 단계(10-27 §24 '읽은 단계', 원문 [10-27 SUMMARY §24](../debug_log/2026-10-27/SUMMARY.md)):
  - prep = `Docs/tools/prep_patrol.sh` → `prep_fast.sh`(정리 · base · 자이로 캘리브 · SLAM · Nav2 · `chk_prep.py` 한 노드 확인) + 날짜별 래퍼 `prep_smac_1027.sh`(`ros2 param get` 약 11 번).
  - 러너 = 스크래치패드 `run_f2c.sh` → `run_f0.sh`(전송) → Jetson `job551_f0drive.sh`: A 프로세스 중복 · B `ros2 topic hz /wheel_odom` 12 s · J nvblox · C `job386_slamalive.py` 5 s · G2 `job440_startclear.py` ≤ 60 s · `sleep 30` · P CPU 10 s · bag · tegrastats · top 2 s · /proc 2 s · UDP 손실 2 s → `job550_f0run.py`.
  - 대화 쪽: 내가 따로 둔 30 s 대기 · 1 s top(f2tf1).
- 같은 정지 상태에서 옛 B · C · G2 = 12.34 + 7.02 + 4.22 = **23.6 s**([`cmp_gate_1027.txt`](../debug_log/2026-10-27/outputs/gate/cmp_gate_1027.txt)). f2tf1 실주행: 게이트 14:58:55 → 주행 15:00:01 = **66 s**([`run_f2tf1.txt`](../debug_log/2026-10-27/outputs/drives/f2tf1/run_f2tf1.txt) 2 · 11 행).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론 | 데이터 |
|---|---|---|---|---|
| 09-17 mp7 | 게이트 C 신설 `job386_slamalive.py` | mp7 고장 때 간격 5.1 s · 지연 4.8 s, 정상 지연 −0.08~+0.55 s(timeout 0.2 시절) | 문턱 간격 < 0.5 s · 지연 < 1.0 s | [`job386_slamalive.py`](../debug_log/2026-09-17/jobs/job386_slamalive.py) 22~23 행 |
| 09-18 dy3 · dy5 | 게이트 G2 `job440_startclear.py` | 로컬 LETHAL(100) · 라이다 점 ↔ 차체 외곽 | 문턱 0.10 m(러너 쪽) | [`job440_startclear.py`](../debug_log/2026-09-18/jobs/job440_startclear.py) |
| 09-23 | F0 러너 `job551` 에 `sleep 30`(09-21 cc1 규칙) | — | 게이트가 만든 참여자 뒤 30 s | → [DDS 참여자 카드](pre-drive-dds-participants.md) |
| 10-01 §8.9 | 부하 게이트 P | 정지 기준선 36 % · f2a3 주행 중 88 % | 정지 10 s > 60 % 면 주행 안 함 | `job551` 28~32 행(11-03 사본) |
| 10-12 §13 | prep 확인을 한 노드로(`job971` → 10-13 `chk_prep.py`) | `ros2 topic hz/param get` 약 25 번 → 1 노드 | 참여자 폭주 줄이기 | → [빠른 prep 카드](prep-fast-startup.md) |
| 10-20 §9.7 · 10-21 | B 한도 6 → 12 s(첫 출력 4.5~5.6 s) · `PREP_POSE` · `LOAD_MAX` | — | 게이트 자신의 발견 지연 | → [8 기 운용 카드](drive-ops-1019-1023.md) |
| 10-27 §24 | 중복 정리(아래 §4 표) · 옛 / 새 게이트 같은 정지 상태 비교 | 옛 B 25.03 Hz · 12.3 s / C OK(지연 0.38) · 7.0 s / G2 0.397 · 4.2 s = 23.6 s; 새 B 25.0 · G2 0.397 · **6.7 s** · 새 C **FAIL(1.14 s)** → 20 s 관찰 최대 −0.27 s OK | 새 노드 결함 아님 — 그때 로버가 −175° 로 서 있어 위치 추정이 틀린 상태(PREP_FAIL)의 SLAM 정체로 봄(**추정**). C 기준은 생존 검사로 그대로 | [`cmp_gate_1027.txt`](../debug_log/2026-10-27/outputs/gate/cmp_gate_1027.txt) · [`chk_slam_idle_1027.txt`](../debug_log/2026-10-27/outputs/gate/chk_slam_idle_1027.txt) · `jobs/cmp_gate_1027.sh` · `chk_slam_idle_1027.sh` |
| 10-27 §24 | 래퍼 `prep_smac_1027b.sh`(param get 뺀 판, grep 필터) | 11 s 만에 prep 출력 없이 끝남 — 출력은 BT 사본 한 줄뿐 | **원인 모름** → prep 은 원문을 파일로 남기는 방식으로 | [`prep_1027b.txt`](../debug_log/2026-10-27/outputs/gate/prep_1027b.txt) |
| 10-27 §24 | 필터 없는 prep `run_prep_full_1027.sh` | **PREP_OK** +84 s · 0.003 m · 0.0° · 파라미터 한 노드로 전부 · 출력 이름표 결함(Critic 셋이 모두 'PreferForward') | 이름표 고침(다음 prep 부터) | [`prep_full_1027b.txt`](../debug_log/2026-10-27/outputs/gate/prep_full_1027b.txt) |
| 10-27 §25 | **정리판 러너 첫 실주행 f2tt1** | 게이트 15:54:40 → 출발 15:55:20 = **40 s** · 게이트 노드 5.0 s(B 25.3 Hz · C 최대 간격 0.05 s · 지연 −1.39 s · G2 0.316 m) · P 49 % · 8/8 | 정상 동작 | [`run_f2tt1.txt`](../debug_log/2026-10-27/outputs/drives/f2tt1/run_f2tt1.txt) 2~13 행 |
| 10-28 §2 | 재부팅 뒤 재전송 · prep | prep_fast aeb6e6cf3b · prep_patrol 4fe16954f6 · chk_prep 64b8beeadd · chk_drive_gate 5e92ec4a0a — PC HEAD 와 같음 · CR 0 · PREP_OK +86 s · 이름표 PathAlign · PathFollow 로 찍힘 | 이름표 수정 반영 | [`prep_smac_1028_1.txt`](../debug_log/2026-10-28/outputs/prep_smac_1028_1.txt) · `jobs/up_prep_1028.sh` · `prep_smac_1028.sh` |
| 10-28 §3 · §3.1 | f2tt2 첫 시도 — PC 쪽 출력 0 B · WSL E_FAIL | 'Jetson 러너는 시작 안 됨, 로버 안 움직였을 것' 이라고 보고 → **틀림**(Jetson job551 은 setsid nohup 으로 끝까지 감) | 실수(§5.1) | [10-28 §3.1](../debug_log/2026-10-28/SUMMARY.md) |
| 10-28 §4 | f2tt2 결과(판정 ⑤ 게이트 → 출발 ≤ 50 s 를 미리 선언) | 게이트 10:21:43 → 출발 10:22:23 = **40 s** · 게이트 노드 5.0 s(C 72 개/5 s · 지연 −1.30 s · G2 0.344 m) · P 47 % | 판정 ⑤ 통과 → **10-27 정리판을 운용으로 확정**(2 회) | [`f0_f2tt2.log`](../debug_log/2026-10-28/outputs/drives/f2tt2/f0_f2tt2/f0_f2tt2.log) 1~13 행 · `jobs/get_f2tt2.sh` |
| 이후 10-28 §7~§14 | 장소 이름 이동 러너 `run_place_s1_1028.sh` 가 같은 게이트 노드 + `sleep 30` | f2pl1 게이트 C `100 개/5 s, 최대 간격 0.06 s, 최대 stamp 지연 0.92 s`(통과) — 2.7 h 정지 뒤 방향 7° 틀린 채 출발한 주행 | 게이트 C 는 통과(문턱 1.0) — 카드 작성 중 대조(§6) | [`f2pl1/place_s1.log`](../debug_log/2026-10-28/outputs/drives/f2pl1/place_s1.log) 3 행 · `2026-10-28/jobs/run_place_s1_1028.sh` 9 · 18 행 · → [장소 이동 카드](f25-place-navigation.md) · [정지 드리프트 카드](stationary-yaw-drift.md) |
| 이후 11-03 §3 · 11-04 §1 | 러너 bag QoS 재정의 분리(게이트와 무관) · `up_tools.sh` 를 저장소 판 전송으로 | — | — | [11-03 SUMMARY §3](../debug_log/2026-11-03/SUMMARY.md) · [11-04 SUMMARY §1](../debug_log/2026-11-04/SUMMARY.md) |

## 3. 판단 항목별 근거 (10-27 §24 표 + 확인)
| 항목 | 판단 | 근거 · 확인 | 판정 |
|---|---|---|---|
| B · C · G2 가 참여자 3 개 · 약 24 s | 같은 기준을 한 노드로 | 같은 정지 상태 B 25.03 ↔ 25.0 Hz · G2 0.397 ↔ 0.397 m(로컬 · 라이다 모두), 23.6 → 6.7 s | **같음 확인**(C 는 그 순간 SLAM 상태가 달라 비교 불가 — §2) |
| sleep 30 뒤 P 10 s 따로 | 대기 중에 재도 같다 | 30 s 규칙은 '참여자 생성 뒤 30 s 동안 새 참여자 금지' — P 는 `/proc/stat` 읽기라 참여자 없음 | 타당(규칙의 수치 근거 자체는 측정 아님 — [DDS 카드 §5](pre-drive-dds-participants.md)) |
| 러너 top 2 s 루프 | /proc 프로세스별 틱 기록과 겹침 · top 실행 자체 CPU | 명령줄은 `rss_` 스냅숏 args 로 | 타당. 대가: 10-27 §21.2 처럼 1 s top 명령줄로 이름을 붙이던 분석(`anal_load_f2tf1.py`)은 입력이 없어짐 |
| UDP 손실 기록 | 10-12 포화 조사용, 10-13 해결 | `NET_LOG=1` 일 때만 | 타당 |
| prep 래퍼 `ros2 param get` 약 11 번 | 회당 참여자 · 수 초, chk_prep 조회와 겹침 | `chk_prep.py` PARAMS 에 Smac 6 · MPPI PathAlign/PathFollow · 깊이 프리셋 · EKF odom1 · SLAM mode/transform_timeout · BT xml | 타당 — 단 **기록만**(값이 틀려도 PREP_FAIL 아님, §4.3) |
| 대화 쪽 30 s 대기 · 1 s top | 러너가 게이트 노드 뒤 30 s 를 이미 기다림 · CPU 는 러너가 기록 | — | 타당(CLAUDE.md §6 '대화 쪽 별도 30 s 대기 없음') |
| 유지 | A(고아 · 중복 프로세스) · J(nvblox · 깊이) · 러너 30 s · prep 위치 추정 검사 · 코스트맵 재마킹 대기 · 사후 params 스냅숏(job451) | 각자 다른 실패를 거름 | 유지 |

## 4. 조치와 효과
| 단계 | 전(f2tf1 · 10-21 판) | 후(f2tt1 · f2tt2 · 10-27 판) |
|---|---|---|
| B · C · G2 | 3 프로세스(참여자 3) · 23.6 s(정지 비교) | 1 노드 · 5.0 s(게이트 노드 줄) / 6.7 s(전체) |
| 대기 + P | `sleep 30` + P 10 s = 40 s | `sleep 20` + P 10 s = 30 s |
| 게이트 → 주행 줄 | 66 s(f2tf1) | 40 s(f2tt1) · 40 s(f2tt2) |
| 주행 중 기록 | top 2 s · /proc 2 s · UDP 2 s | /proc 2 s(top 없음, UDP 는 `NET_LOG=1` 때만) |
| prep 파라미터 확인 | 래퍼 `ros2 param get` ≈ 11 번 | `chk_prep.py` 한 노드 출력 줄 |

### 4.1 판단에 쓴 핵심 줄 · 출력
- **게이트 노드** — [`chk_drive_gate.py`](../tools/chk_drive_gate.py) 39~48 행(관찰 루프 · B · C), 77~79 행(G2 · 마지막 줄):
  ```python
  while time.time() - t0 < SEC or ((S['cm'] is None or S['scan'] is None) and time.time() - t0 < 12.0):
      rclpy.spin_once(n, timeout_sec=0.05)
  w = [x for x in wheel if x >= t0]; bhz = (len(w) - 1) / (w[-1] - w[0]) if len(w) > 2 else 0.0
  B = 'OK' if bhz >= 1.0 else 'FAIL'
      gap = max(mo[i][0] - mo[i - 1][0] for i in range(1, len(mo))); lag = max(r[1] for r in mo)
      C = 'OK' if (gap < 0.5 and lag < 1.0) else 'FAIL'
  print('GATE B=%s C=%s G2=%s' % (B, C, ('%.3f' % g2) if not math.isnan(g2) else 'nan'))
  ```
  G2 는 로컬 코스트맵 값 ≥ 100 칸(62 행 — 99 내접은 반경을 두 번 세므로 뺌, 09-18 dy5)과 2 m 안 라이다 점을 base_link 로 옮겨 차체 사각형(반길이 0.25 · 반폭 0.165) 바깥 거리 최소(`fp_dist`, 24 행), 둘 중 작은 값.
- **같은 정지 상태 비교** — [`cmp_gate_1027.sh`](../debug_log/2026-10-27/jobs/cmp_gate_1027.sh) 3~6 행이 옛 B · C · G2 와 새 노드를 차례로 돌려 걸린 시간을 `date +%s.%N` 차로 찍음. 출력([`cmp_gate_1027.txt`](../debug_log/2026-10-27/outputs/gate/cmp_gate_1027.txt)):
  ```
  옛 B: average rate: 25.032 · 12.34 s
  옛 C: map->odom 101 개/5 s, 최대 간격 0.06 s, 최대 stamp 지연 0.38 s
     7.018 s
  옛 G2: 0.397
     4.216 s
    B /wheel_odom 25.0 Hz
    C map->odom 100 개/5 s, 최대 간격 0.06 s, 최대 stamp 지연 1.14 s
    G2 로컬 코스트맵 LETHAL ↔ 차체 외곽 최소 0.397 m @ 차체 (-0.14, -0.56)
    게이트 노드 5.0 s
  GATE B=OK C=FAIL G2=0.397
  새 게이트 전체 6.730 s
  ```
- **러너가 읽는 방식** — 11-03 사본 [`job551_f0drive.sh`](../debug_log/2026-11-03/jobs/job551_f0drive.sh) 13~14 · 21 · 23~25 · 27 · 30~32 행:
  ```bash
  GT=$(timeout 40 python3 /tmp/chk_drive_gate.py 2>&1 | grep -av "^\["); echo "$GT" | grep -av "^GATE"; GL=$(echo "$GT" | grep -a "^GATE" | tail -1)
  echo "$GL" | grep -q "B=OK" || { echo "  B 불합격(보드 무발행) — 주행하지 않음"; exit 1; }
  echo "$GL" | grep -q "C=OK" || { echo "  C 불합격(SLAM) — 주행하지 않음"; exit 1; }; echo "  C 통과"
  G2=$(echo "$GL" | grep -o "G2=[^ ]*" | cut -d= -f2)
  awk -v d="$G2" 'BEGIN{exit !(d+0>=0.10)}' || { echo "  G2 불합격(출발 자세 여유 $G2 m < 0.10) — 주행하지 않음"; exit 1; }
  sleep 20   # DDS 참여자 생성 뒤 30 s (09-21 cc1 규칙) = 20 s + 아래 P 측정 10 s
  L0=$(head -1 /proc/stat); sleep 10; L1=$(head -1 /proc/stat)
  ```
  순서는 A → 게이트 노드(B 판정) → J → C 판정 → G2 판정 → 20 s → P. 즉 J(nvblox, 도커 exec · 로그 읽기)는 게이트 노드 뒤에 돌지만 참여자를 만들지 않는다.
- **첫 실주행(f2tt1)** — [`run_f2tt1.txt`](../debug_log/2026-10-27/outputs/drives/f2tt1/run_f2tt1.txt) 2~14 행:
  ```
  ########## F0 게이트 15:54:40 ##########
    B /wheel_odom 25.3 Hz
    C map->odom 20 개/5 s, 최대 간격 0.05 s, 최대 stamp 지연 -1.39 s
    G2 로컬 코스트맵 LETHAL ↔ 차체 외곽 최소 0.316 m @ 차체 (-0.27, +0.48)
    게이트 노드 5.0 s
    P 통과 (정지 부하 49 %)
  ########## F0 주행 15:55:20 — 목표 2.25,-1.6,p;-1.6,-2.0,p;…
  ```
- **prep 파라미터 한 노드** — [`chk_prep.py`](../tools/chk_prep.py) 36~42 행(10-27 추가분):
  ```python
  '/planner_server': ['SmacHybrid.tolerance', 'SmacHybrid.motion_model_for_search', 'SmacHybrid.cost_penalty',
                      'SmacHybrid.analytic_expansion_max_length', 'SmacHybrid.max_planning_time', 'SmacHybrid.cache_obstacle_heuristic'],
  '/camera/camera': ['depth_module.visual_preset'],
  '/ekf_filter_node': ['odom1'],
  '/slam_toolbox': ['mode', 'transform_timeout'],
  '/bt_navigator': ['default_nav_to_pose_bt_xml']}
  ```
  출력(10-28, [`prep_smac_1028_1.txt`](../debug_log/2026-10-28/outputs/prep_smac_1028_1.txt)):
  ```
    /controller_server: PreferForward=15.0 · vx_min=-0.06 · visualize=True · trajectory_step=100 · time_step=4 · PathAlign=28.0 · PathFollow=5.0
    /planner_server: tolerance=0.35 · motion_model_for_search=REEDS_SHEPP · cost_penalty=3.0 · analytic_expansion_max_length=1.0 · max_planning_time=2.0 · cache_obstacle_heuristic=False
    /slam_toolbox: mode=localization · transform_timeout=1.5
  PREP_OK
  ```
  10-27 판 출력은 같은 줄이 `… · PreferForward=28.0 · PreferForward=5.0` 이었다([`prep_full_1027b.txt`](../debug_log/2026-10-27/outputs/gate/prep_full_1027b.txt) — 이름표 결함, 값은 맞음).

### 4.2 한계
- 같은 정지 상태 비교 1 번 · 실주행 2 번(+ 10-28 장소 이동 5 회). 판정 기준을 그대로 옮겼다는 것은 코드 대조(머리 주석 5~7 행 '판정 기준은 그대로 옮긴다') + B · G2 값 일치이고, C 는 그 비교 순간 SLAM 이 정체 상태여서 값이 달랐다 — 같은 상태에서 C 를 나란히 잰 기록은 없다.
- '66 → 40 s' 에는 B · C · G2 정리(≈ 17 s)와 P 합치기(10 s)가 함께 들어 있다. 출발 전 총 시간(prep 포함)은 재지 않았다.
- 주행 중 Control loop missed 84 → 43(f2tt1) → 70(f2tt2): 게이트 정리 · timeout 1.5 가 같은 주행에 들어가 몫을 나눌 수 없다(SUMMARY §25 '원인 분리 안 함').

### 4.3 지금 코드 영향 (11-04 저장소 기준)
- 게이트 노드 [`chk_drive_gate.py`](../tools/chk_drive_gate.py) blob `5e92ec4a0a`(10-28 Jetson 판과 같음). 관찰 기본 5 s(19 행), 코스트맵 · 스캔이 없으면 12 s 까지 기다림(39 행), 마지막 줄 형식은 러너 · 장소 러너가 grep 으로 읽음 — 바꾸면 두 러너를 같이 고쳐야 한다.
- 러너: 실행본은 PC 스크래치패드(저장소엔 사본만). 최신 사본 [`2026-11-03/jobs/job551_f0drive.sh`](../debug_log/2026-11-03/jobs/job551_f0drive.sh) 12~32 행이 위 §4.1 판. ⚠ [`run_f0.sh`](../debug_log/2026-10-27/jobs/run_f0.sh) 7 행 `for f in … chk_drive_gate.py; do tr -d '\r' < $N/$f …` — 러너는 게이트 노드를 **스크래치패드 사본**에서 보낸다(저장소 `Docs/tools/` 가 아님). 10-28 의 blob 일치는 prep 재전송 쪽(`up_prep_1028.sh` 가 `tools_*` 사본을 보냄) 확인이고, 그 뒤 러너가 같은 경로 `/tmp/chk_drive_gate.py` 를 덮어쓴다 — 두 사본이 같은지 확인한 기록은 없음(**미확인**). 11-04 §1 의 `up_tools.sh` 저장소 판 전송 수정은 러너 전송 목록에는 미치지 않는다.
- prep: [`prep_fast.sh`](../tools/prep_fast.sh) 66 행 `python3 -u /tmp/chk_prep.py $WAIT 150` · [`chk_prep.py`](../tools/chk_prep.py) 31~42 행 PARAMS · 135 행 이름표(`Critic` 이 든 이름은 앞 부분을 씀). PARAMS 는 **기록만** — 122~129 행의 위치 추정 검사만 PREP_FAIL 을 낸다. Smac 주행은 `NAV_ADD="planner:=smac" REPLAN_HZ=0.01`(예 [`prep_smac_1028.sh`](../debug_log/2026-10-28/jobs/prep_smac_1028.sh) 4 행)로 띄웠고, 표준 [`prep_patrol.sh`](../tools/prep_patrol.sh) 17 행 기본은 `replan_hz:=${REPLAN_HZ:-0.5}` · planner 는 [`navigation.launch.py`](../../ros2_ws/src/rover_navigation/launch/navigation.launch.py) 203 행 기본 `navfn`. Smac 플러그인은 planner 와 상관없이 늘 올라가므로([`nav2_params.yaml`](../../ros2_ws/src/rover_navigation/config/nav2_params.yaml) 731 행 `planner_plugins: ["GridBased", "SmacHybrid"]`) chk_prep 의 `/planner_server` 줄만으로는 '이번 주행이 Smac 경로인지' 알 수 없다 — BT 사본(`PlanSmacOrNavFn`, `navigation.launch.py` 115~124 행)을 따로 봐야 한다(`prep_smac_1027b.sh` 5 행이 그렇게 함).
- 문서: 단일 출처 [`TEST_COURSE_AND_GATES.md`](../04_navigation/TEST_COURSE_AND_GATES.md) §3 표 53 행 C = `job386_slamalive.py` · '최대 간격 ≤0.2 s', 58 행 G2 = `job440_startclear.py`, §7(105~110 행) '게이트 A·B·J·C·G2(`job551` 내장)' — 지금 도구 · 문턱(< 0.5 s · 지연 < 1.0 s) · P 게이트가 없다(§5.2-2).

## 5. 내 실수 · 기록 어긋남
### 5.1 10-28 §3 '러너는 시작 안 됨, 로버 안 움직였을 것' (SUMMARY §3.1 이 칸 형식으로 기록)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | f2tt2 러너 실행(`run_f2c.sh` → `run_f0.sh` → Jetson `job551_f0drive.sh`), 출력은 `outputs/drives/f2tt2/run_f2tt2.txt` 로 |
| 본 것 | 명령이 바로 끝나고 출력 파일 0 B, 'grep: write error: No medium found'. 이어 WSL 실행이 'E_FAIL' |
| 처음 추론 | WSL 이 처음부터 안 떠서 러너가 시작조차 못 함 → 로버 안 움직임 |
| 틀린 이유 | `run_f0.sh` 가 Jetson 에 `job551` 을 **setsid nohup** 으로 띄움(독립 실행). PC 쪽은 출력을 F: 파일로 쓰다 실패(추정)해 폴링 · 회수만 죽음 → 주행은 끝까지 감(f0 로그 10:21:43 게이트 → 10:29:49 끝) |
| 판별 | Jetson `/tmp/f0_f2tt2.log` · bag 존재, 사용자 '주행 완료' |
| 다음에 알아보는 법 | PC 쪽 출력이 끊겨도 Jetson 러너는 계속 돈다 — '안 움직였다' 전에 Jetson `/tmp/f0_<이름>.log` · `pgrep job551` 을 본다(안 되면 '모름' + 현장 확인). 주행 중 PC 연결이 끊기면 PC 에서 멈출 수 없다 — 정지 수단은 온보드 · 현장 |
| 데이터 | [10-28 SUMMARY §3 · §3.1](../debug_log/2026-10-28/SUMMARY.md) · 회수 [`get_f2tt2.sh`](../debug_log/2026-10-28/jobs/get_f2tt2.sh) · [`f0_f2tt2.log`](../debug_log/2026-10-28/outputs/drives/f2tt2/f0_f2tt2/f0_f2tt2.log) · 0 B 파일 [`run_f2tt2.txt`](../debug_log/2026-10-28/outputs/drives/f2tt2/run_f2tt2.txt) |

### 5.2 기록 어긋남(원문 대조, 11-04 카드 작성 중)
1. **10-27 §25 'f2tf1 77 s'**: 같은 정의(게이트 줄 → 주행 줄)로 [`run_f2tf1.txt`](../debug_log/2026-10-27/outputs/drives/f2tf1/run_f2tf1.txt) 는 14:58:55 → 15:00:01 = **66 s**. 66 − 40 = 26 s 는 정리 몫(B · C · G2 ≈ 17 s + P 10 s)과 맞는다. 77 이 어디서 왔는지 원문 없음.
2. **`TEST_COURSE_AND_GATES.md` v2.3 §3**: C 문턱 '최대 간격 ≤0.2 s'(53 행)는 09-17 `job386` 코드(`gap < 0.5 and lag < 1.0`)와도 이미 달랐고, 도구 이름 job386 · job440 · job254 와 P 게이트 부재는 10-27 정리 뒤 낡았다. CLAUDE.md 는 이 문서를 '게이트 단일 출처' 라 부른다.
3. **[`Docs/tools/README.md`](../tools/README.md) 도구 표**(17~52 행)에 `chk_drive_gate.py` · `run_slam_replay.sh` · `slam_replay_feed.py` 행이 없다(파일은 `Docs/tools/` 에 있음, 자동 색인 [JOBS](index/JOBS.md) 29 · 45 행에는 있음).
4. **러너 머리 주석**: `job551_f0drive.sh` 2 행 '… → bag·tegrastats·top·RSS → …' — top 은 10-27 에 뺐다(74~75 행). `run_f0.sh` 16 행 회수 목록에도 `top_$NAME.log` 가 남아 있음(없으면 조용히 건너뜀, 동작 영향 없음).
5. (참고) 11-02 §2 가 '10-27 §24 같은 값(새 게이트 C FAIL)' 을 어긋남으로 꼽았다가 11-03 이 '원문 337 행이 FAIL 을 이미 적음' 으로 철회 — 이 카드도 철회 쪽과 같다.

### 5.3 그 밖의 작은 실수(SUMMARY 서술)
- `chk_prep.py` 출력 이름표: Critic 세 값이 모두 'PreferForward' 로 찍힘(10-27 판 135 행 이름 자르기) → 고침, 10-28 확인. 값은 맞았음.
- `prep_smac_1027b.sh`(grep 필터판) 무출력 11 s — 원인 미확인. 교훈으로 prep 원문을 파일(`/tmp/prep_full_<n>.txt`)에 남기고 요약만 출력하는 방식(`run_prep_full_1027.sh` · `prep_smac_1028.sh`)이 됨.

## 6. 남은 것
- **게이트 C 의 실제 관찰 창**(카드 작성 중 발견): 관찰 루프는 노드 시작부터 5 s 인데 수신 수가 `20 개/5 s`(f2tt1) · 56 · 65 · 72(f2tt2) · 95 · 100 · 101 로 흔들린다(map→odom 은 20 Hz 발행). f2tt1 은 최대 간격 0.05 s 인데 20 개 = 실제 수신 ≈ 1 s — 새 참여자의 `/tf` 구독이 맺어지기까지 수 초 걸린 것으로 **추정**(10-20 §9.7 의 `ros2 topic hz` 첫 출력 4.5~5.6 s 와 같은 꼴). 그러면 '5 s 동안 간격 < 0.5 s' 는 실제로는 1~5 s 동안만 본 것이다. B 도 같은 구조(첫 · 마지막 수신 사이로 Hz 계산). 대안(결정 안 함): 첫 수신부터 SEC 를 세기.
  원문: [`run_f2tt1.txt`](../debug_log/2026-10-27/outputs/drives/f2tt1/run_f2tt1.txt) 4 행 · [`f0_f2tt2.log`](../debug_log/2026-10-28/outputs/drives/f2tt2/f0_f2tt2/f0_f2tt2.log) 3 행 · `2026-10-28/outputs/drives/f2pl{1..5}/place_s1.log` · [`cmp_gate_1027.txt`](../debug_log/2026-10-27/outputs/gate/cmp_gate_1027.txt). 셈은 카드 작성 중 `grep -rhao 'C map->odom …'` 로(원문 없음 — 위 값이 전부).
- **C 문턱의 뜻**: lag = 수신 − stamp 라 timeout 1.5 에서 평소 −1.3~−1.45 s. 문턱 1.0 은 stamp 가 ≈ 2.5 s 넘게 멈춰야 걸린다 — nav2 가 실패하기 시작하는 1.5 s 정체는 통과. 10-27 §24 의 옛 C 0.38 s · 새 C 1.14 s 는 그 순간 정체가 ≈ 1.9 · 2.6 s 였다는 뜻(계산, 카드 작성 중), f2pl1 의 0.92 s 는 ≈ 2.4 s(통과). '생존 검사로 그대로 둠'(§24)은 결정이지만, 실패 창을 거르는 검사는 없다.
- 30 s 규칙의 수치 근거 · P 문턱 60 % 의 근거(경험값) — [DDS 카드](pre-drive-dds-participants.md) · [8 기 운용 카드](drive-ops-1019-1023.md) 그대로.
- 러너 게이트 노드 사본(스크래치패드)과 저장소 판의 일치를 주행마다 남기는 방법(§4.3).
- `TEST_COURSE_AND_GATES.md` 게이트 표 · `Docs/tools/README.md` 갱신(§5.2-2 · 3) — 문서 작업, 결정 대기.

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| 정지 비교(10-27 §24) | 옛 / 새 게이트 같은 상태 | [`outputs/gate/cmp_gate_1027.txt`](../debug_log/2026-10-27/outputs/gate/cmp_gate_1027.txt) · [`chk_slam_idle_1027.txt`](../debug_log/2026-10-27/outputs/gate/chk_slam_idle_1027.txt) |
| prep 1027b · prep_full_1027b | 필터판 무출력 · 필터 없는 판 PREP_OK | `outputs/gate/prep_1027b.txt` · `prep_full_1027b.txt` |
| f2tf1 | 정리 전 마지막 주행(게이트 → 주행 66 s) | `2026-10-27/outputs/drives/f2tf1/` |
| f2tt1 · f2tt2 | 정리판 첫 · 두 번째 실주행(40 s) | `2026-10-27/outputs/drives/f2tt1/` · `2026-10-28/outputs/drives/f2tt2/` |
| f2pl1 ~ f2pl5 | 같은 게이트 노드를 쓴 장소 이동 러너 | `2026-10-28/outputs/drives/f2pl*/place_s1.log` |
| `chk_drive_gate.py` · `chk_prep.py` | 게이트 · prep 확인 노드 | `Docs/tools/` |
| `job551_f0drive.sh` · `run_f0.sh` | 러너(사본) | `2026-10-27/jobs/`(10-27 판) · `2026-11-03/jobs/job551_f0drive.sh`(최신 사본) · 이전 판 `2026-10-21/jobs/` |
| `cmp_gate_1027.sh` · `chk_slam_idle_1027.sh` | 비교 · 정지 SLAM 20 s | `2026-10-27/jobs/` |
| `prep_smac_1027b.sh` · `run_prep_full_1027.sh` · `prep_smac_1028.sh` · `up_prep_1028.sh` · `get_f2tt2.sh` | prep 래퍼 · 재전송 · 회수 | `2026-10-27/jobs/` · `2026-10-28/jobs/` |
| (옛) `job386_slamalive.py` · `job440_startclear.py` | 옛 C · G2 | `2026-09-17/jobs/` · `2026-09-18/jobs/` |

## 8. 도구 해설
공통: 게이트 · prep 도구는 Jetson 에서 rclpy 노드 하나로 돈다(로버 안 움직임). PC 쪽 전송 · 실행은 스크래치패드 러너(`run_jn.sh` · `run_f0.sh` · `run_f2c.sh`, 저장소엔 `<PW>` 가린 사본).

### 8.1 `Docs/tools/chk_drive_gate.py` — 주행 직전 게이트 B · C · G2 한 노드 (10-27 §24) ★
- 실행 위치 · 형태: Jetson, 러너가 `timeout 40 python3 /tmp/chk_drive_gate.py`(인자 = 관찰 s, 기본 5). `chk_slam_idle_1027.sh` 는 `chk_drive_gate.py 20` 으로 20 s 관찰에 씀.
- 왜: 같은 기준의 세 검사가 참여자 3 개 · 약 24 s 를 쓰고, 주행 직전 참여자 생성을 줄이자는 규칙([DDS 카드](pre-drive-dds-participants.md))과 어긋났다.
- 하는 일(코드 기준):
  1. 노드 `drive_gate` 하나에 구독 넷: `/wheel_odom`(수신 시각), `/tf`(map→odom 이면 `(지금, 지금 − stamp)`), `/local_costmap/costmap`(transient local · reliable, 마지막 한 장), `/scan`(마지막 한 장) + TF 버퍼.
  2. SEC(5 s) 동안 spin, 코스트맵 · 스캔이 아직 없으면 12 s 까지 더(39 행).
  3. B: 받은 `/wheel_odom` 이 3 개 이상이면 `(n − 1) / (마지막 − 처음)` Hz(아니면 0), ≥ 1 Hz 면 OK(옛 기준 '평균이 찍히면 통과' 를 옮김).
  4. C(job386 그대로): 수신 간격 최대 < 0.5 s 그리고 지연 최대 < 1.0 s.
  5. G2(job440 그대로): 코스트맵 프레임 ← base_link TF(10 s 기다림) → 값 ≥ 100 칸 중심을 차체 좌표로 → 사각형 바깥 거리 최소; 스캔은 base_link ← 라이다 TF 로 2 m 안 점을 옮겨 같은 거리; 둘 중 작은 값.
  6. 마지막 줄 `GATE B=<OK|FAIL> C=<OK|FAIL> G2=<m|nan>`. G2 문턱 0.10 은 러너 쪽.
- 출력: 게이트 줄 4~5 개 + `게이트 노드 5.0 s` + GATE 줄(§4.1 발췌). 남은 곳: 각 주행 러너 출력(`run_<주행>.txt` · `f0_<주행>.log` · `place_s1.log`).
- 쓰인 곳: 10-27 §24 비교 · §25 f2tt1 · 10-28 §4 f2tt2 · f2pl1~5.
- 계보: `job254_s4run.sh`(A · B, 게이트 표 근거 09-11 · 사본 `2026-09-18/jobs/`) → `job386`(09-17 C) · `job440`(09-18 G2) → 10-23 까지 `job551` 안에서 따로 → 이 노드. 알려진 결함: 관찰 창이 노드 시작 기준(§6) · C 지연 문턱이 timeout 0.2 시절 값 · G2 코스트맵 칸 판정은 칸 중심 기준(칸 크기 5 cm 만큼 거칠다). 지금 운용 도구.

### 8.2 `Docs/tools/chk_prep.py` 의 PARAMS 확장 (10-27 §24)
- 형태: `prep_fast.sh` 66 행이 부름(인자 WAIT 15 · 한도 150 s). 이 카드 범위는 PARAMS 확장(36~42 행) — 전체 해설은 [빠른 prep 카드](prep-fast-startup.md) · 출발 위치 검사는 [8 기 운용 카드 §8.1](drive-ops-1019-1023.md).
- 하는 일: 노드마다 `GetParameters` 서비스를 비동기로 한 번 부르고 응답 개수가 맞으면 저장(79~88 행 — 백오프 없는 재요청은 8 기 카드가 적은 결함 그대로). 출력은 노드별 한 줄, `Critic` 이 든 이름은 크리틱 이름으로 줄여 찍음(135 행).
- 판정에 주는 영향: 없음(기록). 값이 틀려도 PREP_OK — 사람이 출력 줄을 읽어 확인한다(10-27 §24 · 10-28 §2 가 그렇게 함).

### 8.3 러너 `job551_f0drive.sh` (10-27 판 · 11-03 사본) — 게이트 부분
- 형태: Jetson `setsid nohup bash /tmp/job551_f0drive.sh NAME "GOALS" [SPEED] [PAUSE]`, 환경 `LOAD_MAX` · `G2_SKIP` · `NET_LOG` 등. PC `run_f0.sh` 가 파일 전송(7~9 행) · 기동(10 행) · 2 s 폴링(11~15 행) · 회수(16 행).
- 10-21 판 대비 바뀐 줄(diff, 13 줄 추가 · 10 줄 삭제): B 의 `ros2 topic hz` → 게이트 노드, C 의 `job386` → GATE 줄 grep, G2 의 `job440` → GATE 줄에서 값, `sleep 30` → `sleep 20`, top 루프 삭제, UDP 기록 `NET_LOG=1` 조건.
- 출력 예: §4.1 f2tt1 발췌. 불합격이면 '… — 주행하지 않음' 한 줄 뒤 종료 코드 1, PC 폴링이 이 문자열로 멈춤(`run_f0.sh` 14 행).
- 결함: §4.3(게이트 노드 사본 경로) · §5.2-4(낡은 주석).

### 8.4 `cmp_gate_1027.sh` · `chk_slam_idle_1027.sh` (10-27 §24, Jetson, bash)
- `cmp_gate_1027.sh`: 같은 정지 상태에서 옛 B(`timeout 12 ros2 topic hz`) · 옛 C(job386) · 옛 G2(`timeout 60` job440) · 새 노드를 차례로 돌리고 각자 걸린 시간을 `bc` 로. 출력 §4.1. 한계: 차례로 돌려 C 는 같은 순간이 아님(7 s 차).
- `chk_slam_idle_1027.sh`: 새 노드를 20 s 관찰로 돌려 C 줄 · GATE 줄 + slam.log 스캔 버림 수 · 최근 3 줄. 출력 `C map->odom 379 개/20 s, 최대 간격 0.07 s, 최대 stamp 지연 -0.27 s` · `slam 스캔 버림(전체) 15`. 쓰인 곳: '새 노드 결함 아님' 판단.

### 8.5 prep 래퍼 `prep_smac_1027b.sh` → `run_prep_full_1027.sh` → `prep_smac_1028.sh` (+ `up_prep_1028.sh`)
- `prep_smac_1027b.sh`: `NAV_ADD="planner:=smac" REPLAN_HZ=0.01 bash /tmp/prep_patrol.sh lite` 출력을 grep 필터 · `tail -24` 로 + BT 사본 확인 한 줄. 결과는 BT 줄만(원인 미확인).
- `run_prep_full_1027.sh`: 같은 prep 을 `/tmp/prep_full_1027b.txt` 로 통째로 남기고 `tail -45`.
- `prep_smac_1028.sh`: 먼저 `/tmp` 의 네 도구 git blob · CR 수를 찍고(3 행 — PC HEAD 와 대조용), 같은 prep 원문을 `/tmp/prep_full_<n>.txt` 에 두고 요약 줄만. `up_prep_1028.sh` 는 스크래치패드 `tools_<이름>` 사본을 CR 제거 · scp 한 뒤 이 래퍼를 `run_jn.sh` 로 부름.
- 계보: 10-23 `prep_rp_1023.sh` · `chk_rp_cfg.sh`([경로 추종 카드](path-tracking-replan-b0.md)) → 이 판. 지금 다시 쓸 수 있음(Smac 시험 구성 prep 의 본보기).

### 8.6 `get_f2tt2.sh` (10-28 §4, PC → Jetson, 읽기만)
- PC 폴링이 끊긴 주행의 산출물(`f0_` 로그 · csv · tegra · rss · proc · bag tgz · net) · nav2/slam/sensors 로그를 `scp` 로 회수. §5.1 실수 뒤 회수 절차의 본보기.

## 9. 용어
- **게이트**: 주행 전에 러너가 자동으로 거는 통과 조건. 이 카드의 A(프로세스) · B(보드 `/wheel_odom`) · J(nvblox) · C(SLAM map→odom) · G2(출발 자세 여유 ≥ 0.10 m) · P(정지 부하 ≤ 60 %).
- **게이트 노드**: B · C · G2 를 한 rclpy 노드(DDS 참여자 1 개)로 재는 `chk_drive_gate.py`.
- **관찰 창**: 게이트가 토픽을 받아 보는 시간(기본 5 s). 새 참여자는 구독이 맺어지기까지 수 초 걸릴 수 있어(추정) 실제로 받은 시간은 더 짧을 수 있다.
- **stamp 지연(게이트 C)**: 수신 시각 − map→odom stamp. SLAM 이 stamp 를 미래(transform_timeout)로 찍으므로 평소 음수(1.5 s 면 ≈ −1.45 s).
- **PARAMS(chk_prep)**: prep 확인 노드가 조회해 출력만 하는 실행 중 파라미터 목록 — 판정에는 안 씀.
- **setsid nohup**: Jetson 에서 러너를 ssh 세션과 떼어 띄우는 방식 — PC 연결이 끊겨도 주행은 계속된다.
