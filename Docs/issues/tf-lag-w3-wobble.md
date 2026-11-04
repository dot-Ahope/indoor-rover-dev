# W3 통로 저속 떨림과 'TF 지연' 가설 — 컨트롤러 중단은 map→odom stamp 정체, 떨림 자체는 미확정

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **조사 중** — 떨림(저속 · ω 부호 잦은 바뀜) 원인 미확정. 같은 창의 follow_path 중단은 TF(map→odom stamp 1.49 s 멈춤)로 판정 → MPPI `transform_tolerance` 0.2 → 0.5 로 **우회**(이 시기 효과 미측정) | 10-07 (6 기) · 10-12 ~ 10-13 (7 기 — 같은 오류 서명의 통신 포화는 [별도 카드](network-saturation-mppi-viz.md), §7.1) · 이후(10-19 ~) | [10-07 §2.4](../debug_log/2026-10-07/SUMMARY.md) 사용자 "지금도 전진하면서 이상하게 움직이고 있다"(f2c2, PC 11:12 무렵) | `ros2_ws/src/rover_navigation/config/nav2_params.yaml`(`FollowPathMPPI.transform_tolerance` 0.2 → 0.5, 커밋 `a096f227`) · `navigation.launch.py`(`mppi_viz` 인자 신설, 커밋 `e3e1fe88` — 이 카드 문제의 조치는 아니지만 10-12 포화의 출발점) | [SLAM map→odom 시각 정체](slam-stamp-freeze.md)(같은 중단 기제의 10-01 · 10-27 판) · [통신 포화 — MPPI 궤적 발행 · reliable `/tf` 기록기](network-saturation-mppi-viz.md)(10-12 ~ 13, 같은 '미래 시각 TF' 오류를 내는 다른 기전) · ['후진하고 멈췄다' — CPU · 위치 추정 정지](cpu-load-stalls.md)(같은 'TF 조회 실패' 서명의 09-09 판) · [주행 직전 DDS 참여자 금지](pre-drive-dds-participants.md)(통신 부하 계열) · [DDS 공유메모리 사고](dds-shm-incident.md) · [MPPI 조향 흔들림 · temperature](mppi-wobble-temperature.md)(떨림 후보 ② 의 ESS 기제) · [rf2o 도입](rf2o-introduction.md)(f2c 주행의 목적) · [pad_relief · 실행 중 패딩](pad-relief-runtime-padding.md) (7 기) · [cuVSLAM 속도 융합](cuvslam-velocity-fusion.md) · [경로 추종 · B0](path-tracking-replan-b0.md) (8 기) · [nvblox 층 TF 실패](nvblox-layer-tf-drop.md) · [주행 전 검사 정리](drive-gate-consolidation.md) (9 기) |

**한 줄**: 10-07 rf2o 켠 F2 순회 f2c2 의 W3 통로(직선 1.7 m)에서 로버가 0.035 m/s 로 느리게 가며 ω 부호를 6 s 에 21~34 번 바꿨다(좌우 떨림). 떨림이 끝난 경계 t ≈ 235 에 컨트롤러가 `Exception in transformPose: Lookup would require extrapolation into the future` 로 중단돼, 'TF 가 늦어 MPPI 가 묵은 자세로 떤다' 는 가설을 세우고 bag 의 수신 − stamp 지연을 6 s 창으로 쟀다(`job917`). 떨림 구간과 매끄러운 구간의 지연이 같아 **떨림에 대한 TF 가설은 기각**, 다만 t 234~240 창에서만 map→odom stamp 간격이 **1.49 s** 로 벌어져 t 235 중단의 원인은 TF(SLAM stamp 정체가 미래 여유 0.5 s 를 넘김)로 판정했다. MPPI `transform_tolerance` 를 0.5 로 올렸지만 다음 주행(f2d1 · f2d2)에서 효과도, 떨림 재발 여부도 보고하지 않았다. 떨림 원인 후보(오래된 계획 유지 · MPPI 표본 분포)는 미검증.

## 1. 증상
- 사용자(10-07 §2.4, 주행 중): "지금도 전진하면서 이상하게 움직이고 있다". 그 시각 나는 로그만 읽었다(DDS 참여자 만들지 않음, `jobs/job911_navtail.sh` → [`outputs/j911_navtail_1112.txt`](../debug_log/2026-10-07/outputs/j911_navtail_1112.txt)).
- 10-07 §3.5(주행 뒤 bag, 러너 t 기준 — t 0 = epoch 1791338894): t 188~236 동안 통로 (−1.24 → 0.47, −2.05) 1.7 m 를 48 s(**0.035 m/s**), cmd v 0.033~0.058 ± 0.02 로 출렁, **ω 부호가 6 s 에 21~34 번 바뀜**, 방향은 일정. t 236 이후 v 0.08 고정 · 부호 바뀜 0~18 → 매끄러움.
  - ⚠ 이 속도 · 부호 바뀜 수치를 낸 스크립트와 출력이 저장소에 없다(`jobs/` · `outputs/` 어디에도 부호 세기 코드 없음) → **원천 소실**(SUMMARY 서술만). 입력 bag 은 PC 에 남아 있다: `Docs/debug_log/2026-10-07/bags/bag_f2c2.tgz`(git 제외) — `/cmd_vel` 로 다시 셀 수 있음.
- 경계 t ≈ 235(= 11:12:09) 원문([`outputs/j914_w3log.txt`](../debug_log/2026-10-07/outputs/j914_w3log.txt), 첫 줄 WSL 경고는 깨진 글자 · NUL 바이트라 뺌):
  ```
  [ERROR] [1791339129.331844627] [controller_server]: Exception in transformPose: Lookup would require extrapolation into the future.  Requested time 1791339129.089612 but the latest data is at time 179…
  [ERROR] [1791339129.332093627] [controller_server]: Unable to transform robot pose into global plan's frame
  [WARN] [1791339129.332281024] [controller_server]: [follow_path] [ActionServer] Aborting handle.
  [INFO] [1791339129.343584163] [local_costmap.local_costmap]: Received request to clear except a region the local_costmap
  …
  [INFO] [1791339129.586758277] [behavior_server]: Running wait
  [INFO] [1791339134.590420174] [behavior_server]: wait completed successfully
  ```
  → 중단 · 로컬 정리 · wait 5 s · 재계획 뒤 정상 주행.

## 2. 흐름 (시간순)
jobs 는 [2026-10-07/jobs/](../debug_log/2026-10-07/jobs/), 출력은 [2026-10-07/outputs/](../debug_log/2026-10-07/outputs/). 도구 대부분은 Jetson 에서 `/tmp/bag_f2c2` · `/tmp/nav2.log` 를 읽었다(nav2.log 원본은 Jetson `/tmp` — 이후 prep 이 덮음 → 원문 발췌 파일만 남음).

| 날짜 § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-07 §2.4 | 주행 중 관찰 → 로그만 읽음 | 러너 로그 tail 이 '주행 11:08:14' 머리줄에서 멈춤 · nav_guard 남은 거리 1.75 → **7.26 m** · 11:12:09 follow_path 중단 | '목표 5(D)가 4 분 넘게 결과 없음 · 재계획이 먼 우회로' — **틀림**(같은 § 정정: D 는 41.3 s 성공, 7.26 m 는 W3 직선 7.1 m 의 정상 경로) → §5.1 | `job911_navtail.sh` → `j911_navtail_1112.txt` |
| §3.5 | 떨림 현상 측정 | 위 §1 수치 · 경계 t 235 외삽 오류 2 회 | 현상은 측정, 원인 미확정 | 속도 · 부호 수치 원천 소실 · `job914_w3log.sh` → `j914_w3log.txt` |
| §3.5 | 로컬 코스트맵이 통로를 좁혔나 | 옆 치명 칸 외곽까지 0.47~0.70 m(SUMMARY) · 앞 띠(차체 폭 ±0.27, 앞 1.2 m) 치명 0, t 207 한 번 카메라만 3 칸 | 아님 — 단 SUMMARY 범위가 t 188(왼 **0.112**) · t 209(오 **−0.077**) 두 표본을 뺐다(§6-1) | `f2c2_w3cost.py` → [`f2c2_w3cost.txt`](../debug_log/2026-10-07/outputs/f2c2_w3cost.txt) · `f2c2_w3ahead.py` → [`f2c2_w3ahead.txt`](../debug_log/2026-10-07/outputs/f2c2_w3ahead.txt) |
| §3.5 | map→odom TF 수신 간격 | 0.05 s 일정, 0.5 s 넘는 틈 0 | TF 끊김 없음 — **잰 양이 '수신' 간격**이라 stamp 정체를 못 봄(§6-2) | 원천 소실(스크립트 · 출력 없음) |
| §3.5 | 후보 정리 | 컨트롤 10 Hz 놓침 경고 '이 구간 1~2 건' | 후보 ① TF 시각(외삽 오류가 신호) ② CPU — 미검증 | `j914_w3log.txt`(§6-7) |
| §5 선언 | 판정 기준을 분석 **전에** 적음 | — | 떨림 구간(t 188~236)에서만 지연 · stamp 간격이 커지면 TF 가설 채택, 매끄러운 구간(t 240~300)과 같으면 기각 | SUMMARY §5 |
| §5 | 6 s 창별 수신 − stamp 지연 · stamp 간격(bag) | odom→base · /odometry 0.01/≤ 0.14 s, /scan 0.00~0.01, 로컬 코스트맵 0.00 — 두 구간 같음. map→odom 은 stamp 가 수신보다 0.38~0.44 s **미래**, stamp 간격 최대 0.11~0.78 s, **t 234~240 창만 1.49 s**(지연 최대 +1.03 s) | **떨림에 대한 TF 가설 기각** · t 235 중단 원인 = SLAM map→odom stamp 1.49 s 멈춤 → 미래 여유 0.5 s 소진(10-01 f2a1 · f2a2 와 같은 기제) | `job917_tflag.py` · `job917_run.sh` → [`j917_tflag.txt`](../debug_log/2026-10-07/outputs/j917_tflag.txt) |
| §5 | 계획 경로 대비 자세(4 s 마다) | t 204~236 옆 +0.007~+0.017 m · 방향 −2~+4° · 쓰인 계획 = t 183 판 계속, t 244 부터 t 241 판 | '경로 위에 정확히 있으면서 느림' — 경로 이탈 가설 기각. 떨림 끝 = 중단 뒤 재계획(t 241) | `f2c2_w3lat.py` → [`f2c2_w3lat.txt`](../debug_log/2026-10-07/outputs/f2c2_w3lat.txt) |
| §5 | 떨림 원인 후보 | t 176 목표 시작에도 'Optimizer reset' 있음 | reset 만으로는 설명 안 됨. 남은 후보(추정) ① t 183 계획(출발 회전 포함 290 점)을 58 s 그대로 씀 ② MPPI 표본이 저속 쪽에 머묾(09-17 §12 ESS 기제 관련 가능) — 오프라인 MPPI 재현으로만 가름 | 미검증 |
| §6 | MPPI `transform_tolerance` 0.2 → 0.5 · F2 재주행 선언 | 관찰 항목 선언: 'transformPose 중단 0 회 · W3 저속 떨림(6 s 창 cmd v 평균 < 0.05 이고 ω 부호 바뀜 ≥ 20) 재발 여부 — 재발하면 계획 나이 기록' | 우회 조치 | 커밋 `a096f227` |
| §6.1 | prep 뒤 새 설정 반영 확인 | prep 출력은 `MPPI transform_tolerance … 0.2` — 실제로는 RPP `FollowPath` 를 읽음. `job919` · `job920` 로 `FollowPathMPPI.transform_tolerance` **0.5** 확인 | 반영 확인(첫 확인은 **내 오독** → §5.2). BT RateController 는 첫 틱 · 목표 변경 · 실패 때만 재계획(BT 주석) — 후보 ① 과 맞는 구조 | [`j918_prep.txt`](../debug_log/2026-10-07/outputs/j918_prep.txt) · `job919_chk.sh` · `job920_chk.sh`(출력 원천 소실) |
| §6.2 · §7.1 | f2d1(목표 1~4) · f2d2(목표 5~10) | f2d2 목표 9 W3 **96.3 s**(f2c2 126.7 s). 중단 원인은 남서 방향 맞춤 · 상자 ② 정지 — TF 와 무관 | §6 의 관찰 항목(TF 중단 0 · W3 떨림 재발)을 **보고하지 않음**(§6-5) | `f0_f2d1_runner.log` · `f0_f2d2_runner.log`(nav2 로그 아님) · bag `bags/bag_f2d1.tgz` · `bag_f2d2.tgz` |
| §11 | 장기 주행만 MPPI 후보 궤적 발행 · 기록 | `mppi_viz:=true` → visualize true · `trajectory_step 20` · `time_step 2` | 시각화용 — 부하 측정 없음. 10-12 §7.3 에서 이 설정이 통신 포화의 한 축으로 드러남(→ 이후) | 커밋 `e3e1fe88` · `jobs/job932_topics.sh` |
| §15 | 하루 결론 | — | 'W3 저속 떨림: TF 지연 가설 기각, 원인 미확정. 11:12 중단은 slam map→odom stamp 1.49 s 멈춤 → MPPI transform_tolerance 0.5' | SUMMARY §15 |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 로컬 코스트맵 치명 칸이 통로를 좁혀 MPPI 가 망설임 | `f2c2_w3cost` · `w3ahead`: 차체 앞뒤 1 m 안 옆 치명 칸 거리 · 진행 앞 띠 치명 칸 수 | 옆 0.47~0.70 m(t 193~205) · 0.60~0.94 m(t 212~260), 앞 띠 치명 0(t 207 만 3 칸, 전부 카메라만) | **기각**(측정). 단 t 188 왼 0.112 · t 209 오 −0.077 두 표본은 설명 없이 빠짐(§6-1) — 순간 칸이 차체 안까지 들어온 것으로 보이나 미분석 |
| TF · 토픽 지연이 떨림 구간에서만 큼(MPPI 가 묵은 자세 사용) | `job917`: 6 s 창 30 개, 수신 − stamp 중앙/최대 | odom→base 0.01/0.02~0.14, /odometry 동일, /scan 0.00~0.01, 로컬 코스트맵 0.00/≤ 0.01 — 떨림 · 매끄러운 구간 같음 | **기각**(측정, §5 선언 기준). 한계: '수신' 은 bag 기록기의 수신 시각이지 컨트롤러의 것이 아님(§9.6 결함) |
| map→odom stamp 정체가 t 235 중단을 일으킴 | `job917` stamp 간격 · 외삽 오류 원문 | t 234~240 창만 1.49 s · 지연 최대 +1.03 s. 오류: 요청 …129.089612 vs 최신 …129.083021(**6.6 ms** 모자람) | **지지**(측정) — 10-01 f2a1 · f2a2 와 같은 기제([SLAM 시각 정체 카드](slam-stamp-freeze.md)) |
| map→odom stamp 정체가 떨림 전체를 일으킴 | 같은 표 다른 창 | 떨림 창들의 stamp 간격 0.11~0.61 s 는 매끄러운 창(0.11~0.78 s)과 같은 범위 | **기각** |
| 로버가 경로를 벗어나 MPPI 가 되돌리려 떪 | `f2c2_w3lat` | t 204~236 옆 ≤ 0.017 m · 방향 −2~+4° | **기각** |
| CPU 부족(컨트롤 10 Hz 놓침) | `j914_w3log.txt` 경고 시각 | 떨림 창(t 188~236) 안 1 건(epoch …113.93 = t 219.9), 바로 앞 t 185.4~185.8 에 3 건 | **약함 · 미확인** — 이 창의 CPU · load 측정 없음 |
| 오래된 계획(t 183 판)을 58 s 그대로 써서 | `f2c2_w3lat` 계획 시각 · BT 주석 | t 183 판 → t 241 판 바뀐 직후부터 매끄러움, BT 는 막힘 · 실패 때만 재계획 | **정황 일치 · 미검증**(재계획 없이 같은 계획을 오래 쓴 다른 구간과 비교 안 함) |
| MPPI 표본 분포가 저속 쪽에 머묾(ESS) | 오프라인 MPPI 재현 필요 | 시험 안 함 | **미확인** — 09-17 §12 ESS 기제 자체가 실주행에서 확인 안 됨(`nav2_params.yaml` 234 행 temperature 주석, 11-02 정리) |
| (참고) W3 바닥 전선 | 좌표 | 떨림 구간 x −1.24~0.47 은 09-29 전선 흔들림 창(x 4.9~5.4) 에서 4 m 넘게 떨어짐(계산) | 무관으로 봄 — [전선 밟기 카드](cable-step-over.md) |

## 4. 조치와 효과
- **`FollowPathMPPI.transform_tolerance` 0.2 → 0.5**(10-07 §6, 커밋 `a096f227`). 그날의 근거 주석(지금 `nav2_params.yaml` 230~233 행):
  ```yaml
  # ★ 2026-10-07 §5·§6: 0.2 → 0.5. slam 의 map→odom stamp 가 1.49 s 멈춰 '미래 여유'(transform_timeout 0.5)를 다 쓰자
  #   MPPI 경로 변환이 6.6 ms 차로 실패 → follow_path 중단·wait 5 s(f2c2 t 235, 같은 오류 7 회). 10-01 f2a1·f2a2 와 같은 기제.
  #   대가: 최대 0.5 s 묵은 map→odom 으로 경로를 odom 에 옮길 수 있으나 map→odom 은 느리게 변하는 보정값이라 영향 작음(추정).
  transform_tolerance: 0.5
  ```
  - 효과: **이 시기 미측정**. f2d1 · f2d2 의 nav2 로그는 저장되지 않았고(Jetson `/tmp/nav2.log` → 원천 소실), 러너 로그(`f0_f2d1_runner.log` · `f0_f2d2_runner.log`)에는 nav2 오류 줄이 들어가지 않는다(`grep -ac transformPose` = 0 은 '오류 0' 이 아니라 '기록 안 함'). bag 은 남아 있어(`bags/bag_f2d1.tgz` · `bag_f2d2.tgz`) `/rosout` 이 녹화돼 있으면 다시 셀 수 있다(녹화 토픽 미확인).
  - 이 값이 '기다리는 시간' 인지 '허용 오차' 인지(상류 Nav2 Humble 의 쓰임)는 코드로 확인하지 않았다 — **미확인**. 이후 10-21 §12 에서 0.5 인데도 같은 예외가 50 회 남았고(요청이 최신보다 0.004~0.088 s 앞섬), 그 기전도 미확인으로 남았다(→ 이후).
  - 같은 날 SUMMARY §5 가 함께 적은 '로컬 코스트맵 transform_tolerance(지금 0.2)' 는 바꾸지 않았다 — 그리고 그 0.2 는 로컬 코스트맵 자체가 아니라 `stvl_layer` 의 값이었다(§6-6).
- 떨림 자체에는 조치 없음. §6 에 재발 관찰 항목만 선언.

### 4.1 지금 코드에서 이 문제와 닿는 곳 (11-02 확인, 바꾸지 않음)
| 항목 | 지금 값 · 위치 | 이 카드와의 관계 |
|---|---|---|
| MPPI 경로 변환 허용 | `transform_tolerance: 0.5` — `ros2_ws/src/rover_navigation/config/nav2_params.yaml:233`(블록 `FollowPathMPPI:` 200 행) | 10-07 조치 그대로 |
| RPP 경로 변환 허용 | `transform_tolerance: 0.2` — 같은 파일 `:136`(블록 `FollowPath:`, `controller_plugins: ["FollowPath", "FollowPathMPPI"]` 90 행) | BT 가 쓰지 않는 플러그인 — 10-07 prep 확인이 이 값을 읽었다(§5.2) |
| 코스트맵 쪽 | `:403` · `:606` 의 0.2 는 `stvl_layer` 안 값, `:822` 는 `wait` 행동 — 로컬 · 전역 코스트맵 블록에는 `transform_tolerance` 키가 없음(상류 기본값 사용, 값은 확인 안 함) | §6-6 |
| SLAM 미래 여유 | `'transform_timeout': 1.5` — `ros2_ws/src/rover_bringup/launch/slam.launch.py:77`(10-01 0.2 → 0.5, 10-27 §21 → 1.5, 주석 67~76 행) | 이 카드의 t 235 정체(1.49 s)는 지금 여유 1.5 s 면 덮였을 크기(계산 — 1.49 < 1.5, 재생으로 확인 안 함) |
| 주행 전 게이트 C | `Docs/tools/chk_drive_gate.py:6`(설명) · `:47~48`: `gap = max(수신 간격)` · `lag = max(수신 − stamp)` → `C = 'OK' if (gap < 0.5 and lag < 1.0)`, 관찰 5 s(`SEC` 기본 5.0, 19 행) | 주행 **전** 5 s 만 본다 — 주행 중 정체(t 235 같은)는 못 잡음. 또 `gap` 은 **수신** 간격이라 §3.5 처럼 stamp 정체를 놓친다(SLAM 이 같은 stamp 를 계속 다시 보냄). `lag` 문턱 1.0 은 stamp 가 미래(지금 +1.5 s)로 찍히므로 stamp 가 약 2.5 s 넘게 멈춰야 걸린다(계산). 판정 기준의 출처는 09-17 `job386_slamalive.py`(정상 SLAM 지연 −0.08~+0.55 s, 고장 때 간격 5.1 · 지연 4.8 s) |
| MPPI 궤적 발행 | `navigation.launch.py:205`(`mppi_viz` 기본 `'false'`) · `:136~140`(`true` → `trajectory_step 20 · time_step 2`, `lite` → `100 · 4`) · 주석 `:130~135`(10-12 §7.3: true 206 kB × 10 Hz, PreferForward 15 와 함께 4/4 포화) | 10-07 §11 신설 → 10-12 포화([통신 포화 카드](network-saturation-mppi-viz.md) — 지금 순회 prep 기본 `lite`, `Docs/tools/prep_patrol.sh:8`) |
| prep 파라미터 확인 | `Docs/tools/chk_prep.py:31~33` — `FollowPathMPPI.*`(PreferForward · vx_min · visualize · TrajectoryVisualizer · PathAlign · PathFollow)는 보지만 `transform_tolerance` 는 목록에 없음 | §5.2 의 같은 실수는 지금 도구에서는 안 생기지만, 이 값의 반영 확인도 하지 않는다 |

## 5. 내 실수
### 5.1 '목표 5 가 4 분 넘게 결과 없음' — 늦게 쌓인 러너 출력을 '결과 없음' 으로 읽음 (10-07 §2.4, 같은 § 에서 정정)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 주행 중 사용자 관찰("이상하게 움직임")에 DDS 참여자 없이 로그만으로 답하기 — `jobs/job911_navtail.sh` |
| 본 것 | 러너 로그 tail 4 줄이 `F0 주행 11:08:14` 머리줄에서 끝남(11:12:27 시점), nav_guard `남은 거리 1.75 m` → `7.26 m`, 11:12:09 follow_path 중단 |
| 처음 추론 | '목표 5(D, 직선 2.8 m)가 출발 4 분 넘게 결과 없음(f2b 의 D 는 45.4 s) · 재계획이 먼 우회로를 고름' |
| 의심한 이유 | 주행 뒤 러너 결과: 목표 5 는 41.3 s SUCCEEDED. 7.26 m 는 그 시각 목표가 W3(직선 7.1 m)라는 것과 맞음 |
| 판별 시험 | 주행 뒤 러너 출력 · nav_guard 목표 id 대조(SUMMARY §2.4 정정, §2.5 표) |
| 결론 | 결과 줄이 아직 파일에 안 쓰였던 것. SUMMARY 는 'PC 로 늦게 넘어온 것' 이라 적었지만 `job911` 이 읽은 것은 Jetson 쪽 `/tmp/f0_f2c2.log` 다 — 왜 4 분 동안 결과 줄이 없었는지(출력 버퍼링 추정)는 **미확인** |
| 다음에 알아보는 법 | 러너 '결과 없음' 은 nav_guard 의 **목표 id**(`목표 8df9abaa` · `ed69588c`)가 바뀌었는지로 먼저 본다 — id 가 바뀌었으면 앞 목표는 끝난 것. 남은 거리가 갑자기 커지면 '우회' 보다 '다음 목표' 를 먼저 의심 |
| 스크립트 핵심 | `tail -4 /tmp/f0_f2c2.log` · `grep -aE "PathBlocked|nav_guard|Fail|fail|Abort|abort|Optimizer|collision|clear|Received a goal|stuck" /tmp/nav2.log \| tail -14`(`jobs/job911_navtail.sh` 3~4 행) |
| 나온 결과 | `11:12:27` / `########## F0 주행 11:08:14 — …` / `[nav_guard]: 목표 8df9abaa: 남은 거리 1.75 m …` / `[nav_guard]: 목표 ed69588c: 남은 거리 7.26 m → 시간 한도 237 s` / `[follow_path] [ActionServer] Aborting handle.` |
| 데이터 | [`outputs/j911_navtail_1112.txt`](../debug_log/2026-10-07/outputs/j911_navtail_1112.txt) · 도구 [`jobs/job911_navtail.sh`](../debug_log/2026-10-07/jobs/job911_navtail.sh) · 러너 원문 [`outputs/f0_f2c2_runner.log`](../debug_log/2026-10-07/outputs/f0_f2c2_runner.log) · 입력 원천 Jetson `/tmp/nav2.log`(원천 소실) |

### 5.2 prep 확인이 쓰이지 않는 RPP 플러그인의 값(0.2)을 읽음 (10-07 §6.1)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | `transform_tolerance` 0.5 배포가 실행 중 컨트롤러에 반영됐는지 prep 에서 확인 — `jobs/job918_prep.sh` 7 행 |
| 본 것 | `MPPI transform_tolerance Double value is: 0.2` |
| 처음 추론 | 반영 안 됨(SUMMARY §6.1 이 '첫 확인에서 이 값을 잘못 읽음' 으로 기록) |
| 의심한 이유 | 같은 prep 이 새 파일로 기동했고, 파일에는 0.5 가 들어 있었다 |
| 판별 시험 | `job919_chk.sh`(실행 중 params 파일의 `transform_tolerance` 줄 · `ros2 param list` 의 tolerance) → `job920_chk.sh`(`controller_plugins` · `FollowPath.plugin` · `FollowPathMPPI.plugin` · 두 플러그인의 `transform_tolerance`) |
| 결론 | prep 이 `FollowPath.transform_tolerance`(= RPP, 0.2)를 물었다. BT 가 쓰는 `FollowPathMPPI.transform_tolerance` 는 0.5 — 반영돼 있었다 |
| 다음에 알아보는 법 | 이 저장소의 `controller_plugins` 는 두 개(`FollowPath` = RPP, `FollowPathMPPI` = MPPI, `nav2_params.yaml:90`). MPPI 값은 항상 `FollowPathMPPI.` 접두로 묻는다. 값 확인 줄의 이름표('MPPI')와 실제 키가 같은지 본다 |
| 스크립트 핵심 | `echo "  MPPI transform_tolerance $(timeout 8 ros2 param get /controller_server FollowPath.transform_tolerance 2>&1 \| tail -1)"`(`jobs/job918_prep.sh` 7 행) |
| 나온 결과 | `  MPPI transform_tolerance Double value is: 0.2`(같은 출력의 `v_ref` 칸은 비어 있음 — `게이트 v_mode String value is: on · v_ref `) |
| 데이터 | [`outputs/j918_prep.txt`](../debug_log/2026-10-07/outputs/j918_prep.txt) 49~50 행 · 도구 [`jobs/job918_prep.sh`](../debug_log/2026-10-07/jobs/job918_prep.sh) · [`job919_chk.sh`](../debug_log/2026-10-07/jobs/job919_chk.sh) · [`job920_chk.sh`](../debug_log/2026-10-07/jobs/job920_chk.sh)(두 확인의 출력은 **원천 소실** — 0.5 · v_ref wheel 은 SUMMARY §6.1 서술뿐) |

## 6. 기록 사이 어긋남 (원문 대조)
1. **§3.5 '옆 치명 칸 0.47~0.70 m'**: `f2c2_w3cost.txt` 는 t 188 `왼 0.112`, t 209 `오 -0.077`(차체 외곽 안쪽)을 함께 보인다. 범위는 t 193~205 의 값만 옮긴 것이다. 결론('통로를 좁히지 않음')은 앞 띠 치명 0 과 함께라 크게 바뀌지 않지만, 두 표본(특히 차체 안으로 들어온 t 209 칸)은 설명이 없다.
2. **§3.5 'map→odom 수신 간격 0.05 s 일정' 과 §5 'stamp 간격 1.49 s'**: 둘 다 맞을 수 있다 — SLAM 은 map→odom 을 짧은 주기로 다시 보내되 처리가 밀리면 **같은 stamp** 를 계속 싣는다(CLAUDE.md '같은 stamp 를 두 번 발행'). 그래서 수신 간격으로는 정체가 안 보인다. 수신 간격 측정의 스크립트 · 출력은 없다(원천 소실). 지금 게이트 C(`chk_drive_gate.py:47`)도 `gap` 은 수신 간격이다.
3. **'f2c2 에서 같은 오류 7 회'**(§5 · `nav2_params.yaml` 주석): `job917_run.sh` 가 `grep -a "extrapolation" /tmp/nav2.log | … | tail -6` 이라 출력엔 마지막 6 줄(t 373 · 381 · 389 · 393 · 395 · 425, 계산)과 별도 창의 t 235 두 줄이 보인다. '7 회' 는 t 235 를 1 회로 센 사건 수와 맞지만, t 235~373 사이에 다른 줄이 있었는지는 `tail -6` 이라 원문으로 확인할 수 없다.
4. **도구 머리 주석**: `job914_w3log.sh` · `f2c2_w3cost.py` · `f2c2_w3ahead.py` 머리 주석은 '10-07 §3.3', 결과가 쓰인 곳은 §3.5(§3.3 은 번짐 판정). 또 `job914` 의 주석 시각 범위(t 176~240)와 정규식이 실제로 고른 범위(t ≈ 106~305, §9.3)가 다르다.
5. **§6 의 관찰 항목이 보고되지 않음**: §6 · §7 이 'TF 중단 0 · W3 저속 떨림 재발 여부(cmd v 평균 < 0.05 이고 ω 부호 바뀜 ≥ 20)' 를 판정에 넣었으나, §6.2 · §7.1 · §15 어디에도 그 결과가 없다. §15 의 '→ MPPI transform_tolerance 0.5' 는 조치를 적은 것이지 효과가 아니다.
6. **§5 '컨트롤러 · 로컬 코스트맵 transform_tolerance 0.2 → 0.5~1.0(지금 0.2)'**: 그날 판(커밋 `a096f227`)에서도 로컬 코스트맵 블록에 `transform_tolerance` 키는 없고, 0.2 는 `stvl_layer` 안의 값(그날 판 389 행)이었다. 그날 기본 로컬 층은 nvblox 라 STVL 값은 쓰이지 않았을 가능성이 크다(추정 — `camera_layer` 인자로 층을 바꿈).
7. **§3.5 '컨트롤 10 Hz 놓침 경고는 이 구간엔 1~2 건'**: `j914_w3log.txt` 로 세면 t 188~236 안 1 건(t 219.9), 바로 앞 t 185.4~185.8 에 3 건(계산: epoch − 1791338894).
8. **(미분석) 지연이 양수인 창이 여럿인데 오류는 t 235 에만**: `j917_tflag.txt` 에서 map→odom 지연 최대가 양수(stamp 가 수신보다 과거)인 창이 162~168(+0.07) · 180~186(+0.18) · 216~222(+0.18) · 252~258(+0.20) · 294~300(+0.30) 등 여럿인데, 이 시각의 외삽 오류 줄은 출력에 없다. 지연은 기록기 수신 시각 기준이고, 컨트롤러가 변환을 요청한 시각 · 그때 버퍼 상태는 다르다 — 어느 크기부터 실패하는지는 이 자료로 못 정한다.
9. **§5 '경로 대비 방향 ±2°'**: `f2c2_w3lat.txt` 의 t 204 는 `+4°`(t 208~236 은 −2~+2°).

## 7. 남은 것
- 떨림 원인: 후보 ① 오래된 계획(재계획 없는 58 s) ② MPPI 표본 분포 — `bags/bag_f2c2.tgz` 로 오프라인 MPPI 재현, 같은 계획을 오래 쓴 다른 구간과 비교.
- 떨림 수치(속도 · ω 부호 바뀜) 재계산 — 지금은 원천 소실. 같은 기준으로 f2d2 W3(96.3 s) 구간도 세어 §6 의 재발 관찰을 채울 것.
- `transform_tolerance` 의 상류 쓰임(대기 시간인가 허용 오차인가) 확인 — 10-21 §12 의 '0.5 인데 0.004 s 차를 못 덮음' 과 같은 질문.
- 기록기 수신 시각을 컨트롤러의 시각 대용으로 쓴 판정의 타당성 — 10-13 에 bag 기록기 자체가 reliable `/tf` 를 못 따라간 일이 있다 → §7.1 ③ 에서 f2c2 에 대해 다시 읽음(포화 서명은 없었음, 대용의 한계는 남음).
### 7.1 이후(10-12 ~ 10-15) — 통신 포화와의 관계 (11-03 채움)
10-12 · 10-13 의 통신 포화([통신 포화 카드](network-saturation-mppi-viz.md))는 이 카드 t 235 와 **같은 컨트롤러 오류**(`Exception in transformPose: Lookup would require extrapolation into the future` → follow_path 중단)를 냈지만, 자료로 보면 **다른 기전**이다.

| | 10-07 f2c2 t 235(이 카드) | 10-12 ~ 13 포화(f2f1 · f2f3 · f2g2 · f2i1 · f2j1 · f2k1 · f2m1) |
|---|---|---|
| 구성 | PreferForward **5**, `mppi_viz` 없음(10-07 §11 의 `mppi_viz` · `LONG_REC` 는 f2c2 뒤 16:06 커밋 `e3e1fe88` — f2d1 · f2d2 prep `job918` 에도 그 전엔 없었음), 기록기 `/tf` reliable | PreferForward **15** + `mppi_viz:=true`(206 kB × 10 Hz) + 기록기 `/tf` reliable |
| bag `/tf` 수신 | map→odom 수신 간격 0.05 s 일정(10-07 §3.5, 원천 소실 — §6-2) | 50 → 5~20 Hz 로 무너져 끝까지(10-12 §3.3 `f2f3_tf.txt`, `anal_tf_rate.py`) |
| stamp | map→odom stamp 간격 **1.49 s**(t 234~240 창만, `j917_tflag.txt`) | 측정의 중심이 아님 — 발행은 계속됐고(10-13 §1.2 캡처: `/tf` DATA 는 오히려 증가) 읽는 쪽이 못 받음 |
| 컨트롤러가 모자란 시간 | 6.6 ms(요청 …129.089612 vs 최신 …129.083021) | 요청 − 최신 중앙 0.071 s · 최대 0.829 s(f2f3, 22 회) |
| 지속 | 한 창(수 s) | 포화 시작부터 주행 끝까지(정지하면 풀림, 10-12 §5.2 `j965_state.txt`) |
| 원인 | SLAM 이 같은 stamp 를 다시 실음(정체) → 미래 여유 초과 | 기록기가 reliable `/tf` 읽는 쪽으로 뒤처짐 → `/tf` 쓰는 쪽 HEARTBEAT 폭주(79 %) → UDP 10 배 · 모든 소켓 손실(10-13 §1.2, 지지) |
| 조치 | MPPI `transform_tolerance` 0.5(→ 10-27 SLAM `transform_timeout` 1.5) | `mppi_viz:=lite` · 기록기 `/tf` best effort · 경로 조회기 상주 |

이 시기 자료로 이 카드에 더해지는 것:
1. **'순간 TF 지연 · 중단은 정상 주행에도 있다'** — 포화가 없던 f2g1(PF 5, 10-12 §4.2)에도 "미래 시각 TF" 로 follow_path 중단 **6 회**(11:56:14 1 회, 11:58:10 ~ 38 5 회)가 있었다(`f2g1_navlog.txt`). 같은 날 미래 시각 TF 줄 수: f2g1 12 · f2g2 18 · f2h1 **0**(10-12 §6.2), f2l1 · f2l2 **0**(§12.2 · §13.1), 10-13 f2o1 은 같은 종류인지 불분명한 `Can't transform map→odom … extrapolation into the future` **경고** 16 회(§4.4 — 그날 '포화 때의 수백 회와 다른 수준', 평상 대비는 비교 안 함). 즉 이 카드 계열(stamp 정체 · 순간 지연)의 중단은 포화와 별개로 0 ~ 수 회 남고, lite 구성에서 0 이 나온 주행도 있다 — **원인별로 갈라 센 적은 없다**(그날 `navlog_pc.py` 는 `transformPose` 와 `Unable to transform robot pose` 를 한 종류로 묶음).
2. **'TF 지연 → 컨트롤러 중단 → 멈춤이 멈춤을 부르는 고리'**(10-12 §2, 추정) — 포화 주행에서 중단 뒤 BT 재계획 · 경로 다듬기 · 응답 시간 초과가 이어졌고(f2f3 서버 시간 초과 15, BT 틱 초과 767), 이 카드의 t 235 이후 'wait 5 s' 와 같은 계열의 복구가 반복된 것이다. 고리가 포화를 유지했는지, 포화가 고리를 만들었는지는 10-13 캡처(통신량이 손실 · 중단보다 먼저, 10-12 §9.2)로 보면 **포화가 먼저**다.
3. **기록기 수신 시각을 대용으로 쓴 판정(§7 넷째 항목)** — 10-13 은 기록기가 포화 때 **가장 먼저 뒤처지는 읽는 쪽**임을 보였다(`cap_f2m1_acklag.txt`). 그러니 bag 기반 TF 지연은 포화 구간에서는 컨트롤러의 상태를 과장할 수 있다. f2c2 는 포화 서명(`/tf` 수신 붕괴)이 없고 수신 − stamp 지연이 떨림 · 매끄러운 구간에서 같았으므로 §3 의 '떨림에 대한 TF 가설 기각' 이 이것으로 뒤집히지는 않는다(추론). 다만 '컨트롤러가 본 시각' 을 직접 잰 적은 여전히 없다.
4. 떨림 자체(저속 · ω 부호 잦은 바뀜)에 대해서는 이 시기에 새 자료가 없다. 10-12 PreferForward 15 주행들의 W3 통로 구간을 같은 기준(cmd v 평균 < 0.05 · 6 s 에 ω 부호 바뀜 ≥ 20)으로 센 적도 없다.

- **이후(10-19 ~): 다음 시기에서 채움** — 포인터만: 10-21 §12 transformPose 예외 50 회(tolerance 0.5 인데 요청이 최신보다 0.004 ~ 0.088 s 앞섬), 10-27 §21 SLAM `transform_timeout` 1.5(§21.2 'TF 지연의 정체 = CPU 포화가 아니라 SLAM map→odom stamp 정체') · §22 '통신 탓 아님 → 공유메모리로는 안 풀림'.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2c2(run) | rf2o + G4 켠 F2 목표 5~10, 이 카드의 W3 떨림 · t 235 중단 | 러너 `outputs/f0_f2c2_runner.log`, bag `bags/bag_f2c2.tgz`(git 제외) |
| f2d1 · f2d2(run) | 같은 코스, tolerance 0.5 뒤 | `outputs/f0_f2d1_runner.log` · `f0_f2d2_runner.log`, bag `bags/bag_f2d1.tgz` · `bag_f2d2.tgz` |
| `job911_navtail.sh` | 주행 중 로그 tail | → `j911_navtail_1112.txt` |
| `job912_extract.py` · `job912_run.sh` | f2c2 bag → `x912_f2c2.npz`(궤적 · 계획 · 코스트맵 · 스캔 · cmd) | npz 는 Jetson `/tmp` · PC 스크래치 → 원천 소실 |
| `job914_w3log.sh` | W3 구간 nav2 로그 전부 | → `j914_w3log.txt` |
| `f2c2_w3cost.py` · `f2c2_w3ahead.py` | 옆 · 앞 띠 치명 칸 | → `f2c2_w3cost.txt` · `f2c2_w3ahead.txt` |
| `job917_tflag.py` · `job917_run.sh` | 6 s 창 TF · 토픽 지연 · stamp 간격 + 외삽 오류 원문 | → `j917_tflag.txt`(첫 줄 NUL 40 바이트 — WSL 경고) |
| `f2c2_w3lat.py` | 계획 대비 옆 · 방향 · 쓰인 계획 | → `f2c2_w3lat.txt` |
| `job918_prep.sh` · `job919_chk.sh` · `job920_chk.sh` | 재주행 prep · 설정 반영 확인 | → `j918_prep.txt`(919 · 920 출력 원천 소실) |

## 9. 도구 해설
**공통**: PC WSL 에서 `run_jn.sh`(JX_WHY 안내)로 스크립트를 Jetson `/tmp` 에 올려 실행, 출력은 PC 로 받아 `outputs/` 에 tee. 첫 줄의 깨진 글자는 WSL 의 `localhostForwarding` 경고(로캘 깨짐 + NUL 바이트 40 개) — 발췌에서 뺀다. 러너 시각 t = epoch − **1791338894**(f2c2 러너 시작, 모든 f2c2 도구에 하드코딩).

**도구 계보**: 주행 중 `job911`(로그만) → 주행 뒤 bag 추출 `job912` → 공간(코스트맵) 가설 `f2c2_w3cost` · `w3ahead`(§3.5) → 시간(TF) 가설 `job917`(§5) + 경로 가설 `f2c2_w3lat`(§5) → 설정 반영 `job918` → `job919` → `job920`. 주행 전 TF 건강 검사의 계보는 09-17 `job386_slamalive.py` → 10-27 `Docs/tools/chk_drive_gate.py` C(같은 기준). bag TF 지연 분석은 이후 10-27 의 SLAM stamp 정체 도구들(→ [SLAM 시각 정체 카드](slam-stamp-freeze.md))로 이어짐.

### 9.1 `job911_navtail.sh` — 주행 중 로그 엿보기(Jetson, 읽기만)
- 왜: 주행 중 사용자 관찰에 답하되 DDS 참여자를 만들지 않으려고(주행 직전 · 중 참여자 금지 규칙 — [DDS 참여자 카드](pre-drive-dds-participants.md)).
- 하는 일: `date +%T` → 러너 로그 `tail -4 /tmp/f0_f2c2.log` → nav2 로그에서 `PathBlocked|nav_guard|Fail|fail|Abort|abort|Optimizer|collision|clear|Received a goal|stuck` 줄 마지막 14 개(노드 접두 지움, 190 자 자름) → `tail -3 /tmp/f2c2.csv`.
- 출력: [`j911_navtail_1112.txt`](../debug_log/2026-10-07/outputs/j911_navtail_1112.txt). 쓰인 곳 §2.4(그리고 오독 §5.1).
- 결함: 러너 로그가 늦게 쓰이면 tail 이 거짓 '진행 없음' 을 보인다(§5.1). 목표 id 를 함께 보지 않으면 nav_guard 줄이 어느 목표인지 헷갈린다.

### 9.2 `job912_extract.py`(+ `job912_run.sh`) — f2c2 bag 추출(Jetson)
- 부른 형태: `python3 /tmp/job912_extract.py /tmp/bag_f2c2 1791339064 1791339330 /tmp/x912_f2c2.npz`(목표 5 · 6 구간 epoch).
- 하는 일: `/tf` 의 map→odom · odom→base_link(수신 시각 · x · y · yaw), `/odometry/ekf_a`, `/cmd_vel`(v · ω), `/plan` 전부, 전역 코스트맵 2 s 간격, 로컬 코스트맵 1 s 간격, `/scan` 1 s 간격, `/map` 첫 장. 궤적 = odom→base 3 개마다, 그 수신 시각 직전의 map→odom 과 합성(`pose_map`).
- 출력: `x912_f2c2.npz` — Jetson `/tmp` · PC 스크래치에만 → **원천 소실**(bag 에서 다시 만들 수 있음). §2.6 · §3.5 · §5 의 그림 · 수치 입력.
- 결함 · 주의: 궤적에 map→odom 계단 보정이 섞인다(로버 움직임이 아닌 점프, 10-07 §11). 시각은 기록기 수신 시각 기준.

### 9.3 `job914_w3log.sh` — W3 구간 nav2 로그(Jetson, 읽기만)
- 하는 일: `/tmp/nav2.log` 에서 대괄호 epoch 가 `17913390[7-9][0-9]` 또는 `1791339[01][0-9][0-9]` 인 줄 중 `Message Filter|tick rate` 제외, 노드 접두 지움, 같은 줄은 2 번까지만(`c[$0]<=2`), 60 줄.
- 출력: [`j914_w3log.txt`](../debug_log/2026-10-07/outputs/j914_w3log.txt) — §1 의 중단 원문 · §3 의 'Control loop missed' 시각 원천.
- 결함: 머리 주석은 '러너 t 176~240 ≈ epoch 1791339070~1791339135' 인데, 정규식 둘째 갈래 `1791339[01][0-9][0-9]` 가 epoch 1791339000~1791339199(t ≈ 106~305) 전체를 덮는다 — 실제 출력 첫 줄이 `[1791339007.08…] Reached the goal!`(t 113, 목표 6 끝). 넓게 읽은 덕에 결과에는 해가 없었지만 `head -60` 으로 뒤가 잘렸다(출력 마지막 줄 t ≈ 240). 시각 범위를 손으로 넣는 방식이라 다른 주행엔 고쳐 써야 함.

### 9.4 `f2c2_w3cost.py` — 옆 치명 칸 · 라이다 근거(PC, npz)
- 하는 일: 로컬 코스트맵(1 s 표본) 중 러너 t 186~262 · 정수 초가 4 의 배수인 장마다 → 값 ≥ 100 칸 중심을 odom → map(가장 가까운 map→odom) → 차체 좌표로 → 차체 앞뒤 |x| < 1.0 m 인 칸의 왼(y > 0) · 오(y < 0) 최소 |y| − 반폭 0.165 = '외곽까지 옆 거리'. 같은 시각 스캔(라이다 x +0.152, yaw π − 0.04677)과 비교해 치명 칸 중 라이다 점에서 **7.5 cm** 넘게 떨어진 수(= 카메라만 본 칸).
- 출력: [`f2c2_w3cost.txt`](../debug_log/2026-10-07/outputs/f2c2_w3cost.txt), 예: `t 209 | 앞뒤 1 m 안 치명 칸: 왼 0.685 · 오 -0.077 m(외곽까지 옆 거리) | 라이다 옆 최소 왼 0.737 · 오 0.667 | 치명 중 라이다 7.5 cm 밖 166/294`.
- 결함: 음수(차체 안 칸)를 따로 표시하지 않음 — §6-1 처럼 요약 때 빠지기 쉽다. 시각 대응은 가장 가까운 표본(보간 없음).

### 9.5 `f2c2_w3ahead.py` — 진행 앞 띠(PC, npz)
- 하는 일: t 186~250 · 3 의 배수 초, 차체 앞끝 0.262 m ~ 1.2 m · |y| < 0.165 + 0.10 = **0.265 m** 띠 안의 치명(≥ 100) 칸 수 · 가장 가까운 거리 · 카메라만(라이다 7.5 cm 밖) 수, 그리고 비용 ≥ 60 칸 수.
- 출력: [`f2c2_w3ahead.txt`](../debug_log/2026-10-07/outputs/f2c2_w3ahead.txt), 예: `t 207 앞 띠 치명   3 (최근 0.44 m, 카메라만 3) | 비용≥60 147 (최근 0.08 m)`. SUMMARY 의 '차체 폭 ±0.27' 은 이 0.265 의 반올림.

### 9.6 `job917_tflag.py`(+ `job917_run.sh`) — TF · 토픽 지연 6 s 창 ★
- 부른 형태: `python3 /tmp/job917_tflag.py /tmp/bag_f2c2 1791338894 /tmp/x917_f2c2.npz`(인자 BAG · T0 · OUT), 이어 `job917_run.sh` 가 nav2 로그에서 외삽 오류 원문 `tail -6`, epoch 1791339100~135 의 warn|error 줄 12 개, 같은 창 `Message Filter` 줄 수.
- 왜: §3.5 후보 ①(TF 시각 문제)을 §5 에 선언한 기준(떨림 구간에서만 커지면 채택)으로 가르려고.
- 하는 일(코드 그대로):
  ```python
  # 수집: /tf 의 (map,odom) · (odom,base_link), /odometry/filtered, /scan, /local_costmap/costmap → (bag 수신 시각 t, header stamp)
  for a in range(150, 330, 6):            # 6 s 창
      lag = X[s, 0] - X[s, 1]              # 수신 − stamp
      row.append('%.2f/%.2f' % (np.median(lag), lag.max()))
      u = np.unique(X[s, 1]); gaps.append('%.2f' % np.diff(u).max())   # 서로 다른 stamp 사이 최대 간격
  ```
  (`jobs/job917_tflag.py` 27~31 행) — cmd_vel 은 수신 시각끼리 간격.
- 출력: [`j917_tflag.txt`](../debug_log/2026-10-07/outputs/j917_tflag.txt)(5 773 바이트, 첫 줄 WSL 경고에 NUL 40 개 — 인용 때 지움). 핵심 줄:
  ```
  228~234 | -0.43/-0.36 | 0.01/0.02 | 0.01/0.02 | 0.00/0.02 | 0.00/0.00 || 0.12 | 0.04 | 0.06
  234~240 | -0.41/1.03 | 0.01/0.02 | 0.01/0.02 | 0.00/0.02 | 0.00/0.00 || 1.49 | 0.04 | 0.06
  240~246 | -0.41/-0.05 | 0.01/0.02 | 0.01/0.02 | 0.01/0.04 | 0.00/0.01 || 0.40 | 0.04 | 0.06
  [ERROR] [1791339129.331844627] [controller_server]: Exception in transformPose: Lookup would require extrapolation into the future.  Requested time 1791339129.089612 but the latest data is at time 1791339129.083021, when
  ```
  마지막 줄 `2` = 1791339100~135 창의 `Message Filter` 줄 수.
- 결과가 쓰인 곳: §5 'TF 가설 기각 · t 235 = stamp 정체' 판정 전부.
- 결함: ① '수신' 은 **bag 기록기**의 수신 시각 — 컨트롤러가 본 시각이 아니다(기록기가 밀리면 지연이 커 보이고, 컨트롤러만 밀리면 안 보임). ② 6 s 창의 중앙 · 최대만 — 짧은 정체의 시작 시각은 창 경계에 묻힘. ③ T0 · 창 범위가 f2c2 에 맞춰 하드코딩. ④ 외삽 오류는 `tail -6` 이라 전체 수를 못 봄(§6-3).
- 지금 다시 쓸 수 있나: 그대로 유효(인자만 바꿔). 이후 SLAM stamp 정체 분석(10-27)은 stamp 정체 길이를 직접 세는 쪽으로 갔다.

### 9.7 `f2c2_w3lat.py` — 계획 경로 대비 자세(PC, npz)
- 하는 일: t 184~260 을 4 s 마다, 그 시각 이전 마지막 `/plan` 에서 로버에 가장 가까운 점 q 와 q+3 점으로 접선 방향 → 옆 오차(접선 수직 성분) · 방향 차 · 계획 끝까지 거리 · 쓰인 계획의 시각.
- 출력: [`f2c2_w3lat.txt`](../debug_log/2026-10-07/outputs/f2c2_w3lat.txt), 예: `t 236 자세 (0.39,-2.05,  +0°) | 계획 t 183 | 옆 +0.016 m · 방향   +0° | 계획 끝까지 5.11 m` → `t 244 … | 계획 t 241 | …`.
- 결함: 계획은 `/plan`(전역, 스무더 뒤) — MPPI 가 실제로 받은 경로(odom 변환 · 가지치기)와 다를 수 있다. 궤적은 §9.2 의 합성(계단 보정 포함).

### 9.8 `job918_prep.sh` · `job919_chk.sh` · `job920_chk.sh` — 재주행 prep · 설정 반영(Jetson)
- `job918`: rf2o + G4(휠 잔차) + 그림자 A + tolerance 0.5 prep 뒤 확인 줄 — 6 행 게이트 `v_mode` · `v_ref`, 7 행 `FollowPath.transform_tolerance`(← §5.2 의 잘못 고른 키). 출력 [`j918_prep.txt`](../debug_log/2026-10-07/outputs/j918_prep.txt).
- `job919`: `/rf2o_gate` 파라미터 목록 · `v_ref` · 설치본 `v_ref` 줄 수, 실행 중 controller_server 의 `--params-file` 경로들과 그 안의 `transform_tolerance` 줄, `ros2 param list /controller_server | grep -i tolerance`.
- `job920`: `controller_plugins` · `FollowPath.plugin` · `FollowPathMPPI.plugin` · 두 플러그인의 `transform_tolerance` 를 `ros2 param get`.
- 출력: 919 · 920 은 **원천 소실**(SUMMARY §6.1 서술: v_ref wheel · `FollowPathMPPI` 0.5 · RPP 0.2).
- 지금: prep 확인은 `Docs/tools/chk_prep.py` 한 노드로 바뀌었고(10-27), 그 목록(31~33 행)은 `FollowPathMPPI.` 접두를 쓰지만 `transform_tolerance` 는 없다.

### 9.9 (지금 도구) `Docs/tools/chk_drive_gate.py` 게이트 C — 주행 직전 SLAM TF 건강
- 이 카드에서 쓴 도구는 아니지만 10-07 러너가 부른 C 게이트(`job386_slamalive.py`, `jobs/job551_f0drive.sh` 19 행: `[ "$(echo "$SA" | tail -1)" = OK ] || { echo "  C 불합격(SLAM) …"; exit 1; }`)의 후속이라 적는다. f2c2 · f2d2 러너 출력 `C 통과`.
- 판정(코드): 5 s 동안 `/tf` 의 (map, odom) 수신마다 `(now, now − stamp)` → `gap = max(수신 간격) < 0.5` 이고 `lag = max(now − stamp) < 1.0` 이면 OK(`chk_drive_gate.py:47~48`, `job386` 20 · 23 행과 같은 식).
- 이 카드에서 본 한계: 주행 전 5 s 만 봄 · `gap` 은 수신 간격(§6-2) · stamp 가 미래로 찍혀 `lag` 가 작게 나옴(§4.1 계산).

## 10. 용어
- **ω 부호 바뀜**: `/cmd_vel` 회전 속도 지령의 부호가 + ↔ − 로 바뀐 횟수. 직진 중 많으면 좌우로 비트는 떨림.
- **수신 − stamp 지연**: 메시지를 받은 시각(여기선 bag 기록기)에서 메시지 머리의 stamp 를 뺀 값. 음수면 stamp 가 미래.
- **stamp 간격**: 서로 다른 stamp 값 사이의 최대 간격 — 같은 stamp 를 되풀이해 보내는 발행자(SLAM 의 map→odom)의 '실제 갱신이 멈춘 시간'.
- **transform_timeout(slam_toolbox)**: map→odom stamp 를 '마지막 스캔 시각 + 이 값' 으로 미래에 찍는 여유(10-01 §8.5, `slam.launch.py` 주석). 처리가 이 값보다 오래 밀리면 stamp 가 현재보다 과거가 되어 '지금' 조회가 외삽 오류.
- **transform_tolerance(Nav2 컨트롤러 플러그인)**: 경로 · 자세 변환 때 TF 시각 차를 얼마나 봐주는지(또는 기다리는지)의 값. 정확한 쓰임은 이 카드에서 확인 안 함.
- **외삽 오류(extrapolation into the future)**: tf2 가 요청 시각보다 늦은 데이터가 버퍼에 없어 '미래로 늘려야' 답할 수 있을 때 거부하는 예외.
- **Optimizer reset**: MPPI 가 새 목표 · 새 경로를 받을 때 내부 제어열을 초기화했다는 로그.
- **RateController(우리 BT)**: 전역 재계획 빈도 제한. 이 시기 BT 는 첫 틱 · 목표 변경 · 주행 실패 때만 재계획(0.01 Hz) — 그래서 한 계획을 수십 초 그대로 쓸 수 있다.
