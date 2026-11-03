# BT 끝 방향 0° 결함 — TruncatePath → CopyPath (7 기: 10-14 §13 · §13.1~§13.5 · §14 · §15 · §15.1 · §16 · §17)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **해결**(원인 측정 + 조치 + 재발 0). 10-14 f2t1 에서 스무딩이 실패하는 동안에도 목표 1 m 안 컨트롤러 끝 방향 = 계획기 끝 방향(차 0.0°), 서쪽 통로 '방향까지(p)' 목표 2/2 성공(§17). 이후 10-15 f2v1 · f2v2 · f2v3 · f2w2 의 서쪽 통로 p 목표 6 번도 모두 SUCCEEDED(러너 출력). ⚠ 고친 뒤 '맞는 방향' 자체가 상자 쪽일 때 생긴 정지(f2v3)는 다른 문제 — [F2 기준선 no5](f2-baseline-no5.md) | 10-14(결함 자체는 09-17 mp6 부터 BT 에 있었음 — 그때 `TODO(improve)` 로 적어 둠) | [10-14 §13.1](../debug_log/2026-10-14/SUMMARY.md) f2s1 목표 3(서쪽 통로) 위치 2.9 cm 인데 nav_guard 취소 | 새 [`copy_path_action.cpp`](../../ros2_ws/src/rover_navigation/src/copy_path_action.cpp)(커밋 `dc155dcb`) · [`nav_to_pose_no_spin.xml`](../../ros2_ws/src/rover_navigation/config/nav_to_pose_no_spin.xml) 85 행 `TruncatePath` → `CopyPath` · [`CMakeLists.txt`](../../ros2_ws/src/rover_navigation/CMakeLists.txt) 19~22 · 39 행 · [`nav2_params.yaml`](../../ros2_ws/src/rover_navigation/config/nav2_params.yaml) 76 행 `rover_copy_path_bt_node` | [남서 구석 방향 맞춤 정체](southwest-orient-stall.md)(같은 결함의 앞 사례 — 10-14 §16 재확인) · [MPPI 상자 옆 통로 튜닝](mppi-passage-tuning.md)(09-17 mp6 — TruncatePath 를 넣은 곳) · [코스트맵이 상자를 지움](costmap-clear-recovery.md)(같은 BT) · [온보드 정지 수단 · nav_guard](onboard-stop-nav-guard.md)(취소 주체) · [pad_relief · 실행 중 패딩](pad-relief-runtime-padding.md)(§15.1 '이걸로 pad_relief 가 필요 없나') · [상자 옆 정지 원인](box-side-stall-cause.md)(가는 길 중간 정지 — 이 결함과 무관) · [낮은 상자 기억 · 전역 nvblox](low-box-global-memory.md)(§13.5 시야 밖 감쇠) · [F2 기준선 no5](f2-baseline-no5.md)(검증 주행 f2t1 이 기준선 코스 그림의 원본) · [전역 계획기 NavFn vs Smac](global-planner-choice.md)(10-26 Smac 경로도 CopyPath 로 넘김) · [상자 옆 정지 대책](box-side-stall-remedies.md) (7 기) · [경로 추종 · B0](path-tracking-replan-b0.md) (8 기) |

**한 줄**: 8 목표 순회 f2s1 에서 로버가 서쪽 통로 목표 (−1.65, −3.70) 에 **위치 2.9 cm · 방향 −7.6°**(러너 기준)로 와 있는데도 45 s 를 서 있다가 nav_guard 에 취소됐다. 원인은 BT 였다 — 목표 자세가 좁은 곳이라 경로 다듬기(SmoothPath)가 매번 '충돌'로 실패했고, 실패 때 원경로를 넘기던 `TruncatePath(distance 0)` 가 **마지막 점 방향을 0° 로 덮어써** 컨트롤러는 −56° 가 아니라 0°(odom 으로 +4.5~+5.2°)를 목표 방향으로 받았다. 로버는 −64° 에서 왼쪽으로 64° 를 돌아야 했고, 앞 왼쪽 2.1 cm 에 라이다 아래 실제 물체(밑동)가 있어 돌 수 없었다. 09-17 에 `TODO(improve)` 로 적어 둔 결함이 27 일 동안 남아 있던 것. 점 위치 · 방향을 그대로 복사하는 BT 노드 `CopyPath` 로 바꾸고 f2t1 로 검증(8/8). 10-07 남서 구석 정체도 같은 결함이었을 가능성이 높아졌다(§16 — [남서 카드](southwest-orient-stall.md) §7).

## 1. 증상
- f2s1(10-14 13:45:22 출발, 8 목표 `no5`, pad_relief on) — [`run_f2s1.txt`](../debug_log/2026-10-14/outputs/run_f2s1.txt):
  ```
    경로 자동 yaw: 경로 75 점, 끝 0.305 m 구간 방향 -56.2° (직선 방향 -91.7°, 차 35.5°)
  목표 3 출발: map (-1.65, -3.70, -56°), 거리 1.70 m, 한도 79 s
    목표 3 CANCELED 70.6 s | 도착 map (-1.669, -3.678, -63.8°) 목표 대비 0.029 m, -7.6°
  ```
  사용자: "현재 멈췄다. 확인해라." 러너가 보기엔 위치 · 방향 모두 허용(0.15 m · 20°) 안이다.
- Nav2 로그 — [`navlog_f2s1.txt`](../debug_log/2026-10-14/outputs/navlog_f2s1.txt)(도구 [`chk_navlog_f2s1.sh`](../debug_log/2026-10-14/jobs/chk_navlog_f2s1.sh)):
  ```
  13:47:25.6 [ERROR] [smoother_server]: Smoothed path leads to a collision at x: -1.650000, y: -3.700000, theta: -0.981032
  ...(2 s 마다, 처음 5 번은 충돌 지점 = 목표 자세 그 자체 −0.981 rad = −56°)
  13:48:10.6 [ERROR] [controller_server]: Failed to make progress
  [nav_guard] nav_guard 개입 — 무진행: 45 s 동안 최대 0.24 m 이동 < 0.25 m → 모든 목표 취소·정지   (epoch 1791953307.9 = 13:48:27.9)
  ```
- 장면 그림 [`2026-10-14_f2s1_westpass_yaw0.png`](../04_navigation/figures/2026-10-14_f2s1_westpass_yaw0.png)(13:48:00): 보라 화살표(계획기 `/plan` 끝) −56° · 주황(컨트롤러가 받은 `/transformed_global_plan` 끝) **+0°** · 로버 −64°, 명령 0.001 m/s, 경로 길이 0.06 m.

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-17 mp6(앞 이력) | 스무딩 실패 때 `{path}` 가 3 s 묵은 경로로 남는 문제 → `Fallback(SmoothPath, TruncatePath raw→path distance 0)` | 상자 뒤 모서리 'Smoothed path leads to a collision' 3 연속 | 해결. 단 `TODO(improve): TruncatePath 는 마지막 점 방향을 atan2(0,0)=0 으로 덮어쓴다 — 전용 복사 노드로 교체할 것` | [09-17 SUMMARY](../debug_log/2026-09-17/SUMMARY.md) 44 행 · BT 커밋 `64aa041` 80~85 행 |
| 10-14 §12 | 10 목표 순회 코스 그림(사용자가 뺄 곳 고름) | 2 · 8 은 0.1 m 차이라 한 원 | 사용자 "5 번 빼고" | [`2026-10-14_patrol_goals.png`](../04_navigation/figures/2026-10-14_patrol_goals.png) · [`fig_patrol_goals.py`](../tools/fig_patrol_goals.py) → [F2 기준선](f2-baseline-no5.md) |
| 10-14 §13 선언 | f2s1 = `no5` 8 목표(5 와 함께 6 도 뺌 — 같은 자리 연속 목표가 되므로, 내 판단 · 사용자에게 알림), 구성 f2r1 · f2r2 + pad_relief on | 판정: 8 목표 성공 · 접촉 0 · nav_guard 취소 0 | — | [`run_f2c.sh`](../debug_log/2026-10-14/jobs/run_f2c.sh) 8 행 `NO5` |
| 10-14 §13.1 | f2s1 주행 | 1 B 51.4 · 2 C 54.0 s 성공, **3 서쪽 통로 CANCELED 70.6 s**(§1). 컨트롤러 경로 끝 방향 odom **+4.5~+5.2°**, 계획기 −56.2°, map↔odom 각 차 4° 안. 'Optimizer fail' 1 회 → pad_relief 안 켜짐(정상) | 원인 = BT `TruncatePath` 가 끝 방향을 0 으로 덮음(측정 + BT 코드). '목표 판정이 컨트롤러 경로 끝 자세를 쓴다' 는 Humble 동작에 대한 이해로 **소스 대조 없음**(SUMMARY 가 밝힘). 영향 범위: 스무딩이 실패하는 좁은 곳 목표(서쪽 통로 · 남서 구석) | [`run_f2s1.txt`](../debug_log/2026-10-14/outputs/run_f2s1.txt) · [`navlog_f2s1.txt`](../debug_log/2026-10-14/outputs/navlog_f2s1.txt) · bag `2026-10-14/bags/bag_f2s1.tgz`(`/transformed_global_plan` 있음). 끝 방향 계산 출력은 그날 **원천 소실** → 11-03 재실행(§3) |
| 10-14 §13.2 · §13.3 | f2s2 = 남은 5 목표 이어 가기, 서쪽 통로를 **위치만(f)** 으로(결함 우회). 로버 · 스택 그대로, G2 생략 | 5/5 성공 315.0 s, 상자 구역 최소 여유 5.8 cm, 접촉 없음(사용자). 남서(f) 는 Nav2 가 SUCCEEDED 36.7 s · 도착 **−1.6°**(목표 대비 99.8°) | 통과. f2s1 + f2s2 = 8 중 7 목표, 목표 3 은 결함으로 취소. bag 을 주행 끝나기 전에 풀어 손상 오류(내 실수 4) | [`run_f2s2.txt`](../debug_log/2026-10-14/outputs/run_f2s2.txt) · [`anal_box_pass.py`](../tools/anal_box_pass.py) |
| 10-14 §13.4 | 영상에 목표 방향 두 화살표 추가(사용자 요청) | f2s2 가 같은 통로에 다시 들어갈 때(13:55:07)도 보라 +66° · 주황 **+0°** — 결함 그대로. 위치만 목표라 러너가 0.15 m 안에서 끝내 회전 단계까지 안 감 | 고친 것은 결함이 아니라 **성공 조건**. 정지 조건 = ① 스무딩이 실패할 만큼 좁은 목표 ② 방향까지 맞춰야 하는 목표 — ② 를 없앤 우회 | [`fig_run_video.py`](../tools/fig_run_video.py)(커밋 `f478572b`) · 그림 [`…_f2s2_westpass_xyonly.png`](../04_navigation/figures/2026-10-14_f2s2_westpass_xyonly.png) · 영상 `videos/f2s1_westpass_stop.mp4` · `f2s2_resume_return.mp4`(git 제외) |
| 10-14 §13.5 | 사용자 관찰 "같은 자리인데 멈춤 영상엔 모서리 옆 빨간 칸, 두 번째엔 없다" | 같은 자세 (−1.67, −3.67, −64°) 에서 최근접 치명 칸 **2.1 → 13.9 cm**, 카메라 칸 96 → 18, 라이다 점 869 → 849. 멈춤 때 8 cm 안 4 칸 전부 앞 왼쪽 · 카메라 칸 · 라이다 점 0. 사용자 실물 확인: **라이다 아래로 넓게 퍼진 밑동**(유령 아님) | 코스트맵은 맞았고 회전 거부도 옳았다 — 틀린 것은 **필요 없는 회전을 요구한 BT**. 6 분 뒤 칸이 사라진 것은 시야(±43°) 밖 감쇠(약 80 s)로 실물을 잊은 것 → [낮은 상자 기억](low-box-global-memory.md) | [`westpass_cells.txt`](../debug_log/2026-10-14/outputs/westpass_cells.txt) · [`anal_westpass_cells.py`](../debug_log/2026-10-14/jobs/anal_westpass_cells.py) |
| 10-14 §14 | `CopyPath` BT 노드 작성 · 배포 | Jetson 소스 3 파일은 저장소와 **주석 7 줄만** 다름 → 저장소 판으로 덮고 빌드 7.1 s, `.so` 에 등록 함수 1. 재기동(prep 59 s) 뒤 bt_navigator Configuring → Activating, 오류 없음, 설치 BT `<CopyPath` 1 | 배포 · 적재 확인. 미확인: 포트 형(첫 목표에서 해석 — 틀리면 움직이지 않고 실패), 실제 끝 방향 | [`up_bt_copypath.txt`](../debug_log/2026-10-14/outputs/up_bt_copypath.txt) · [`chk_bt_load.txt`](../debug_log/2026-10-14/outputs/chk_bt_load.txt) · 커밋 `dc155dcb` |
| 10-14 §14 선언 | 검증 주행: 서쪽 통로를 다시 p 로 한 `no5` | 판정 ① 첫 목표 정상 출발 ② 스무딩 실패 목표에서 `/transformed_global_plan` 끝 = `/plan` 끝 ± 5° ③ 서쪽 통로 취소 0 (스무딩 실패가 없으면 ② 판정 불가) | — | SUMMARY §14 |
| 10-14 §15 · §15.1 | 전체 구성 재검토(층별 표) · 'CopyPath 가 pad_relief 를 필요 없게 하나' | 되풀이 실패 3 모양: ① 좁은 곳 칸 하나 차이 갇힘 ② **필요 없는 동작 요구**(이 결함) ③ 멈춘 동안 기억 잃음. pad_relief 가 겨누는 상자 옆 정지 3 번은 목표에서 1.37~1.59 m — GoalAngleCritic(0.4 m)·목표 판정(도착 때)은 그 거리에서 안 쓰임 | **부분적으로만** — CopyPath 는 '도착 뒤 방향 맞추기' 정지, pad_relief 는 '가는 길 중간' 정지. 권고 순 1 = CopyPath 검증, 2 = 10-02 · 10-07 남서 재확인 | SUMMARY §15 표 · §15.1 · `nav2_params.yaml` GoalAngleCritic → [pad_relief](pad-relief-runtime-padding.md) |
| 10-14 §16 | 10-07 f2c1 남서 정체 재확인(주행 없음) | 그 bag 엔 `/transformed_global_plan` 이 없어 `anal_path_endyaw.py` 실패. 10-07 Nav2 로그: 목표 시작 직후 스무딩 실패 1 회(재계획 목표당 1 회 시절) → 그 경로가 목표 내내 쓰임. 멈춘 방향 **−0.3°** · 위치 0.165 m · 목표 −109° | **같은 결함일 가능성 높음(추정, 측정과 맞음)** — 0° 에 이미 맞춰 놓고 마지막 1.5 cm 를 못 들어간 모양. 10-07 '−109° 로 못 돎' 해석은 재검토 대상. 10-02 f2b3 은 bag 이 PC 에 없어 미확인 | [`2026-10-07/outputs/j908_g4log.txt`](../debug_log/2026-10-07/outputs/j908_g4log.txt) · [`f0_f2c1_runner.log`](../debug_log/2026-10-07/outputs/f0_f2c1_runner.log) → [남서 카드 §7](southwest-orient-stall.md) |
| 10-14 §17 | f2t1 검증 주행(15:20:56) | **8/8**(남서 위치만) 605.5 s, 접촉 없음(사용자). 목표 3 SUCCEEDED 27.9 s(−20.1°, 허용 경계) · 목표 5 SUCCEEDED 41.2 s. 스무딩 실패 중 끝 방향: 목표 3 −45.0 = −45.0°, 목표 5 +68.6 = +68.6°. 멀 때 0° 구간은 잘린 경로의 **중간 점**(결함 아님, 해석 정정) | **CopyPath 검증 통과(1 회)** — ① ✔ ② ✔ ③ ✔. 서쪽 통로를 위치만으로 우회할 필요 없어짐. 같은 주행에서 pad_relief 첫 작동(목표 4) — 이후 멈칫의 원인(→ [pad_relief](pad-relief-runtime-padding.md)) | [`run_f2t1.txt`](../debug_log/2026-10-14/outputs/run_f2t1.txt) · [`navlog_f2t1.txt`](../debug_log/2026-10-14/outputs/navlog_f2t1.txt) · [`anal_path_endyaw.py`](../debug_log/2026-10-14/jobs/anal_path_endyaw.py)(출력 그날 **원천 소실** → 11-03 재실행 §3) · bag `bag_f2t1.tgz` |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 목표 근처 물리 갇힘(회전할 공간이 없음) 만의 문제 | 컨트롤러가 받은 목표 방향이 보낸 방향과 같은가 | 다름(아래) — 보낸 방향(−56°)이면 로버는 −64° 라 허용 20° 안이었다(러너 오차 −7.6°) | **기각(단독 원인으로는)**. 회전 공간이 없었던 것은 사실(§13.5) — 요구가 틀려서 그 사실이 문제가 됨 |
| 컨트롤러가 받은 끝 방향 ≈ 0° | bag `/transformed_global_plan` 마지막 점 방향 vs `/plan` | f2s1 13:47:28~13:48:28 odom **+4.5~+5.2°**(589 메시지, 점 수 1~41), 지도로 옮기면 **+0.0°**, 계획기 −56.2° | **지지(측정)** |
| 그 0° 는 스무딩 실패 → `TruncatePath` 가 만든 것 | ① 스무딩 실패가 목표 내내 이어졌나 ② 실패 없는 목표 · CopyPath 뒤에도 0° 인가 | ① 13:47:25.6 부터 2 s 마다 끝까지(처음 5 번은 목표 자세 자체가 충돌) ② f2t1(CopyPath): 목표 3 도 15:22:55~15:23:20 내내 스무딩 실패였는데 0.83 m 안부터 −45.0 = −45.0° | **지지(측정 + BT 코드 + 09-17 TODO)**. TruncatePath 소스 자체를 읽은 기록은 없음 — 09-17 TODO 와 측정이 일치 |
| 멀 때 컨트롤러 끝 0° 도 결함 | f2t1 목표 3 · 5 의 먼 구간 | 0° 는 목표가 컨트롤러 창(prune 약 1 m) 밖일 때 — 그때 끝 = NavFn 원경로 **중간 점**(방향 0°). 창 안에 목표가 들어오면 끝 = 목표 자세 | **기각**(§17 정정). f2s1 의 증거는 목표 0.03~0.07 m 앞(경로 1~2 점)에서도 0° 라 그대로 유효 |
| CopyPath 가 pad_relief 를 대신한다 | 정지 자리와 목표 거리 · 크리틱 적용 거리 | 상자 옆 정지 3 번은 목표에서 1.37~1.59 m. GoalAngleCritic 은 0.4 m 안 | **기각(부분만)** — §15.1 |
| 10-07 남서 정체도 같은 결함 | 그날 로그 · 멈춘 방향 | 스무딩 실패 1 회(목표 시작 직후) · 멈춘 방향 −0.3° | **지지(정황)** — 10-07 당일의 직접 증거(`/transformed_global_plan`) 없음. 같은 남서 목표의 **직접 측정 1 건**(11-03 재실행): TruncatePath 시절 f2s2 남서에서 목표 0.26 m 앞까지 컨트롤러 끝 0.0°(계획기 −101.3°), CopyPath 뒤 f2t1 은 −107.8 = −107.8° — [남서 카드 §7.1](southwest-orient-stall.md) |

- 11-03 재실행(카드 작성 중, 위 표의 수치 확인용): 그날 대화에만 있던 `anal_path_endyaw.py` 출력을 같은 스크립트 · 같은 bag(`2026-10-14/bags/`)으로 다시 냄. 결과 원문은 파일로 남기지 않음 — **발췌가 전부**.
  ```python
  # jobs/anal_path_endyaw.py — 4 s 마다 /plan 끝 방향 vs /transformed_global_plan 끝 방향(odom → map 으로 map→odom yaw 를 더함)
  cyaw = q[3] + m[3]; ryaw = o[3] + m[3]
  print('%s   %+6.1f°  %+6.1f°  %+6.1f°  %+6.1f°  %.2f m' % (..., math.degrees(p[3]), math.degrees(cyaw), math.degrees(wrap(cyaw - p[3])), math.degrees(ryaw), math.hypot(...)))
  ```
  ```
  f2s1 목표 3 (계획기 · 컨트롤러(지도로) · 차이 · 로버 · 로버→목표)
  13:47:26    -56.2°   -0.0°   +56.2°   -100.9°   1.39 m
  13:47:46    -56.2°   +0.4°   +56.6°    -70.7°   0.07 m
  13:48:26    -56.2°   +0.0°   +56.2°    -63.3°   0.03 m
  f2t1 목표 3
  15:23:06    -45.0°   +0.0°   +45.0°   -103.8°   1.06 m     ← 목표가 창 밖: 끝 = 중간 점
  15:23:10    -45.0°  -45.0°    +0.0°    -94.8°   0.83 m
  15:23:18    -45.0°  -45.0°    +0.0°    -76.3°   0.22 m
  f2t1 목표 5
  15:24:51    +68.6°   -0.0°   -68.6°   +108.8°   0.89 m
  15:24:55    +68.6°  +68.6°    +0.0°   +110.1°   0.81 m
  15:25:07    +68.6°  +68.6°    +0.0°    +73.4°   0.19 m
  ```
  SUMMARY §17 의 경계 거리(목표 3 '0.68 m 안부터', 목표 5 '0.86 m 안부터')는 4 s 표본 격자와 창 시작 시각에 따라 달라진다 — 위 표본으론 0.83 · 0.81 m. 판정(차 0.0°)은 같음.

## 4. 조치와 효과
- **`CopyPath`**(10-14 §14, 커밋 `dc155dcb`) — [`copy_path_action.cpp`](../../ros2_ws/src/rover_navigation/src/copy_path_action.cpp) 45~50 · 76~77 행(10-14 판은 step 없는 복사만, 10-26 에 step 재표본 추가):
  ```cpp
  BT::NodeStatus tick() override {
    nav_msgs::msg::Path p;
    if (!getInput("input_path", p) || p.poses.empty()) return BT::NodeStatus::FAILURE;
    ...
    setOutput("output_path", p);   // 점의 위치 · 방향을 바꾸지 않음
    return BT::NodeStatus::SUCCESS; }
  ```
  BT 는 `<Fallback name="SmoothOrRaw"> <SmoothPath unsmoothed_path="{raw_path}" smoothed_path="{path}" …/> <CopyPath input_path="{raw_path}" output_path="{path}"/> </Fallback>`(지금 84~85 행). 기각한 대안(코드 주석 17~20 행): BT.CPP `SetBlackboard`(v3 값 포트가 문자열이라 경로를 못 옮김) · 계획기가 `{path}` 에 바로 쓰고 스무더가 덮기(09-16 mp4 한 틱 두 번 갱신 → 'Aborting handle' 매초).
- 효과(측정): f2t1 에서 스무딩 실패 중 끝 방향 차 0.0°(§3 재실행), 서쪽 통로 p 목표 2/2 성공 — f2s1 은 같은 목표에서 70.6 s 취소. 이후(같은 BT) 10-15 서쪽 통로 p 목표 성공: f2v1 목표 3 · f2v2 목표 3 · 5 · f2v3 목표 3 · f2w2 목표 3 · 5(각 run 출력) — 같은 모양의 '위치는 맞는데 서 있다가 취소' 는 0.
- 한계: ① CopyPath 는 **보낸 방향을 정직하게 전달**할 뿐 — 러너 · place_server 의 `p` 방향(경로 끝 0.3 m 방향)이 주행마다 −45~−56° 로 바뀌고, −45° 는 상자 쪽이라 f2v3 에선 그 방향으로 서다가 다음 목표에서 막혔다([F2 기준선](f2-baseline-no5.md) §2 · [상자 옆 정지 원인](box-side-stall-cause.md)). ② 목표 판정이 컨트롤러 경로 끝 자세를 쓴다는 것은 소스 대조 없이 측정과 맞는 이해. ③ 남서 목표는 여전히 `f`(위치만) — p 재시험 없음([남서 카드 §7](southwest-orient-stall.md)).
- **지금 코드 확인(11-03)**:
  - BT [`nav_to_pose_no_spin.xml`](../../ros2_ws/src/rover_navigation/config/nav_to_pose_no_spin.xml) 82 행 `ComputePathToPose … planner_id="GridBased"` · 84 행 `SmoothPath` · **85 행 `<CopyPath input_path="{raw_path}" output_path="{path}"/>`** · 80~81 행 옛 TODO 원문(해소 표시) · 108 행 `PathBlockedAhead … min_cost="99" only_new="true"`(10-23 추가) · 60 행 `NavigateRecovery` 6 회 · 126~127 행 복구 `BackUp … server_name="monotone_escape"`(10-15 §26) · `Wait 5`. ⚠ 74 행 주석 '실패 시 ForceSuccess 로 원 경로를 그대로 쓴다'(09-16)는 지금 구조(Fallback + CopyPath)와 맞지 않는 옛 설명.
  - 노드 [`copy_path_action.cpp`](../../ros2_ws/src/rover_navigation/src/copy_path_action.cpp) 36~43 행 포트(`input_path` · `output_path` · `step` 기본 0) · 84~87 행 `BT_REGISTER_NODES` → `"CopyPath"`. [`CMakeLists.txt`](../../ros2_ws/src/rover_navigation/CMakeLists.txt) 19~22 행 `rover_copy_path_bt_node` · 39 행 install. [`nav2_params.yaml`](../../ros2_ws/src/rover_navigation/config/nav2_params.yaml) 75~76 행 `plugin_lib_names`(`rover_path_blocked_ahead_bt_node` 다음). 23 행 BT 경로 = 설치본 절대 경로.
  - [`navigation.launch.py`](../../ros2_ws/src/rover_navigation/launch/navigation.launch.py) 116~125 행: `planner:=smac` 이면 `PlanSmacOrNavFn` 블록을 끼워 Smac 경로를 `<CopyPath … step="0.03"/>` 로 넘김(스무더 안 거침), NavFn 블록(위 85 행)은 대체 경로로 남음 → 사본 `/tmp/nav_to_pose_active.xml`. launch 기본 `planner` = `navfn`(203 행), smac 은 prep `NAV_ADD`([`prep_patrol.sh`](../tools/prep_patrol.sh) 16 행).
  - goal checker: `nav2_params.yaml` 102 행 `stateful: True` · 108 행 `xy_goal_tolerance: 0.15` · 115 행 `yaw_goal_tolerance: 0.35` — 10-14 과 같음.

## 5. 내 실수 · 기록 어긋남
1. **알려진 결함을 27 일 묵힘** — 하려 한 것: 09-17 mp6 에서 묵은 경로 문제를 급히 막음 · 본 것: TruncatePath 가 끝 방향을 0 으로 덮는다는 것을 그때 알고 `TODO(improve)` 로 적음 · 처음 추론: 'yaw ≠ 0 목표에서만 문제' 라 미룸 · 의심한 이유(10-14): f2s1 컨트롤러 끝 +5° · 판별: §17 · 결론: 10-02 f2b3 · 10-07 f2c1 · f2d1 남서 정체(3 회)와 10-07 '−109° 로 못 돎' 해석이 이 TODO 와 연결되지 않은 채 지나감 · 다음에 알아보는 법: '위치는 허용 안인데 방향 맞추기에서 정체' 면 먼저 코드의 `TODO(improve)` 목록과 컨트롤러가 받은 목표(`/transformed_global_plan`)를 본다 · 데이터: [09-17 SUMMARY](../debug_log/2026-09-17/SUMMARY.md) 44 행 · BT 커밋 `64aa041` 80~81 행.
2. **끝 방향 계산 출력을 파일로 안 남김**(§13.1 · §17) — f2s1 '+4.5~+5.2°' 와 f2t1 '차 0.0°' 의 원문이 대화에만 있었다(하루 보고서 `REPORT_2026-10-14.html` 결론 1 근거 칸이 '원천 소실' 로 표시). 11-03 같은 bag · 같은 스크립트로 재실행해 수치 확인(§3) — 단 재실행 출력도 파일 없음(발췌가 전부). 다음에 알아보는 법: README §2.3 `| tee outputs/…`.
3. **'멀 때 0°' 를 처음엔 결함으로 읽을 뻔함**(§17 SUMMARY '내 해석 정정 포함') — 컨트롤러 창(prune 약 1 m) 밖이면 끝 = 원경로 중간 점(방향 0°). 다음에 알아보는 법: 끝 방향 비교는 '로버→목표 < 창 길이' 표본만.
4. **bag 을 주행 끝나기 전에 풀어 손상**(§13.3) — "database disk image is malformed", 끝난 뒤 다시 풀어 정상. 원문 없음(SUMMARY 서술뿐).
5. **'55 s 공백' 오보**(§17 처리하지 못한 것 3) — 주행 중 보고에서 목표 4 가 15:23:31 취소 뒤 55 s 비었다고 했으나, 러너 기준 목표 4 는 15:24:26 위치 도달로 끝남 = 공백이 아니라 목표 4 진행 시간. 'Goal was canceled' 는 복구 순서 안의 컨트롤러 목표 취소. 데이터: [`run_f2t1.txt`](../debug_log/2026-10-14/outputs/run_f2t1.txt) 목표 4 65.0 s · [`navlog_f2t1.txt`](../debug_log/2026-10-14/outputs/navlog_f2t1.txt) 36 · 61 행.
6. 기록 어긋남(경미): `up_bt_copypath.txt` 의 빌드 전 `ls` 는 설치본 `nav2_params.yaml` 이 **일반 파일**(`-rwxr-xr-x … 69907 … 13:42`)이었음을 보여 주는데 SUMMARY §14 는 '설치본 yaml 은 소스로의 링크' 만 적었다 — 링크는 `colcon build --symlink-install` 뒤 `chk_bt_load.txt` 에서 확인된 상태(`lrwxrwxrwx`). 그 전 prep 의 `sed -i` 가 링크를 끊은 사례로 보임 — 10-15 §30 이 같은 현상('prep_fast 가 설치본 nav2_params.yaml 에 `sed -i` → 링크가 일반 파일로')을 측정으로 찾음(이 사례와의 연결은 추정).

## 6. 남은 것 (10-15 시점)
- 남서 목표 `f` → `p` 되돌림 시험 — 10-14 §16 제안, 10-15 까지 안 함([남서 카드 §7](southwest-orient-stall.md)).
- `p` 방향이 주행마다 경로 끝 0.3 m 로 달라지는 것(−45~−56°) — 좁은 곳에선 '맞는 방향' 이 위험할 수 있음. 10-15 §18.1 후보 '서쪽 통로 목표 방향 고정(남행 −90° · 북행 +90°)' — 시험 안 함([F2 기준선](f2-baseline-no5.md)).
- 목표 판정의 기준 자세(컨트롤러 경로 끝)를 Nav2 Humble 소스로 확인 — 안 함.
- `/transformed_global_plan` 은 `LONG_REC=1` 일 때만 기록 — 10-02 · 10-07 처럼 기록이 없으면 이 결함은 판별할 수 없다(§16).

## 7. 이후 (10-19 ~): 다음 시기에서 채움
- 포인터만: 10-23 §20.2 `PathBlockedAhead only_new`(같은 BT) · 10-26 §7 `CopyPath step` 재표본 + `planner:=smac` 블록(커밋 `36e59493`) · 10-28 `places.yaml` 통로 북쪽 x −1.65 → −1.78(가운데).

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2s1 | 8 목표 1~3, 서쪽 통로 CANCELED 70.6 s(끝 방향 0°) | `2026-10-14/outputs/run_f2s1.txt` · `navlog_f2s1.txt` · bag `bags/bag_f2s1.tgz` |
| f2s2 | 이어 가기 5/5, 서쪽 통로 위치만 | `outputs/run_f2s2.txt` · bag `bag_f2s2.tgz` |
| f2t1 | CopyPath 검증 8/8 | `outputs/run_f2t1.txt` · `navlog_f2t1.txt` · `prep_f2t1.txt` · bag `bag_f2t1.tgz` |
| `chk_navlog_f2s1.sh` · `chk_navlog_f2t1.sh` | Nav2 · nav_guard 로그 발췌 | `2026-10-14/jobs/` → `outputs/navlog_*.txt` |
| `anal_path_endyaw.py` | 계획기 끝 vs 컨트롤러 끝 방향 | `2026-10-14/jobs/`(출력 원천 소실, 11-03 재실행 발췌 §3) |
| `fig_run_video.py` | 영상 + 목표 방향 두 화살표 | `Docs/tools/` → 그림 `04_navigation/figures/2026-10-14_f2s1_westpass_yaw0.png` · `…_f2s2_westpass_xyonly.png` |
| `anal_westpass_cells.py` | 같은 자리 두 시각 칸 · 카메라 · 라이다 비교 | `2026-10-14/jobs/` → `outputs/westpass_cells.txt` |
| `chk_jetson_navsrc.sh` · `up_bt_copypath.sh` · `chk_bt_load.sh` | Jetson 소스 비교 · 배포 빌드 · 적재 확인 | `2026-10-14/jobs/` → `outputs/up_bt_copypath.txt` · `chk_bt_load.txt` |
| `run_f2c.sh` | 목표 문자열 래퍼(`no5` · `s1rest`) | `2026-10-14/jobs/` |

## 9. 도구 해설
공통: 주행 러너 체인(`run_f2c.sh` → `run_f0.sh` → Jetson `job551_f0drive.sh` → `job550_f0run.py`)의 해설 본체는 [남서 카드 §9](southwest-orient-stall.md) · [F2 순회와 위치 점프 §9](f2-patrol-loc-jump.md). 이날 `run_f2c.sh` 는 `NO5` · `S1REST` 를 더한 판(아래), Jetson 주소 기본 `172.30.1.8`(§8.6 뒤).

### run_f2c.sh — 목표 문자열 래퍼 (PC/WSL, bash) · 10-14 판
- 인자 `NAME NOTE GIT_HEAD [rest5|rest5f|fullf|b910|no5|s1rest]`. 10-14 에 추가: 8 행 `NO5="2.25,-1.6,p;-1.6,-2.0,p;-1.65,-3.7,p;-1.6,-5.5,f;-1.65,-3.7,p;-1.6,-2.1,p;5.5,-2.2,p;0,0,p"` · 9 행 `S1REST="-1.6,-5.5,f;-1.65,-3.7,f;…"`(서쪽 통로를 f 로 — 결함 우회). 11 행 `JETSON_HOST=${JETSON_HOST:-172.30.1.8}` · `LONG_REC=${LONG_REC:-1}`(→ `/transformed_global_plan` 기록 — 이 결함을 볼 수 있었던 조건).
- 계보: 10-07 판 → 이 판 → 10-15 판(`HOMEW` 추가, 기본 주소 192.168.0.110 — [F2 기준선 §9](f2-baseline-no5.md)).

### chk_navlog_f2s1.sh · chk_navlog_f2t1.sh — Nav2 로그 발췌 (Jetson, bash, 로버 안 움직임)
- `/tmp/nav2.log` 에서 `[노드] [수준] [epoch] [이름]: 본문` 꼴 줄을 grep 으로 뽑고 awk 로 epoch 를 `HH:MM:SS.d` 로 바꿈. f2s1 판은 13:47:13~13:48:40 창 · 'Received a path to smooth · Passing new path · missed its desired rate' 제외 · `uniq -c -f3`(같은 문구 연속은 횟수로) · 끝에 nav_guard · stuck_monitor 줄 8 개. f2t1 판은 15:20:50 이후 전부, 'Begin navigating · Goal succeeded/canceled/failed · Smoothed path leads · fail to compute · Failed to make · Running backup · backup failed · Running wait · wait completed · canceled. Stopping · clear except' 만, 끝에 `/tmp/pad_relief.log`.
- 출력 [`navlog_f2s1.txt`](../debug_log/2026-10-14/outputs/navlog_f2s1.txt) · [`navlog_f2t1.txt`](../debug_log/2026-10-14/outputs/navlog_f2t1.txt). 쓰인 곳 §13.1(스무딩 실패가 목표 자세 자체) · §17(pad_relief 첫 작동 순서). 결함: 시각 하드코딩. `uniq -f` 는 필드 기준이라 시각만 다른 같은 줄을 합침(횟수 열 = 연속 수). 다음 판: 10-15 `chk_navlog_f2v*.sh`(같은 본문).

### anal_path_endyaw.py — 계획기 끝 vs 컨트롤러 끝 방향 (PC/Jetson, Python rosbags)
- 부른 형태: `anal_path_endyaw.py bag 시작HH:MM:SS 끝HH:MM:SS [YYYY-MM-DD]`.
- 왜(§16 · §17): 10-07 남서 정체가 같은 결함이었는지 · CopyPath 가 끝 방향을 지키는지.
- 하는 일: bag 의 `/plan`(map) · `/transformed_global_plan`(odom) 마지막 점 방향, `/tf` 의 odom→base_link · map→odom 을 모아 4 s 격자마다 직전 값으로 — 컨트롤러 끝 방향을 `+ map→odom yaw` 로 지도 좌표에 옮기고 차이(−180~180 로 감음), 로버 방향, 로버 ↔ 계획기 끝 거리를 한 줄로. 판정 문턱은 없음(§14 선언 ± 5° 는 사람이 읽음).
- 출력: 화면 표(머리 '시각 · 계획기 끝 방향 · 컨트롤러 끝 방향(지도로) · 차이 · 로버 방향 · 로버→목표'). 그날 출력은 **원천 소실**(§5 실수 2). 10-07 bag 엔 `/transformed_global_plan` 이 없어 실행 실패(§16).
- 결함: 시각을 PC 지역 시각으로 해석(`time.mktime`) — PC · Jetson 이 같은 KST 라 맞음. 4 s 격자라 경계 거리는 표본에 따름. map→odom 은 yaw 만 더함(odom 경로 점 위치는 안 옮김 — 방향 비교엔 충분).
- 재사용: 가능(LONG_REC 주행 bag). 계보: 없음(이날만) — 영상판은 `fig_run_video.py` 주황 화살표.

### fig_run_video.py — 주행 영상 + 방향 화살표 (PC, Python matplotlib → mp4) · 10-14 §13.4 추가분
- `Docs/tools/fig_run_video.py bag 출력.mp4 시작 끝 [배속=3]`. 10-14 추가(머리말 9~10 행 · 50 · 105~107 행): 오른쪽 3 × 3 m 확대판에 보라 = `/plan` 끝 방향, 주황 = `/transformed_global_plan` 끝 방향 화살표 + 아래 글 '목표 방향(보라) · 컨트롤러가 받은 끝 방향(주황) · 로버'. 그 밖 바탕(전역 코스트맵) · 로컬 치명 칸 · 라이다 · 카메라 시야(±43°, 1.4 m)는 §10 판과 같음.
- 출력: 영상 `2026-10-14/videos/*.mp4`(git 제외) · 장면 PNG 2 장(`04_navigation/figures/`). 계보: 10-23 `fig_drive_video.py` 가 기본 영상 도구로 바뀜(메모리 '영상 도구 재설계').

### anal_westpass_cells.py — 같은 자리 두 시각의 칸 · 카메라 · 라이다 (PC, Python rosbags)
- `anal_westpass_cells.py bag HH:MM:SS …`. 각 시각에: TF(odom→base_link · map→odom, tf_static 사슬)로 로컬 코스트맵 값 ≥ 100 칸 중심을 차체 좌표로 → `clr()` = 차체 외곽(x −0.248~+0.262, y ±0.165)까지 거리 − 반 칸 = '최소 여유', 0.6 m 안 칸 수 · 오른쪽(y < 0) 칸 수, nvblox `static_map_slice` 거리 ≤ 0 칸(카메라 장애물) 수, 라이다 점(0.05~3 m) 수, map→odom. 덧붙임: 차체 8 cm 안 치명 칸마다 그 칸에 nvblox 장애물이 있나(카메라 O/X) · 5 cm 안 라이다 점 수.
- 출력 [`westpass_cells.txt`](../debug_log/2026-10-14/outputs/westpass_cells.txt) — 13:48:00 `(+0.22, +0.21) 2.1 cm 카메라O 라이다 0 | … 4.6 · 5.7 · 7.2 cm 카메라O 라이다 0`, 13:54:03 `없음`. 쓰인 곳 §13.5(정지 조건 · 시야 밖 감쇠). 결함: '여유' 는 칸 중심 거리 − 반 칸이라 대각선에선 칸 가장자리 거리와 다름(최대 ≈ 1 cm). 계보: 10-15 `anal_motion_probe.py` · `anal_near_cells_src.py`([상자 옆 정지 원인](box-side-stall-cause.md))가 같은 질문(카메라 칸인가 · 여유)을 일반화.

### chk_jetson_navsrc.sh · up_bt_copypath.sh · chk_bt_load.sh — 배포 3 단 (Jetson, bash, 로버 안 움직임)
- `chk_jetson_navsrc.sh`: Jetson 소스 `CMakeLists.txt` · `nav2_params.yaml` · `nav_to_pose_no_spin.xml` 을 `/tmp/j_*` 로 복사 → PC 에서 저장소와 diff(결과 '주석 7 줄만 다름' — diff 원문 없음).
- `up_bt_copypath.sh`: `/tmp/up_*` 4 파일을 소스에 덮고(`set -e`) `grep -c` 로 등록 줄 확인 → 설치본 yaml `ls -la` → `colcon build --symlink-install --packages-select rover_navigation` → `.so` 존재 · `nm -D | grep -c BT_RegisterNodesFromPlugin`. 출력 [`up_bt_copypath.txt`](../debug_log/2026-10-14/outputs/up_bt_copypath.txt)(`CMakeLists.txt:4` · `nav2_params.yaml:1` · `1` · 빌드 7.12 s · 등록 함수 `1`).
- `chk_bt_load.sh`: 설치본 링크 여부 · 플러그인 줄 수 · `<CopyPath` 수 · PreferForward 값 → `prep_patrol.sh lite 15.0` 재기동 → nav2.log 의 bt_navigator 오류 · 'copy' 줄. 출력 [`chk_bt_load.txt`](../debug_log/2026-10-14/outputs/chk_bt_load.txt)(`lrwxrwxrwx … · copy 플러그인 줄 1 · BT CopyPath 1 · PreferForward 15.0` · `PREP_OK` · Configuring/Activating). 한계(§14 SUMMARY): BT XML 은 첫 목표 때 해석 — 적재 확인으로는 포트 형 오류를 못 잡음.

## 10. 용어
- **SmoothPath · SimpleSmoother**: 계획기 원경로의 꺾임을 펴는 Nav2 스무더. `check_for_collisions="true"` 면 편 경로의 점이 코스트맵 치명 칸에 닿을 때 'Smoothed path leads to a collision' 으로 실패한다 — 목표 자세 자체가 닿으면(좁은 통로) 매번 실패.
- **TruncatePath(Nav2 BT 노드)**: 경로 끝에서 `distance` 만큼 점을 지우는 노드. 남은 마지막 점의 방향을 '직전 점 → 원래 끝점' 방향으로 다시 쓰는데, distance 0 이면 두 점이 같아 atan2(0, 0) = 0 이 된다(09-17 TODO 원문 · 10-14 측정과 일치, 소스 대조 기록 없음).
- **`{raw_path}` · `{path}`**: BT 블랙보드 키. 계획기는 `{raw_path}`, 컨트롤러(FollowPath) · PathBlockedAhead 는 `{path}` 만 본다(09-16 mp4 — 한 틱에 `{path}` 를 두 번 쓰지 않으려는 구조).
- **`/transformed_global_plan`**: MPPI 컨트롤러가 받은 경로를 로컬 좌표(odom)로 옮기고 로버 앞 약 1 m(prune 거리)로 자른 것. 목표가 그 창 안에 들어와야 마지막 점 = 목표 자세. `LONG_REC=1` 주행에서만 bag 에 기록.
- **'p' · 'f' 목표**: 러너 · place_server 의 목표 방향 모드 — p = 보내기 직전 계획 경로 끝 0.3 m 구간 방향, f = p 와 같되 위치 0.15 m 안이면 방향 맞춤 없이 끝(SUCCEEDED_XY).
- **stateful goal checker**: 위치가 0.15 m 안에 한 번 들면 그 뒤로는 방향(0.35 rad ≈ 20°)만 본다 — 비교 대상은 컨트롤러가 받은 경로 끝 자세([남서 카드 §10](southwest-orient-stall.md)).
