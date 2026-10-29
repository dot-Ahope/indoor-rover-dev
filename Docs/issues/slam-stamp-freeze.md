# SLAM map→odom 시각 정체 → nav2 TF 조회 실패

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **우회**(증상 차단) · 근본 미해결 | 10-01 ~ 10-28 | [10-01 §8.5](../debug_log/2026-10-01/SUMMARY.md) f2a2 | `ros2_ws/src/rover_bringup/launch/slam.launch.py`(transform_timeout 0.2 → 0.5 → **1.5**) | nvblox 전역 층 TF 실패 처리(같은 방아쇠, 카드 예정) · [정지 중 방향 드리프트](stationary-yaw-drift.md) |

**한 줄**: SLAM 위치 추정이 스캔 정합에 0.3~1.3 s 를 쓰는 동안 map→odom 의 시각(stamp)이 멈추고, 그 멈춤이 미래 여유(transform_timeout)를 넘으면 nav2 가 '지금' 변환을 못 찾아 컨트롤러가 멈추거나 전역 코스트맵이 틀어진다. 여유를 1.5 s 로 늘려 실패는 0 이 됐고(2 주행), 정합이 느린 원인(LinkNearChains)은 찾았지만 줄이는 설정은 아직 못 찾았다.

## 1. 증상
- 주행 중 nav2 로그 `extrapolation into the future … from frame [odom] to frame [map]` → 컨트롤러 중단 · BT 재시도 · Wait 로 1 s 넘게 정지(f2tf1 5 번, 그중 1 번 5.1 s). [10-27 §19](../debug_log/2026-10-27/SUMMARY.md)
- 같은 순간 전역 코스트맵의 카메라 장애물이 0.55 m · 7.5° 틀어진 자리에 한 장 찍힘('문이 막혔다 풀림 · 상자가 벽 쪽으로') — 이것은 nvblox 층의 실패 처리 결함이 더해진 것. [10-27 §15](../debug_log/2026-10-27/SUMMARY.md)

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론 | 데이터 |
|---|---|---|---|---|
| 10-01 §8.5 | f2a2 transformPose 오류 3 · follow_path 중단 1 조사, 포크 소스 읽기 | map→odom stamp = 마지막 스캔 시각 + transform_timeout(0.2). 관측 최대 밀림 0.57 s | 처리 밀림이 여유를 넘으면 실패 → **0.2 → 0.5** | `2026-10-01/jobs/job733_tfstamp.py` · `outputs/j733` |
| 10-27 §15 | 영상의 '코스트맵 튐' 원자료 대조 | 튄 장 2 장 = 슬라이스를 변환 없이 map 에 적은 것 · 그 0.3 s 전 층 경고 | nvblox 층이 TF 실패 때 단위 변환을 씀(결함) | `2026-10-27/outputs/block_cell/*` · `jobs/chk_gcm_fit.py` |
| 10-27 §16 | TF 실패와 부하 | 층 경고 22 중 20 이 Control loop missed ±0.5 s 안(무작위 11 %) | 방아쇠는 부하(**추정**) | `outputs/block_cell/chk_tf_lag_f2st1.txt` |
| 10-27 §21.2 | 부하 · TF 다시 봄 | CPU 68.5 %(사건 초 73 %) — 포화 아님. 실패 33/33 이 odom→map, 그때 map→odom 은 20 Hz 로 오지만 **stamp 가 0.6~1.1 s 같은 값** · 최대 간격 1.296 s · 실패 전부 '여유 소진 창' 안 | 원인은 CPU 가 아니라 **SLAM stamp 정체**(§16 추정 정정) | `outputs/load/anal_load_f2tf1.txt` · `chk_mapodom_window_f2tf1.txt` · `anal_slam_freeze_f2tf1.txt` |
| 10-27 §21.3 | 조치 | — | **transform_timeout 0.5 → 1.5**(대가: 보정 반영 최대 1.5 s 늦음 ≈ 1~2 mm · 0.03°, 추정) | `jobs/up_slam_tt15_1027.sh` |
| 10-27 §22 | 통신(UDP) 탓인가 · 공유메모리로 풀리나 | 정체 중에도 /scan · odom TF 수신 간격 평소와 같음, SLAM CPU 정체 중 72.7 % vs 기준 45.1 %, 스캔 버림 동반 37/56 | 통신 아님 → 공유메모리로는 안 풀림(**추정**, SLAM 내부 수신 시각은 미측정) | `outputs/load/anal_slam_freeze_cause_f2tf1.txt` |
| 10-27 §23 | 최근 생긴 것인가 | bag 112 개: 09 월 매핑 모드는 거의 0 · **10-07 이후 위치 추정 순회 전부 1 m 당 1~4 번** | 회귀 아님 — 위치 추정 운용 내내 있던 성질. 10-01(0.06/m) → 10-07 사이 무엇이 바뀌었는지는 미확인 | `outputs/load/anal_slam_freeze_hist.tsv` |
| 10-27 §25 | f2tt1(timeout 1.5) | 정체 그대로(> 0.5 s 33 · 최대 1.10) · 미래 여유 최소 1.139 s · **TF 실패 0 · 1 s 넘는 정지 0** | 정체 → 실패 경로가 끊김(1 회) | `outputs/load/anal_slam_freeze_f2tt1.txt` |
| 10-27 §26.1 | 정체는 언제 나나 | 정체 사이 이동 0.35 m · 0.32 rad, 정합 문턱(0.30 m · 0.15 rad) 이상 **53/54** · 10 s 지도 갱신 주기 가설 13 %(무작위 20 %) | 정합할 때마다 (지지) · 지도 갱신 (기각) | `outputs/slamproc/anal_slam_freeze_trigger_*.txt` |
| 10-27 §26.3 | 재생 A/B(루프 끔 · 해상도 · 탐색 범위 · 버퍼) | 기준 두 번 19 · 23 정체, 변형 15~19 · 루프 끔은 위치 차 중앙 0.4 → 3.6 cm | 채택 없음 · 무거운 곳은 이 넷이 아님 | `outputs/slamproc/anal_slam_replay_ab1.txt` · `Docs/tools/run_slam_replay.sh` |
| 10-27 §29.1 | 포크에 단계별 시간 계측(동작 불변) | addScan 중앙 168 · 최대 1138 ms 중 **LinkNearChains 64 %**(중앙 261 ms) | 가까운 지도 스캔 사슬마다 다시 정합하는 비용 | `outputs/slamproc/anal_slam_timing*.txt` · `jobs/prep_slam_dbg_1027.sh` |
| 10-27 §29.2 | link_scan_maximum_distance 1.5 → 1.0 · 0.75 | 0.75: > 0.4 s 정체 19~23 → 13 · 최대 1.14 → 0.81 s · 위치 차 중앙 1.0 cm | 줄지만 기준(절반) 미달 — 운용 안 바꿈 | `outputs/slamproc/anal_slam_*_link.txt` |
| 10-28 §4 | f2tt2(같은 구성 반복) | > 0.5 s 정체 31 · 최대 0.996 s · **TF 실패 0** | timeout 1.5 운용 확정(2/2) | `2026-10-28/outputs/drives/f2tt2/*` |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| CPU 포화(부하) | 사건 초의 코어 사용률 · 프로세스별 | 평균 68.5 %, 사건 초 73 % | **기각**(§21.2) — §16 의 '부하가 방아쇠' 추정을 정정 |
| 노드 사이 통신(UDP) 지연 | 정체 구간 vs 기준 구간의 입력 수신 간격 | 같음(0.115 vs 0.113 s) | **기각**(§22, 추정 — SLAM 프로세스 안쪽은 미측정) |
| 최근 회귀 | 과거 bag 112 개 같은 지표 | 10-07 이후 일정 | **기각**(§23) |
| 위치 추정 정합 때마다 처리 지연 | 정체 사이 이동 · 회전 vs 정합 문턱 | 53/54 | **지지**(§26.1) |
| 정합 안 어느 단계 | 포크 계측 | LinkNearChains 64 % | **확인**(§29.1) |

## 4. 조치와 효과
- transform_timeout 0.2 → 0.5(10-01) → **1.5**(10-27). 효과: f2tf1(0.5) TF 실패 33 · 1 s 넘는 정지 1 → f2tt1 · f2tt2(1.5) 둘 다 0.
- 한계: 정체 자체는 그대로(주행당 > 0.5 s 30 번 안팎). 정체가 1.5 s 를 넘으면 다시 실패한다(관측 최대 1.296 s, 10-12 이상 시기 4.4 s 한 번).

## 5. 내 실수
- §16 에서 '부하가 방아쇠'(Control loop missed 겹침 20/22)로 답했다가 §21.2 에서 CPU 포화가 아니라 stamp 정체로 정정 — 실수 칸 형식 기록은 [10-27 정리 페이지](../debug_log/2026-10-27/figures/day_summary_1027.html)의 '바로잡은 내 오류'.

## 6. 남은 것
- 정합 1 회 비용(correlation_search_space_dimension · 각도 해상도)과 link 0.75 m 조합 재생 A/B — 결정 대기(§29.2).
- 10-01 → 10-07 사이 정체가 늘어난 이유(표본 1 개).
- 전역 nvblox 층을 켠 09-22 이후 주행의 '가짜 막힘' 을 이 기전으로 다시 볼지(§23 함의 ②).

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2a2 | 첫 관측(timeout 0.2) | 10-01 §8.5 |
| f2st1 · f2tf1 | 정체 · 실패 측정(timeout 0.5) | 10-27 §15 · §19 · §21 |
| f2tt1 · f2tt2 | timeout 1.5 확인 | 10-27 §25 · 10-28 §4 |
| 재생 V0a~V4 · T0dbg · L10 · L075 | 재생 A/B · 계측 | 10-27 §26.3 · §29, `outputs/slamproc/rep/` |
| `anal_slam_freeze.py` · `anal_slam_freeze_hist.py` · `anal_slam_freeze_trigger.py` · `anal_slam_timing.py` | 정체 지표 · 과거 · 정합 문턱 · 단계 시간 | `2026-10-27/jobs/` |
| `run_slam_replay.sh` · `slam_replay_feed.py` | 재생 A/B(도메인 42) | `Docs/tools/` |
