# PathBlockedAhead 막힘 판정 — 99 → 100 안은 내 오류, '계획 뒤 새로 생겼나' 로 가르는 only_new (8 기: 10-23 §20.1 ~ §20.5 · §20.7 ~ §20.9)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **조사 중(조치 적용 · 판정 논리는 오프라인으로 확인 · 실주행 효과 미확인)** — 서쪽 통로 막힘 오판의 원인(계획기가 이미 99 칸을 지나는 경로를 냄 → 같은 틱에 '막힘')을 로그 시각으로 측정했고, 막힘을 '받을 때보다 값이 커진 점' 만 세는 `only_new` 를 넣었다. bag 재생 4 주행 · 9 사건에서 기대대로 빠지고 남음(§20.7). 그러나 10-23 실주행(f2rp4 · f2rp5)에선 only_new 알림이 **0 줄** — 서쪽 통로 막힘 0 은 경로가 덜 빠듯하게 그려진 덕(§20.5). 실주행 첫 알림은 이후 10-26 f2sa3 | 10-23 §20.1 ~ §20.9 (판정 노드 자체는 10-01 §8.39 부터) | [10-23 §20.1](../debug_log/2026-10-23/SUMMARY.md) f2rp3(no5) 서쪽 통로에서 막힘 중단 5 번 · 복구 Wait 2 회 | [`path_blocked_ahead_condition.cpp`](../../ros2_ws/src/rover_navigation/src/path_blocked_ahead_condition.cpp) 19~24 · 71 · 108~122 · 152 행(`only_new`, 커밋 `0a6e5f73`) · BT [`nav_to_pose_no_spin.xml`](../../ros2_ws/src/rover_navigation/config/nav_to_pose_no_spin.xml) 103~108 행 `only_new="true"`. Jetson 배포 [`up_pba_onlynew_1023.sh`](../debug_log/2026-10-23/jobs/up_pba_onlynew_1023.sh)(빌드만, 다음 prep 부터) | [경로 추종 · 재계획 → B0](path-tracking-replan-b0.md)(재계획을 끈 구성 — 이 판정이 유일한 '주행 중 재계획' 계기, B0 확정 조건) · [F2 기준선 no5](f2-baseline-no5.md)(같은 서쪽 통로 · 같은 코스) · [상자 옆 정지 — 기전](box-side-stall-cause.md)(내접 99 칸 = 칸 판정이 최대 한 칸 보수적인 이유) · [상자 옆 정지 — 대책](box-side-stall-remedies.md)(MonotoneEscape — 막힘 뒤 복구 차례) · [F2 순회 · 위치 점프](f2-patrol-loc-jump.md)(10-01 §8.39 이 노드를 만든 f2a12 의자 정체) · [낮은 상자 기억 · 전역 nvblox](low-box-global-memory.md)(재계획 0.01 ↔ 0.5 Hz 의 앞 결정) · [BT 끝 방향 CopyPath](bt-copypath-end-yaw.md)(BT 경로의 절반이 원경로 — 재생 도구가 따라야 했던 분기) · [주행 운영 10-19 ~ 10-23](drive-ops-1019-1023.md)(§20.6 영상 도구) |

**한 줄**: 주기 재계획을 끈 구성(0.01 Hz + 막힘 때만)으로 no5 를 달리자 서쪽 통로에서 PathBlockedAhead 가 새 경로마다 같은 틱에 '막힘'(비용 99 = 내접)을 내 5 번 멈추고 복구 Wait 까지 갔다(f2rp3). 처음엔 문턱을 99 → 100(치명)으로 올리자고 했으나, 세어 보니 **쓸모 있던 상자 막힘도 전부 99** 였다 — 문턱을 올리면 둘 다 꺼진다(내 오류). 둘을 가르는 것은 값이 아니라 **경로를 받은 뒤 몇 초에 막혔나**(서쪽 통로 0.01~0.02 s · 상자 58~60 s)였고, 그래서 '받을 때 이미 99 였던 점은 값이 더 커질 때만 센다' 는 `only_new` 를 넣었다. bag 재생으로 판정 논리를 확인했지만 그날 실주행에선 작동 기회가 없었다.

## 1. 증상
- 10-23 §20.1 f2rp3(no5, 재계획 0.01 Hz + PathBlockedAhead): 8/8 · 접촉 0 · 최소 정확 여유 4.0 cm, 그러나 **복구 Wait 2 회**(선언 기준 ≤ 1) — PathBlockedAhead 주행 중단 6 번 중 5 번이 서쪽 통로 같은 자리((−1.64, −4.72) · (−1.65, −4.70~−4.75) · (−1.64, −4.47), 비용 99). 로버는 그 자리를 실제로 지나갔다(여유 4 cm 이상).
- 같은 날 b910(f2rp1 · f2rp2)은 막힘 중단이 각 1 번(상자, 예상된 것).
- 영상(사용자 요청) `videos/f2rp3_west_corridor.mp4`(git 제외): 통로 y ≈ −4.7 에서 왼쪽 덩어리(−2.1~−1.9, −4.6~−5.2)와 오른쪽 벽 사이를 전역 경로가 내접(분홍) 띠로 지나고 막힘 검사 구간에 빨간 × (−1.65, −4.70). 사용자: "해당 위치에 상자 존재한다"(§20.2) — 유령 칸 아님.

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-01 §8.39(앞 이야기) | PathBlockedAhead 노드 도입 | f2a12 의자가 통로를 0.39 m 로 좁혔는데 목표당 1 회 계획이라 45 s 떪 | 앞 0.30~1.5 m 경로점 비용 ≥ 99 가 2 s → 중단 · 재계획 | 노드 머리 주석 3~17 행 · [F2 순회 카드](f2-patrol-loc-jump.md) |
| 10-23 §20 · §20.1 | f2rp3(no5) | 막힘 중단 6(서쪽 통로 5 · 출발 상자 1), Wait 2, 목표 5 52.1 s(10-15 f2v2 31.6 s), 짧은 멈칫 20 | `min_cost 99` 는 막힘 신호로 너무 예민. **숨은 결합(추론)**: 10-01 이후 0.5 Hz 재계획이 2 s 마다 타이머를 리셋해 99 칸이 2 s 를 못 채웠다 → 재계획을 끄자 드러남. 대책 ① 99 → 100(가장 단순) ② 다시 그려도 같은 자리면 무시 ③ 연속 칸 수 | [`run_f2rp3.txt`](../debug_log/2026-10-23/outputs/run_f2rp3.txt) · [`pathblocked_f2rp3.txt`](../debug_log/2026-10-23/outputs/pathblocked_f2rp3.txt) · [`nav_events_ms_f2rp3.txt`](../debug_log/2026-10-23/outputs/nav_events_ms_f2rp3.txt) · [`anal_stops_f2rp3.txt`](../debug_log/2026-10-23/outputs/anal_stops_f2rp3.txt) · [`anal_dip_events_f2rp3.txt`](../debug_log/2026-10-23/outputs/anal_dip_events_f2rp3.txt) · [`fig_replan_video_f2rp3.txt`](../debug_log/2026-10-23/outputs/fig_replan_video_f2rp3.txt) |
| 10-23 §20.2 | 바꾸기 전 '쓸모 있던 막힘' 의 값을 셈 → **①은 내 오류** | 처음 막힘이 **전부 비용 99**(상자 f2rp1 (1.46, 0.04) · f2rp2 (1.41, 0.02) · f2rp3 복귀 (1.35, 0.04) · f2von2 (1.34, 0.05)), 100 은 0 번. 경로 받은 뒤 처음 막힘까지: 서쪽 통로 0.01~0.02 s × 5 + 4.54 s × 1, 상자(0.01 Hz) 58.4~59.2 s, 14:48:15 (−1.64, −4.47) 29.87 s | 100 으로 올리면 상자 막힘 재계획도 꺼짐 → 기각. 판정 기준은 '값' 이 아니라 '계획 뒤 새로 생겼나' → **`only_new` 구현 · 배포**(빌드만) | [`anal_pba_timing.txt`](../debug_log/2026-10-23/outputs/anal_pba_timing.txt) · [`anal_pba_timing.sh`](../debug_log/2026-10-23/jobs/anal_pba_timing.sh) · 입력 [`nav2_f2rp1.log`](../debug_log/2026-10-23/outputs/nav2_f2rp1.log) ~ `nav2_f2rp3.log` · [`nav2_f2von2.log`](../debug_log/2026-10-23/outputs/nav2_f2von2.log) · [`up_pba_onlynew_1023.txt`](../debug_log/2026-10-23/outputs/up_pba_onlynew_1023.txt) |
| 10-23 §20.3 | 사용자 "99 를 막힘으로 셌는데 어떻게 통과했나" | 막힘을 세는 2 s 동안 로버는 계속 감(한 주기 ≈ 0.1 m). 마지막 새 경로 14:47:28.58 막힘 점 0.35 m 앞 → 30.0 s 에 점이 0.30 m 안(검사 안 하는 구간)으로 → 2 s 를 0.5 s 남기고 해제 → 통과 · 43.6 도착 | '0.1 m 씩 기어가다 사각(skip_near)에 들어가 풀림' — 우연에 가까운 통과. 99 칸이라도 실제로 닿지는 않음(칸 판정이 최대 한 칸 보수적, 추정) | [`anal_pose_at_f2rp3.txt`](../debug_log/2026-10-23/outputs/anal_pose_at_f2rp3.txt) · [`anal_pose_at.py`](../debug_log/2026-10-23/jobs/anal_pose_at.py) |
| 10-23 §20.4 · §20.5 | **f2rp4**(no5, only_new) — 판정 ③ '서쪽 통로에서 only_new 알림이 찍힘' | 8/8 · 접촉 0 · 막힘 중단 1(복귀 상자, 경로 받고 56.6 s) · Wait 0 · 목표 5 52.1 → **32.6 s**. 최소 정확 여유 2.9 cm(남서 돌아서기). **only_new 알림 0 줄**, 스무더 충돌 거부 f2rp3 다수 → 4 | ③ ✘(확인 불가): 서쪽 통로 막힘 0 은 **경로가 덜 빠듯하게 그려진 것**이지 only_new 덕이 아님. 새 .so 적재는 BT 가 `only_new` 포트를 받아들였다는 것으로 간접 확인(미확인으로 둠) | [`run_f2rp4.txt`](../debug_log/2026-10-23/outputs/run_f2rp4.txt) · [`anal_pba_timing_f2rp4.txt`](../debug_log/2026-10-23/outputs/anal_pba_timing_f2rp4.txt) · [`anal_band_run_f2rp4.txt`](../debug_log/2026-10-23/outputs/anal_band_run_f2rp4.txt) · [`nav2_f2rp4.log`](../debug_log/2026-10-23/outputs/nav2_f2rp4.log) |
| 10-23 §20.7 | **오프라인 재생** — C++ 판정을 파이썬으로 옮겨 기록 입력으로 50 Hz. 판정(실행 전) ① false 가 실제 중단을 ±0.1 s 로 모두 재현 ② true 에서 서쪽 통로 빠짐 ③ 상자 남음 | f2rp1 · rp2 · rp4 1 → 1(상자, 받을 때 41~51), **f2rp3 6 → 2**(서쪽 통로 4 빠짐 · 14:48:15(받을 때 84) · 상자(45) 남음). 반사실 보강: 경로 #3 을 도착까지 이어 판정 → 연속 막힘 0.00 s | ①②③ ✔ — '계획기가 알고 지나간 99 만 빼고 새 막힘은 잡는다'(4 주행 · 9 사건). 시험한 것은 **판정 논리**, .so 자체는 아님. 도구 첫 판 실수 2 개(0.1 s 간격 · 부동소수 비교) 고침. **§20.1 · §20.2 정정**: 서쪽 통로 막힘 4 번은 목표 4 구간, 목표 5 의 52 s 와 무관 | [`anal_pba_replay_f2rp3.txt`](../debug_log/2026-10-23/outputs/anal_pba_replay_f2rp3.txt) · [`_f2rp1.txt`](../debug_log/2026-10-23/outputs/anal_pba_replay_f2rp1.txt) · [`_f2rp2.txt`](../debug_log/2026-10-23/outputs/anal_pba_replay_f2rp2.txt) · [`_f2rp4.txt`](../debug_log/2026-10-23/outputs/anal_pba_replay_f2rp4.txt) · [`anal_pba_replay_extend_f2rp3.txt`](../debug_log/2026-10-23/outputs/anal_pba_replay_extend_f2rp3.txt) |
| 10-23 §20.8 · §20.9 | **f2rp5**(b910, B0 확정) — 판정 ② 상자가 막으면 재계획이 일어남 | (1.30, 0.04) 비용 99, 경로 받고 **59.8 s** 뒤 → 17:22:42 중단 → 새 경로. only_new 알림 0 줄 | ② ✔ — only_new 가 새 정보를 지우지 않음(실주행 2 사례: f2rp4 · f2rp5). 상자 옆 여유 3.1 cm 는 다른 문제(→ [B0 카드](path-tracking-replan-b0.md)) | [`anal_pba_timing_f2rp5.txt`](../debug_log/2026-10-23/outputs/anal_pba_timing_f2rp5.txt) · [`nav_events_ms_f2rp5.txt`](../debug_log/2026-10-23/outputs/nav_events_ms_f2rp5.txt) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 서쪽 통로 막힘은 유령 칸 탓 | 영상 · 사용자 현장 확인(§20.2) | 실물 상자와 벽 사이 | **기각** |
| 막힘 문턱을 100 으로 올리면 오판만 없앤다(§20.1 대책 ①, '상자는 100' 은 추정이었음) | 쓸모 있던 막힘의 실제 값(§20.2) | 상자 막힘 4 개 모두 99, 100 은 0 | **기각** — 내 오류(§5 실수 1) |
| 오판과 진짜 막힘은 '경로를 받은 뒤 처음 막힘까지 걸린 시간' 으로 갈린다 | smoother 'Received a path to smooth' ↔ 첫 'PathBlockedAhead … 지속되면' 시각 차(§20.2) | 서쪽 통로 0.01~0.02 s(같은 틱 — 계획기가 그 칸을 알고 지남) · 상자 58~60 s(주행 중 새 정보) | **지지(측정)** |
| 10-01 이후 0.5 Hz 재계획이 막힘 타이머를 리셋해 서쪽 통로 오판을 가려 왔다 | 재계획 끈 f2rp3 에서 처음 드러남(§20.1) | 정황(같은 통로 10-15 f2v2 · 0.5 Hz 는 막힘 정지 없이 통과 — 이 카드의 비교는 f2v2 의 막힘 로그를 세지 않음) | **추정**(0.5 Hz 주행의 막힘 '감지' 줄 수를 세어 보지 않음) |
| only_new 는 오판만 빼고 새 막힘은 남긴다 | bag 재생 4 주행 · 9 사건(§20.7) · 실주행 f2rp4 · f2rp5 상자 막힘 | 재생 기대대로 · 실주행 상자 2/2 재계획 | **지지(판정 논리)** — 실주행에서 '빠지는 쪽' 작동은 10-23 엔 0 회 |
| 99 칸을 지나도 실제로 닿지 않는 것은 칸 판정이 보수적이라서 | §20.3 실제 정확 여유 4.0 cm 이상 | 내접 = 칸 중심 거리 ≤ 0.175, 장애물 칸은 점이 칸 어디에 있어도 칸 전체 | **추정**(10-15 칸 판정 뒤집힘 2.7~4.4 cm 와 같은 기제로 봄) |

## 4. 조치와 효과
- **바꾼 것(10-23 §20.2, 커밋 `0a6e5f73`)** — 경로를 받은 순간 각 점의 칸 값을 저장(`init_cost_`), 막힘은 `지금 값 ≥ min_cost` **이고** `지금 값 > 받을 때 값` 일 때만. `only_new="false"` 면 예전 동작. 코드(지금 [`path_blocked_ahead_condition.cpp`](../../ros2_ws/src/rover_navigation/src/path_blocked_ahead_condition.cpp)):
  ```cpp
  // 108~121 행: 경로가 바뀌면(stamp · 점 수) 타이머 리셋 + 받은 순간의 칸 값 저장
  init_cost_[i] = cell_cost(path.poses[i]);
  if (init_cost_[i] >= min_cost) {++known;}
  ...
  RCLCPP_INFO(..., "PathBlockedAhead: 새 경로 점 %d 개가 받을 때 이미 비용 ≥ %d — 값이 더 커질 때만 막힘으로 셈", known, min_cost);
  // 151~152 행: 앞 0.30~1.5 m 점마다
  if (c < min_cost) {continue;}
  if (only_new && c <= init_cost_[i]) {continue;}   // 계획 때 이미 알던 값 — 다시 계획해도 같은 답
  ```
  BT(지금 [`nav_to_pose_no_spin.xml`](../../ros2_ws/src/rover_navigation/config/nav_to_pose_no_spin.xml) 108 행): `<PathBlockedAhead path="{path}" lookahead="1.5" skip_near="0.30" hold_time="2.0" min_cost="99" only_new="true"/>`.
- **판단의 원천 출력** — [`anal_pba_timing.txt`](../debug_log/2026-10-23/outputs/anal_pba_timing.txt)(도구 [`anal_pba_timing.sh`](../debug_log/2026-10-23/jobs/anal_pba_timing.sh) — awk 로 'Received a path to smooth' 시각 `p` 를 기억, 'PathBlockedAhead: 앞 경로 … 지속되면 재계획' 줄에서 `t-p` 출력):
  ```
  == nav2_f2rp1.log
    처음 막힘 (1.46, 0.04) 비용 99 · 경로 받고 59.23 s 뒤
    처음 막힘 (1.46, 0.04) 비용 99 · 경로 받고 62.99 s 뒤
  == nav2_f2rp3.log
    처음 막힘 (-1.64, -4.72) 비용 99 · 경로 받고 0.02 s 뒤
    처음 막힘 (-1.64, -4.72) 비용 99 · 경로 받고 4.54 s 뒤
    처음 막힘 (-1.65, -4.70) 비용 99 · 경로 받고 0.02 s 뒤
    ...
    처음 막힘 (-1.64, -4.47) 비용 99 · 경로 받고 29.87 s 뒤
    처음 막힘 (1.35, 0.04) 비용 99 · 경로 받고 58.38 s 뒤
  == nav2_f2von2.log
    처음 막힘 (1.34, 0.05) 비용 99 · 경로 받고 0.03 s 뒤
  ```
  (f2rp1 의 두 줄은 한 사건 — 타이머가 한 번 다시 시작됨, §17.1. f2von2 는 0.5 Hz 재계획 구성이라 상자도 새 경로 0.03 s 뒤.)
- **재생 결과** — [`anal_pba_replay_f2rp3.txt`](../debug_log/2026-10-23/outputs/anal_pba_replay_f2rp3.txt):
  ```
  == only_new=false(예전 · 재현 확인) → 막힘 중단 6 번
    14:47:15.57  점 (-1.64, -4.72) 비용 99 · 경로 #3(원경로, 받은 14:47:09.01, 받을 때 그 칸 99) · 실제 중단과 차 0.01 s
    ...
    14:51:40.56  점 (1.35, 0.04) 비용 99 · 경로 #12(스무딩, 받은 14:50:40.16, 받을 때 그 칸 45) · 실제 중단과 차 0.01 s
  == only_new=true(새 판) → 막힘 중단 2 번
    14:48:15.57  점 (-1.64, -4.47) 비용 99 · 경로 #8(원경로, 받은 14:47:43.67, 받을 때 그 칸 84) · 실제 중단과 차 0.03 s
    14:51:40.56  점 (1.35, 0.04) 비용 99 · 경로 #12(스무딩, 받은 14:50:40.16, 받을 때 그 칸 45) · 실제 중단과 차 0.01 s
  ```
- 효과: 재생 f2rp3 막힘 중단 6 → 2(서쪽 통로 4 빠짐), 반사실 보강에서 경로 #3 을 계속 썼어도 막힘 0.00 s. 실주행 f2rp4 · f2rp5 상자 막힘 재계획 그대로.
- 한계: ① 재생은 판정 논리만 — 막힘을 안 셌을 때의 이후 경로 · 로버 움직임은 재현 못 함(반사실은 옛 동작의 실제 길로 근사) ② 전역 코스트맵 발행 1 Hz 라 '받을 때 값' 이 최대 1 s 묵음 — 그 사이 생긴 장애물은 계획기도 같은 판을 봤을 것으로 보고 같은 판단(추정, 노드 주석 24 행) ③ 14:48:15 (−1.64, −4.47) 처럼 '주행 중 84 → 99' 로 오른 칸은 only_new 로도 남는다 — 원인 미확인 ④ **only_new 는 '목표당 1 회 + 막힘' 구성 전제**(§20.2): 0.5 Hz 재계획에선 상자도 새 경로 0.03 s 뒤라 '이미 알던 것' 으로 빠진다.
- **지금 코드 영향(11-03 확인)**: 노드 기본 `only_new` = true(71 · 90 행) · BT 108 행도 true. 이 BT 는 `replan_hz` 와 무관하게 쓰이므로 **표준 순회 prep(`prep_patrol.sh` 17 행 `REPLAN_HZ` 기본 0.5)에서도 only_new 가 켜져 있다** — 그 구성에선 2 s 마다 새 경로가 상자를 이미 '안다' 고 보아 상자 막힘 재계획이 거의 일어나지 않을 것(추정; 대신 0.5 Hz 재계획 자체가 상자를 피해 다시 그림). 0.5 Hz + only_new 조합의 주행 기록은 이 시기에 없음. 작업 트리 cpp 의 sha256 앞 12 자 = 배포 해시 `d8e03afcc44b`(10-23 이후 cpp 변경 없음).

## 5. 내 실수 · 기록 어긋남
1. **막힘 문턱 99 → 100 을 '가장 단순 · 설명 쉬움' 으로 1 순위에 둠**(10-23 §20.1 → §20.2 정정, 칸 형식은 SUMMARY 에) — 하려 한 것: 서쪽 통로 오판 제거 · 처음 추론: 상자가 경로를 막으면 경로점이 상자 칸(100)에 들어가 100 으로도 잡힘('추정' 이라 적었으나 확인 안 함) · 의심한 이유: 바꾸기 전에 쓸모 있던 막힘의 수를 세다가 · 본 것: 상자 막힘도 전부 99 · 결론: 100 은 상자 재계획까지 끔 → 기각, 기준은 '계획 뒤 새로 생겼나' · 다음에 알아보는 법: 판정 문턱을 바꾸기 전에 그 판정이 **쓸모 있게 걸린 사례들의 실제 값**을 먼저 센다. '추정' 전제 위에 대책 순위를 매기지 않는다 · 데이터: [`anal_pba_timing.txt`](../debug_log/2026-10-23/outputs/anal_pba_timing.txt).
2. **'목표 5 52 s 를 only_new 가 줄인다'**(§20.1 · §20.2 · §20.4 판정 ⑤ 의 기대) → §20.7 정정: 서쪽 통로 막힘 4 번(14:47:15~28)은 **목표 4(남서행, 34.6 s)** 구간이었고, 목표 5 의 막힘은 14:48:15 1 번(주행 중 새로 99 — only_new 로도 남음) + 14:47:52 최적화 실패. f2rp4 의 목표 5 32.6 s 는 only_new 와 무관(알림 0 줄).
3. **재생 도구 첫 판 실수 2 개**(§20.7) — 0.1 s 간격 + `≥ 2.0` 부동소수 비교로 f2rp4 상자 막힘을 재현 못 함(시작을 0.1 s 늦게 봄 · 1.9999 < 2.0) → 0.02 s · 1e-6 여유([`anal_pba_replay.py`](../debug_log/2026-10-23/jobs/anal_pba_replay.py) 22~23 행 주석). 다음에 알아보는 법: 재현 시험이 실제 사건 하나라도 놓치면 결론 전에 그 사건의 시간열을 찍어 본다.
4. **기록 어긋남**:
   1. **지금 코드 주석이 §20.7 정정을 반영하지 않음** — [`path_blocked_ahead_condition.cpp`](../../ros2_ws/src/rover_navigation/src/path_blocked_ahead_condition.cpp) 21 행 '막힘 5 회 · 탈출 · 대기 2 회, **목표 5 에 52 s**(f2v2 31.6 s)'. §20.7 이 'cpp 주석의 그 문구도 틀림 — 다음 코드 수정 때 고침' 이라 적었으나 11-03 현재 그대로. 같은 주석 22 행 '상자 막힘 … 경로를 받고 59 s 뒤' 는 58.4~59.8 s 범위라 대략 맞음.
   2. **배포 해시 · 작동 확인**: f2rp4 · f2rp5 에서 새 .so 가 적재됐다는 직접 증거(알림 줄)는 없음 — §20.5 가 '미확인으로 둠'. 간접 근거(옛 판이면 선언 안 된 포트로 BT 적재 실패)만.
   3. '막힘 중단 6 번' 은 nav2 로그에서 **한 번에 두 줄씩**(0.05~0.10 s 차) 찍힌다([`pathblocked_f2rp3.txt`](../debug_log/2026-10-23/outputs/pathblocked_f2rp3.txt) 11 줄 = 사건 6, 14:48:15 만 한 줄). 줄 수로 세면 틀림 — SUMMARY 는 '한 번에 두 줄씩 찍힘' 이라 적어 둠. 두 줄이 되는 이유는 기록 없음(ReactiveSequence 가 같은 틱에 두 번 부르는 것으로 추정).

## 6. 남은 것 (10-23 시점)
- 실주행에서 only_new 알림이 찍히는 경우 1 회 — '빠지는 쪽' 작동 확인(§20.7 결론의 남은 확인).
- 14:48:15 (−1.64, −4.47) '주행 중 84 → 99' 의 원인 — 카메라 칸 갱신 · 로버 접근으로 칸이 커진 것으로 보이나 미확인.
- 0.5 Hz 재계획 + only_new 조합(표준 prep)의 동작 — 시험 없음.
- 같은 코스 · 같은 구성에서 서쪽 통로 경로가 99 칸을 지나느냐가 주행마다 다름(f2rp3 매번 · f2rp4 0) — 기억된 상자 칸 위치 · 진입 자세 차이 추정(미확인).
- skip_near 0.30 m 사각에 들어가 풀리는 '우연한 통과'(§20.3)는 only_new 와 별개로 남는 성질.

## 7. 이후 (10-26 ~) — 포인터
- **10-26 §14 · §15 f2sa3**(no5, Smac → NavFn 대체 · MPPI 28/5 · 재계획 0.01 + only_new): 실주행 **첫 only_new 알림 2 줄**(16:12:15.59 · 22.07, 서쪽 통로 목표 4 — `새 경로 점 1 개가 받을 때 이미 비용 ≥ 99`). 그 주행의 막힘 중단은 서쪽 통로 16:13:08.54 (−1.63, −4.60) 1 회 · 상자 16:16:36.52 (1.25, 0.14) 1 회(각 두 줄) — [`nav_events_ms_f2sa3.txt`](../debug_log/2026-10-26/outputs/drives/f2sa3/nav_events_ms_f2sa3.txt) 142 · 166 · 224 · 287 행. 그 주행 판정은 Smac 시기 카드에서 채움.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2rp3(no5) | only_new 전 — 서쪽 통로 오판 5 · Wait 2 | `2026-10-23/outputs/run_f2rp3.txt` · `nav2_f2rp3.log` · `pathblocked_f2rp3.txt` · bag `bags/bag_f2rp3.tgz` · 영상 `videos/f2rp3_west_corridor.mp4` |
| f2rp4(no5) | only_new 첫 주행 — 알림 0 | `outputs/run_f2rp4.txt` · `nav2_f2rp4.log` · `anal_pba_timing_f2rp4.txt` · `f0_f2rp4/` · 영상 `videos/f2rp4_west_corridor.mp4` |
| f2rp5(b910) | only_new + 상자 막힘 재계획 | `outputs/run_f2rp5.txt` · `anal_pba_timing_f2rp5.txt` |
| f2rp1 · f2rp2 · f2von2 | 상자 막힘 시각 비교(only_new 전) | `outputs/nav2_f2rp1.log` · `nav2_f2rp2.log` · `nav2_f2von2.log` |
| `anal_pba_timing.sh` | 경로 받은 뒤 첫 막힘까지 | `2026-10-23/jobs/` → `outputs/anal_pba_timing*.txt` |
| `anal_pose_at.py` | 지정 시각 로버 지도 자세 | `jobs/` → `outputs/anal_pose_at_f2rp3.txt` |
| `anal_pba_replay.py` · `anal_pba_replay_extend.py` | 판정 재생 · 반사실 보강 | `jobs/` → `outputs/anal_pba_replay_f2rp1~4.txt` · `anal_pba_replay_extend_f2rp3.txt` |
| `up_pba_onlynew_1023.sh` | cpp · xml 배포 + 빌드 | `jobs/` → `outputs/up_pba_onlynew_1023.txt` |
| `fig_replan_video.py` | 막힘 검사 구간 영상 | `jobs/` — 해설은 [B0 카드 §9](path-tracking-replan-b0.md) |
| `anal_band_run.py`(10-15) | 차체 ↔ 치명 칸 정확 여유 · 띠 | `2026-10-15/jobs/` → `outputs/anal_band_run_f2rp3~5.txt` — 해설은 [상자 옆 정지 대책](box-side-stall-remedies.md) |

## 9. 도구 해설
### anal_pba_timing.sh — 경로 받은 뒤 첫 막힘까지 (PC, bash/awk, 10-23 §20.2)
- 부른 형태: `bash anal_pba_timing.sh outputs/nav2_f2rp1.log …`(nav2 로그 PC 사본들).
- 왜: 같은 99 인 서쪽 통로 오판과 상자 막힘을 가르는 양을 찾으려고.
- 하는 일: 각 줄의 `[17927…초]` 를 `t` 로, `Received a path to smooth`(BT 가 새 경로를 만들 때마다 smoother 가 한 번) 시각을 `p` 로 기억, `PathBlockedAhead: 앞 경로` 와 `지속되면 재계획` 이 있는 줄(처음 막힘)에서 좌표 · 비용 · `t − p` 출력.
- 출력: `outputs/anal_pba_timing.txt` · `_f2rp4.txt` · `_f2rp5.txt`(위 §4 발췌). 결함: 스무딩을 거치지 않는 경로(Smac 판 10-26 의 PlanSmac 분기)는 'Received a path to smooth' 가 안 찍혀 시각 기준이 없다(10-23 엔 해당 없음). 지금 다시 쓸 수 있음(NavFn 판).

### anal_pose_at.py — 지정 시각 로버 자세 (PC, rosbags, 10-23 §20.3)
- 부른 형태: `anal_pose_at.py bag 14:47:09.0 14:47:13.5 …`(현지 시각). bag 시작을 `time.localtime` 로 맞춰 map→odom ∘ odom→base_link.
- 출력: `outputs/anal_pose_at_f2rp3.txt`(예 `14:47:30.0  (-1.66, -4.46)  yaw -69°` — 원문은 도 기호가 깨져 저장됨). 쓰인 곳: '사각에 들어가 풀림' 의 거리 계산.

### anal_pba_replay.py · anal_pba_replay_extend.py — 판정 재생 (PC, rosbags, 10-23 §20.7)
- 부른 형태: `anal_pba_replay.py bag nav2.log` · `anal_pba_replay_extend.py bag nav2.log`.
- 왜: f2rp4 에선 only_new 가 쓰일 기회가 없었음 — f2rp3 기록으로 노드 판정만 시험.
- 하는 일: ① 경로 = BT 가 컨트롤러에 준 `{path}` — nav2 로그 'Received a path to smooth' 마다 스무딩 성공이면 그 뒤 `/plan_smoothed`, 'Smoothed path leads to a collision' 이면 직전 `/plan`(CopyPath 원경로, 러너 조회기 경로가 섞이므로 BT 계획 시각에 가장 가까운 것) ② 지도 = bag `/global_costmap/costmap`(≈ 1.5 s 간격) ③ 로버 = `/tf` ④ 인자 = BT xml 값(1.5 · 0.30 · 2.0 · 99) ⑤ 0.02 s 마다 C++ 와 같은 판정, only_new 면 `hit &= c > init[idx]`(75 행), 지속 `≥ HOLD − 1e-6` 이면 중단(78 행) — false 로 실제 중단 재현을 먼저 보고 true 를 돌림. extend 판은 경로 #3 을 다음 경로가 아니라 목표 도착(14:47:43.57)까지 이어 판정.
- 출력: 위 §4 발췌 · `anal_pba_replay_extend_f2rp3.txt`(`가장 긴 연속 막힘 0.00 s → 막힘 중단 없음`).
- 결함: 기록은 옛 동작의 결과 — 반사실 길은 근사. 지도 간격 1.5 s(실제 노드는 전역 코스트맵 발행마다). C++ .so 자체는 시험 안 함. 계보: 이 시험 뒤 영상 도구도 같은 'BT 경로 분기' 를 쓰게 고침(10-23 §20.7).

### up_pba_onlynew_1023.sh — 배포 · 빌드 (Jetson, bash, 로버 안 움직임)
- 실행 형태: 스크래치패드 묶음이 `/tmp/up_pba.cpp` · `/tmp/up_bt.xml` 을 base64 로 풀어 둔 뒤 이 본문 실행(`set -e`). 이전 · 새 sha256 앞 12 자 → 복사 → `grep -c 'only_new="true"'` → `colcon build --symlink-install --packages-select rover_navigation` → 설치본 xml 링크 · .so 링크 확인 · `strings .so | grep -c only_new`.
- 출력 [`up_pba_onlynew_1023.txt`](../debug_log/2026-10-23/outputs/up_pba_onlynew_1023.txt): `이전 … 78710d858c05` → `새 … d8e03afcc44b`, xml `62d8fd06bee1` → `b448fcc23ff1`, 빌드 28.2 s, `strings` 1. 실행 중 스택은 다음 prep 부터.
- 한계: 이전 해시가 저장소 HEAD 와 같은지(덮어쓰기 안전)는 SUMMARY 가 따로 확인했다고 적음(78710d858c05 · 62d8fd06bee1 = HEAD).

## 10. 용어
- **PathBlockedAhead**: 우리 BT 조건 노드(10-01). 로버에서 가장 가까운 경로점부터 앞 0.30(skip_near)~1.5 m(lookahead) 경로점의 전역 코스트맵 값이 `min_cost`(99) 이상인 상태가 2 s(hold_time) 이어지면 SUCCESS → Inverter 로 FollowPath 중단 → 복구 → 로버 자리에서 재계획.
- **내접(99) · 치명(100)**: OccupancyGrid 로 낸 코스트맵 값. 99 = costmap 253 = 로버 중심이 그 칸에 가면 원형 내접 반경상 차체가 닿는 칸(지날 수는 있으나 빠듯함), 100 = 254 = 장애물 칸 자체.
- **only_new**: 경로를 받은 순간 이미 `min_cost` 이상이던 점은 값이 그보다 커질 때만 막힘으로 세는 옵션 — '같은 지도로 다시 계획해도 같은 답이면 재계획은 소용없다' 는 논리(노드 주석 19~24 행).
- **skip_near 사각**: 로버 0.30 m 안 경로점은 안 봄(벽 옆 출발점 비용 오판 방지). 막힘 점이 이 안으로 들어오면 타이머가 풀린다(§20.3).
