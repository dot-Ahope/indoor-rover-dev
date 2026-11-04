# SLAM map→odom 시각 정체 → nav2 TF 조회 실패

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **우회**(증상 차단) · 근본 미해결 — 정체 → TF 실패의 길은 transform_timeout 1.5 로 끊김(f2tt1 · f2tt2 실패 0, **측정 2 회**). 정체 자체(주행당 > 0.5 s 30 번 안팎, 최대 ≈ 1.1~1.3 s)와 그 비용(정합 1 회 중 LinkNearChains 64 %)은 그대로 · 줄이는 설정은 미채택 | 10-01 ~ 10-28 (11-04 코드 대조) | [10-01 §8.5](../debug_log/2026-10-01/SUMMARY.md) f2a2 | `ros2_ws/src/rover_bringup/launch/slam.launch.py`(위치 추정 모드 transform_timeout 0.2 → 0.5(10-01) → **1.5**(10-27), 처리 문턱 0.30 m · 0.15 rad · 지도 갱신 10 s(10-01 §9)) · `ros2_ws/src/rover_navigation/config/nav2_params.yaml`(MPPI transform_tolerance 0.2 → 0.5, 10-07) · 도구 `Docs/tools/run_slam_replay.sh` · `slam_replay_feed.py`(10-27 신설) | [nvblox 전역 층 TF 실패 처리](nvblox-layer-tf-drop.md)(같은 방아쇠, 9 기) · [주행 전 검사 정리](drive-gate-consolidation.md)(게이트 C 의 뜻이 바뀜) · [정지 중 방향 드리프트](stationary-yaw-drift.md) · [SLAM 포크](slam-fork-rotation.md)(계측 사본) · [CPU 부하](cpu-load-stalls.md) · [남서 구석 정체](southwest-orient-stall.md) · [W3 떨림 · TF 지연](tf-lag-w3-wobble.md) (6 기) · [통신 포화](network-saturation-mppi-viz.md) (7 기) · [카메라 ↔ 컨테이너 공유메모리](camera-container-shm.md) · [주행 전 검사 · 운용(8 기)](drive-ops-1019-1023.md) · [F1 매핑](f1-office-mapping.md)(10-01 §9 재생 A/B) |

**한 줄**: SLAM 위치 추정이 스캔 정합에 0.3~1.3 s 를 쓰는 동안 map→odom 의 시각(stamp)이 멈추고, 그 멈춤이 미래 여유(transform_timeout)를 넘으면 nav2 가 '지금' 변환을 못 찾아 컨트롤러가 멈추거나 전역 코스트맵이 틀어진다. 여유를 1.5 s 로 늘려 실패는 0 이 됐고(2 주행), 정합이 느린 원인(LinkNearChains)은 찾았지만 줄이는 설정은 아직 못 찾았다.

## 1. 증상
- 주행 중 nav2 로그 `extrapolation into the future … from frame [odom] to frame [map]` → 컨트롤러 중단 · BT 재시도 · Wait 로 1 s 넘게 정지(f2tf1 5 번, 그중 1 번 5.1 s). [10-27 §19](../debug_log/2026-10-27/SUMMARY.md)
- 같은 순간 전역 코스트맵의 카메라 장애물이 0.55 m · 7.5° 틀어진 자리에 한 장 찍힘('문이 막혔다 풀림 · 상자가 벽 쪽으로') — 이것은 nvblox 층의 실패 처리 결함이 더해진 것. [10-27 §15](../debug_log/2026-10-27/SUMMARY.md)
- 원문 한 줄(f2tf1 전역 층, [`nav2_f2tf1.log`](../debug_log/2026-10-27/outputs/drives/f2tf1/nav2_f2tf1.log) 290 행, 뒤 생략):
  ```
  [planner_server-5] [WARN] [1793080839.244104102] [global_costmap.global_costmap]: [NvbloxCostmapLayer] Can't transform: map to odom. Error: Lookup would require extrapolation into the future.  Requested time 1793080839.137708 but the latest data is at time 1793080839.102246, when looking up transform from frame [odom] to fra…
  ```
  요청 시각이 최신 stamp 보다 0.035 s 뒤 — '미래' 쪽으로 0.035 s 모자라 실패.

### 1.1 기전(소스 · 측정으로 맞춘 그림)
```
 slam_toolbox 위치 추정:  스캔 처리(정합)할 때만 '마지막 처리 스캔 시각' 이 바뀐다
                          map→odom 은 20 Hz 로 계속 다시 보내되 stamp = 마지막 처리 스캔 시각 + transform_timeout
 평소:   stamp − 지금 ≈ +transform_timeout − (스캔 처리 지연)   (0.5 일 때 중앙 +0.44 s, 1.5 일 때 +1.45 s)
 정체:   정합 한 번이 길어지면(0.4~1.3 s) stamp 가 그대로 → 지금이 stamp 를 넘는 순간부터 '지금' 조회 실패
 실패 창 = [고정된 stamp, 다음 새 stamp 수신]   → 정체 길이 > transform_timeout 일 때만 생긴다
```
- stamp 규칙은 10-01 §8.5 의 소스 읽기(`slam_toolbox_common.cpp` publishTransformLoop, 원문은 [`slam.launch.py`](../../ros2_ws/src/rover_bringup/launch/slam.launch.py) 67~70 행 주석이 요약). '정합 때만 바뀐다' 는 10-27 §26.1 의 새 stamp 간격 분포(97 % < 0.15 s, 정합 스캔에서만 0.4~1.3 s)와 §29.1 계측이 뒷받침.
- MPPI 쪽 `transform_tolerance 0.5`(10-07)는 MPPI 의 경로 변환만 '최신 stamp 보다 0.5 s 미래' 까지 견디게 하는 여유다(전역 nvblox 층 등 다른 조회에는 해당 없음, 정체 자체도 그대로). 10-27 f2tf1 의 컨트롤러 TF 중단 5 번은 이 여유까지 넘은 경우로 봄(추정 — 중단 순간 여유 −0.60 s 인 15:02:03 은 맞음, §4.1).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론 | 데이터 |
|---|---|---|---|---|
| 10-01 §9 (§8.2 f2a1 의 map→odom 지연 뒤, §8.5 보다 먼저) | 위치 추정 노드 부하 재생 A/B — 09-30 매핑 bag 0~560 s 를 도메인 42 · sim time 으로 `localization_slam_toolbox_node`(office_v2)에, 라이브 Nav2 · SLAM · nvblox 정지. 지표 = 주행 구간(250 s 이후) (EKF stamp − map→odom 최신 stamp) > 0.2 s 비율 · map→odom 고유 stamp 간격 · 노드 CPU | base(노드 간격 0.05 m · 0.03 rad) **14.46 %** · 결손 최대 +1.066 s · 간격 95 % 0.400 / 최대 1.200 s · CPU **134 %**(f2a1 실주행 11.4 % 와 같은 수준) → t2(0.20 · 0.10) 1.66 % · 48 % → t2nolc(t2 + 루프 끔) 1.26 % · 최대 0.600 s → t3(0.30 · 0.15) 0.82 % · 40 % → **t3m(t3 + map_update_interval 10 s) 0.19 % · 최대 +0.395 s · 간격 95 % 0.112 · CPU 22 %** | 원인 = 위치 추정 노드 자체 처리량(라이브 CPU 경쟁 아님). 남은 0.6 s 멈춤은 루프 클로저 탓 아님 · 지도 다시 그리기(2 s 마다 전체 그래프로 격자) 가설 **지지**(간격만 2 → 10 s 로 CPU 40 → 22 %) → `slam.launch.py` localization 일 때만 0.30 · 0.15 · 10.0 채택. 남은 위험: 최대 0.40 s 가 컨트롤러 대기 0.2 s 를 넘음(→ §8.5). 재생은 Nav2 · nvblox 없이라 낙관적. ※ 10-27 §26.1 의 '10 s 지도 갱신 주기 가설 기각' 은 이 조치 **뒤에 남은** 정체에 대한 것이라 이 결론과 충돌하지 않는다 | `2026-10-01/outputs/j736_locreplay_base_t2.txt` · `j736b_locreplay_t3_t2nolc.txt` · `j736c_locreplay_t3m.txt`, `jobs/job736_locreplay.sh` · `.py`(해설은 [F1 카드 §8](f1-office-mapping.md)) |
| 10-01 §8.5 | f2a2 transformPose 오류 3 · follow_path 중단 1 조사, 포크 소스 읽기 | map→odom stamp = 마지막 스캔 시각 + transform_timeout(0.2). 관측 최대 밀림 0.57 s | 처리 밀림이 여유를 넘으면 실패 → **0.2 → 0.5** | [`job733_tfstamp.py`](../debug_log/2026-10-01/jobs/job733_tfstamp.py) · [`j733_tfstamp.txt`](../debug_log/2026-10-01/outputs/j733_tfstamp.txt) |
| 10-07 §5 · §6 (6 기) | W3 떨림 조사 중 f2c2 t 235 follow_path 중단 | t 234~240 창만 stamp **1.49 s** 멈춤(여유 0.5 를 넘음 → 수신 − stamp 최대 +1.03 s), 같은 오류 7 회 | 10-01 과 같은 기전, 0.5 뒤에도 드물게 재발 → MPPI `transform_tolerance` 0.2 → 0.5(정체 원인은 미확인 · '후보: slam 처리 멈춤 원인(CPU) 확인') | [10-07 SUMMARY §5](../debug_log/2026-10-07/SUMMARY.md) · [W3 떨림 카드](tf-lag-w3-wobble.md) · `nav2_params.yaml` 230~233 행 주석 |
| 10-27 §15 | 영상의 '코스트맵 튐' 원자료 대조 | 튄 장 2 장(⚠ 11-04 정정: 영상 구간만 본 수 — 주행 전체는 3 장, `outputs/tffix/anal_tffix_sig_f2st1.txt`) = 슬라이스를 변환 없이 map 에 적은 것 · 그 0.3 s 전 층 경고 | nvblox 층이 TF 실패 때 단위 변환을 씀(결함) | [`chk_gcm_fit_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_gcm_fit_f2st1.txt) 등 `outputs/block_cell/` · → [J 카드](nvblox-layer-tf-drop.md) |
| 10-27 §16 | TF 실패와 부하 | 층 경고 22 중 20 이 Control loop missed ±0.5 s 안(무작위 11 %) · '슬라이스 앞섬' > 0 은 22 중 8 | 방아쇠는 부하(**추정**) — §21.2 에서 정정 | [`chk_tf_lag_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_tf_lag_f2st1.txt) · 도구 `jobs/chk_tf_lag.py` |
| 10-27 §21.2 | 부하 · TF 다시 봄 | CPU 68.5 %(사건 초 73 %) — 포화 아님. 실패 33/33 이 odom→map, 그때 map→odom 은 20 Hz 로 오지만 **stamp 가 0.6~1.1 s 같은 값** · 최대 간격 1.296 s · 실패 전부 '여유 소진 창' 안 | 원인은 CPU 가 아니라 **SLAM stamp 정체**(§16 추정 정정) | [`anal_load_f2tf1.txt`](../debug_log/2026-10-27/outputs/load/anal_load_f2tf1.txt) · [`chk_mapodom_window_f2tf1.txt`](../debug_log/2026-10-27/outputs/load/chk_mapodom_window_f2tf1.txt) · [`anal_slam_freeze_f2tf1.txt`](../debug_log/2026-10-27/outputs/load/anal_slam_freeze_f2tf1.txt) |
| 10-27 §21.3 | 조치 · 배포 · prep | 배포: Jetson src blob 1eca8ad01b → 921d5993b0(PC 와 같음), 설치본은 src 링크, CR 0. prep 은 **PREP_FAIL**(0.176 m · −13.6°, 로버가 f2tf1 끝 자세 −175° 그대로) — 같은 출력에 `transform_timeout = 1.5 · mode = localization` | **transform_timeout 0.5 → 1.5**(대가: 보정 반영 최대 1.5 s 늦음 ≈ 1~2 mm · 0.03°, 추정). PREP_FAIL 은 로버 배치 문제로 봄 → 사용자가 출발 테이프로 옮김 | [`up_slam_tt15_1027.txt`](../debug_log/2026-10-27/outputs/load/up_slam_tt15_1027.txt) · [`prep_tt15_1027.txt`](../debug_log/2026-10-27/outputs/load/prep_tt15_1027.txt) · `jobs/up_slam_tt15_1027.sh` · `apply_slam_tt15_1027.sh` |
| 10-27 §22 | 통신(UDP) 탓인가 · 공유메모리로 풀리나 | 정체 중에도 /scan · odom TF 수신 간격 평소와 같음, SLAM CPU 정체 중 72.7 % vs 기준 45.1 %, 스캔 버림 동반 37/56 | 통신 아님 → 공유메모리로는 안 풀림(**추정**, SLAM 내부 수신 시각은 미측정) | [`anal_slam_freeze_cause_f2tf1.txt`](../debug_log/2026-10-27/outputs/load/anal_slam_freeze_cause_f2tf1.txt) |
| 10-27 §23 | 최근 생긴 것인가 | bag 112 개: 09 월 매핑 모드는 거의 0 · **10-07 이후 위치 추정 순회 전부 1 m 당 1~4 번** | 회귀 아님 — 위치 추정 운용 내내 있던 성질. 10-01(0.06/m) → 10-07 사이 무엇이 바뀌었는지는 미확인 | [`anal_slam_freeze_hist.tsv`](../debug_log/2026-10-27/outputs/load/anal_slam_freeze_hist.tsv) |
| 10-27 §24 | 주행 전 게이트 정리 중 새 C 가 한 번 FAIL | 같은 정지 상태(위 PREP_FAIL 자세)에서 옛 C 지연 0.38 s(OK) · 새 C **1.14 s(FAIL)**, 20 s 뒤 관찰 최대 −0.27 s | 위치 추정이 틀린 상태의 정체로 봄(추정). C 문턱 '지연 < 1.0 s' 는 timeout 1.5 에서 '≈ 2.5 s 넘는 정체' 를 뜻하게 됨 — 생존 검사로 그대로 둠 | [`cmp_gate_1027.txt`](../debug_log/2026-10-27/outputs/gate/cmp_gate_1027.txt) · [`chk_slam_idle_1027.txt`](../debug_log/2026-10-27/outputs/gate/chk_slam_idle_1027.txt) · → [게이트 정리 카드](drive-gate-consolidation.md) |
| 10-27 §25 | f2tt1(timeout 1.5) | 정체 그대로(> 0.5 s 33 · 최대 1.10) · 미래 여유 최소 1.139 s · **TF 실패 0 · 1 s 넘는 정지 0** | 정체 → 실패 경로가 끊김(1 회) | [`anal_slam_freeze_f2tt1.txt`](../debug_log/2026-10-27/outputs/load/anal_slam_freeze_f2tt1.txt) · 그림 [`f2tt1_summary.png`](../debug_log/2026-10-27/figures/f2tt1_summary.png) |
| 10-27 §26.1 | 정체는 언제 나나 | 정체 사이 이동 0.35 m · 0.32 rad, 정합 문턱(0.30 m · 0.15 rad) 이상 **53/54** · 10 s 지도 갱신 주기 가설 13 %(무작위 20 %) · 정체 직전 1 s 회전 포함 39/55 | 정합할 때마다 (지지 — 판별력 약함, §3) · 지도 갱신 (기각) | [`anal_slam_freeze_trigger_f2tt1.txt`](../debug_log/2026-10-27/outputs/slamproc/anal_slam_freeze_trigger_f2tt1.txt) · `_f2tf1.txt` |
| 10-27 §26.3 | 재생 A/B(루프 끔 · 해상도 · 탐색 범위 · 버퍼) | 기준 두 번 19 · 23 정체, 변형 15~19 · 루프 끔은 위치 차 중앙 0.4 → 3.6 cm · 해상도 0.02 는 기동 중 종료 | 채택 없음 · 무거운 곳은 이 넷이 아님 | [`anal_slam_replay_ab1.txt`](../debug_log/2026-10-27/outputs/slamproc/anal_slam_replay_ab1.txt) · [`run_slamrep_batch_1027.txt`](../debug_log/2026-10-27/outputs/slamproc/run_slamrep_batch_1027.txt) · `Docs/tools/run_slam_replay.sh` |
| 10-27 §29.1 | 포크에 단계별 시간 계측(동작 불변) | addScan 중앙 168 · 최대 1138 ms 중 **LinkNearChains 64 %**(중앙 261 ms) | 가까운 지도 스캔 사슬마다 다시 정합하는 비용 | [`anal_slam_timing_T0dbg.txt`](../debug_log/2026-10-27/outputs/slamproc/anal_slam_timing_T0dbg.txt) · `jobs/prep_slam_dbg_1027.sh` |
| 10-27 §29.2 | link_scan_maximum_distance 1.5 → 1.0 · 0.75 | 0.75: > 0.4 s 정체 19~23 → 13 · 최대 1.14 → 0.81 s · 위치 차 중앙 1.0 cm | 줄지만 기준(절반) 미달 — 운용 안 바꿈 | [`anal_slam_replay_link.txt`](../debug_log/2026-10-27/outputs/slamproc/anal_slam_replay_link.txt) · [`anal_slam_timing_link.txt`](../debug_log/2026-10-27/outputs/slamproc/anal_slam_timing_link.txt) |
| 10-27 §30 | 시스템 성능 평가(4 회) | nav2 TF 실패 f2st1 23 · f2tf1 33 · f2tt1 0 · Control loop missed 70 · 84 · 43 | 'SLAM 정합 처리 지연(근본 미해결)' 을 약점 ③ 으로 | [10-27 §30](../debug_log/2026-10-27/SUMMARY.md) · 표는 [CPU 카드 '이후'](cpu-load-stalls.md) |
| 10-28 §0 | 하루 시작 점검(밤사이 재부팅) | `slam.launch.py` transform_timeout 1.5 · nvblox 층 수정 유지 | 재부팅에도 남음(src 파일) | [`chk_day_start_1028.txt`](../debug_log/2026-10-28/outputs/chk_day_start_1028.txt) |
| 10-28 §1 · §4 | f2tt2(같은 구성 반복, 판정 주행 전 선언) | > 0.5 s 정체 31 · 최대 0.996 s · 미래 여유 최소 1.003 s · 스캔 버림 53 · **TF 실패 0 · 층 경고 0 · 컨트롤러 TF 중단 0** · Control loop missed 70 | timeout 1.5 운용 확정(2/2). 남은 정지는 TF 가 아니라 막힘 판정(경로 위 99) | [`anal_slam_freeze_f2tt2.txt`](../debug_log/2026-10-28/outputs/drives/f2tt2/anal_slam_freeze_f2tt2.txt) · [`anal_tffix_sig_f2tt2.txt`](../debug_log/2026-10-28/outputs/drives/f2tt2/anal_tffix_sig_f2tt2.txt) |
| 이후(10-29 ~) | 이 카드의 실험은 없음. 10-29 의 정지 중 yaw 드리프트 조사가 f2tt2 bag 을 다시 씀(스캔 ↔ 지도 맞춤) | — | — | → [정지 중 방향 드리프트](stationary-yaw-drift.md) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| CPU 포화(부하) | 사건 초의 코어 사용률 · 프로세스별 | 평균 68.5 %, 사건 초 73 % | **기각**(§21.2) — §16 의 '부하가 방아쇠' 추정을 정정 |
| 노드 사이 통신(UDP) 지연 | 정체 구간 vs 기준 구간의 입력 수신 간격 | 같음(0.115 vs 0.113 s) | **기각**(§22, 추정 — SLAM 프로세스 안쪽은 미측정) |
| 최근 회귀 | 과거 bag 112 개 같은 지표 | 10-07 이후 일정 | **기각**(§23) |
| 지도 갱신 주기(10 s) | 정체 사이 시간이 10 s 배수에 모이나 | 13 · 11 %(무작위 ≈ 20 %) | **기각**(§26.1) |
| 위치 추정 정합 때마다 처리 지연 | 정체 사이 이동 · 회전 vs 정합 문턱 | 53/54 · 53/55 | **지지**(§26.1). ⚠ 판별력 약함(카드 작성 중 판단): 정체 사이 중앙 5.2~5.5 s 동안 평균 0.067 m/s 로 가면 무작위 정체라도 0.30 m · 0.15 rad 를 거의 늘 넘는다. 직접 근거는 아래 §29.1(정합 스캔의 처리 시간 자체) |
| 루프 탐색 · 정합 탐색 범위 · 버퍼 | 재생 A/B(변형별) | 정체 15~19 vs 기준 19~23 — 기준 두 번 차보다 작음 | **기각**(§26.3) |
| 정합 안 어느 단계 | 포크 계측 | LinkNearChains 64 % · 순차 정합 16 % · 루프 7 % | **확인**(§29.1) |
| 가까운 사슬 수를 줄이면 | link_scan_maximum_distance A/B | 0.75 m: 긴 정체 절반 이하 · 전체 > 0.4 s 정체는 절반 미달 | **부분**(§29.2, 기준 미달) |

## 4. 조치와 효과
- transform_timeout 0.2 → 0.5(10-01) → **1.5**(10-27). 효과: f2tf1(0.5) TF 실패 33 · 1 s 넘는 정지 1 → f2tt1 · f2tt2(1.5) 둘 다 실패 0(정지는 f2tt1 0 · f2tt2 1 번 4.9 s — TF 아님, 막힘 판정).
- 한계: 정체 자체는 그대로(주행당 > 0.5 s 30 번 안팎). 정체가 1.5 s 를 넘으면 다시 실패한다(관측 최대 1.296 s, 10-12 이상 시기 4.4 s 한 번).

### 4.1 판단에 쓴 핵심 줄 · 출력
- **실패 창(§21.2 · §25)** — [`anal_slam_freeze.py`](../debug_log/2026-10-27/jobs/anal_slam_freeze.py) 24~26 · 39~42 행: 같은 stamp 구간마다 [그 stamp, 다음 stamp 수신] 을 실패 창으로, nav2 로그 'extrapolation into the future … [odom] to frame [map]' 의 Requested time 이 창 안이면 셈.
  ```python
  for k in range(len(seg) - 1):
      st = seg[k][2]; nxt = seg[k + 1][0]
      if nxt > st: fail.append((st, nxt, nxt - st, seg[k + 1][2] - st))
  ```
  출력 f2tf1(0.5) → f2tt1(1.5):
  ```
  stamp 새로 바뀌는 간격: 중앙 0.096 · 99% 0.497 · 최대 1.296 s · > 0.5 s 36 번 · > 0.4 s 56 번
  새 stamp 가 처음 올 때의 미래 여유(stamp − 수신): 중앙 0.442 · 최소 -0.313 s
  현재 시각 조회가 실패하는 창(여유 소진) 63 번 · 합 12.99 s:
  nav2 odom→map 외삽 실패 33 번 중 위 창 안 33 번 · SLAM 스캔 버림 51 번(주행 창)
  ---
  stamp 새로 바뀌는 간격: 중앙 0.096 · 99% 0.496 · 최대 1.102 s · > 0.5 s 33 번 · > 0.4 s 55 번
  새 stamp 가 처음 올 때의 미래 여유(stamp − 수신): 중앙 1.451 · 최소 1.139 s
  현재 시각 조회가 실패하는 창(여유 소진) 0 번 · 합 0.00 s:
  ```
  ([`anal_slam_freeze_f2tf1.txt`](../debug_log/2026-10-27/outputs/load/anal_slam_freeze_f2tf1.txt) 1~4 · 마지막 행, [`anal_slam_freeze_f2tt1.txt`](../debug_log/2026-10-27/outputs/load/anal_slam_freeze_f2tt1.txt) 1~4 행.) 정체 간격 분포는 두 주행이 거의 같고(최대 1.30 · 1.10 s), 바뀐 것은 미래 여유 중앙 0.44 → 1.45 s 뿐.
- **중단 순간의 map→odom(§21.2)** — [`chk_mapodom_window.py`](../debug_log/2026-10-27/jobs/chk_mapodom_window.py) 11~13 행: 중단 로그 시각 −1.6 ~ +0.3 s 의 map→odom 수신 시각 · stamp 를 그대로 나열. 출력(15:02:03 중단, [`chk_mapodom_window_f2tf1.txt`](../debug_log/2026-10-27/outputs/load/chk_mapodom_window_f2tf1.txt) 13~26 행에서 골라):
  ```
    수신 -1.050 s · stamp -0.603 s (수신 기준 stamp +0.446)
    수신 -0.598 s · stamp -0.603 s (수신 기준 stamp -0.005)
    수신 +0.000 s · stamp -0.603 s (수신 기준 stamp -0.604)
    수신 +0.101 s · stamp +0.485 s (수신 기준 stamp +0.384)
  ```
  수신은 0.05~0.1 s 마다 계속 오는데 stamp 가 1.05 s 동안 −0.603 그대로 → 중단 순간 여유 −0.60 s.
- **통신 아님(§22)** — [`anal_slam_freeze_cause.py`](../debug_log/2026-10-27/jobs/anal_slam_freeze_cause.py) 46~47 · 50~54 행: 정체(새 stamp 간격 > 0.4 s) 구간과, 정체와 겹치지 않는 같은 길이 무작위 200 구간(`default_rng(0)`)의 같은 지표를 비교.
  ```
  정체(새 stamp 간격 > 0.4 s) 56 구간 · 길이 중앙 0.57 s | 기준선(정체 아님, 같은 길이) 200 구간
    /scan 최대 수신 간격 s                 정체: 중앙 0.115 · 90% 0.124 | 기준선: 중앙 0.113 · 90% 0.122
    SLAM %CPU(최대, 1 s top)           정체: 중앙 72.650 · 90% 103.850 | 기준선: 중앙 45.100 · 90% 89.500
    정체 중 /scan 간격 > 0.2 s 인 구간 0/56 · odom→base_link 간격 > 0.2 s 0/56 · SLAM CPU ≥ 90 % 15/56 · 스캔 버림 ≥ 1 37/56
  ```
  ([`anal_slam_freeze_cause_f2tf1.txt`](../debug_log/2026-10-27/outputs/load/anal_slam_freeze_cause_f2tf1.txt) 1~2 · 5 · 7 행.)
- **이력(§23)** — [`anal_slam_freeze_hist.py`](../debug_log/2026-10-27/jobs/anal_slam_freeze_hist.py) 43 · 47 행(새 stamp 간격 · 미래 여유 중앙 = 적용된 timeout 근사 · 1 m 당 > 0.5 s 정체). tsv 원문 행:
  ```
  bag_mp7	09-17 11:01	36	1.6	354	0.096	1.622	2.896	11	8	5.07	0.163	-	-	-
  bag_f2a12	10-01 16:59	344	16.3	6881	0.096	0.218	0.610	10	1	0.06	0.446	localization	0.5	0.3
  bag_f2f1	10-12 10:31	230	13.3	3985	0.096	0.742	4.382	61	47	3.53	0.447	localization	0.5	0.3
  bag_f2tf1	10-27 15:00	419	27.9	8391	0.096	0.497	1.296	56	36	1.29	0.442	localization	0.5	0.3
  ```
  (열: bag · 시작 · 길이 s · 이동 m · map→odom 수 · 간격 중앙 · 99 % · 최대 · > 0.4 · > 0.5 · 1 m 당 · 여유 중앙 · mode · timeout · min_travel, [`anal_slam_freeze_hist.tsv`](../debug_log/2026-10-27/outputs/load/anal_slam_freeze_hist.tsv) 26 · 51 · 63 · 113 행.)
- **정합 문턱(§26.1)** — [`anal_slam_freeze_trigger.py`](../debug_log/2026-10-27/jobs/anal_slam_freeze_trigger.py) 31~33 행: 이웃한 두 정체 시작 사이 EKF 누적 이동 · |회전| 을 재고 `(dd >= 0.30) | (da >= 0.15)` 인 비율. 출력(f2tt1):
  ```
  정체 사이 이동: 중앙 0.35 m · 10% 0.06 · 90% 1.03 | 회전: 중앙 0.32 rad · 10% 0.24 · 90% 1.01
    (이동 ≥ 0.30 m 또는 회전 ≥ 0.15 rad 인 정체 사이 53/54)
  정체 직전 1 s 운동: 서 있음 0 · 직진 위주(회전 < 3°) 16 · 회전 포함 39
  새 stamp 간격 분포: < 0.15 s 97 % · 0.15~0.4 2 % · > 0.4 1 %
  ```
- **단계별 시간(§29.1)** — 계측판 [`prep_slam_dbg_1027.sh`](../debug_log/2026-10-27/jobs/prep_slam_dbg_1027.sh) 35 행(AddEdges 안 LinkNearChains 앞뒤에 시각, 사슬 수 `means.size()` 함께):
  ```python
  g = sub(g, '  LinkNearChains(pScan, means, covariances);\n', '  auto _b2 = ROVER_NOW();\n  LinkNearChains(pScan, means, covariances);\n  fprintf(stderr, "[ROVER_T] AE near=%.1f nmeans=%zu\\n", ROVER_MS(_b2), means.size());\n', 'AE near')
  ```
  분석 [`anal_slam_timing.py`](../debug_log/2026-10-27/jobs/anal_slam_timing.py) 18 · 22 행(몫 = 단계 합 / addScan 합). 출력([`anal_slam_timing_T0dbg.txt`](../debug_log/2026-10-27/outputs/slamproc/anal_slam_timing_T0dbg.txt)):
  ```
  처리한 스캔 101 개 (단위 ms)
  CB.add        167.7    534.4   1138.0    21.63     100   addScan 전체
  PL.match       70.8     94.2    100.9     3.40      16   순차 정합
  AE.near       260.6    449.6    615.5    13.82      64    └ LinkNearChains
  PL.loop         4.3    104.0    364.0     1.61       7   TryCloseLoop
  addScan > 300 ms 인 스캔 34 개 — 그 스캔들의 단계 평균(ms):
     AE.near    363.8
  ```
  (열: 단계 · 중앙 · 90 % · 최대 · 합 s · 몫 %.) 원 로그 한 스캔: `[ROVER_T] AE near=353.6 nmeans=6` · `[ROVER_T] CB stamp=1793084121.823 odom=3.0 add=397.7`([`rep/T0dbg.log`](../debug_log/2026-10-27/outputs/slamproc/rep/T0dbg.log)).
- **link 거리 A/B(§29.2)** — [`anal_slam_replay_link.txt`](../debug_log/2026-10-27/outputs/slamproc/anal_slam_replay_link.txt)(열: 변형 · MO 수 · 간격 중앙 · 99 % · 최대 · > 0.4 · > 0.5 · 여유 최소 · 중앙 · CPU % · 위치 차 중앙 · 최대 cm · yaw 차 최대 °):
  ```
  V0a | 4205 | 0.096 · 0.400 · 1.008 | 19 · 8 | 0.967 · 1.458 | 23 | 0.4 · 11.2 · 1.25
  T0dbg | 4204 | 0.096 · 0.401 · 1.088 | 23 · 10 | 1.294 · 1.455 | 23 | 0.4 · 11.2 · 1.25
  L10 | 4204 | 0.096 · 0.400 · 1.008 | 18 · 4 | 1.337 · 1.458 | 21 | 0.9 · 11.8 · 1.30
  L075 | 4205 | 0.096 · 0.316 · 0.800 | 13 · 4 | 0.799 · 1.453 | 21 | 1.0 · 9.9 · 1.12
  ```
  > 300 · > 500 ms 스캔 수와 사슬 수 중앙은 출력 파일에 없다 — 카드 작성 중 `rep/*.log` 로 다시 셈(PC, 원문 없음 — 발췌가 전부):
  ```
  T0dbg 101 34 15 near med 260.6 nmeans med 4.0 50
  L10 101 28 9 near med 176.0 nmeans med 3.5 50
  L075 101 28 5 near med 141.2 nmeans med 3.0 50
  ```
  (열: 변형 · 처리 스캔 · add > 300 ms · > 500 ms · LinkNearChains 중앙 · 사슬 수 중앙 · LinkNearChains 줄 수.) SUMMARY §29.2 표의 34 · 15 / 28 · 9 / 28 · 5 와 사슬 4 · 3.5 · 3 은 그대로 맞고, L075 의 'LinkNearChains 중앙 134' 만 다름(→ §5 어긋남 1).

### 4.2 한계
- 확인 주행 2 회(f2tt1 · f2tt2), 같은 no5 코스 · 같은 날 근처. 재생 A/B 는 정지 스택 옆(CPU 경쟁 작음)이라 절대값이 아니라 변형 간 비교로만 읽었다(§26.2 선언).
- 재생 위치 차 '최대 11 cm' 는 기준끼리도 같아 재생 고유 차(시작 정렬)로 봤다 — 그 정체는 미확인.
- §22 의 '통신 아님' 은 bag 기록기(다른 프로세스) 기준 수신 — SLAM 프로세스 안쪽 콜백 진입 시각은 §29 계측에도 없다(계측은 처리 시간만).
- timeout 1.5 의 대가(보정 반영이 최대 1.5 s 늦음 → 1~2 mm · 0.03°)는 보정 변화율로 낸 **추정**, 측정 아님.

### 4.3 지금 코드 영향 (11-04 저장소 기준)
- [`slam.launch.py`](../../ros2_ws/src/rover_bringup/launch/slam.launch.py) 62~78 행: `slam_mode == 'localization'` 일 때만 `params.append({'mode': 'localization', 'minimum_travel_distance': 0.30, 'minimum_travel_heading': 0.15, 'map_update_interval': 10.0, 'transform_timeout': 1.5})`(75~77 행), 근거 주석 63~74 행(10-01 §9 · §8.5 · 10-27 §21). 주석의 '전역 nvblox 층 50 · 컨트롤러 중단 6' 은 f2st1(22 + 1) · f2tf1(28 + 5) 합 = 56 = 23 + 33 과 맞다.
- 매핑 모드(launch 기본 `slam_mode:=mapping`, 91 행)는 [`slam.yaml`](../../ros2_ws/src/rover_bringup/config/slam.yaml) 30 행 `transform_timeout: 0.2` · 37~38 행 노드 간격 0.05 m · 0.03 rad 그대로 — F1 매핑을 다시 하면 이 카드의 여유는 0.2 다(매핑 모드 09 월 bag 은 정체 거의 0, §23).
- 표준 prep [`prep_fast.sh`](../tools/prep_fast.sh) 61 행 `slam.launch.py map_file:=$D/$MAP slam_mode:=localization`(MAP 기본 office_v3, 9 행) → 운용 주행은 모두 1.5.
- 정체를 줄이는 설정(`link_scan_maximum_distance` 등)은 [`slam.yaml`](../../ros2_ws/src/rover_bringup/config/slam.yaml) 42 행 `link_scan_maximum_distance: 1.5` · 51~52 행 정합 탐색 0.5 · 0.01 그대로(§29.2 결정 안 함).
- MPPI [`nav2_params.yaml`](../../ros2_ws/src/rover_navigation/config/nav2_params.yaml) 233 행 `transform_tolerance: 0.5`(10-07 주석 230~232 행). 같은 파일의 다른 `transform_tolerance: 0.2`(136 행 RPP FollowPath — 안 씀, 403 · 606 행 코스트맵, 822 행 behavior wait)는 바뀌지 않음.
- 게이트 C [`chk_drive_gate.py`](../tools/chk_drive_gate.py) 47~48 행 `C = 'OK' if (gap < 0.5 and lag < 1.0)` — lag = 수신 − stamp 라 timeout 1.5 에서 평소 ≈ −1.45 s, FAIL 은 stamp 가 ≈ 2.5 s 넘게 멈출 때. 실패 창(> 1.5 s 정체)을 직접 잡는 검사는 없다(→ [게이트 정리 카드](drive-gate-consolidation.md)).
- 재생 도구 [`run_slam_replay.sh`](../tools/run_slam_replay.sh) 12~13 행이 지도 `office_v3` · 0.30 · 0.15 · 10.0 · 1.5 를 **손으로 다시 적는다** — `slam.launch.py` 를 바꾸면 이 줄도 같이 고쳐야 재생이 운용과 같다.
- Jetson `~/slam_dbg_ws`(계측판)는 운용에 안 쓰임(launch 는 `~/slam_ws`, `slam_build:=fork`). 계측판 소스 변경은 저장소에 없고 `prep_slam_dbg_1027.sh` 의 치환 스크립트가 전부.

## 5. 내 실수 · 기록 어긋남
### 5.1 §16 '방아쇠는 부하' → §21.2 정정
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 사용자 "부하가 문제 아닌가?" 에 답 — `jobs/chk_tf_lag.py`(층 경고 ↔ Control loop missed 겹침 · 슬라이스 앞섬) |
| 본 것 | 경고 22 중 20 이 ±0.5 s 안에 Control loop missed(무작위 11 %) · bag 기준 '슬라이스 앞섬' > 0 은 22 중 8 |
| 처음 추론 | 두 경고가 같은 nav2 처리 지연에서 나옴 → 방아쇠는 부하. 앞섬이 없는 14 번은 '코스트맵 쪽이 TF 를 못 받은 것' |
| 의심한 이유 | 사용자가 부하 · TF 지연을 '해결할 문제' 로 지정 → 부하 자체를 재 봄 |
| 판별 시험 | 주행 중 CPU(/proc · tegrastats) · 사건 초 코어 사용률 · 실패 로그의 Requested time 을 map→odom stamp 정체 창과 대조 |
| 결론 | 포화 아님(68.5 %, 사건 초 73 %) · 실패 33/33 이 stamp 정체 창 안 → 원인 = SLAM stamp 정체. 겹침 20/22 는 같은 순간의 결과끼리 겹친 것으로 봄(Control loop missed 와 정체의 인과는 미확인) |
| 다음에 알아보는 법 | TF 외삽 실패는 먼저 그 프레임 쌍의 **stamp 진행**(수신 간격이 아니라)을 본다. '겹침' 은 원인이 아니라 같은 사건의 두 증상일 수 있다 — 부하는 포화 지표로 따로 잰다 |
| 스크립트 핵심 | `anal_slam_freeze.py` 24~26 · 46 행(§4.1) |
| 나온 결과 | `nav2 odom→map 외삽 실패 33 번 중 위 창 안 33 번` |
| 데이터 | [`chk_tf_lag_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_tf_lag_f2st1.txt) → [`anal_load_f2tf1.txt`](../debug_log/2026-10-27/outputs/load/anal_load_f2tf1.txt) · [`anal_slam_freeze_f2tf1.txt`](../debug_log/2026-10-27/outputs/load/anal_slam_freeze_f2tf1.txt). 정리 페이지 [10-27](../debug_log/2026-10-27/figures/day_summary_1027.html) '바로잡은 내 오류' |

### 5.2 기록 어긋남(원문 대조, 11-04 카드 작성 중)
1. **§29.2 표 'LinkNearChains 중앙 176 · 134'**: [`anal_slam_timing_link.txt`](../debug_log/2026-10-27/outputs/slamproc/anal_slam_timing_link.txt) 에는 `AE.near` 줄이 없고 `PL.edges`(AddEdges 전체) 176.3 · 133.6 만 있다 — 표가 AddEdges 를 옮긴 것. 로그로 다시 센 LinkNearChains 중앙은 176.0 · **141.2**(§4.1). 기준 260 은 두 값이 같아(260.0 · 260.6) 차이 없음. 결론(기준 미달)은 그대로.
2. **§16 '앞섬 > 0 은 22 중 8' 과 §21.2 'f2st1 23/23 이 창 안'**: §16 은 **슬라이스 stamp** 를 bag 최신 map→odom stamp 와 비교했고(`chk_tf_lag.py` 4 행), §21 은 nav2 로그의 **Requested time** 을 실패 창과 비교했다 — 다른 양이다. SUMMARY 는 §16 의 '14 번은 코스트맵이 못 받음' 읽기를 따로 철회하지 않았다(§21.2 가 원인 판정만 바꿈).
3. **§23 표의 bag 수 · 합**: '10-07~10-13 순회 21 개 · 724' · '10-14~10-23 28 개 · 873' 은 tsv 를 날짜 · mode=localization 으로 다시 묶은 값(rt1 · rt2 제외 21 개 · **881**, 27 개 · **812**)과 다르다. 1 m 당 중앙 1.83 은 같다. 묶음 목록 원문 없음 — 결론(위치 추정 모드에서만 매 주행 수십 번)은 바뀌지 않음.
4. **§30 '계산 부하' 행** 은 머리 '최근 no5 4 회 기준' 아래 있지만 tegrastats 원문은 f2tf1 · f2tt1 두 주행뿐([`anal_sys_perf.txt`](../debug_log/2026-10-27/outputs/load/anal_sys_perf.txt) 2 줄; SUMMARY 는 f2st1 만 없다고 적음, f2sa3 도 없음).
5. 게이트 쪽 어긋남(§25 'f2tf1 게이트 → 출발 77 s' 등)은 [게이트 정리 카드 §5](drive-gate-consolidation.md).

## 6. 남은 것
- 정합 1 회 비용(correlation_search_space_dimension · 각도 해상도)과 link 0.75 m 조합 재생 A/B — 결정 대기(§29.2).
- 처리 스캔의 절반쯤은 ProcessLocalization 이 ≈ 0 ms(`AS.proc` 중앙 0.1 ms, `AE near` 줄 50 개 / 처리 101 개) — 어떤 스캔이 정합 경로를 타는지 미확인(카드 작성 중 본 것).
- 10-01 → 10-07 사이 정체가 늘어난 이유(표본 1 개).
- 전역 nvblox 층을 켠 09-22 이후 주행의 '가짜 막힘' 을 이 기전으로 다시 볼지(§23 함의 ②).
- 정체가 1.5 s 를 넘는 일을 주행 중 알리는 감시 — 없음(게이트 C 는 주행 전 5 s 만, 문턱 2.5 s 상당).
- [정지 중 방향 드리프트](stationary-yaw-drift.md) 와의 관계: 위치 추정은 0.30 m · 0.15 rad(포크는 거리 또는 회전) 넘게 움직일 때만 스캔을 처리한다 — 정지 중 SLAM 이 안 고치는 것과 이 문턱의 관계는 이 카드에서 재지 않음(**미확인**).

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2a2 | 첫 관측(timeout 0.2) | 10-01 §8.5 |
| f2c2 | 1.49 s 정체 → MPPI tolerance 0.5 | 10-07 §5 · §6 |
| f2st1 · f2tf1 | 정체 · 실패 측정(timeout 0.5) | 10-27 §15 · §19 · §21, `outputs/drives/f2st1/` · `f2tf1/`, bag `2026-10-27/bags/bag_f2st1.tgz` · `bag_f2tf1.tgz`(git 제외) |
| f2tt1 · f2tt2 | timeout 1.5 확인 | 10-27 §25 · 10-28 §4, `2026-10-27/outputs/drives/f2tt1/` · `2026-10-28/outputs/drives/f2tt2/` |
| 재생 V0a · V0b · V1_noloop · V2_res02 · V3_dim03 · V4_buf10 | 재생 A/B(f2tt1 첫 210 s) | 10-27 §26.3, [`outputs/slamproc/rep/`](../debug_log/2026-10-27/outputs/slamproc/rep/) |
| 재생 T0dbg · L10 · L075 | 계측판 · link 거리 | 10-27 §29, 같은 곳 |
| bag 112 개 이력 | §23 | [`anal_slam_freeze_hist.tsv`](../debug_log/2026-10-27/outputs/load/anal_slam_freeze_hist.tsv) |
| `anal_slam_freeze.py` · `chk_mapodom_window.py` · `anal_load_f2tf1.py` · `anal_slam_freeze_cause.py` · `anal_slam_freeze_hist.py` · `anal_slam_freeze_trigger.py` · `anal_slam_replay.py` · `anal_slam_timing.py` · `chk_tf_lag.py` | 정체 지표 · 중단 순간 · 부하 · 원인 · 이력 · 정합 문턱 · 재생 비교 · 단계 시간 · (§16) | `2026-10-27/jobs/` |
| `up_slam_tt15_1027.sh` · `apply_slam_tt15_1027.sh` · `run_prep_tt15_1027.sh` | timeout 1.5 배포 · prep | 같은 곳 |
| `prep_slam_dbg_1027.sh` · `up_slam_replay_1027.sh` · `run_slamrep_batch_1027.sh` · `up_slamrep_batch_1027.sh` · `up_slamrep_dbg_1027.sh` · `up_slamrep_link_1027.sh` | 계측판 빌드 · 재생 묶음 실행 | 같은 곳 |
| `run_slam_replay.sh` · `slam_replay_feed.py` | 재생 A/B(도메인 42) | `Docs/tools/` |
| `fig_f2tt1_summary.py` | 미래 여유 시간선 · 지표 표 그림 | `2026-10-27/jobs/` → [`f2tt1_summary.png`](../debug_log/2026-10-27/figures/f2tt1_summary.png) |

## 8. 도구 해설
공통: `anal_*` · `chk_mapodom_window.py` · `chk_tf_lag.py` 는 PC(Git Bash, Python rosbags), 입력 = PC 로컬 `bags/bag_<주행>.tgz` 를 푼 폴더 + `bags/logs_<주행>/`(slam.log · nav2.log · top) — bag · 로그는 git 제외. Jetson 쪽(`run_*` · `prep_*` · `apply_*`)은 스크래치패드 러너 `run_jn.sh` 경유, 로버 안 움직임.

### 8.1 `anal_slam_freeze.py` — stamp 정체 · 실패 창 · nav2 실패 대조 (10-27 §21.2 · §25, 10-28 §4)
- 부른 형태: `anal_slam_freeze.py bag폴더 slam.log nav2.log`.
- 왜: TF 실패 33 번이 정말 map→odom stamp 가 멈춘 창 안인가(부하 가설과 가르기).
- 하는 일: `/tf` 의 map→odom 을 (bag 수신 시각, stamp) 로 모아 같은 stamp 구간으로 나눔 → 새 stamp 간격 분포(> 0.4 · > 0.5 s 수) · '새 stamp 첫 수신 때 미래 여유'(stamp − 수신) → 실패 창 [고정 stamp, 다음 stamp 수신](24~26 행) → slam.log 'Message Filter dropping'(스캔 버림) · nav2.log 'extrapolation into the future … frame [odom] to frame [map]' 의 Requested time(39~42 행) 을 창과 대조.
- 출력: 머리 4 줄 + 창마다 한 줄 + 끝 줄(§4.1 발췌) → `outputs/load/anal_slam_freeze_{f2st1,f2tf1,f2tt1}.txt` · `2026-10-28/outputs/drives/f2tt2/anal_slam_freeze_f2tt2.txt`.
- 쓰인 곳: §21.2 원인 판정 · §21 판정 선언 ② · §25 · 10-28 §4. 결함: 수신 시각이 bag 기록기 기준(nav2 가 실제로 받은 시각과 다를 수 있음). 지금 다시 쓸 수 있음.

### 8.2 `chk_mapodom_window.py` — 중단 순간 앞뒤 map→odom 나열 (10-27 §21.2)
- 부른 형태: `chk_mapodom_window.py bag폴더 epoch초…`(컨트롤러 TF 중단 로그 시각).
- 하는 일: 각 시각 −1.6 ~ +0.3 s 의 map→odom 수신 · stamp 를 '시각 기준 상대값' 으로 그대로 출력(계산 없음, 17 줄짜리).
- 출력 `outputs/load/chk_mapodom_window_f2tf1.txt`(§4.1 발췌). 쓰인 곳: '20 Hz 로 오지만 stamp 가 같은 값' 의 직접 근거. 지금 다시 쓸 수 있음.

### 8.3 `anal_load_f2tf1.py` — 부하가 포화였나 (10-27 §21.2)
- 부른 형태: `anal_load_f2tf1.py proc.log tegra.log nav2.log top1s.txt 시작 끝`.
- 하는 일: 러너 proc 기록(2 s, `/proc/<pid>/stat` utime+stime, CLK_TCK 100 · 6 코어 가정)로 프로세스별 평균 % · 전체 /proc/stat 사용률, tegrastats 코어 평균 분포 · 주파수, nav2 사건(층 경고 · Control loop missed · 컨트롤러 TF 중단) 초의 코어 사용률.
- 출력 `outputs/load/anal_load_f2tf1.txt`: `주행 15:00:03~15:07:02 (421 s) · 전체 CPU 사용률(/proc/stat) 68.5 %` · `코어 평균 ≥ 95 % 인 초 비율 1 %` · `층 경고 28 번 · 그 초 코어 평균 % 중앙 73 (전체 중앙 67)`. 프로세스 이름은 1 s top 명령줄에서(러너가 top 을 뺀 10-27 §24 뒤에는 이 입력이 없다 — 10-28 부터는 `rss_` 스냅숏 args 로 대신해야 함).
- 쓰인 곳: §16 정정. 계보: 10-22 `anal_cpu_nodes.py`([CPU 카드](cpu-load-stalls.md)) 와 같은 원천.

### 8.4 `anal_slam_freeze_cause.py` — 통신인가 처리인가 (10-27 §22)
- 부른 형태: `anal_slam_freeze_cause.py bag폴더 top1s.txt slam.log SLAM_PID`.
- 하는 일: 정체(새 stamp 간격 > 0.4 s) 구간마다 (가) `/scan` bag 수신 최대 간격 (나) odom→base_link 수신 최대 간격 (다) map→odom 발행 자체 최대 간격 (라) 1 s top 의 SLAM %CPU 최대 (마) 스캔 버림 수, 기준선 = 정체와 겹치지 않는 같은 길이 무작위 200 구간(seed 0).
- 출력 `outputs/load/anal_slam_freeze_cause_f2tf1.txt`(§4.1). 결함(머리 주석 7~8 행이 적음): bag 기록기도 UDP 로 받는 별도 프로세스 — SLAM 안쪽 수신은 못 봄. top 은 날짜를 '2026-10-27' 로 박아 둠(26 행) — 다른 날 쓰려면 고쳐야 함.

### 8.5 `anal_slam_freeze_hist.py` — 예전부터 있었나 (10-27 §23)
- 부른 형태: `anal_slam_freeze_hist.py 출력.tsv tgz…`(로컬 bag 112 개, `TMPX` 로 임시 폴더 위치).
- 하는 일: tgz 마다 .db3 · metadata · params.txt 만 풀어 `/tf` 를 읽고 지움 → 새 stamp 간격 · > 0.4 / > 0.5 s 수 · 미래 여유 중앙(= 적용된 timeout 근사) · odom→base_link 경로 길이 · 1 m 당 정체 · params.txt 의 slam mode · transform_timeout · minimum_travel_distance.
- 출력 `outputs/load/anal_slam_freeze_hist.tsv`(112 행). 묶음 표(SUMMARY §23)는 손으로 만든 것 — 묶음 목록 원문 없음(§5.2-3). 결함: params.txt 가 없는 09 월 bag 은 mode '-'; 여유 음수 bag 은 시작 정렬 문제로 추정(미확인). 지금 다시 쓸 수 있음.

### 8.6 `anal_slam_freeze_trigger.py` — 무엇에 맞춰 나나 (10-27 §26.1)
- 부른 형태: `anal_slam_freeze_trigger.py bag폴더`.
- 하는 일: 정체(> 0.4 s) 시작 시각들에 대해 ② 정체 사이 시간의 10 s 배수(±1 s) 비율 ① 정체 사이 EKF 누적 이동 · |회전|이 정합 문턱(0.30 m · 0.15 rad)을 넘는 비율 ③ 정체 직전 1 s 운동 분류(서 있음 < 1 cm · < 1° / 직진 < 3° / 회전 포함).
- 출력 `outputs/slamproc/anal_slam_freeze_trigger_{f2tt1,f2tf1}.txt`(§4.1). 결함: ① 은 정체 간격이 길면(중앙 5 s) 무작위여도 거의 늘 문턱을 넘는다 — 판별력이 약한 시험(§3). 이동 · 회전을 '이전 정합 뒤 누적' 이 아니라 '이전 정체 뒤 누적' 으로 잼.

### 8.7 `Docs/tools/run_slam_replay.sh` + `slam_replay_feed.py` — 위치 추정 재생 A/B (10-27 §26.2 · §29) ★
- 실행 위치: Jetson. 부른 형태: `SLAM_EXTRA="-p 이름:=값" [SLAM_WS=~/slam_dbg_ws] bash /tmp/run_slam_replay.sh 변형 bag폴더 [시작 s] [길이 s]`. PC 에서는 `jobs/up_slam_replay_1027.sh`(두 파일 CR 제거 · scp → `run_jn.sh`) 또는 묶음 `run_slamrep_batch_1027.sh`(+ `up_slamrep_*.sh`).
- 왜: 정체를 줄이는 SLAM 설정을 주행 없이 같은 입력으로 비교하려고(10-01 `job736` · 09-28 `job580` 의 위치 추정판).
- 하는 일(셸): `ROS_DOMAIN_ID=42` · UDP 전용 프로파일(8 행) → `SLAM_WS`(기본 `~/slam_ws`) 의 `localization_slam_toolbox_node` 를 `slam.yaml` + 위치 추정 값(office_v3 · 0.30 · 0.15 · 10.0 · 1.5 · use_sim_time, 12~13 행) + `SLAM_EXTRA` 로 `setsid nohup` → '$!' 가 곧 SLAM pid(15 행 주석: **pgrep/pkill 패턴 금지** — 본 스택 SLAM 도 같은 명령줄 꼴) → 'Registering sensor' 를 30 s 까지 기다림 → 공급기 → `kill -INT` · `-9` 그 pid 만 → 끝 줄 `MO 줄 · 스캔 버림 · 오류`.
- 하는 일(공급기): rosbag2_py 로 `/scan` · `/tf` · `/tf_static` 만 읽어 **실시간 1 배**로 다시 발행(45~54 행 대기 루프에서 /clock 0.01 s 마다), `/tf` 에서 원래 map→odom 은 빼고(57 행), 재생 SLAM 이 낸 map→odom 을 `MO <sim 수신> <stamp> <x> <y> <yaw>` 로, SLAM_PID 가 있으면 1 s 마다 `CPU <sim> <utime+stime>` 을 기록.
- 출력: Jetson `/tmp/slamrep/<변형>.txt · .log`(재부팅 소실) → PC 사본 [`outputs/slamproc/rep/`](../debug_log/2026-10-27/outputs/slamproc/rep/). 화면 줄 예: `[L075] SLAM pid 1868730(localization_sl) · 기동 1 · 추가 인자: -p link_scan_maximum_distance:=0.75` · `[L075] MO 4205 줄 · 스캔 버림 19 · 오류 0`([`run_slamrep_L075.txt`](../debug_log/2026-10-27/outputs/slamproc/run_slamrep_L075.txt)). 기동 실패 예: V2 `what():  Mapper FATAL ERROR - unable to get pointer in probability search!` · `MO 0 줄`.
- 쓰인 곳: §26.3 · §29.1 · §29.2. 계보: `job580_slamreplay.py` + `job581_b1.sh`(09-28, 매핑 · 회전 bag — [SLAM 포크 카드](slam-fork-rotation.md)) → 이 판(위치 추정 · 띄운 pid 만 정리 · `SLAM_WS`). 알려진 결함: ① 위치 추정 값 · 지도 이름을 손으로 다시 적음(§4.3) ② 입력 odom 은 bag 의 EKF 그대로 — SLAM 만 바뀐다 ③ 정지 스택 옆에서 돌아 CPU 경쟁이 작음. 지금 다시 쓸 수 있음(입력 bag 은 Jetson `/tmp/bag_<주행>` 이 있어야 함 — PC tgz 를 다시 올려야 할 수 있음).

### 8.8 `anal_slam_replay.py` — 재생 변형 비교 (10-27 §26.3 · §29.2)
- 부른 형태: `anal_slam_replay.py 원bag폴더 변형.txt…`.
- 하는 일: 변형마다 새 stamp 간격(중앙 · 99 % · 최대 · > 0.4 · > 0.5) · 미래 여유 최소 · 중앙 · CPU 평균(`CPU` 틱 차 / 시간) · **원래 SLAM 대비 위치 차**(재생 map→odom 을 같은 시각 원 bag map→odom 과 비교 — odom 이 같으므로 로버 위치 차와 같음, 첫 5 s 제외, 29~30 행).
- 출력 `outputs/slamproc/anal_slam_replay_ab1.txt` · `_link.txt`(§4.1). 결함: 원래 SLAM 자체도 정답이 아님(기준끼리 최대 11 cm 같음).

### 8.9 `prep_slam_dbg_1027.sh` + `anal_slam_timing.py` — 단계별 시간 계측 (10-27 §29)
- 실행: Jetson(빌드 ≈ 14 분, `nice -n 10 colcon build --packages-select slam_toolbox` Release) → 재생(`SLAM_WS=~/slam_dbg_ws`) → PC 분석.
- 하는 일(빌드): `~/slam_ws/src/slam_toolbox` 를 `~/slam_dbg_ws` 로 복사(없을 때) · 두 파일을 git checkout 으로 되돌린 뒤 Python 문자열 치환으로 계측 줄만 넣음 — 기준 문자열이 정확히 1 번이 아니면 중단(13~15 행). 넣는 곳: `ProcessLocalization`(순차 정합 · AddVertex · AddEdges · TryCloseLoop · 버퍼), `AddEdges` 안(LinkChainToScan · LinkNearChains + 사슬 수), `laserCallback`(odom 조회 · addScan), `addScan`(ProcessLocalization). 모두 `[ROVER_T]` 줄을 stderr 로.
- 하는 일(분석): `[ROVER_T]` 줄을 CB 줄 단위로 묶어 단계별 중앙 · 90 % · 최대 · 합 · 몫(addScan 합 대비), addScan > 300 ms 스캔의 단계 평균.
- 출력: 빌드 [`prep_slam_dbg_1027.txt`](../debug_log/2026-10-27/outputs/slamproc/prep_slam_dbg_1027.txt)(diff stat 3 파일 · 34 줄 — `slam_toolbox_common.cpp` 8 줄은 포크의 회전 조건이 같은 diff 에 보이는 것), 분석 `anal_slam_timing_T0dbg.txt` · `_link.txt`(§4.1). 결함: `_link.txt` 는 `AE.near` · `PL.match` 줄이 빠진 판(§5.2-1); 사슬 수 · > 300 ms 수는 파일에 없음.
- 동작 불변 확인: T0dbg 스캔 버림 22 · 정체 23 — 기준 V0a · V0b(19~23)와 같은 수준.

### 8.10 `up_slam_tt15_1027.sh` · `apply_slam_tt15_1027.sh` — timeout 1.5 배포 (10-27 §21.3)
- PC(WSL) 쪽이 스크래치패드 `up_slam.launch.py` 를 CR 제거 · scp → Jetson `apply_…` 가 src 에 복사, 설치본이 링크가 아니면 함께 복사, 이전 · 새 git blob · CR 수 · `'transform_timeout'` 줄 출력. 출력 [`up_slam_tt15_1027.txt`](../debug_log/2026-10-27/outputs/load/up_slam_tt15_1027.txt) `새 src blob 921d5993b0 · 설치본 blob 921d5993b0 · CR 0` · `77:                       'transform_timeout': 1.5})`. 실행 중 노드엔 적용 안 됨 — 다음 prep 부터(같은 출력 뒤 prep 에서 확인).

### 8.11 (10-01 · 10-27 §16) `job733_tfstamp.py` · `job736_locreplay.*` · `chk_tf_lag.py`
- `job733` 은 라이브 TF 의 수신 − stamp · 고유 stamp 간격(10-01 §8.5, 출력 `j733_tfstamp.txt`: `map→odom 183 개 18.3 Hz | 지연(수신−스탬프) 중앙 -0.110 …`). `job736` 은 10-01 §9 위치 추정 재생 A/B — 해설은 [F1 카드 §8](f1-office-mapping.md). `chk_tf_lag.py` 는 §16(§5.1) — 슬라이스 stamp 기준이라 nav2 의 실제 요청 시각과 다름(§5.2-2), 해설은 [J 카드](nvblox-layer-tf-drop.md).

## 9. 용어
- **stamp(시각 도장)**: 변환 메시지가 '이 시각의 값' 이라고 적는 시각. tf2 는 요청 시각을 앞뒤 stamp 사이로 보간하고, 최신 stamp 보다 뒤를 요청하면 '미래 외삽' 실패.
- **transform_timeout(slam_toolbox)**: map→odom 을 '마지막 처리 스캔 시각 + 이 값' 으로 미래에 찍는 여유. 늘리면 정체를 더 오래 견디고, 보정이 그만큼 늦게 반영된다.
- **미래 여유**: stamp − 지금. 평소 ≈ transform_timeout − 처리 지연, 0 아래면 '지금' 조회 실패.
- **정체(stamp 정체)**: map→odom 은 계속 오는데 stamp 가 안 바뀌는 구간(이 카드 지표: 새 stamp 간격 > 0.4 · > 0.5 s).
- **여유 소진 창(실패 창)**: [고정된 stamp, 다음 새 stamp 수신] — 그 안에서 '지금' 을 요청하면 실패.
- **위치 추정 모드(localization)**: 저장 포즈 그래프를 고정하고 새 스캔을 그 지도에 맞춰 위치만 추정. 새 스캔은 0.30 m · 0.15 rad 마다만 처리(10-01 §9).
- **순차 정합(MatchScan)**: 새 스캔을 최근 스캔 묶음(running scans)에 맞추는 상관 탐색(탐색 범위 0.5 m · 해상도 0.01 m).
- **LinkNearChains**: 새 스캔 둘레 `link_scan_maximum_distance`(1.5 m) 안에 있는 지도 스캔 사슬마다 순차 정합기를 다시 돌려 그래프 간선을 잇는 단계 — 이 카드에서 처리 시간의 64 %.
- **TryCloseLoop**: 멀리 떨어진 지도 부분과 맞는지 보는 루프 탐색(끄면 위치 차 중앙 0.4 → 3.6 cm, §26.3).
- **도메인 42 재생**: `ROS_DOMAIN_ID` 를 바꿔 떠 있는 스택과 통신이 섞이지 않게 같은 Jetson 에서 노드를 따로 돌리는 것.
