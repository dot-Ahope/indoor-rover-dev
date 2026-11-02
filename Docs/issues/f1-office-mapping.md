# F1 사무실 지도 — office_v1 → 이어 그리기 오정합 2 회 → bag 재생으로 office_v2

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **완료(office_v2 저장 · F1-1 ~ F1-3 통과 · F1-4 = slam_toolbox 위치 추정 모드 결정)** · 이어 그리기 오정합의 근본 대책은 **미결**(창 축소만으로 불충분, 응답 문턱 · 각도 창 A/B 안 함) · 이후 10-02 에 office_v3 로 대체 | 09-30 ~ 10-01 (이 카드는 09-30 §0~§6 · §8~§17, 10-01 §0~§7 · §9 까지) | [09-30 §1](../debug_log/2026-09-30/SUMMARY.md) | `rover_navigation/config/nav2_params.yaml`(footprint 앞 0.262 · 뒤 −0.248 · 폭 ±0.165, 09-30 §3) · `rover_bringup/launch/slam.launch.py`(`map_file` · `map_start_pose` 09-30 §4, `slam_mode:=localization` 10-01 §7, 위치 추정 노드 간격 0.30 m · 0.15 rad · 지도 다시 그리기 10 s 10-01 §9.3) · `rover_bringup/config/slam.yaml`(`loop_search_space_dimension` 8.0 → **3.0**, 09-30 §14) · `rover_bringup/launch/joy_teleop.launch.py`(`profile:=mapping`) · `rover_bringup/launch/foxglove.launch.py`(`viz:=map`) · 지도 `Docs/04_navigation/maps/office_v1.*` · `office_v2.*` | [첫 SLAM 지도](first-slam-map.md)(08 월 지도 · 이 카드의 앞) · [Foxglove 스냅 · 브리지 부하](foxglove-snap-cpu.md)(09-30 §5 · §12) · [조이스틱](joystick-teleop.md)(mapping 프로필 · 무선 끊김 F1-0) · [SLAM map→odom 시각 정체](slam-stamp-freeze.md)(10-01 §9 위치 추정 부하) · [제자리 회전 옆 밀림](f0-rotation-side-slip.md)(180° 당 10~27 cm — 루프 창 근거) · [정체 감시](stuck-monitor.md)(매핑 중 관찰 모드) |

**한 줄**: 09-30 에 무선 패드로 출발 방 + 문 밖 책상 구역을 그려 `office_v1`(15.1 × 10.7 m)을 저장하고 루프 닫힘 · 이중 벽 · 저장/복원 · 줄자 정확도(F1-1 ~ F1-3)를 통과했다. 같은 날 사무실 전체로 넓히려고 office_v1 위에 **이어 그리기**를 두 번 했으나 두 번 다 **루프 클로저 오정합**(4.2 m 평행 이동, 1.67 m · +33°)으로 지도가 깨졌다. 루프 탐색 창을 8 → 3 m 로 줄였지만 두 번째 오정합은 못 막았다. 10-01 에 남긴 bag 을 오정합 전까지 재생해 지도를 되살렸는데, 루프 클로저를 켜면 옛 지도(동쪽 방)가 10 cm 옮겨지고 끄면 새 남쪽 통로가 0.17 m 휘었다 → 휜 구간(+590 s 이후)을 빼고 루프 클로저 끔으로 다시 재생해 `office_v2`(16.7 × 11.4 m)를 만들었다. 운용은 '저장 지도 고정' 의 slam_toolbox 위치 추정 모드로 정했다(AMCL 제외).

> 읽는 법: '측정' 은 출력 파일 원문이 있는 값, **추정** 은 그렇게 표시, '미확인' 은 기록이 없는 것. 사용자 줄자 · 관찰은 '사용자' 로 표시(대화 기록, 파일 없음). 지도 bag `map_0930_1724`(780 s, 219 MB)은 **Jetson `~/bags/` 에만** 있다 — 저장소 `bags/` 에는 없고 PC 사본은 미확인.

## 1. 증상 · 목표
- 목표(F1, `NAV2_EXPLORATION_PLAN.md §7.4`): 사무실 저장 지도 — 뒤의 F2 웨이포인트 · F2.5 장소 이름 이동이 '세션마다 같은 좌표' 를 쓰려면 고정 지도와 그 위 위치 추정이 필요하다(09-30 §9 의 선행 순서).
- 막힌 곳:
  1. 앞선 F0 복귀 시험의 지도 ↔ 줄자 앞뒤 편차 +3.6 / +5.5 / +5.2 cm(09-29 §12.5)가 무엇 때문인가(09-30 §2~§3).
  2. 매핑 중 Foxglove 에서 '로봇이 멈췄다 점프' · '회전하면 스캔만 돈다'(사용자) — 위치 추정 문제인지 표시 문제인지(§5 · §11 · §12).
  3. 이어 그리기 중 로버가 지도 위에서 **엉뚱한 자리로 점프**(사용자 ≈ 17:10, §13)하고, 두 번째 매핑도 '또 지도가 깨졌다'(§16).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-30 §1 | F1 방향 논의(사용자 질문 2 건) | — | 넓혀 가기 = `serialize_map` + 다음 세션 `map_file_name` · `map_start_pose`(출발 테이프). 지도 수정 = pgm 손 편집보다 **Costmap Filter 마스크** 권장. 위험(시작 자세 어긋남 → 이중 벽, 그날 물체가 영구 장애물, Humble 2.6 이어 그리기 덜 검증 — 미확인) | SUMMARY 만 |
| 09-30 §2 | 편차 원인 1 차: 차체 치수 실측(사용자) | 라이다 중심 → 뒤 트랙 끝 ≈ 0.40 m · 앞 끝 ≈ 0.11 m → base_link 앞 **+0.262** · 뒤 −0.248(가정 ±0.25). 출발 표시를 +0.262 로 고친 예측 vs 줄자: f0a6 +2.4 · f0a7 +4.3 · f0b2 +4.0 cm | 치수로는 1.2 cm 만 설명, **평균 ≈ 3.6 cm 같은 방향으로 남음** | SUMMARY(계산, 원천 = 09-29 §12.5) |
| 09-30 §3 | footprint 실측 반영 + SLAM 앞뒤 치우침 시험(판정 전 선언: ≤ 1.0 cm 없음 · ≥ 1.5 cm 있음 · 사이는 1 회 반복) | 1 회차 0.70 m 전진: SLAM 예측 69.5 cm vs 줄자 ≈ 71 cm(차 1.5 cm, 경계 → 반복). 2 회차 0.70 m 후진: SLAM 4.1 cm 뒤 · 1.2 cm 오른쪽 vs 줄자 4 cm 뒤 · 1 cm 오른쪽(차 0.1 · 0.2 cm). 후진 EKF 는 SLAM 보다 3.0 cm 적음 | **S-a: SLAM 직선 이동 치우침 없음** → 복귀 잔차 3.6 cm 의 남은 후보(**추정**) = 목표에서 ~180° 도는 동안의 SLAM 오차 · 대각 측정 기준 차. 가를 시험(제자리 180° → 줄자)은 미실시 | `outputs/j682_slambias.txt` · `j683_slambias_rev.txt`, `jobs/job680_slambias.py` |
| 09-30 §4 | F1 결정(사용자: 이어 그리기 · 무선 패드 · Foxglove 로 보며 조종 · 유리 있음) · 준비 | `slam.launch.py map_file:=` · `map_start_pose:=`, `joy_teleop profile:=mapping`(0.07 m/s · 0.3 rad/s), 저장 = 포즈 그래프 + 격자(Jetson `~/maps/office/`) | 판정 선언: F1-1a 루프 닫힘 ≤ 5 cm · F1-1b 이중 벽 0 · F1-2 복원 ≤ 5 cm · 5 s · F1-5 유리 기록 · F1-0 무선 끊김 시험 | `jobs/job684_map_save.sh` · `job685_f1_teleop.sh` · `job686_f1_deploy.sh` |
| 09-30 §4.1 | prep · F1-0 | Nav2 첫 기동 실패(`behavior_server get_state … async_send_request failed`) → STARTUP 재전송으로 active. F1-0: 기록에는 '전진 유지 → 전원 끔' 이 안 잡힘(1 s 칸 표 전부 axis1 0 근처, /joy 공백 없음) | **F1-0 합격은 사용자 관찰**('/joy 1 유지 중 패드 전원 끔 → 0') — 기록 도구로는 판정 못 함 | `outputs/j687_f1_prep.txt` · `j691_joydrop.txt`, `jobs/job689_nav2_startup.sh` · `job690_joydrop.py` |
| 09-30 §4.2 | 1 차 매핑 → `office_v1` 저장 | 301 × 213 셀(5 cm) = 15.1 × 10.7 m, 원점 (−5.09, −6.96), 점유 4,653 · 빈 27,103 · 미지 32,357. posegraph 50.3 MB · data 38.4 MB. 저장 직후 자세 (0.0044, 0.0006, 1.07°) → 오른쪽 앞 모서리 세로 +0.75 · 가로 +0.55 cm. slam.log 루프 폐합 로그 0 줄(로그 수준이 낮아 판단 불가) | 동쪽 벽 15~20 cm 띠 = 실제 두께인지 이중 벽인지 그림만으론 모름 → 사용자 확인 | `outputs/j693_f1_save.txt`, 그림 [`2026-09-30_office_v1.png`](../04_navigation/figures/2026-09-30_office_v1.png) |
| 09-30 §4.3 | F1-1a · 1b · 5 판정(사용자) | 줄자 세로 ≈ 2 · 가로 ≈ 1.5 cm vs SLAM 0.75 · 0.55 → 차 ≈ 1.3 · 1.0 cm. 동쪽 띠 = 실제 ≈ 20 cm 벽. 출발 오른쪽 벽(map y ≈ −0.65, x −1.2~1.8) = 필름 유리 → 연속 벽선 | **F1-1a · 1b 통과**, F1-5 필름 유리 1 곳(필름 없는 유리는 미측정) | 사용자 |
| 09-30 §5 · §5.1 | 매핑 중 '멈췄다 점프'(사용자) 원인 | 부하 평균 11.3(6 코어), EKF 주기 미달 760 · SLAM Message Filter 버림 106(≈ 40 분 누적). A/B 30 s: Foxglove 연결 EKF 미달 +12 · 브리지 62.4 % · ekf 48.6 % vs 끊음 +0 · ekf 12.1 % | Foxglove 연결이 EKF 를 굶김 → odom TF 늦음 → SLAM 스캔 버림 → 표시 위 멈춤 · 점프(**추정**, 수치는 측정) → `viz:=map` 세트 적용, 개선 측정 C 는 보류 | `outputs/j694_lagchk.txt` · `j695_load_A.txt` · `j695_load_B.txt` → [Foxglove 카드 §4c](foxglove-snap-cpu.md) |
| 09-30 §4.4 | F1-2 복원(움직이지 않은 채 불러옴) | "Load From File …/office_v1.posegraph", /map 301 × 213 · 원점 같음, 시작 map (−0.0112, −0.0032, +0.26°) = **1.16 cm**, 16 s 동안 변화 0.00 cm | 통과. 한계: 로버를 테이프에 다시 놓고 불러오는 경우는 아직 | `outputs/j698_f1_restore.txt` |
| 09-30 §6 | 충전 중단 | — | 다음 세션 절차 기록(재부팅 → `/tmp` 스크립트 재전송 → `map_file:=office_v1` prep) | SUMMARY |
| 09-30 §8 · §8.1 | F1-3 지도 정확도(선언: 3 구간 ±5 cm) | 지도(job703): 방 폭 1.96 m · 문 0.81~0.86 · 벽 0.20. 줄자: 오른쪽 트랙 → 유리벽 0.41 · 왼쪽 트랙 → 북쪽 벽 1.23 → 방 폭 1.97, 문 0.90, 벽 ≈ 0.20 | **통과**: 방 폭 차 1 cm(벽 절대 위치까지 1 cm 안), 벽 0, 문 3.7 / 8.7 cm **경계** — 라이다 높이 0.185 m 에서 문짝 · 문막이가 찍힌 탓(**추정**) | 지도 측정 원문 없음(`jobs/job703_map_spans.py` 의 출력 파일 없음 — SUMMARY 표만) |
| 09-30 §9 | 사용자 최종 목표 제시 | 이름 붙인 장소로 '가' · '돌아와' 를 온디바이스 LLM 텍스트로 | 금지 구역 마스크는 **사무실 전체 매핑 뒤로 연기**. 결정: 입력 텍스트 · 로드맵 F2.5. 선행 = 전체 매핑 → F1-4 → F2 → 장소 이동 → LLM | SUMMARY · `NAV2_EXPLORATION_PLAN.md §7.4` |
| 09-30 §10 | 이어 그리기 준비 · F1-2 재확인(테이프에 다시 맞춰 놓고) | 4 s 에 TF, map (−0.0014, −0.0030, +0.19°) = **0.33 cm**, 12 s 흔들림 0.00 | F1-2 재확인 통과 — 세션 간 같은 좌표계로 시작 가능 | `outputs/j704_f1v2_prep.txt` |
| 09-30 §11 | 이어 그리기 중 지도 오류 · 위치 점프(사용자: 메모리 의심) → **저장 안 함** | available 5.1 GB / 7.6 GB · 스왑 0. 부하 10.6~10.9, 24 s 에 EKF 미달 +25 · SLAM 버림 +4. CPU: slam 56.6 · ekf 50.3 · nvblox 35.3 · 대기 Nav2 합 ≈ 130 % · 브리지 18.1 %(viz:=map) · 합 347.7 % | **메모리 아님 · CPU 과부하**(실행 대기 스레드) → prep `MAPPING=1`(Nav2 · nvblox 생략) | `outputs/j705_jumpchk.txt` · `j706_cputop.txt` |
| 09-30 §11.1 | 매핑 전용 모드 검증 | 첫 시도(job707 → job657 경로) ≈ 80 s 에 'Terminated'(원인 미확정). job240 직접(job709) 정상. 30 s(Foxglove 1 연결): 부하 **2.72**, EKF 미달 **0** · SLAM 버림 **0**, slam 57.5 · ekf 53.6 · 브리지 28.7 % | 과부하 해소 — 패드 매핑은 `MAPPING=1` | `outputs/j707_mapmode_prep.txt` · `j709_mapmode_prep_full.txt` · `j710_mapmode_teleop.txt` |
| 09-30 §12 | 매핑 모드에서도 '회전하면 스캔만 돌고 로버는 안 움직임'(사용자) | odom→base_link yaw −92.3° → −175.8° → +172.1° → +97.3°(12 s, ±180° 를 넘어 ≈ 171°, 초당 ≈ 14°), map→odom −2.7 ~ −5.0°, 입력 휠 25 · 컨디셔너 25 · IMU ≈ 200 · EKF 30 Hz 끊김 없음 | 로버 쪽 TF 정상 → 브리지 `max_qos_depth 1` 이 /tf 를 버린다(**추정**) → map 세트만 10 | `outputs/j712_rotchk.txt` → [Foxglove 카드 §4c](foxglove-snap-cpu.md) |
| 09-30 §13 | 로버가 지도 위 엉뚱한 자리로 점프(사용자 ≈ 17:10) 사후 조사(bag 없음) | Ceres 흔적 2 건: 16:59:10(불러오기) · **17:10:34**. map→odom (+4.171, +0.644, −2.7°) — odom 은 (−2.506, +0.081), SLAM 은 (+1.672, +0.845). 입력 정상(IMU 199.7 · scan 10.0 · EKF 30.0 Hz), SLAM 버림 73(queue is full), stuck_monitor 원격 조종 회전 중 3 회 발동 | 17:10:34 루프 클로저가 비슷한 구조에 잘못 맞춤(**추정**) — 각도 3° 차 · 위치 4 m 차는 평행 이동 오정합의 전형 | `outputs/j713_jump2.txt` · `j714_jump2b.txt` |
| 09-30 §14 | 판정 확정(사용자: "slam 이 틀리고 바퀴+자이로가 맞다") · 조치 | 창 8.0 = ±4 m 에 4.2 m 가짜 정합이 들어옴 | **`loop_search_space_dimension` 8.0 → 3.0**(±1.5 m, 하나만 바꿈). 기각: 루프 클로저 끔(누적 오차 못 잡음) · 응답 문턱 상향(수치 근거 없음). 매핑 prep 에 경량 bag 자동 기록 · stuck_monitor 관찰 모드 | `jobs/job715_slamcfg_deploy.sh` · `job240_clean.sh` |
| 09-30 §15 | 조이스틱 mapping 프로필 = 펌웨어 상한(사용자) | 0.07 · 0.3 → 0.085 · 0.38 | → [조이스틱 카드](joystick-teleop.md) | `jobs/job716_joymax_deploy.sh` |
| 09-30 §16 | 2 차 매핑(17:24~17:37, 창 3 m · 패드 최대) → '또 깨졌다'(사용자) · **저장 안 함** | 출발 오차 0.7 · 0.9 cm. bag 780 s: map→odom 은 7.5 분 동안 서서히 (0,0,0°) → (+0.02, +0.05, −11.1°), 5 cm 넘는 보정 11 건 모두 ≤ 0.11 m · ≤ 1°. 17:31:34~39 Ceres 10 회(출발점 복귀) 동안 변화 없음. **17:36:18.4 Ceres 1 회 = (+0.06, +0.08, −11.5°) → (−1.14, −1.08, +21.6°): 1.67 m · +33.2°**, 이어 0.50 · 0.18 m 흔들림 | 11 분에 11° 흐른 추측항법을 한 번에 33° 고친 것은 물리적으로 안 맞음 → **오정합**. 창 ±1.5 m 는 위치 창일 뿐(각도 ±20° · 그래프 최적화가 합쳐짐) → **창 축소만으로 불충분** | `outputs/j717_map2_prep.txt` · `j718_map2_break.txt`, `jobs/job718_ana.py` |
| 09-30 §17 | 오정합 전까지만 되살리기(사용자) — 재생 준비 | bag 을 `~/bags/map_0930_1724`(219 MB)로 복사, 라이브 SLAM 정지, 도메인 42 재생 SLAM 기동. 5 분 넘게 '재생: 앞 …' 출력 없음 → 사용자 '멈추고 내일' 로 중단 | 출력 없음의 원인은 다음 날 grep 파이프 버퍼로 **추정**(§5.3 실수) | `jobs/job719_cut.sh` · `job719_cutreplay.py` · `job720_stop_replay.sh`, 출력 원문 없음 |
| 10-01 §1 · §1.1 | +699 s(오정합 3 s 전)까지 재생, 루프 클로저 켬(선언: R1 점프 0 · CUT 값 라이브와 ≤ 0.15 m · 2°, R2 이중 벽 0) | 스캔 6,994, 5 cm 넘는 보정 13 건 최대 0.12 m · 1.0°, CUT 시점 (+0.056, +0.075, −11.3°) vs 라이브 (+0.02, +0.05, −11.1°) = 4.4 cm · 0.2°. save_map 255 → 그래프만 불러와 map_saver 로 격자(332 × 227). 영역별 최적 이동: 출발 방 0 · **동쪽 방 x −0.10** · 남쪽 (−0.05, −0.05). 벽 두께 office_v1 0.20 → 후보 **0.10** | **R1 통과(같은 입력 → 같은 결과)**, 그러나 F1-3 벽 두께 불합격 — 이어 그리는 동안의 루프 클로저가 office_v1 옛 노드까지 다시 최적화해 동쪽 방을 10 cm 옮김(**추정**, 어느 루프 클로저인지 미확인) | `outputs/j719b_cutreplay.txt` · `j722_cand_grid.txt` · `j_cand_compare.txt`, 그림 [`2026-10-01_cand_cut699_vs_v1.png`](../04_navigation/figures/2026-10-01_cand_cut699_vs_v1.png) |
| 10-01 §2 · §2.1 | 같은 재생 · **루프 클로저 끔**(선언: L1 벽 0.15~0.25 · 방 폭 1.92~2.02, L2 최적 이동 ≤ 0.05, L3 두 줄 벽 0) | Ceres 1 회(불러올 때), 5 cm 넘는 보정 12 건 최대 0.14 m · 1.4°, CUT (+0.078, +0.057, −10.9°). 벽 0.15(경계) · 방 폭 1.95 · 최적 이동 **모두 0** · 그대로 겹침 83/88/68/80 %. 남쪽 끝 벽(y ≈ −6.3)이 v1 보다 0.05~0.30 m 남쪽 | L1 · L2 통과, 큰 보정은 루프 클로저가 아니라 스캔 정합에서 나옴. 남쪽 벽은 어느 쪽이 맞는지 지도만으론 모름 → 사용자 | `outputs/j723_nolc.txt` · `j_nolc_compare.txt`, `jobs/southwall.py` |
| 10-01 §2.2 | 남쪽 벽 판정(사용자: 줄자 5.5 m 한계 → '책상 구역 남쪽 벽은 일직선') | 2 m 구간 평균 y(x 0~2 / 2~4 / 4~6): office_v1 −6.24 / −6.19 / −6.23(휨 ≤ 0.05) · 두 후보 −6.33 / −6.30 / −6.47(4~6 m 에서 0.17 m 아래) | **office_v1 이 맞고 2 회차 남쪽 통로가 휘었음** → L3 불합격. 원인(**추정**, 구조적): mapping 모드 새 스캔은 최근 버퍼(20)에만 맞고 옛 지도와는 루프 클로저로만 이어짐 | `outputs/j_straight.txt`, `jobs/straight.py` |
| 10-01 §3 | 사용자 지시: 끔 후보의 남쪽 벽(x ≥ 0, y ≤ −5.95)을 office_v1 셀로 교체 | 바뀐 셀 1,097(점유 지움 460 · 추가 214), 기울기 −2.1° → −0.2°, 겹침 83/88/78/86 % | 격자만 고침 — 포즈 그래프는 휜 그대로라 slam_toolbox 로 쓰면 다시 나옴. x = 0 에 5~15 cm 단차 | 출력 원문 없음(`jobs/edit_south.py` 화면 출력, SUMMARY), 그림 `2026-10-01_cand_nolc_s_*.png` |
| 10-01 §4 | 사용자 '포즈 그래프도 해당 부분만 제거' → 휜 구간 스캔을 빼고 재생(+590 s 에서 자름, 루프 클로저 끔) | 스캔 5,903, **5 cm 넘는 보정 0 건**, CUT (−0.074, −0.007, −8.0°). 남쪽 벽 −6.23 / −6.19 / −6.24 · 기울기 −0.3° · 최적 이동 0 · 겹침 86/100/81/96 % · 벽 0.15/0.20/0.15 · 방 폭 1.95. save_map 다시 255(job722 방식으로 생성) | **모두 통과**(손 편집 없음, 그래프 · 격자 일치). 대가: +590 s 이후에만 본 영역(동쪽 끝 L 자 등)은 빠짐. 기각한 대안: 그래프 파일 편집(바이너리) · RViz 수동 루프(Foxglove 미지원 — 내 이해, 미확인) · 노드 삭제(포크 수정 필요) | `outputs/j724_cut590_nolc.txt`, `jobs/run_x724.sh`, 그림 [`2026-10-01_cand_cut590_nolc_vs_v1.png`](../04_navigation/figures/2026-10-01_cand_cut590_nolc_vs_v1.png) |
| 10-01 §5 | `office_v2` 저장(사용자 승인) | = `cand_0930_cut590_nolc` 복사, sha256 앞 16 자 일치(posegraph ad2a7edbe06a6ccb · data 9ff8aa0d6b2478c6 · pgm bab32fa3e216a69b), 333 × 227, 원점 (−5.29, −6.96). posegraph 94.5 MB · data 87.2 MB | 교훈 3 줄(루프 클로저는 옛 지도를 옮길 수 있음 · 끄면 새 구간 오차가 남음 · 휜 구간은 bag 재생으로 뺄 수 있음) | `outputs/j725_save_v2.txt`, 그림 [`2026-10-01_office_v2.png`](../04_navigation/figures/2026-10-01_office_v2.png) |
| 10-01 §6 · §6.1 | F1-2 복원(office_v2, 테이프에 놓고 · 전체 스택) | /map 333 × 227 · 원점 같음, 시작 map (−0.0055, −0.0079, +0.69°) = **0.97 cm**, 2 s 부터 변화 0. 기동 직후 EKF 미달 23 · SLAM 버림 8, load 7.4 → 4.4 | **통과**. controller_server '?' 는 조회 시간 초과 — 곧 6 노드 active | `outputs/j727_f12_v2.txt` · `j728_nav2state.txt` |
| 10-01 §7 · §7.1 | F1-4 위치 추정 방식 비교 준비(① 지금 = mapping 이어 그리기 ② slamloc ③ amcl), F1-4a 정지 기동 | slamloc: 3 s 부터 (+0.0007, −0.0154, +0.32°) = **1.55 cm**. amcl: 0.00 cm(움직이기 전엔 입력한 시작 자세를 그대로 냄 — 정지 시험으론 정합 품질 못 봄). amcl CPU 8.8 % · map_server 6.8 %, slamloc CPU 는 ps 이름 잘림으로 못 잼 | 두 후보 기동 통과 | `outputs/j730_f14a.txt`, `jobs/job730_f14_deploy.sh` |
| 10-01 §7.2 · §7.3 | F1-4b 주행 비교 선언(F0-b 코스 2 회씩) → 사용자 결정 | — | **② slam_toolbox 위치 추정 모드**. 4 회 비교는 취소, L-b(복귀 줄자 ≤ 5 cm) · L-c(0.30 m 넘는 튐 0) · L-d(시작 ≤ 5 cm)는 F2 첫 주행 판정에 넣음 | SUMMARY |
| 10-01 §9 · §9.0 | AMCL 계획에서 제외(사용자) · 위치 추정 모드 부하 재생 A/B | base(0.05 m · 0.03 rad) > 0.2 s 결손 14.46 % · CPU 134 % → t3m(0.30 · 0.15 · 지도 다시 그리기 10 s) 0.19 % · 최대 +0.395 s · 22 % | t3m 채택(`slam.launch.py` localization 일 때만) → [SLAM 시각 정체 카드](slam-stamp-freeze.md) | `outputs/j736_locreplay_base_t2.txt` · `j736b_…` · `j736c_locreplay_t3m.txt` |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 복귀 앞뒤 편차 = 차체 앞 끝 위치 가정(+0.25) | 라이다 → 앞 · 뒤 끝 줄자(09-30 §2) | 앞 끝 +0.262 → 1.2 cm 만 설명 | **부분**(3.6 cm 남음) |
| 편차 = SLAM 직선 이동 앞뒤 치우침 | 0.70 m 전진 · 후진 vs 줄자(§3) | 1.5 · 0.1 cm, 부호 일정하지 않음 | **기각** |
| 편차 = 목표에서 ~180° 회전 중 SLAM 오차 · 대각 측정 기준 | 제자리 180° → 줄자 | 안 함 | **미확인** |
| 매핑 중 '멈췄다 점프' = 메모리 | `free` · RSS(§11) | available 5.1 GB · 스왑 0 | **기각** |
| 같은 증상 = CPU 과부하(EKF 지연 → odom TF 늦음 → SLAM 스캔 버림) | 매핑 전용 모드 30 s(§11.1) | 부하 10.9 → 2.72, EKF 미달 · SLAM 버림 0 | **지지**(표시 점프와의 인과는 **추정**) |
| '스캔만 돈다' = 로버 TF 문제 | 회전 중 1 s 간격 TF · 입력(§12) | odom · map TF 매끄럽고 입력 끊김 없음 | **기각** → 브리지 쪽(**추정**, Foxglove 가 받은 /tf 간격은 미측정) |
| 17:10 점프 = SLAM 오정합(추측항법 아님) | 사용자가 실제 위치 확인(§14) | "slam 이 틀리고 바퀴+자이로가 맞다" | **확인** |
| 오정합은 루프 탐색 창이 넓어서(±4 m) | 창 3 m 로 2 차 매핑(§16) | 1.67 m · 33° 오정합 또 발생 | **부분** — 4.2 m 건은 창 밖이 됐을 수 있으나 이번 건은 못 막음. 각도 탐색 · 응답 문턱의 몫은 미확인 |
| 재생이 라이브를 재현한다 | 같은 bag 재생, 보정 시각 · CUT 값 대조(10-01 §1.1) | 보정 시각 0.1~0.2 s 안 일치, CUT 4.4 cm · 0.2° | **지지**(재생 1 회) |
| 이어 그리기 루프 클로저가 옛 지도를 옮긴다 | 켬 vs 끔 재생, 영역별 최적 이동(§1.1 · §2.1) | 켬 동쪽 방 0.10 m · 끔 모두 0 | **지지**(어느 루프 클로저인지 미확인) |
| 끔 후보의 남쪽 벽 차이 = office_v1 쪽 오차 | 사용자 기준 '남쪽 벽은 일직선'(§2.2) | v1 곧음(≤ 0.05) · 후보 0.17 m 휨 | **기각**(후보가 휨) |
| 휨 출처 = +590 s 이후 남쪽 통로 주행 | 그 구간 빼고 재생(§4) | 휨 사라짐, 보정 0 건 | **지지** |

## 4. 조치와 효과
- **footprint 실측**(09-30 §3): `[[0.262, ±0.165], [−0.248, ±0.165]]`(이전 ±0.25) — 앞 여유 계산 1.2 cm 개선. 지금도 그 값(`nav2_params.yaml` 302 · 537 줄). ⚠ 같은 파일 264 줄 MPPI 주석은 아직 '0.5×0.33'.
- **이어 그리기 인자**: `slam.launch.py map_file:=<확장자 없이>` · `map_start_pose:=x,y,yaw`(기본 0,0,0 = 출발 테이프), 10-01 에 `slam_mode:=mapping|localization`(위치 추정은 `map_file` 필수). F1-2 복원 0.33~1.16 cm(office_v1) · 0.97 cm(office_v2), 모두 5 s 안 안정.
- **매핑 전용 모드**(`job240_clean.sh MAPPING=1`): Nav2 · nvblox 생략, stuck_monitor 단독(09-30 §14 부터 기본 관찰), 경량 bag 자동 기록(`/tmp/bags/map_<월일_시분>`: /scan · /tf · /tf_static · /odometry/filtered · /wheel_odom · /imu/data · /cmd_vel · /joy). 효과: 부하 10.9 → 2.72, EKF 미달 0. 한계: 날짜 폴더의 job240 에만 있다 — 지금 고정 prep(`Docs/tools/prep_fast.sh` · `prep_patrol.sh`)에는 `MAPPING` 이 없다(11-02 확인).
- **루프 탐색 창 8.0 → 3.0**(09-30 §14): 지금도 3.0(`slam.yaml` 57 줄, 주석에 근거). 효과: 2 차 매핑에서 1.67 m · 33° 오정합을 **못 막음**(§16). `loop_match_minimum_response_fine 0.45` · `coarse_search_angle_offset 0.349` 는 그대로 — 09-30 §17 의 'A/B 비교'(응답 문턱 상향 · 각도 창 축소 · 루프 클로저 끔)는 이 범위에서 안 했다.
- **지도 되살리기 = bag 재생**(10-01 §1 · §4): 도메인 42 · sim time, 기록 당시 map→odom 을 빼고 odom→base · 정적 TF · 스캔만 재생 → 새 slam_toolbox 가 office_v1 에서 이어 그림. office_v2 = +590 s 컷 · 루프 클로저 끔. 지금 매핑 기본(`slam.yaml`)은 여전히 `do_loop_closing: true` — 끔 권장은 `job726_prep_map.sh` 주석에만 있다.
- **위치 추정 운용 = slam_toolbox localization**(10-01 §7.3 · §9.0): AMCL 제외(`localization.launch.py` · `amcl.yaml` 은 미사용으로 남김 — 주석 예시가 아직 office_v2). 노드 간격 0.30 m · 0.15 rad · 지도 다시 그리기 10 s(§9.3)는 지금 `slam.launch.py` 75~77 줄에 그대로(+ 뒤에 transform_timeout 1.5).
- **Foxglove `viz:=map`**(§5.1 · §12): `/tf` · `/tf_static` · `/robot_description` · `/map` · `/map_metadata` · `/scan`, capabilities `clientPublish` 만, `max_qos_depth` 10 — 지금도 그 값(`foxglove.launch.py` 49 · 54 · 73 줄). 자세히는 [Foxglove 카드 §4c](foxglove-snap-cpu.md).
- 한계: office_v2 는 10-02 에 office_v3 로 바뀌었고(지도 구멍 → 위치 점프, 다음 시기), 지금 운용 지도는 **office_v3**(`places.yaml` 8 줄 · `prep_fast.sh` 기본 · `run_slam_replay.sh`). office_v1 · v2 의 pgm/yaml 은 `Docs/04_navigation/maps/` 에 기록으로 남아 있고 포즈 그래프는 Jetson 에만 있다.

## 5. 내 실수
### 5.1 후진 시험 시간 한도가 음수 — 로버가 안 움직임(09-30 §3.2) — 칸 형식
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 0.70 m **후진**으로 SLAM 앞뒤 치우침 2 회차 — `job680_slambias.py 0.70 -0.06`(`job683`) |
| 본 것 | 첫 시도에서 로버가 움직이지 않고 바로 '주행 … 정지 지령' 출력 |
| 처음 추론 | (따로 세운 추론 없음 — 바로 코드를 봄) |
| 의심한 이유 | 전진(1 회차)은 됐고 인자만 V<0 로 바뀜 |
| 판별 시험 | 루프 조건 `time.time() - ts < DIST/V*2 + 5` 를 V = −0.06 으로 계산 → −18.3 s, 첫 비교에서 거짓 |
| 결론 | 시간 한도에 부호 있는 속도를 씀 → `abs(V)` 로 수정(같은 파일, 주석 '09-30: 후진(V<0) 때 한도가 음수') |
| 다음에 알아보는 법 | 속도 · 거리 인자를 받는 러너는 **부호가 바뀌는 쪽(후진 · 우회전)으로 한 번 마른 실행**(지령 0, 루프 횟수만 출력)을 한다. 한도식에는 크기(`abs`)를 쓴다 |
| 데이터 | `jobs/job680_slambias.py`(수정판만 남음) · `jobs/job683_slambias_rev.sh` · `outputs/j683_slambias_rev.txt`(수정 뒤 실행분). 첫 시도의 출력은 원천 소실 |

### 5.2 루프 창 축소를 '대책' 으로 믿음(09-30 §14 → §16) — 칸 형식
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 17:10 오정합(4.2 m 평행 이동) 재발 방지 — 한 개만 바꿔 효과를 분리: `loop_search_space_dimension` 8 → 3(`job715_slamcfg_deploy.sh`) |
| 본 것 | 2 차 매핑(창 3 m)에서 17:36:18 한 번의 최적화로 map→odom 1.67 m · +33.2°(`j718_map2_break.txt`) |
| 처음 추론 | 정상 보정은 추측항법 오차 규모(180° 당 10~27 cm · 직진 ≤ 1.5 cm)라 ±1.5 m 창이면 정상은 담고 수 m 오정합은 창 밖이 된다 |
| 의심한 이유 | 위치 차는 1.67 m 로 창 경계와 비슷했지만 **각도 33°** 는 창이 다루지 않는 축 — 11 분에 11° 흐른 추측항법을 한 번에 33° 고친 것 |
| 판별 시험 | bag 의 map→odom 시계열 · Ceres 시각 · 휠ω−자이로ω 차(job718_ana) — 입력 이상 없음(EKF 미달 2 · 휠−자이로 ≤ 0.03 rad/s) |
| 결론 | 창은 **위치** 창일 뿐이고 각도 탐색(±20°)과 그래프 전체 최적화가 합쳐지면 창보다 큰 보정이 나온다. 축소만으로는 불충분 — 4.2 m 건을 막았는지도 재현 시험이 없어 미확인 |
| 다음에 알아보는 법 | 설정 하나로 '막았다' 고 하기 전에 **실패를 담은 bag 을 그 설정으로 재생해 재현이 사라지는지** 본다. 09-30 §13 은 bag 이 없어 이 판별이 불가능했다 → 그래서 §14 에서 bag 자동 기록을 넣었다. 오정합 서명 = '추측항법 누적 각도보다 큰 한 번의 각도 보정' |
| 데이터 | `jobs/job715_slamcfg_deploy.sh` · `jobs/job718_ana.py` · `outputs/j718_map2_break.txt` · 원천 bag Jetson `~/bags/map_0930_1724`(PC 사본 미확인) · §13 은 원천 없음(bag 안 뜸) |

### 5.3 재생기가 5 분 넘게 무출력 — 원인 확인 전에 중단(09-30 §17 → 10-01 §1) — 칸 형식
| 칸 | 내용 |
|---|---|
| 하려 한 것 | bag +699 s 까지 재생해 후보 지도 — `job719_cut.sh` → `job719_cutreplay.py` |
| 본 것 | 5 분 넘게 '재생: 앞 …' 줄이 안 나옴, 사용자 요청으로 중단(`job720`), 후보 파일 없음 |
| 처음 추론 | bag 읽기가 느림 — 700 s 분량 /tf 39 k · 스캔 7.8 k 역직렬화(**추정**) |
| 의심한 이유 | 파이썬 쪽 `print(..., flush=True)` 인데도 안 보임 — 출력이 화면까지 오는 길(`| grep -av "^\["`)이 남음 |
| 판별 시험 | 10-01 판: `python3 -u` + `grep --line-buffered` 로 바꿔 재실행 → 정상 진행 · 완주(`j719b`) |
| 결론 | 화면 무출력의 주원인은 grep 이 파이프에서 출력을 모아 둔 것으로 **추정**(바꾼 뒤 됐다는 것까지 확인, 읽기 시간 자체는 안 잼). 같은 날 §11.1 의 prep 'Terminated' 도 출력을 grep 으로 걸러 원인을 가린 같은 형태 |
| 다음에 알아보는 법 | 오래 도는 Jetson 작업을 grep 으로 거를 땐 `--line-buffered`, 파이썬은 `-u`. 거른 출력이 원인을 가릴 수 있으면 원문을 파일로 남기고(`tee`) 거른 것은 화면용으로만 |
| 데이터 | `2026-09-30/jobs/job719_cut.sh` vs `2026-10-01/jobs/job719_cut.sh`(diff: `--line-buffered` · `-u` · bag 경로) · `2026-10-01/outputs/j719b_cutreplay.txt` · 09-30 무출력 원문 없음 |

### 5.4 그 밖(한 줄)
- `job696_bridge_map.sh` 출력의 'topic_whitelist:' 라벨 줄이 실제로는 `max_qos_depth` 를 찍는다(바로 다음 줄이 진짜 whitelist) — 출력 원문은 남지 않아 화면 해석에 영향이 있었는지는 미확인.
- F1-0 '끊김 시험' 기록 도구(`job690`)가 전진 유지 · 전원 끔을 못 잡았다(30 칸 전부 axis1 ≈ 0) — 합격은 사용자 관찰. 사람이 하는 동작에 맞춰 1 s 칸으로 30 s 만 녹화한 설계라 시점이 어긋나면 비는 구조. **다음에 알아보는 법**: 사람 동작 판정은 '시작 신호 → 기록' 순서로 하거나 축 값이 0 이 아닌 구간을 자동으로 찾게 한다.

## 6. 남은 것 (10-01 시점)
- 복귀 앞뒤 잔차 ≈ 3.6 cm 의 원인(회전 중 SLAM 오차 vs 측정 기준) — 제자리 180° → 줄자 시험 미실시.
- 이어 그리기 오정합의 근본 대책 — 17:36:18 오정합을 재생으로 재현한 뒤 응답 문턱 상향 · 각도 창 축소 · 루프 클로저 끔 A/B(09-30 §17 계획, 판정 = 그 시점 점프 ≤ 0.5 m · 5° 이면서 17:31 정상 루프 클로저 유지) — 이 범위에서 안 함.
- mapping 모드 구조(새 스캔이 옛 지도에 직접 묶이지 않음)에서 '검증된 지도 + 새 구역' 을 붙이는 정석(평생 매핑 · 부분 노드 삭제 등) — 미검토.
- 금지 구역 마스크(W3 전선) — 사용자 결정으로 사무실 전체 매핑 뒤.
- 필름 없는 유리(출입문 · 창문) — 사용자가 알려 주기로, 미측정.
- 매핑 중 stuck_monitor 발동(§13 회전 중 3 회, §16 직진 5 회 — 지령 16 cm 대 관측 2~3 cm) — bag 확인 보류([정체 감시 카드](stuck-monitor.md)).
- prep 'Terminated'(job707 → job657 경로, §11.1) 원인 미확정.
- 재생 직후 `save_map` 255(sim time 에서 map_saver 가 2 s 안에 /map 을 못 받음 — **추정**) — job722 우회만.

이후(10-01 §8 ~): 다음 시기에서 채움(F2 쪽은 [f2-patrol-loc-jump.md](f2-patrol-loc-jump.md)) — F2 첫 순회 f2a1 ~ f2a12(10-01 §8), §8.41 위치 추정 점프 → §8.42 사용자 가설 '지도 구멍' → 10-02 bag 으로 보완한 **office_v3**(지금 운용 지도), 전역 정적 층 = 저장 지도(`map_server → /map_nav`, 10-01 §8.33).

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| SLAM 치우침 1 · 2 회차 | 0.70 m 전진 · 후진 vs 줄자 | 09-30 §3, `outputs/j682` · `j683` |
| F1-0 · F1-1 · F1-2 · F1-3 · F1-5 | 무선 끊김 · 루프 닫힘 · 이중 벽 · 복원 · 줄자 3 구간 · 유리 | 09-30 §4 ~ §4.4 · §8 · §10, 10-01 §6 |
| office_v1 | 1 차 매핑 저장(09-30 11:42) | Jetson `~/maps/office/office_v1.*`, 저장소 `Docs/04_navigation/maps/office_v1.{pgm,yaml}` |
| 이어 그리기 1 차(16:59~17:12) | 4.2 m 오정합, 저장 안 함, bag 없음 | 09-30 §11 ~ §14, `outputs/j705` · `j706` · `j713` · `j714` |
| 이어 그리기 2 차 `map_0930_1724` | 1.67 m · 33° 오정합, 저장 안 함, bag 780 s | 09-30 §16, `outputs/j717` · `j718`, bag Jetson `~/bags/` |
| `cand_0930_cut699` · `_nolc` · `_nolc_s` · `cand_0930_cut590_nolc` | 재생 후보 4 개(켬 · 끔 · 끔+격자 편집 · 590 컷 끔) | 10-01 §1 ~ §4, Jetson `~/maps/office/`, 그림 `Docs/04_navigation/figures/2026-10-01_cand_*` |
| office_v2 | = cut590_nolc | 10-01 §5, 저장소 `Docs/04_navigation/maps/office_v2.{pgm,yaml}` |
| F1-4a slamloc · amcl | 정지 기동 비교 | 10-01 §7.1, `outputs/j730_f14a.txt` |
| 위치 추정 재생 base · t2 · t2nolc · t3 · t3m | 노드 간격 · 지도 다시 그리기 A/B | 10-01 §9, `outputs/j736*` |

## 8. 도구 해설
공통: 09-30 · 10-01 의 Jetson 도구는 PC 에서 WSL → ssh(비밀번호 `<PW>`)로 `/tmp` 에 올려 부른다. 출력 첫 줄의 깨진 `wsl:` 경고는 WSL localhostForwarding 안내문(한글 코드페이지). DDS 는 `fastdds_udp_only.xml`. prep 은 09-29 의 `job657_prep_f0b.sh`(→ `job240_clean.sh` 를 부르는 래퍼)를 그대로 썼고, 매핑 전용 모드부터는 job240 을 직접 불렀다. 10-01 의 지도 비교 도구(`render_cand.py` 계열)는 **PC** 에서 PC 사본 pgm/yaml(스크래치패드 `cut/`)로 실행 — 스크래치패드는 자동 삭제되므로 후보 pgm 원본은 Jetson `~/maps/office/` 에만 남는다.

**도구 계보**
- SLAM 치우침: `job680_slambias.py`(전진 · 후진 공용, 09-30 에 `abs(V)` 수정) ← `job682`(prep + 확인 + 0.70 m) · `job683`(후진 −0.06). 오른쪽 앞 모서리 예측은 `job692_posenow.py` 와 같은 식.
- 지도 저장 · 복원: `job684_map_save.sh`(serialize + save_map) ← `job693`(자세 + 저장 + 로그 통계). 복원 확인 `job697_restore_chk.py` ← `job698`(office_v1) · `job704`(재정렬 + 조종) · `job707` · `job710`(매핑 모드) · 10-01 `job727`(office_v2) · `job730`(F1-4a, 원점 확인만 재사용). 10-01 판 `job697` 은 /map 기준 문구에 office_v2 크기를 더함.
- prep: `job657_prep_f0b.sh`(09-29) → `job240_clean.sh`(09-30: `SLAM_ARGS` · `SENSORS_ARGS` · `MAPPING=1` · 매핑 bag · `LOCALIZER=slam|amcl`(10-01)) → 10-01 `job726_prep_map.sh`(MAP · MAPPING · LOC 로 감쌈) → 뒤에 `Docs/tools/prep_fast.sh`(위치 추정 전용, 매핑 모드 없음).
- 부하 · 점프 진단: `job694_lagchk.sh`(로그 누계 + top 3 회) → `job695_loadab.sh`(30 s 차분 A/B, 클라이언트 수) → `job705_jumpchk.sh`(메모리 · TF 지연) · `job706_cputop.sh`(top 5 회 평균) → `job711_rotchk.py`(회전 중 TF · 입력) → `job713_jump2.sh` · `job714_jump2b.sh`(사후 · Ceres 시각) → `job718_ana.py`(bag 시계열 — bag 이 생긴 뒤의 정식판).
- 재생: `job719_cut.sh` + `job719_cutreplay.py`(09-30, 08 월 `job580` 재생기 기반) → 10-01 판(변형 `nolc` · `--line-buffered`) → `job722_cand_grid.sh`(격자 다시 만들기) → `run_x724.sh`(719 + 722 묶음, 스크래치패드 판 호출) → `job736_locreplay.*`(같은 재생 틀을 위치 추정 노드 · 지연 지표로) → 10-27 `Docs/tools/run_slam_replay.sh`(고정 도구).
- 지도 비교(PC): `render_cand.py`(두 격자를 월드 좌표에 놓는 공통부 + 3 칸 그림) ← `zoom_cand.py` · `shift_cand.py` · `wall_cand.py` · `southwall.py` · `straight.py` · `edit_south.py` 가 `exec(…split('def panel')[0])` 로 공통부를 가져다 씀.

### job680_slambias.py — SLAM 앞뒤 치우침 시험 (Jetson, rclpy)
- 부른 형태: `python3 /tmp/job680_slambias.py 0.70`(전진 0.07 m/s 기본) · `… 0.70 -0.06`(후진). 래퍼 `job682_slambias_run.sh`(prep + `ros2 param get … footprint` + stuck 모드 확인) · `job683_slambias_rev.sh`.
- 왜: 복귀 앞뒤 편차 3.6 cm 가 SLAM 직선 이동의 고정 치우침인지(09-30 §3). 손으로 들어 옮기면 오도메트리 없이 순간 이동이라 정합이 오염될 수 있어 **로버가 직접 직진**.
- 하는 일: 3 s TF 대기 → 정지 5 s 동안 `map→base_link` 평균(각도는 sin · cos 평균) = P0, odom 1 s 평균 → `/cmd_vel` 에 V 를 20 Hz 로 내며 odom 이동 거리 ≥ DIST − 0.005 또는 시간 한도 `DIST/|V|×2+5` 까지 → 0 지령 20 회 → 6 s 정착 → 다시 5 s 평균 P1. 출발 방향 기준 세로 = cos·dx + sin·dy, 가로 = −sin·dx + cos·dy. 오른쪽 앞 모서리 = base_link (+0.262, −0.165) 를 P0 · P1 로 옮겨 차이 = 줄자 예측.
- 출력: '출발 map (…) [표본 수]', '주행 s · EKF 이동', 'SLAM 이동 세로 · 가로 · 방향', 'EKF 이동 (SLAM 대비)', '줄자 예측 세로 · 가로'. 원문 `outputs/j682_slambias.txt`(1 회차) · `j683_slambias_rev.txt`(2 회차).
- 쓰인 곳: §3.1 · §3.2 S-a 판정.
- 결함: 시간 한도 부호(§5.1, 수정됨). 정착 6 s 는 고정값(SLAM 이 그 안에 정합한다는 가정).
- 다시 쓸 수 있음 — 출발 테이프 기준 직선 이동 정확도 시험 틀. 모서리 좌표는 footprint 가 바뀌면 고쳐야 한다.

### job684_map_save.sh · job693_f1_save.sh · job692_posenow.py — 지도 저장 (Jetson)
- 부른 형태: `bash /tmp/job684_map_save.sh <이름>`. `job693` = `job692`(지금 자세) → `job684 office_v1` → slam.log 의 'Adding node' · 'closure' 줄 수.
- 왜: 이어 그리기에는 포즈 그래프(.posegraph · .data), Nav2 · 편집에는 격자(.pgm · .yaml)가 필요(§4).
- 하는 일: `~/maps/office/<이름>.posegraph` 가 이미 있으면 중단(덮어쓰기 방지) → `/slam_toolbox/serialize_map {filename}` → `/slam_toolbox/save_map {name}`(각 60 s 한도) → `ls -la` · yaml 의 resolution · origin. `job692` 는 2 s 버린 뒤 5 s `map→base_link` 평균으로 오른쪽 앞 모서리의 출발 표시 대비 세로 · 가로.
- 출력: `outputs/j693_f1_save.txt`(자세 · 모서리 · 파일 크기 · '루프 폐합 로그 0 건').
- 쓰인 곳: §4.2 · §4.3(F1-1a 의 SLAM 쪽 값).
- 결함: 'Adding node' · 'closure' 줄 수는 slam 로그 수준이 낮아 늘 0 — 루프 폐합 여부 판단에 못 씀(SUMMARY 도 그렇게 적음).
- 다시 쓸 수 있음. 덮어쓰기 방지 덕에 이름만 바꿔 쓰면 된다.

### job685_f1_teleop.sh · job687_f1_prep.sh · job690_joydrop.py — 패드 조종 · 무선 끊김 시험 (Jetson)
- `job685`: joy_linux · teleop 정리 → `ros2 launch rover_bringup joy_teleop.launch.py profile:=mapping`(setsid · nohup) → 6 s 뒤 `/joy` hz · `scale_linear.x` · `scale_angular.yaw` · `require_enable_button` 확인. 매핑 prep 이 joy 노드를 정리하므로 prep 뒤마다 다시 부름(`job704` · `job707` · `job710` · `job717` · `job726 MAPPING=1`).
- `job687`: prep(새 지도) → `/proc/bus/input/devices` 의 패드 이름 → 끊김 시험용으로 teleop 출력을 `/cmd_vel_test` 로 리매핑(로버 비구동).
- `job690`(← `job691`): 30 s 동안 `/joy` 와 `/cmd_vel_test` 를 받아 1 s 칸마다 `/joy` 수 · axis1 평균 · cmd 수 · vx 평균, `/joy` 0.5 s 넘는 공백 구간 동안의 0 아닌 cmd 수. 출력 `outputs/j691_joydrop.txt`(869 · 866 개, 공백 없음, axis1 전부 ≈ 0 — 동작이 녹화 창과 어긋남).
- 쓰인 곳: §4.1 F1-0(합격은 사용자 관찰), §4.2 이후 매핑 조종.
- 다시 쓸 수 있음(`job685`). 끊김 시험은 §5.4 의 설계 결함이 있다. 프로필 값 변경은 [조이스틱 카드](joystick-teleop.md).

### job689_nav2_startup.sh — Nav2 lifecycle STARTUP 재전송 (Jetson)
- `ros2 service call /lifecycle_manager_navigation/manage_nodes … "{command: 0}"`(90 s 한도) → 4 노드 `ros2 lifecycle get`. 출력 원문 없음(SUMMARY §4.1 '4 노드 active').
- 왜: 첫 기동이 `behavior_server get_state` 서비스 실패로 전체 중단. prep 에 'active 아니면 STARTUP 재시도' 를 넣을 후보로 적었으나 미적용.

### job697_restore_chk.py — 복원 확인 (Jetson, rclpy)
- 부른 형태: 인자 없음. `job698`(office_v1 prep 뒤) · `job704` · `job707` · `job710` · `job727` · `job730`.
- 왜: F1-2 판정(첫 안정값이 원점에서 ≤ 5 cm · 5 s 안 연속 변화 ≤ 1 cm).
- 하는 일: `/map` 을 TRANSIENT_LOCAL · RELIABLE 로 1 개 받아 폭 · 높이 · 해상도 · 원점, 16 s 동안 1 s 마다 `map→base_link`(없으면 nan) → 원점 거리, 마지막 5 표본의 최대 쌍 거리 = 흔들림.
- 출력: '/map W×H … 저장본 …', 초별 자세 · 원점 거리, '마지막 5 표본 흔들림 · 원점 거리'. 원문 `2026-09-30/outputs/j698_f1_restore.txt` · `j704_f1v2_prep.txt` · `j710_mapmode_teleop.txt`, `2026-10-01/outputs/j727_f12_v2.txt` · `j730_f14a.txt`.
- 결함: 원점 = 출발 테이프라는 약속에 기댄다(테이프 정렬 오차는 따로 줄자). AMCL 처럼 움직이기 전엔 입력값을 그대로 내는 방식이면 0.00 이 나와도 정합 품질이 아니다(10-01 §7.1).
- 다시 쓸 수 있음 — 저장 지도 기동 직후 점검. 지금 prep 은 `chk_prep.py` 계열이 대신한다(다음 시기).

### job703_map_spans.py — 저장 지도 구간 길이 (PC 또는 Jetson, numpy · PIL)
- 부른 형태: `python3 job703_map_spans.py office_v1.pgm office_v1.yaml`. 실행 위치는 기록 없음(pgm 경로만 받음 — **추정** PC).
- 왜: F1-3 줄자 3 구간의 지도 쪽 예측(§8).
- 하는 일: 점유 = 픽셀 < 50, 빈 = > 250. 한 점에서 한 방향으로 해상도/4(1.25 cm) 걸음으로 빈 셀을 따라가 점유 셀을 만나면 거리, 미지 셀이면 None. 방 폭 = x −0.5 · 0 · 0.5 · 1.0 에서 남북 양쪽 합, 문 폭 = (2.25, y −0.60 · −0.65 · −0.70) 동서 합, 벽 두께 = x 2.0 에서 동쪽으로 첫 점유 띠 길이(y 0 · 0.5 · 1.0 · 2.0).
- 출력: 화면 줄. **원문 파일 없음**(SUMMARY §8 표만).
- 결함: 측정점 좌표가 코드에 박혀 있다(office_v1 · 출발 방 전용). 10-01 `wall_cand.py` 는 다른 방식(빈 → 점유 → 빈 사이 점유 폭 · 최장 빈 구간)이라 같은 office_v1 방 폭이 1.96(job703) vs 1.95(wall_cand)로 1 cm 다르다.
- 다시 쓸 수 있음(좌표만 바꿔).

### job694_lagchk.sh · job695_loadab.sh · job696_bridge_map.sh — 부하 · 브리지 (Jetson)
- 해설은 [Foxglove 카드 §8](foxglove-snap-cpu.md)(09-30 절). 여기선 결과만: §5 의 A/B 와 §11.1 의 매핑 모드 30 s(같은 `job695`, 라벨 `mapping_mode` · `mapping_mode2`)가 같은 도구라 수치가 서로 비교된다.

### job705_jumpchk.sh · job706_cputop.sh — 메모리 · 부하 · TF 지연 (Jetson)
- 부른 형태: 인자 없음, 이어 그리기 중 '점프' 직후(§11).
- 하는 일(`job705`): `free -m` · 스왑, RSS 상위 8(`ps --sort=-rss`), loadavg, sensors.log 의 'Failed to meet update rate' · slam.log 의 'Message Filter dropping' 누계 → `tf2_monitor odom base_link` · `map odom` 각 12 s → 그 24 s 동안 두 누계의 차, 브리지 클라이언트 수(`ss :8765`). `job706`: `top -b -n1` 5 회(1 s 간격)의 이름별 %CPU 평균(> 3 %), 합계, loadavg.
- 출력: `outputs/j705_jumpchk.txt` · `j706_cputop.txt`. 스캔 버림 사유는 원문에 'discarding message because the queue is full'.
- 결함: `top` 이름 15 자 잘림(`async_slam_tool` 등), Python 노드는 전부 `python3`. `job706` 의 '합계(>3%만)' 는 실제로는 모든 프로세스 합(awk 가 거르지 않음).
- 다시 쓸 수 있음 — 지금은 `Docs/tools/anal_top.py` · `anal_proc_cpu.py`(10-12)가 대신.

### job707 · job709 · job710 — 매핑 전용 모드 검증 (Jetson)
- `job707`: `MAPPING=1 SLAM_ARGS=office_v1 SENSORS_ARGS=viz:=map bash /tmp/job657_prep_f0b.sh | grep …` → `job697` → `job685` → `job695 mapping_mode`. ≈ 80 s 에 'Terminated' 로 스택 전부 내려감(원인 미확정, grep 이 prep 출력을 가림). 원문 `outputs/j707_mapmode_prep.txt`.
- `job709`: 같은 인자로 `job240_clean.sh 15` 를 **직접**, 출력 70 줄 + 끝난 뒤 프로세스 수. 정상. 원문 `outputs/j709_mapmode_prep_full.txt`.
- `job710`: 조종 재기동 → `job697` → `job695 mapping_mode2`(부하 2.72 · EKF 미달 0). 원문 `outputs/j710_mapmode_teleop.txt`.

### job240_clean.sh(09-30 판) — prep 본체 (Jetson)
- 부른 형태: `[MAPPING=1] [SLAM_ARGS=…] [SENSORS_ARGS=…] [LOCALIZER=slam|amcl] bash /tmp/job240_clean.sh 15`.
- 하는 일(이 카드 관련): 정리 목록(joy · teleop · Nav2 · SLAM · 센서 · 브리지 등 `PATS`)을 내림 → 센서 launch(`SENSORS_ARGS`) → SLAM launch(`SLAM_ARGS`, 비우면 새 지도) → `MAPPING=1` 이면 Nav2 · nvblox 대신 stuck_monitor 단독(`shadow_mode:=${STUCK_SHADOW:-true}`) + `ros2 bag record -o /tmp/bags/map_<월일_시분>` 8 토픽, 아니면 `navigation.launch.py` 와 4 노드 상태 확인. 다음 prep 시작 때 `pkill -INT "ros2 bag record"` 로 bag 을 닫는다.
- 쓰인 곳: §11.1 · §14 · §16 · 10-01 전부.
- 결함: bag 이 `/tmp` 라 재부팅에 사라진다(09-30 §17 에서 `~/bags` 로 손 복사).
- 계보 · 지금: 날짜 폴더마다 사본(09-30 · 10-01 jobs/)이 있다. 고정 도구 `Docs/tools/prep_fast.sh` 에는 매핑 모드가 없다.

### job711_rotchk.py · job712_rotchk_run.sh — 회전 중 TF · 입력 (Jetson, rclpy)
- 하는 일: 15 s 동안 1 s 마다 `odom→base_link` · `map→odom` · `map→base_link` yaw(도), `/wheel_odom` · `/wheel_odom/conditioned` · `/odometry/filtered` 의 angular.z 와 `/imu/data` 의 −angular_velocity.y(카메라 IMU 축 → 차체 yaw), 각 토픽 1 s 수신 수. 판정 규칙(독스트링): 돌리는데 odom yaw 가 안 변하면 EKF(입력 끊김), odom 은 변하는데 map 이 늦으면 TF/SLAM.
- 출력: `outputs/j712_rotchk.txt`(첫 1 s 는 휠 0 개 · TF nan — 구독 시작 직후).
- 쓰인 곳: §12 '로버 쪽 TF 정상'.
- 결함: 받는 쪽은 Jetson 안 노드라 **Foxglove 가 받은 /tf** 는 재지 않는다(브리지 기전은 추정으로 남음).
- 다시 쓸 수 있음 — '표시가 이상할 때 로버 쪽부터' 점검.

### job713_jump2.sh · job714_jump2b.sh — 점프 사후 조사 (Jetson)
- `job713`: 인라인 파이썬으로 `map→odom` · `odom→base_link` · `map→base_link` 3 회(1 s), slam.log 의 warn · error · loop · clos · jump · fail · drop · reject 줄 마지막 40 + 끝 15 줄, sensors.log EKF 미달 · ZUPT · 경고, nav2.log 끝 20 줄(stuck), load · 메모리 · 프로세스 생존 · CPU 상위. 출력 `outputs/j713_jump2.txt`.
- `job714`: slam.log 의 `preprocessor.cc` 줄(Ceres 의 'num_threads 50 exceeds … 6' 경고) 시각 = **최적화 실행 흔적**, 스캔 버림 누계, `/imu/data` · `/scan` · `/odometry/filtered` hz. 출력 `outputs/j714_jump2b.txt`(16:59:10 · 17:10:34, 버림 73, 199.678 · 10.041 · 30.002 Hz).
- 결함: 'Ceres 경고 = 루프 클로저 최적화' 는 대응 관계를 **추정**한 것(지도 불러올 때도 1 회 찍힘). slam.log 첫 줄 시각 추출은 빈 값(정규식 불일치).
- 계보: 이 'preprocessor.cc 시각' 지표를 `job718_map2_break.sh` · `job719_cut.sh`(재생 SLAM)도 그대로 쓴다.

### job715_slamcfg_deploy.sh — slam.yaml 배포 (Jetson)
- `/tmp/slam.yaml` 을 src · install 양쪽에 복사, 배포본의 `loop_search_space_dimension` 줄, yaml 파싱 확인, `bash -n job240`. 지금 SLAM 은 안 건드림(다음 prep 부터). 출력 원문 없음.

### job717_map2_prep.sh — 2 차 매핑 prep (Jetson)
- 배포된 루프 창 확인 → `MAPPING=1 SLAM_ARGS=office_v1 SENSORS_ARGS=viz:=map job240_clean.sh 15` → `job685` → 프로세스 수(bag 기록기 포함) → 최신 bag 경로. 출력 `outputs/j717_map2_prep.txt`.

### job718_map2_break.sh · job718_ana.py — 매핑 bag 오정합 분석 (Jetson, rosbag2_py)
- 부른 형태: `bash /tmp/job718_map2_break.sh`(bag 을 SIGINT 로 닫고 `ros2 bag info` · Ceres 시각 · 버림 · stuck 줄 → `python3 job718_ana.py <bag>`).
- 왜: §13 은 bag 이 없어 순간을 못 봤다 — 2 차 매핑의 '깨짐' 을 시계열로.
- 하는 일(`job718_ana`): bag 전체를 읽어 `/tf` 의 map→odom · odom→base_link, `/wheel_odom`(vx · ω), `/imu/data`(−ω_y), `/scan` 시각. map→odom 은 **같은 stamp 를 두 번 발행하므로 시각 중복을 지우고 마지막 값**. 연속 표본 변화 > 5 cm 또는 > 2° = 점프 → 각 점프 직전 3 s 의 휠 v · ω · 자이로 ω 최대와 그때 odom 자세. 10 s 칸 요약(map→odom · odom · 속도 최대 · 휠ω − 자이로ω 평균차).
- 출력: `outputs/j718_map2_break.txt`(map→odom 15,609 · odom 23,411 · 휠 19,504 · 자이로 155,771 · scan 7,809, 780 s, 점프 19 건 — 17:36:18 이전 11 건).
- 쓰인 곳: §16 오정합 판정 · 10-01 §4 컷 지점(+590 s) 선택.
- 다시 쓸 수 있음 — 매핑 bag 의 SLAM 보정 점프 찾기. 지금은 `Docs/tools/` 에 같은 기능의 고정 도구가 없다.

### job719_cut.sh · job719_cutreplay.py — 오정합 전까지 재생해 지도 되살리기 (Jetson, rosbag2_py + rclpy)
- 부른 형태: 09-30 판 `bash /tmp/job719_cut.sh [CUT=699]` · 10-01 판 `bash /tmp/job719_cut.sh <CUT> [nolc]`(출력 `cand_0930_cut<CUT>[_nolc]`).
- 왜: 라이브 그래프에는 오정합이 이미 들어가 되돌릴 수 없다(slam_toolbox 에 노드 삭제 · 되감기 서비스 없음) → 기록된 입력으로 그 전까지만 다시 만들기(09-30 §17).
- 하는 일(`job719_cut.sh`): (09-30) bag 을 `~/bags` 로 복사 · 라이브 bag 기록기와 깨진 SLAM 정지(센서 · EKF · 에이전트 유지) → `ROS_DOMAIN_ID=42` 에서 `async_slam_toolbox_node`(현 slam.yaml, `use_sim_time:=true`, `map_file_name:=office_v1`, 시작 (0,0,0), `$SLAM_EXTRA` = nolc 이면 `do_loop_closing:=false`) → 재생기 → 'preprocessor.cc' 줄 수(Ceres 흔적) → 노드 종료 → 파일 목록 · PNG 변환.
- 하는 일(`job719_cutreplay.py`): bag 을 CUT 초까지 읽어 `/scan` · `/tf`(**map→odom 은 뺌**) · `/tf_static` 만 메모리에 → 정적 TF 를 TRANSIENT_LOCAL 로 먼저 → bag 시각 그대로 1 배속 재생, `/clock` 은 5 ms 넘게 지날 때마다 → 재생 SLAM 이 낸 map→odom 을 받아 > 5 cm · > 2° 점프 목록 · CUT 시점 값 → 시계를 5 s 더 흘린 뒤 `serialize_map` · `save_map` 을 부르는 동안에도 시계 유지(0.2 s 단위).
- 출력: `2026-10-01/outputs/j719b_cutreplay.txt`(699 켬) · `j723_nolc.txt`(699 끔) · `j724_cut590_nolc.txt`(590 끔). 09-30 실행은 출력 없이 중단(§5.3).
- 쓰인 곳: 10-01 §1.1 R1 · §2.1 · §4.
- 결함: 재생 직후 `save_map` 이 255(699 켬 · 590 끔; 699 끔은 0) — map_saver 가 sim time 에서 /map 을 2 초 안에 못 받는 것으로 **추정**, job722 로 우회. 재생은 1 배속이라 bag 길이만큼 걸린다. 처리 순서 · 타이밍이 라이브와 같다는 보장은 없어 R1 대조가 필요하다(이번엔 4.4 cm · 0.2°).
- 계보: 08 월 `job580` 재생기 → 이것 → `job736_locreplay.*` → `Docs/tools/run_slam_replay.sh`.
- 다시 쓸 수 있음 — 매핑 bag 이 있으면 '구간 빼고 다시 그리기' 의 표준 경로.

### job720_stop_replay.sh — 재생 중단 (Jetson)
- job719 프로세스 · 도메인 42 재생 SLAM 종료, 남은 프로세스 수 · 후보 파일 유무 · bag 크기. 출력 원문 없음(SUMMARY '후보 지도 파일 없음, 재생 프로세스 0').

### job722_cand_grid.sh — 후보 포즈 그래프에서 격자 만들기 (Jetson)
- 부른 형태: `bash /tmp/job722_cand_grid.sh <이름>`(기본 `cand_0930_cut699`).
- 하는 일: 도메인 42 · **벽시계**로 slam_toolbox 가 그래프만 불러오게(`map_file_name`) → `/map_metadata` 가 나올 때까지(최대 80 s) → `nav2_map_server map_saver_cli -f … map_subscribe_transient_local:=true`(40 s) → 노드 종료 → yaml 출력 · PNG.
- 출력: `2026-10-01/outputs/j722_cand_grid.txt`(332 × 227, 원점 (−5.30, −6.96)).
- 다시 쓸 수 있음 — 포즈 그래프만 있고 격자가 없을 때.

### render_cand.py 계열 — 두 격자 겹쳐 보기 · 수치 비교 (PC, numpy · PIL · matplotlib)
- 공통부(`render_cand.py` 의 `def panel` 앞): `office_v1` 과 `$CAND` 의 pgm/yaml 을 읽어 두 원점 · 크기를 감싸는 월드 격자(205 = 미지)에 각각 놓음(`GA` · `GB`). 그림 = 단독 2 칸 + 겹침 1 칸(v1 만 점유 파랑 · 후보만 주황 · 둘 다 검정).
- `zoom_cand.py`: 같은 겹침 확대 그림(`*_zoom.png`).
- `shift_cand.py`: 영역 4 곳(출발 방 · 동쪽 방 · 남쪽 책상 · 남동쪽, 좌표 박힘)마다 후보 점유를 ±6 칸(±0.30 m, 5 cm 단위) 평행 이동해 **겹침 = 공통 점유 / min(두 점유 수)** 가 최대인 이동. '그대로 겹침' 은 이동 0 의 값.
- `wall_cand.py`: y 0.5 · 1.0 · 2.0 에서 x 2.3~3.8 사이 첫 점유 ~ 마지막 점유 폭 = 벽 두께, x 0 · 0.5 에서 y −1.0~1.8 의 최장 빈 구간 = 방 폭.
- `southwall.py`: x 별로 y −0.6 부터 아래로 첫 점유(남쪽 벽 위치 차).
- `straight.py`: x −2~6 에서 열마다 y −5.9 아래 첫 점유 → 중앙값 ±0.4 m 밖 제외 → 직선 맞춤(기울기 · σ · 최대) + 2 m 구간 평균 y.
- `edit_south.py`: x ≥ 0 · x < v1 끝 · y ≤ −5.95 띠를 v1 셀로 바꿔 `cand_0930_cut699_nolc_s.{pgm,yaml}`.
- 출력: `outputs/j_cand_compare.txt`(shift + wall, 699 켬) · `j_nolc_compare.txt` · `j_straight.txt`, 그림 `Docs/04_navigation/figures/2026-10-01_cand_*`. `southwall.py` · `edit_south.py` · 590 후보의 비교 수치는 출력 원문 없음(SUMMARY 표만).
- 결함: 영역 · 측정 좌표가 박혀 있다(이 사무실 · 이 원점 전용). 겹침 지표는 점유 칸 일치만 보며 벽 두께 변화와 평행 이동을 구분하지 않는다. 스크래치패드의 `cut/` 에서 `../render_cand.py` 로 불렀다 — 저장소 사본은 경로가 맞지 않아 그대로는 안 돈다.
- 다시 쓸 수 있음(경로 · 좌표 수정 뒤) — 두 지도 버전 비교의 기본 틀.

### run_x724.sh — 590 컷 재생 + 격자 (PC → Jetson)
- 스크래치패드의 `run_x719.sh`(CUT719=590 · V719=nolc) · `run_x722.sh` 를 차례로 부르는 4 줄. 두 하위 스크립트(PC 쪽 전송 · 호출 래퍼)는 **원천 소실**(스크래치패드) — 내용은 `job719_cut.sh` · `job722` 호출로 **추정**. 출력 `outputs/j724_cut590_nolc.txt`.

### job725_save_v2.sh — office_v2 로 복사 (Jetson)
- 같은 이름 있으면 중단 → posegraph · data · pgm 복사, yaml 은 `image:` 줄만 바꿔 생성 → sha256 앞 16 자 대조 · 목록. 출력 `outputs/j725_save_v2.txt`. 다시 쓸 수 있음(이름만 바꿔).

### job726_prep_map.sh · job727_f12_v2.sh · job730_f14_deploy.sh — 저장 지도 prep · F1-2 · F1-4a (Jetson)
- `job726`: `MAP`(기본 office_v2) · `MAPPING` · `LOC=map|slamloc|amcl` → `LOCALIZER` · `SLAM_ARGS`(slamloc 이면 `slam_mode:=localization`, 뒤에 `NAV_ARGS=nav_map:=…yaml` 추가 — 10-01 §8.33) → job240 → (매핑이면 조종) → 위치 추정 로그 · 프로세스 수. 주석에 '이어 그리기 매핑이면 루프 클로저 끔 권장'.
- `job727`: `MAP=office_v2 MAPPING=0 job726` → slam.log 불러오기 줄 → `job697`. 출력 `outputs/j727_f12_v2.txt`.
- `job730`: `/tmp/f14/` 의 `slam.launch.py` · `localization.launch.py` · `navigation.launch.py` · `amcl.yaml` 배포 · 빌드 → `--show-args` 확인 → 후보마다 `job726` + `job697`(초별 줄 일부) + `ps` CPU. 출력 `outputs/j730_f14a.txt`.
- 결함: `ps -eo comm` 15 자 잘림으로 slamloc 노드(`localization_slam_toolbox_node`) CPU 를 못 잡음(§7.1). SUMMARY 의 slamloc yaw +0.30° 는 원문 +0.32°(같은 표본, 반올림 차로 보임).

### job736_locreplay.sh · job736_locreplay.py — 위치 추정 모드 부하 재생 A/B (Jetson)
- 부른 형태: `[END=560] [STOP_LIVE=1] bash /tmp/job736_locreplay.sh base t2` · `t3 t2nolc` · `t3m`.
- 왜: f2a1 에서 위치 추정 노드의 map→odom 이 늦어 컨트롤러 중단(10-01 §8.2) — 노드 자체 처리량인지 라이브 CPU 경쟁인지(§9).
- 하는 일(`.sh`): 라이브 Nav2 · SLAM · nvblox(컨테이너 안 `pkill nvblox_node`) · stuck · nav_guard 정지(센서 · EKF 유지) → 도메인 42 에서 변형마다 `localization_slam_toolbox_node`(office_v2, sim time, `mode:=localization`, 변형 인자: t2 = 0.20 m · 0.10 rad, t3 = 0.30 · 0.15, t2nolc = t2 + 루프 끔, t3m = t3 + `map_update_interval 10`) → pid 를 `SLAM_PID` 로 넘겨 재생기.
- 하는 일(`.py`): `map_0930_1724` 0~END s 를 `job719_cutreplay` 와 같은 방식(map→odom 뺌)으로, **10~250 s 정지 구간은 10 배속**. 250 s 이후 odom→base 를 낼 때마다 (그 stamp − 그때까지 받은 map→odom 최신 stamp) = 결손, map→odom 고유 stamp 간격, `/proc/<pid>/stat` utime+stime 차 / 벽시계 = 노드 CPU.
- 출력: `outputs/j736_locreplay_base_t2.txt` · `j736b_locreplay_t3_t2nolc.txt` · `j736c_locreplay_t3m.txt`.
- 쓰인 곳: 10-01 §9.1 ~ §9.3 → `slam.launch.py` localization 기본값. 판정 표는 [SLAM 시각 정체 카드](slam-stamp-freeze.md).
- 결함: 라이브 Nav2 · nvblox 없이 재서 실주행보다 낙관적(SUMMARY 도 명시). 매핑 bag 을 위치 추정 입력으로 쓴 것이라 경로가 실제 순회와 다르다.
- 계보: `job719_cutreplay.py` → 이것 → 10-27 `Docs/tools/run_slam_replay.sh` · `slam_replay_feed.py`.

## 9. 용어
- **포즈 그래프 · serialize_map**: slam_toolbox 가 스캔마다 만든 '노드(자세 + 스캔)' 와 노드 사이 제약(스캔 정합 · 루프 클로저)의 그래프. `serialize_map` 은 이것을 .posegraph · .data 로 저장해 다음 세션에 불러와 이어 그리거나 위치 추정에 쓴다. 격자(.pgm)는 그래프에서 그려 낸 그림일 뿐이라 격자를 고쳐도 그래프는 안 바뀐다(10-01 §3).
- **이어 그리기(continuation)**: 저장한 그래프를 `map_file_name` · `map_start_pose` 로 불러와 mapping 모드로 계속 그리는 것. 이 카드의 관찰: 새 스캔은 최근 스캔 버퍼(20)에 맞고, 옛 지도와는 루프 클로저로만 묶인다(**추정**, 10-01 §2.2).
- **루프 클로저 · 오정합(false loop closure)**: 예전에 지나간 곳을 다시 봤다고 판단해 두 노드를 묶고 그래프 전체를 다시 최적화(Ceres)하는 것. 비슷한 구조(책상 · 칸막이 줄)에 잘못 묶이면 지도와 위치가 한꺼번에 틀어진다. 서명: 추측항법이 쌓은 오차보다 큰 한 번의 보정(4.2 m, 33°).
- **loop_search_space_dimension**: 루프 후보를 찾는 위치 창의 한 변 길이(m). 3.0 = 현재 추정 중심 ±1.5 m. 각도는 따로 `coarse_search_angle_offset`(0.349 rad ≈ ±20°)으로 찾는다.
- **mapping 모드 vs localization 모드**: mapping = 그래프에 노드를 계속 더하고 루프 클로저로 고침(지도가 바뀜). localization = 저장 그래프를 고정하고 최근 스캔으로만 위치를 맞춤(`localization_slam_toolbox_node`) — 장소 좌표를 세션마다 같게 유지하려는 선택(10-01 §7).
- **도메인 42 · sim time 재생**: `ROS_DOMAIN_ID=42` 로 라이브(도메인 0)와 섞이지 않게 하고, bag 의 시각을 `/clock` 으로 흘려 노드가 그 시각을 '지금' 으로 쓰게 하는 것. 기록 당시 SLAM 출력(map→odom)은 빼야 새 SLAM 의 결과를 볼 수 있다.
- **F1-1a ~ F1-5**: 이 단계의 판정 이름 — 1a 루프 닫힘(출발 테이프 복귀 ≤ 5 cm) · 1b 이중 벽 0 · 2 저장 · 복원(원점 ≤ 5 cm · 5 s) · 3 줄자 3 구간 ±5 cm · 4 위치 추정 방식 · 5 유리 기록 · 0 무선 끊김.
- **Costmap Filter 마스크(KeepoutFilter · SpeedFilter)**: 원본 지도는 그대로 두고 별도 마스크 지도로 금지 · 저속 구역을 Nav2 에 주는 방식(09-30 §1 권장, 아직 미적용).
