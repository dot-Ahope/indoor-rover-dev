# 카메라 상자 칸 과장의 근원 — 관측 오차 · 기억 밀림 · 칸 반올림 (8 기: 10-19 §0 ~ §14 · 10-20 §8 ~ §8.3)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **조사 중(10-20 시점) — 분해는 측정(주행 1 회 f2x1), 대책은 없음.** 출발점 낮은 시험 상자의 로버 쪽(북) 면이 nvblox 조각에서 실제보다 **+5.3 cm** 나와 있던 것(f2x1)을 원시 깊이 점으로 나눠 보니 = 관측 순간의 자세 오차(남동 3~5 cm) + **오도메트리 기억 밀림(북 = 로버 쪽 +2.7~+6.1 cm)** + **5 cm 칸 반올림(최대 +5 cm)**(10-19 §14). nvblox 설정(통합 거리 · site · 복셀 · 깊이 전처리) · 깊이 필터(가장자리 · 회전 프레임) · 지도 좌표 기억 · 깊이 해상도(데시메이션)는 어느 것도 과장을 줄이지 못함(10-19 §6 ~ §13 · 10-20 §8.3). ⚠ 판정 척도('가장 바깥 칸 가장자리')가 5 cm 계단이라 2~7 cm 차이는 못 가른다(10-19 §13) | 10-19 §0 ~ §14, 10-20 §8 ~ §8.3 (이 카드). 이후(10-21 ~): 복귀 상자 칸은 [복귀 길 상자 칸](box-return-cells.md), 오도메트리 대책은 cuVSLAM 쪽 | [10-19 §0](../debug_log/2026-10-19/SUMMARY.md)(사용자 "ClearanceBandCritic가 꼭 필요한가? 다른 스택이 하는 일을 중복하여 하게 되는거 아닌가" → "깊이 bag 기록 준비부터") · 앞 줄기 10-15 §29.4(주행 중 +5~10 cm, [상자 옆 정지 — 기전](box-side-stall-cause.md)) | 설정 변경 없음(모두 되돌림 · 재생만). 코드: `ros2_ws/src/rover_navigation/config/nvblox_local.yaml` 9~10 행 머리 주석 정정('깊이 이미지는 원해상도' → 160×120, 10-19 §1) · 러너 `job551_f0drive.sh` `BAG_DEPTH=1`(10-19 §3) · `rover_bringup/launch/camera.launch.py` `decimation:=` 인자(10-20 §8.2, 기본 4) | [상자 옆 정지 — 기전](box-side-stall-cause.md)(이 카드가 그 카드 §7 '과장 원인 미확정' 을 이어 받음) · [상자 옆 정지 — 대책](box-side-stall-remedies.md)(10-19 §0 크리틱 보류 · 통합 거리 · site 재검토) · [복귀 길 상자 칸](box-return-cells.md)(같은 기전의 복귀 길 · 10-22) · [깊이 점군 아티팩트 · depth_relay](depth-relay-artifacts.md)(09-14 '실루엣 비산점' — §7 · §8 의 가설 출처) · [회전 중 장애물 번짐](rotation-obstacle-smear.md)(odom 기억 번짐의 앞 모양) · [회전 미끄러짐 — rf2o 도입](rf2o-introduction.md)(기억 밀림의 근원 = 회전 중 EKF 미끄러짐) · [Phase N 후반 · 유령 셀](nvblox-n6-global-ghosts.md)(통합 거리 1.4 의 출처) · [유령 칸 · 깊이 프리셋 · 통합 거리 2.0](ghost-cells-depth-preset.md)(10-21 ~ 22, 다른 묶음) · [센서 데크 yaw](sensor-deck-yaw.md)(§9 가설 (b) 외부 보정) |

**한 줄**: 10-15 에 '주행 중 카메라 상자 칸이 실제 면보다 로버 쪽으로 +5~10 cm' 라는 것까지 쟀지만 원인을 못 갈랐다. 10-19 는 깊이 영상 · camera_info · tf 를 담은 bag(f2x1)을 기록하고 **컨테이너 nvblox 에 다시 넣어** 설정만 바꾼 A/B 를 했다(재생 = 실시간 확인, R0). 통합 거리 · site · 복셀 · 깊이 가장자리 거르기 · 회전 프레임 빼기 · map 좌표 기억 어느 것도 과장을 줄이지 못했고, 원시 깊이 점을 그 순간의 tf 로 지도에 옮겨 보니 **출발 정면 관측은 거의 맞고(북 +1.7 cm)**, 복귀 때 지도의 상자는 남동쪽에서 회전 중 본 것의 **odom 기억이 그 뒤 EKF 오차만큼 로버 쪽으로 밀린 것(+2.7~+6.1 cm)** 에 칸 반올림이 더해진 값이었다. 10-20 은 '깊이 해상도를 올리면 줄까' 를 데시메이션 ×4 · ×2 · ×1 정지 A/B 로 시험해 차이 < 1 cm(5 cm 칸의 1/7) → 해상도는 대책 아님. 남은 것은 오도메트리(→ cuVSLAM 융합) 쪽.

## 1. 증상
- 10-15 §29.4(앞 시기) — 기록 상자 대비 찍힌 북쪽 면 +8.2 · +9.6 · +6.1 · +5.3 cm(b910 4 주행, 로컬 코스트맵 기준). 정지 정면 · 옆면 관측(10-15 §22 ~ §24)은 0~3 cm 라 '움직이며 · 비스듬히 · 멀리서' 쪽으로만 좁혀져 있었다([기전 카드 §7](box-side-stall-cause.md)).
- 10-19 §4 — 같은 주행들의 **실시간 nvblox 조각**으로 다시 재니 같은 값 → 과장은 Nav2 코스트맵 단계가 아니라 **nvblox 출력에서 이미 있음**(측정). [`anal_slice_box_baseline.txt`](../debug_log/2026-10-19/outputs/anal_slice_box_baseline.txt):
  ```
  f2u1_실시간       상자 옆 조각 235 (칸 있음 235) · 북쪽 면 과장 중앙  +9.5 cm (범위 +8.7~+10.5) · 서쪽 면 과장 중앙  -1.1 cm · 칸 수 중앙 15
  f2u3_실시간       상자 옆 조각 252 (칸 있음 252) · 북쪽 면 과장 중앙  +6.1 cm (범위 +4.4~+7.5) · 서쪽 면 과장 중앙 +17.1 cm · 칸 수 중앙 9
  f2v4_실시간       상자 옆 조각 375 (칸 있음 375) · 북쪽 면 과장 중앙  +5.3 cm (범위 +3.5~+6.6) · 서쪽 면 과장 중앙  +2.9 cm · 칸 수 중앙 9
  ```
  (SUMMARY §4 의 f2w1 +8.2 는 이 파일에 없음 — §5 어긋남 1.)

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-19 §0 | 사용자 질문 'ClearanceBandCritic 이 다른 스택의 중복 아닌가' | 크리틱은 Humble MPPI 에 없는 '옆면 정확 거리' 벌점이라 완전 중복은 아님, 그러나 상자 옆 대응 층이 이미 여럿(CostCritic · PathBlockedAhead · MonotoneEscape · stuck_monitor · nav_guard)이고 증상 회피 | 크리틱 **보류(코드 유지 · 꺼 둠)**, 근본(과장)을 먼저 — 깊이 bag 을 nvblox 에 다시 넣는 오프라인 A/B 로 | SUMMARY §0(대화 판단, 원문 없음) → [대책 카드](box-side-stall-remedies.md) |
| 10-19 §1 | 깊이 토픽 실측(`chk_depth_topic.sh`) | camera_info **160×120** · 14.99 Hz · 581 KB/s — 데시메이션 ×4(09-08, 점군 CPU 용)가 깊이 이미지 자체에도 걸림 | `nvblox_local.yaml` 머리 주석 '깊이 이미지는 원해상도' 는 **틀림** → 주석 정정(값 그대로). 4×4 평균이 가장자리를 넓힐 수 있음(추정, 1.3 m 에서 화소당 1.2 cm — +5~10 cm 를 다 설명하긴 작음) | `jobs/chk_depth_topic.sh`(출력 **원문 없음** — SUMMARY 서술뿐) · 지금 주석 [`nvblox_local.yaml`](../../ros2_ws/src/rover_navigation/config/nvblox_local.yaml) 9~10 행 |
| 10-19 §2 | 재생 경로 `run_nvblox_replay.sh`(컨테이너에 두 번째 nvblox, 도메인 42, `bag play --clock`) | 정지 30 s bag: 깊이 콜백 15.2 Hz · 조각 270 / 29 s | 경로 동작 ✔, 충실도는 R0 로 | [`run_nvblox_replay.sh`](../debug_log/2026-10-19/jobs/run_nvblox_replay.sh)(출력 원문 없음) |
| 10-19 §3 | 러너에 `BAG_DEPTH=1`(깊이 · camera_info best effort, `~/bags/bag_<이름>` 사본) | — | — | [`job551_f0drive.sh`](../debug_log/2026-10-19/jobs/job551_f0drive.sh) · [`run_f0.sh`](../debug_log/2026-10-19/jobs/run_f0.sh)(비밀번호 가림 사본) |
| 10-19 §4 | 기존 주행 실시간 조각으로 과장(`anal_slice_box.py`) | +9.5 · +6.1 · +5.3(파일), SUMMARY 는 f2w1 +8.2 포함 4 개 | 과장은 **nvblox 조각에서 이미**(측정) | [`anal_slice_box_baseline.txt`](../debug_log/2026-10-19/outputs/anal_slice_box_baseline.txt) |
| 10-19 §5 선언 | 기록 주행 b910 1 회 + R0(실시간 vs 같은 설정 재생: 과장 중앙 차 ≤ 1 cm · 칸 수 중앙 차 ≤ 2) + A/B 판정(같은 bag 재생 기준보다 **3 cm 이상** 감소면 후보, 칸 수 중앙 < 3 또는 안쪽이면 불합격) | — | — | SUMMARY §5 |
| 10-19 §6 | f2x1(b910, `BAG_DEPTH=1`, GIT `aff3a47b`) · R0 · 설정 A/B 4 가지 | 3/3(52.8 · 48.0 · 102.6 s), 깊이 3159 장 14.96 Hz. 첫 R0 조각 2 배(주행 bag 의 실시간 조각까지 재생) → `--topics` 로 고침. **R0 +5.3 / +5.3 · 범위 같음 · 칸 6 / 6** ✔. 통합 1.0 · site 1.0 북 +5.3 그대로, 복셀 0.025 **+6.9**, 0.025 + 절단 4 vox +6.7 | 설정으로는 안 줄음 ✘ — 단 '효과 없음' 은 §13 에서 '5 cm 척도로 안 보임' 으로 다시 읽음 | [`run_f2x1.txt`](../debug_log/2026-10-19/outputs/run_f2x1.txt) · [`anal_slice_box_f2x1_ab.txt`](../debug_log/2026-10-19/outputs/anal_slice_box_f2x1_ab.txt) · [`chk_replay_params.sh`](../debug_log/2026-10-19/jobs/chk_replay_params.sh)(적용 확인, 출력 원문 없음) |
| 10-19 §7 | nvblox 깊이 전처리 `do_depth_preprocessing:=true` 재생 | 조각 1 · 2 개, `image_impl.h:248 Check failed: mask.rows() == image.rows() (0 vs. 120)` → abort | 3.2.5 에서 못 씀(소스 수정 필요) | [`chk_replay_log.sh`](../debug_log/2026-10-19/jobs/chk_replay_log.sh) · [`chk_nvblox_preproc.sh`](../debug_log/2026-10-19/jobs/chk_nvblox_preproc.sh)(로그 원문 없음 — SUMMARY 인용뿐) |
| 10-19 §8 | bag 단계 가장자리 화소 거르기(선언 규칙: 3×3 이웃과 차 > max(5 cm, 4 % × 깊이) 이면 0) | 유효 화소 **22.26 %** 제거 → 북 +5.3 · 범위 +1.3~+6.8 · 서 −0.2 · 칸 7 | 깊이 잡음 가설 ✘ | [`depth_edge_filter.py`](../debug_log/2026-10-19/jobs/depth_edge_filter.py)(22.26 % 출력 원문 없음) · `anal_slice_box_f2x1_ab.txt` '가장자리거름' 줄 |
| 10-19 §9 | 읽기 | 어느 대책도 중앙값 · **범위까지** 안 바꿈, 복셀 줄이면 커짐 | 남은 후보 = 위치 쪽 (a) 기록 상자 위치 (b) 카메라 외부 보정 yaw(1.3 m 에서 1° ≈ 2.3 cm) (c) SLAM/오도메트리(추정) | SUMMARY §9 |
| 10-19 §10 | 원시 깊이 점 → 지도(`anal_box_points.py`) | 상자 점 > 30 개 프레임 272 / 3159 = **출발 173(0.8~1.1 m, 정면) · 복귀 남동쪽 99(t 154~165, 로버 yaw +105~+156° 회전 중)**. 복귀 길 상자 옆에선 **시야 밖**. 출발 관측 북 **+1.7** · 서 +0.2 cm | (a) 기록 위치 맞음 → **기각**(2 cm 안). 복귀 때 지도의 상자 = 남동쪽 관측의 기억 | [`anal_box_points_f2x1.txt`](../debug_log/2026-10-19/outputs/anal_box_points_f2x1.txt) · [`box_points_f2x1.csv`](../debug_log/2026-10-19/outputs/box_points_f2x1.csv) |
| 10-19 §11 | 기억 밀림 계산(`anal_box_memory.py`) | 통과 순간 t 192.4 s map→odom (−0.087, +0.173, −3.37°). 남동쪽 관측 첫(t 154) **+7.3 cm 북** · 끝(t 165) **+2.1 cm**. 출발 관측분 +10.7 cm 는 140 s 넘게 시야 밖이라 감쇠로 사라졌을 것(추정) | (c) 유력 | [`anal_box_memory_f2x1.txt`](../debug_log/2026-10-19/outputs/anal_box_memory_f2x1.txt) |
| 10-19 §12 | nvblox `global_frame:=map` 재생 | 북 **+7.0**(범위 +2.0~+7.0) vs 기준 +5.3 | 지도 좌표 기억은 관측 순간의 지도 자세 오차를 그대로 보존 → 나빠짐 ✘ | `anal_slice_box_f2x1_ab.txt` '재생_map' 줄 |
| 10-19 §13 | 회전 중 깊이 프레임 빼기(선언: ±0.25 s yaw 변화율 > 0.10 rad/s) | 855 / 3159(27.1 %) 제외 → +5.3 · 범위 같음 · 칸 5 | **척도 한계(정정에 가까운 읽기)**: 면 = '가장 바깥 칸 가장자리' 라 5 cm 칸 위치 몇 값만 나옴 → 2~7 cm 차이는 이 척도로 못 가름. §6 의 '효과 없음' 들도 '5 cm 척도로 안 보임' | [`depth_turn_filter.py`](../debug_log/2026-10-19/jobs/depth_turn_filter.py)(855 장 출력 원문 없음) · '회전관측뺌' 줄 |
| 10-19 §14 | 연속값 분해(`anal_box_points.py <bag> <csv> 192.4`) | 출발 173 장 북 +1.7 · 남 −1.8 · 동 −3.8 · 서 +0.2 / 남동 앞(t 150~160) 71 장 남 +2.9 · 동 +4.8, 중심 기억 밀림 **(+2.2, +6.1)** / 남동 뒤(t 160~170) 28 장 동 +2.7, **(−0.3, +2.7)** | 통과 순간 상자 = 관측 오차(남동 3~5 cm) + **기억 밀림(북 +2.7~+6.1)** → 순 북 약 +3 cm + **칸 반올림(최대 +5)** = 조각 +5.3 과 맞음. (b) 는 출발 정면 2 cm 안이라 주원인 아님(남동 3~5 cm 는 (b)/(c) 미분리), **(c) 가 로버 쪽 몫의 주원인**(이 주행). 복셀 0.025 의 +6.7~6.9 는 이 분해와 안 맞음 ？ | [`anal_box_decomp_f2x1.txt`](../debug_log/2026-10-19/outputs/anal_box_decomp_f2x1.txt) |
| 10-19 §15 | (다음 줄기) '오도메트리 기억 밀림이 주원인' 이 cuVSLAM 투입 근거가 됨 | — | 프로젝터 번갈이 · cuVSLAM 쪽으로(다른 묶음) | SUMMARY §15 |
| 10-20 §8.1 | 정지 bag(§2 bt_on/off, 출발 자세, 160×120)으로 '점(센서) 몫' vs '칸(지도) 몫'(`anal_box_face_points.py`) | 북 · 켬: 점 **+6.2 cm**(38 % 가 > 2.5 cm), 칸 +5.5 / 북 · 끔: 점 +2.7, 칸 +5.1 / 서(정면): 점 +1.7 · +1.8, 칸 +2.0 · +2.1 | '정지 북 면 번짐 대부분이 센서(깊이) 몫' · 끔에선 칸 몫 ≈ 2.5 cm. 가설: ×4 는 블록 평균이라 모서리 블록 '중간 깊이' 점이 면 밖에(librealsense 설명을 기억으로 인용, 미확인) → **§8.3 에서 정정** | [`anal_box_face_points.txt`](../debug_log/2026-10-20/outputs/anal_box_face_points.txt) |
| 10-20 §8.2 선언 | 데시메이션 ×4 / ×2 / ×1 / ×4(반복) 정지 A/B | 판정 ① D2 · D1 북 면 점 번짐이 D4 두 번보다 **≥ 2 cm 작음** ② nvblox 북 면 칸 번짐 ≥ 2 cm 작고 상자 칸 ≥ 80 % · 유령 안 늘음 ③ 비용 기록 | — | SUMMARY §8.2 · [`run_decim_ab.sh`](../debug_log/2026-10-20/jobs/run_decim_ab.sh) |
| 10-20 §8.3 | 실행(4 조건 PREP_OK) | nvblox 북 · 서 **+2.3 · +3.1 / +2.2 · +2.4 / +2.0 · +2.9**(×4 · ×2 · ×1), 북 면 점 최댓값 −5.3 · +0.8 · −4.6. CPU 48.3 · 48.9 · **56.7 %**, 깊이 15.1 · 15.1 · **14.4 Hz**(×1 UDP 빠짐). **d4b 는 SLAM 위치 추정 −41° 틀림** → 비교 불가 | ① 가설 **지지 안 됨** ② 개선책 **아님**(차 ≤ 0.7 cm) — 해상도 ×4 유지. **§8.1 정정**: 같은 ×4 · 같은 자리에서 오전 +6.2 → 오후 −5.3, nvblox +5.5 → +2.3 — 세션 사이 ±3 cm(배치 · 위치 추정 yaw −0.90 vs +0.25°)가 해상도 효과보다 큼 | [`run_decim_ab.txt`](../debug_log/2026-10-20/outputs/run_decim_ab.txt) · [`anal_decim_points.txt`](../debug_log/2026-10-20/outputs/anal_decim_points.txt) · [`anal_decim_static.txt`](../debug_log/2026-10-20/outputs/anal_decim_static.txt) · [`get_dc.sh`](../debug_log/2026-10-20/jobs/get_dc.sh) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 과장은 Nav2 코스트맵(층 · 팽창 · 칸 내림)에서 생김 | 같은 주행 실시간 nvblox 조각으로 재측정(10-19 §4) | 조각에서 이미 +5.3~+9.5 | **기각(측정)** |
| 재생이 실시간과 다르다 | R0(10-19 §6) | 북 +5.3 / +5.3, 범위 · 칸 수 같음 | **기각** — 재생으로 A/B 해도 됨(이 bag) |
| 통합 거리 · site 거리가 원인 | 재생 1.0 · 1.0 | 북 그대로(통합 1.0 은 서쪽 −3.1 로 덜 찍힘) | **5 cm 척도로는 기각**(§13 한계) |
| 5 cm 복셀이 원인 | 재생 0.025 · 0.025 + 절단 4 vox | **+6.9 · +6.7**(커짐) | **기각** — 칸 반올림이 줄면 남는 몫이 드러난 것으로 해석 가능(추정), §14 분해와 불일치 ？ |
| 깊이 가장자리 섞인 화소(09-14 실루엣 비산점) | nvblox 전처리(§7 abort) → bag 단계 거르기(§8, 22 % 제거) | 그대로 | **기각(5 cm 척도)** |
| 회전 중 관측이 원인 | 회전 프레임 27 % 빼기(§13) | 그대로 | **5 cm 척도로는 판별 불가** — 척도 한계를 이 시험에서 알아챔 |
| odom 대신 map 좌표로 기억하면 낫다 | `global_frame:=map` 재생(§12) | +7.0(나빠짐) | **기각** |
| (a) 기록 상자 위치가 틀림 | 출발 정면 원시 점(§10) | 북 +1.7 · 서 +0.2 | **기각(측정)** |
| (b) 카메라 외부 보정 yaw | 출발 정면 2 cm 안(§14) | 남동 관측의 3~5 cm 는 (b)/(c) 못 가름 | **주원인 아님(측정) · 남동 몫 미확인** |
| (c) 오도메트리 기억 밀림 | 관측 순간 → 통과 순간 map→odom 변화로 옮김(§11 · §14) | 북 +2.7~+6.1(관측 뒤일수록 작음) | **지지(측정, SLAM 이 참이라는 가정, 주행 1 회)** |
| 깊이 해상도(데시메이션 ×4 평균)가 면 밖 점을 만듦 | ×4 · ×2 · ×1 정지 A/B(10-20 §8.3) | 칸 면 차 ≤ 0.7 cm, 점 지표는 세션마다 ±3 cm | **기각(측정, 정지)** — 주행 중 효과는 안 봄 |

## 4. 조치와 효과
- 이 시기에 바꾼 설정 없음 — 모든 A/B 는 재생 또는 정지 시험이고 기본값은 그대로(통합 거리 1.4 · site 2.0 · 복셀 0.05 · odom · 데시메이션 4). 남긴 것: 재생 도구 체인(`run_nvblox_replay.sh` · `anal_slice_box.py` · `anal_box_points.py`), 러너 `BAG_DEPTH`, `camera.launch.py decimation:=` 인자, `nvblox_local.yaml` 주석 정정.
- 효과: 대책은 없음. 판단의 방향이 바뀜 — 'nvblox · 깊이 쪽 cm 깎기' 에서 **'오도메트리가 기억을 덜 밀게'**(10-19 §14 함의 → §15 cuVSLAM 투입 근거) 와 '상자 옆에 오기 전 가까이서 다시 보는 경로' 두 갈래로.
- 한계: 분해는 **f2x1 한 주행 · 한 상자**. 서쪽 통로 상자(10-15 §13 '약 7 cm')에는 적용해 보지 않음. 남동 관측 3~5 cm 의 출처((b) 외부 보정 vs (c) 그 순간 자세 오차)는 미분리.

### 4.1 지금 저장소 코드(11-03 확인, 고치지 않음)
| 항목 | 지금 | 이 시기(10-19 ~ 20) | 위치 |
|---|---|---|---|
| nvblox 입력 해상도 주석 | '⚠ 2026-10-19 정정(실측): … 160×120 @15 Hz' | 같음(§1 정정) | `ros2_ws/src/rover_navigation/config/nvblox_local.yaml` 9~10 행 |
| nvblox 기억 좌표 | `global_frame: "odom"` | 같음(map 재생 기각) | 같은 파일 16 행 |
| 복셀 · 절단 · 감쇠 · 지우기 반경 | `voxel_size 0.05` · `truncation_distance_vox 2.0` · `tsdf_decay_factor 0.99` · `map_clearing_radius_m 3.0` | 같음 | 17 · 58 · 70 · 42 행 |
| 깊이 전처리 | `do_depth_preprocessing: false` | 같음(켜면 abort) | 48 행 |
| 통합 거리 | **2.0**(10-22 §14 ~ §15 사용자 결정, 프리셋 3 과 함께) | 1.4 | 57 행(이력 주석 49~56 행) — 이유는 [유령 칸 · 프리셋 카드](ghost-cells-depth-preset.md) · [복귀 상자 칸 카드](box-return-cells.md) |
| site 거리 · min_weight | 2.0 · 0.1 | 같음 | 65 · 61 행 |
| 데시메이션 | `decimation` 기본 **4**(160×120), `filter_magnitude` 가 그 값 | 같음(§8.3 '×4 유지') | `ros2_ws/src/rover_bringup/launch/camera.launch.py` 61 · 64 · 120 행 |
| 깊이 프리셋 · 프로젝터 | `depth_preset` 기본 **3**(10-22), 표준 prep 은 `emitter_off:=true`(프로젝터 상시 끔, ODOM=vslam) | 이 시기는 프리셋 없음 · 프로젝터 켬(f2x1) | `camera.launch.py` 118 행 · `Docs/tools/prep_patrol.sh` 11 행 — 이 카드의 f2x1 분해는 **지금과 다른 깊이 구성**에서 잰 것 |
| 오도메트리 | 주 EKF 병진 속도 = cuVSLAM(`ODOM=vslam` 기본, 10-23 §16) | wheel + IMU (+ rf2o 시험) | `prep_patrol.sh` 10~11 행 — 기억 밀림 (c) 를 줄이려는 쪽의 지금 상태. 상자 옆 근접이 이걸로 안 풀린 것은 10-23 §10 ~ §14(→ [경로 추종 · B0 카드](path-tracking-replan-b0.md)) |

## 5. 내 실수 · 기록 어긋남
### 실수 ① 판정 척도가 5 cm 계단임을 시험 6 개 뒤에 알아챔 (10-19 §6 → §13)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 설정 · 필터 A/B 마다 '과장이 3 cm 이상 줄면 후보'(§5 선언) 판정 |
| 본 것 | 기준 · 통합 1.0 · site 1.0 · 가장자리 · 회전 빼기가 **중앙값뿐 아니라 범위(+1.3~+6.8)까지 똑같음** |
| 처음 추론 | §6 · §8 에서 각각 '효과 없음 ✘' 으로 판정 |
| 의심한 이유 | §13 회전 프레임을 27 % 나 뺐는데도 범위까지 한 자리도 안 바뀜 — 연속값이면 있을 수 없는 일 |
| 판별 시험 | 도구 정의 확인: 면 = 칸 중심 + 반 칸(`gy[k].max() + r / 2`) — 칸 위치(통과 순간 map→odom 고정)에 따라 몇 값만 나옴 → §14 에서 원시 점(연속값)으로 다시 잼 |
| 결론 | §6 · §8 · §13 의 '효과 없음' 은 '5 cm 척도로 안 보임' — 2~7 cm 차이는 가르지 못했다. 결론(대책 아님)은 §14 연속값 분해 · 10-20 §8.3 정지 A/B 로 다른 척도에서도 유지 |
| 다음에 알아보는 법 | 칸 지도에서 '면' 을 재는 지표를 판정에 쓰기 전에 **나올 수 있는 값의 간격**(이번엔 칸 0.05 m)을 먼저 적고, 판정 문턱(3 cm)이 그보다 작으면 연속값 지표(원시 점)를 함께 쓴다. 서명 = 다른 조건들이 범위까지 같은 값 |
| 스크립트 핵심 | [`anal_slice_box.py`](../debug_log/2026-10-19/jobs/anal_slice_box.py) 41 · 45 행 `lx = m.origin.x + (ix + 0.5) * r` … `rows.append((st, gy[k].max() + r / 2, gx[k].min() - r / 2, int(k.sum())))` |
| 나온 결과 | [`anal_slice_box_f2x1_ab.txt`](../debug_log/2026-10-19/outputs/anal_slice_box_f2x1_ab.txt) `재생_기준 … +5.3 cm (범위 +1.3~+6.8)` · `통합1.0 … +5.3 cm (범위 +1.3~+6.8)` · `회전관측뺌 … +5.3 cm (범위 +1.3~+6.8)` |
| 데이터 | 위 파일 · 재생 출력 bag(Jetson `~/bags/replay_*`, PC 로컬에 없음 — 11-03 확인 안 함) |

### 실수 ② 정지 한 세션 값으로 '센서 몫이 대부분' 이라 읽음 (10-20 §8.1 → §8.3)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 해상도 시험 전에 번짐을 점 몫 · 칸 몫으로 나눔 |
| 본 것 | 오전 정지 bag: 북 면 점 +6.2 cm · 칸 +5.5 cm(켬) |
| 처음 추론 | '정지 북 면 번짐의 대부분이 센서(깊이) 몫' → ×4 평균 가설 |
| 의심한 이유 | §8.3 의 같은 ×4 · 같은 자리(d4a)에서 점 −5.3 · 칸 +2.3 |
| 판별 시험 | 같은 날 다른 세션 비교 — 북 면은 출발 자세에서 거의 옆(약 3°)으로 보여 띠 점이 10~76 개뿐, 위치 추정 yaw 오전 −0.90° vs 오후 +0.25°(1.2 m 에서 ≈ 2.4 cm), 상자 재배치 |
| 결론 | 세션 사이 ±3 cm 흔들림이 해상도 효과보다 큼 — §8.1 의 결론은 근거 약함(§8.3 정정). 해상도 결론(대책 아님)은 같은 세션 안 비교라 유효 |
| 다음에 알아보는 법 | 정지 '번짐' 수치는 같은 세션의 기준을 같이 재고(이번 d4a · d4b 처럼), 그 면이 몇 도로 보이는지 · 띠 점 수를 함께 적는다 |
| 스크립트 핵심 | [`anal_box_face_points.py`](../debug_log/2026-10-20/jobs/anal_box_face_points.py) 52 · 55 행 `bn = hz & (G[0] > 1.17) & (G[0] < 1.24) & (G[1] > -0.20) & (G[1] < FN + 0.15)` → `N.append((y.max(), np.percentile(y, 99), …))` |
| 나온 결과 | [`anal_box_face_points.txt`](../debug_log/2026-10-20/outputs/anal_box_face_points.txt) `on: … 북 면 … 프레임당 35 점(중앙) · 면 밖 최댓값 중앙 +6.2 cm` / [`anal_decim_points.txt`](../debug_log/2026-10-20/outputs/anal_decim_points.txt) `d4a: … 북 면 … 프레임당 10 점(중앙) · 면 밖 최댓값 중앙 -5.3 cm` |
| 데이터 | 위 두 파일, 정지 bag 은 Jetson `~/bags`(PC 로컬 확인 안 함) |

### 실수 ③ 재생 nvblox 를 래퍼 PID 로만 죽여 고아 4 개 (10-19 §15.1)
- 본 것: 분리 노드 배포 때 컨테이너에 nvblox_node 4 개가 남아 GPU · 메모리를 잡고 있었다. 원인: `run_nvblox_replay.sh` 가 `ros2 run` 래퍼 PID 만 죽임. 판별: §6 ~ §13 재생 출력 8 개 모두 조각 1975~2001 · 중복 stamp 0 · 해상도가 설정과 일치(0.025 판만 0.025) → 결과 오염 없음(측정). 고침: 28 행 `pkill -INT -f nvblox_replay.yaml; sleep 2; pkill -9 -f nvblox_replay.yaml`. 다음에 알아보는 법: 컨테이너 안 프로세스를 띄운 도구는 끝에 `pgrep -f` 로 0 인지 확인. 데이터: [`run_nvblox_replay.sh`](../debug_log/2026-10-19/jobs/run_nvblox_replay.sh) 27~28 행(오염 확인 출력은 원문 없음).

### 기록 어긋남 (이번 확인)
| # | 기록 | 원문 · 코드 | 판정 |
|---|---|---|---|
| 1 | 10-19 §4 '북쪽 면 과장 중앙 f2w1 **+8.2** · f2u1 +9.5 · f2u3 +6.1 · f2v4 +5.3' | [`anal_slice_box_baseline.txt`](../debug_log/2026-10-19/outputs/anal_slice_box_baseline.txt) 는 f2u1 · f2u3 · f2v4 3 줄뿐 | f2w1 값 **원천 소실**. 10-15 판(+9.6)과 f2u1 +9.5 는 0.1 cm 차(SUMMARY '같음' 은 맞음). 파일의 f2u3 서쪽 **+17.1 cm** 는 SUMMARY 에 없음 |
| 2 | 10-19 §1 160×120 · 14.99 Hz · 581 KB/s, §2 조각 270, §7 abort 줄, §8 22.26 %, §13 855 / 3159 | 각 도구 출력 파일 없음(`outputs/` 에 해당 파일 없음) | **원문 없음** — SUMMARY 서술 · 인용뿐 |
| 3 | 10-20 §8.3 'd4b map→odom (+0.10, +0.36 m, −41.0°)' | [`run_decim_ab.txt`](../debug_log/2026-10-20/outputs/run_decim_ab.txt) 에 map→odom 줄 없음, `anal_decim_static.txt` 는 d4b '상자 부피 점 0 · 상자 칸 0' 만 | 값 자체는 **원문 없음**(정황은 파일과 맞음) |
| 4 | `camera.launch.py` 62~63 행 주석 '(×4 평균이) 면 밖에 찍히는지(10-20 §8.1 북 면 +6 cm) 정지 A/B 로 본다 … 시험으로 확인 중' | 10-20 §8.3 이 이미 '가설 지지 안 됨 · 개선책 아님' · §8.1 정정 | **낡은 주석**(값 영향 없음) |
| 5 | `nvblox_local.yaml` 63~64 행 주석 '실패 때 6~7 cm 과장은 이 값이 아니라 비스듬한 먼 첫 관측 쪽으로 추정' | 10-19 §14: 로버 쪽 몫의 주원인 = 오도메트리 기억 밀림 + 칸 반올림(f2x1) | **낡은 추정**(10-15 판 그대로). 57 행 꼬리 '상자(≤1.3 m)' 도 10-22 2.0 결정 뒤 맥락과 안 맞음 |
| 6 | CLAUDE.md §6 '기억된 상자가 4~5 cm 밀림' | 10-19 §11 · §14 f2x1 +2.1~+7.3 cm, 복귀 상자는 [복귀 카드](box-return-cells.md)에서 +4~+10 cm | 기전은 맞고 크기는 주행 · 시점마다 다름(기전 카드 §6 #4 와 같은 지적) |

## 6. 남은 것 (10-20 시점)
- **분해는 1 주행** — f2x1 하나. 다른 주행 · 서쪽 통로 상자에 같은 연속값 분해를 하지 않았다.
- 복셀 0.025 재생 +6.7~6.9 cm 가 '칸 반올림 몫' 해석과 안 맞음(10-19 §14 ？).
- 남동 관측 3~5 cm 의 출처 — (b) 카메라 외부 보정(09-18 데크 보정 뒤 카메라 yaw 미검증, [센서 데크 yaw](sensor-deck-yaw.md)) vs 회전 중 그 순간의 자세 오차.
- 칸 반올림(최대 +5 cm)은 nvblox 5 cm 복셀 · Nav2 5 cm 칸 그대로라 남음 — 10-15 의 '뒤집힘 띠 2.7~4.4 cm' 와 겹친다([기전 카드](box-side-stall-cause.md)).
- 주행 중 깊이 해상도 효과는 안 봄(정지만).
- d4b 출발 위치 추정 −41° — '가끔 나는 문제' 가능성(10-20 §8.3) → 10-21 §1 출발 위치 추정 검사(다른 묶음).

## 7. 이후 (10-21 ~)
- 10-20 §2 ~ §3.2(다른 묶음 — 프로젝터 상시 끔): f2z1 · f2z2 북 면 과장 +4.4~+6.7 cm 로 켬(f2x1 +3.6~+6.5)과 같은 범위, 복귀 길 주변 흩어진 칸만 21 · 27 개로 늘어남 — [`anal_slice_box_f2z.txt`](../debug_log/2026-10-20/outputs/anal_slice_box_f2z.txt).
- 10-22 §11 ~ §11.3: 같은 기전(odom 기억 밀림 + 관측 수 cm + 칸 경계)이 프리셋 3 복귀 길 상자 밖 칸으로 다시 나옴(f2pr1 기억 +4.2~+5.0 cm 북, 출발 기억은 +9.9 cm) → [복귀 길 상자 칸](box-return-cells.md).
- 10-23 §10 ~ §11(다른 묶음): cuVSLAM 병진 속도 융합(`vslam:=on`)으로 위치 추정은 좋아졌으나 상자 옆 실제 여유는 3.3 · 0.3 cm — 근접은 경로 추종 쪽 → [경로 추종 · 재계획 · B0](path-tracking-replan-b0.md).

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2x1 | 깊이 기록 b910(프로젝터 켬, 통합 1.4), 3/3 · 깊이 3159 장 | 10-19 §6, [`run_f2x1.txt`](../debug_log/2026-10-19/outputs/run_f2x1.txt), bag Jetson `~/bags/bag_f2x1`(PC 로컬 없음 — 11-03 `2026-10-19/bags/` 없음) |
| R0 · 설정 A/B · 필터 · map 재생 | 같은 f2x1 깊이 bag 재생 9 가지 | 10-19 §6 ~ §13, [`anal_slice_box_f2x1_ab.txt`](../debug_log/2026-10-19/outputs/anal_slice_box_f2x1_ab.txt), 출력 Jetson `~/bags/replay_*` |
| 기존 주행 기준 | f2u1 · f2u3 · f2v4(· f2w1) 실시간 조각 | 10-19 §4, [`anal_slice_box_baseline.txt`](../debug_log/2026-10-19/outputs/anal_slice_box_baseline.txt) |
| 원시 점 분해 | f2x1 상자 점 272 프레임 | 10-19 §10 · §14, [`anal_box_points_f2x1.txt`](../debug_log/2026-10-19/outputs/anal_box_points_f2x1.txt) · [`anal_box_decomp_f2x1.txt`](../debug_log/2026-10-19/outputs/anal_box_decomp_f2x1.txt) · [`box_points_f2x1.csv`](../debug_log/2026-10-19/outputs/box_points_f2x1.csv) · [`anal_box_memory_f2x1.txt`](../debug_log/2026-10-19/outputs/anal_box_memory_f2x1.txt) |
| bt_on / bt_off | 정지 출발 자세 프로젝터 켬 · 끔(10-20 §2 의 bag) | 10-20 §8.1, [`anal_box_face_points.txt`](../debug_log/2026-10-20/outputs/anal_box_face_points.txt) |
| d4a · d2 · d1 · d4b | 데시메이션 정지 A/B | 10-20 §8.3, [`run_decim_ab.txt`](../debug_log/2026-10-20/outputs/run_decim_ab.txt) · [`anal_decim_points.txt`](../debug_log/2026-10-20/outputs/anal_decim_points.txt) · [`anal_decim_static.txt`](../debug_log/2026-10-20/outputs/anal_decim_static.txt) |
| 도구(10-19) | `chk_depth_topic.sh` · `rec_depth_test.sh` · `run_nvblox_replay.sh` · `anal_slice_box.py` · `chk_replay_params.sh` · `chk_replay_vox.sh` · `chk_nvblox_preproc.sh` · `chk_replay_log.sh` · `depth_edge_filter.py` · `depth_turn_filter.py` · `anal_box_points.py` · `anal_box_memory.py` · `get_replays.sh` · `pack_replay.sh` | `2026-10-19/jobs/`, §9 |
| 도구(10-20) | `anal_box_face_points.py` · `anal_box_static.py` · `run_decim_ab.sh` · `get_dc.sh` | `2026-10-20/jobs/`, §9 |

## 9. 도구 해설
공통: 재생은 Jetson 컨테이너(`isaac_ros_dev-aarch64-container`) 안 두 번째 nvblox_node, 분석은 PC `rosbags`(AnyReader, Humble 타입, `nvblox_msgs/DistanceMapSlice` 손 등록). 조각 · 로컬 코스트맵은 **odom**, 지도 비교는 그 시각 map→odom 으로 옮김. 기록 상자 = 지도 x 1.151~1.261 · y −0.20~−0.02(10-15 §23 · TEST_COURSE §1). '과장 +' = 실제 면보다 바깥(북 = 로버 쪽).

### 9.1 `run_nvblox_replay.sh` — 깊이 bag → 컨테이너 nvblox 재생 (Jetson, bash, 로버 안 움직임) ★ 이 카드 A/B 의 바탕
- 형태: `run_nvblox_replay.sh <깊이bag> <꼬리표> [nvblox 파라미터:=값 …]`.
- 왜(10-19 §0 · §2): 같은 입력으로 설정만 바꾼 A/B — 주행 · 배터리 없이.
- 하는 일: ① 설치본 `nvblox_local.yaml` · UDP 전용 Fast DDS 프로파일을 `/tmp` 로 복사 ② `docker exec -d … ROS_DOMAIN_ID=42 … ros2 run nvblox_ros nvblox_node --params-file /tmp/nvblox_replay.yaml -p use_sim_time:=true -p <덮어쓰기> -r camera_0/depth/image:=/camera/camera/depth/image_rect_raw …` ③ 도메인 42 에서 `ros2 bag record /nvblox_node/static_map_slice` ④ `ros2 bag play <bag> --clock 100 --topics <깊이 · camera_info · /tf · /tf_static>`(10-19 §6 수정 — 첫 판은 주행 bag 의 실시간 조각까지 내보내 출력이 2 배) ⑤ 기록 SIGINT → `pkill -f nvblox_replay.yaml`(§15.1 수정) ⑥ 재생 로그 꼬리 · `ros2 bag info`.
- 출력: Jetson `~/bags/replay_<꼬리표>`, 로그 `/tmp/nvblox_replay_<꼬리표>.log`(휘발). 화면 출력은 저장 안 됨(원문 없음).
- 쓰인 곳: 10-19 §6 ~ §13, 뒤에 10-22 §9 · §11.3 · §14.2(min_weight · site · 통합 2.0 재생, [유령 칸 카드](ghost-cells-depth-preset.md)). 결함: 파라미터가 실제로 적용됐는지는 따로 `chk_replay_params.sh`(로그 grep)로 봐야 하고, site 1.0 은 10-22 에 로그 줄을 못 찾음(10-22 §11.3). 지금 재사용 가능(깊이가 든 bag 이면).

### 9.2 `anal_slice_box.py` — 조각의 상자 면 과장 (PC, Python) ★ §4 · §6 판정 도구
- 형태: `anal_slice_box.py <주행bag> 이름=조각bag …`(조각bag = 주행 bag 자체(실시간) 또는 `replay_<꼬리표>`).
- 하는 일: 주행 bag 의 `/tf` 로 map→odom · odom→base_link 시계열 → 조각마다 그 stamp 의 로버 지도 위치가 상자 옆(x 0.9~1.7, |y| < 0.6)일 때만, 거리 ≤ 0 · unknown 아님 칸 중심을 지도로(`frame_id == 'map'` 이면 그대로 — §12 추가). 상자 구역(x 0.95~1.50, y −0.25~0.25; 남쪽 창문틀 · 드론 띠 y < −0.25 제외) 칸으로 북 면 = `max(y) + r/2`, 서 면 = `min(x) − r/2`, 칸 수. 조각들의 중앙 · 범위 → 기록 면 대비 cm. 10-19 §21 에 '5 s 넘게 끊기면 새 구간' 구간별 출력 추가.
- 출력 줄: `실시간 상자 옆 조각 230 (칸 있음 230) · 북쪽 면 과장 중앙 +5.3 cm (범위 +1.3~+6.8) · 서쪽 면 과장 중앙 -0.1 cm · 칸 수 중앙 6`. 파일 [`anal_slice_box_baseline.txt`](../debug_log/2026-10-19/outputs/anal_slice_box_baseline.txt) · [`anal_slice_box_f2x1_ab.txt`](../debug_log/2026-10-19/outputs/anal_slice_box_f2x1_ab.txt) · 10-20 [`anal_slice_box_f2z.txt`](../debug_log/2026-10-20/outputs/anal_slice_box_f2z.txt).
- 결함: **면 지표가 5 cm 계단**(실수 ①). '상자 옆' 판정이 로버 위치만 봐서 출발 · 복귀가 섞임(§21 에서 구간 출력으로 보완). 남쪽 띠 제외 문턱 y −0.25 는 상자 남쪽 면(−0.20)에서 5 cm — 남쪽 과장은 못 잼.
- 계보: 10-15 `anal_box_true_vs_map.py`(로컬 코스트맵 판) → 이것(조각 판) → 10-20 `anal_box_static.py`(정지 판, 같은 면 정의) · 10-22 `anal_slice_zones.py`(영역별 유령 · 상자 칸). 재사용 가능.

### 9.3 `anal_box_points.py` — 원시 깊이 점 → 지도, 면 · 기억 밀림 (PC, Python) ★ §10 · §14 분해의 도구
- 형태: `anal_box_points.py <bag> <출력csv> [통과시각 s]`.
- 왜(§9): 설정 · 필터가 과장을 못 바꿈 → 점 단계에서 이미 +5 면 위치 · 보정 쪽, 점은 맞고 조각만 +5 면 지도 만들기 쪽.
- 하는 일: 깊이(160×120, mm) × camera_info K → 광학 점(깊이 0.45~1.6 m) → `/tf_static` 사슬(base_link → … → 광학) → odom→base_link · map→odom(깊이 시각 직전 값) → 지도 점. 상자 점 = x 1.05~1.40 · y −0.32~+0.15 · z 0.04~0.17. 30 개 미만 프레임은 건너뜀. 면: 북 = x 1.16~1.25 점 y 의 **98 백분위**, 남 = 같은 띠 y 2 백분위, 서 = y −0.18~−0.04 점 x 2 백분위, 동 = x 98 백분위(띠 점 ≥ 15). 통과 시각을 주면 `Gp = (MP @ inv(mo) @ Gh)` 로 상자 점을 그 순간의 odom 기억 위치로 옮긴 중심도 냄(§14).
- 출력: csv(프레임마다 로버 자세 · 거리 · 방위 · 면 · 중심 · map→odom) + 묶음 요약(구간 · 카메라 방위 · 거리). [`anal_box_points_f2x1.txt`](../debug_log/2026-10-19/outputs/anal_box_points_f2x1.txt):
  ```
    구간 t 1~12 s (로버 yaw +0~+22°)       북쪽 면 과장  +1.7 (n 173, 사분위 +1.1~+2.4) · 서쪽 면 과장  +0.2 (n 161, 사분위 +0.2~+1.2)
    구간 t 154~165 s (로버 yaw +105~+156°) 북쪽 면 과장 -15.2 (n  60, 사분위 -15.8~-14.3) · 서쪽 면 과장  -7.9 (n  73, 사분위 -10.3~-5.5)
  ```
  (뒤 줄의 북 · 서 −15.2 · −7.9 는 남동쪽에서 본 '먼 면' 이라 의미 없음 — §14 는 남 · 동 면을 씀.)
- 결함 · 주의: 로버가 남동쪽에 있으면 북 · 서 면 백분위는 보이지 않는 면의 값 — **어느 면이 보이는지 함께 봐야 함**(이 주의를 어긴 기록 → [복귀 카드 §5](box-return-cells.md) 어긋남). 면 백분위는 점 수에 민감. 계보: 10-20 `anal_box_face_points.py`(띠 정의를 바꾼 정지 판) · 10-22 같은 도구 f2dr2 재사용([`anal_box_points_f2dr2.txt`](../debug_log/2026-10-22/outputs/anal_box_points_f2dr2.txt)).

### 9.4 `anal_box_memory.py` — 통과 순간 기억 밀림 (PC, Python)
- 형태: `anal_box_memory.py <bag> <points_csv>`.
- 하는 일: ① 남동쪽 관측 프레임(t 150~170)의 동 · 남 면 → 기록 대비(그 순간 지도 자세 오차의 크기) ② 기억 밀림 = `mo(t_pass) · mo(t_obs)⁻¹ · 상자 − 상자`(33 · 49 행 `q = mul(mp, inv(mo, p))`) — 출발 관측(t 5) · 남동 첫(t 154) · 끝(t 165)마다 상자 네 모서리 · 중심.
- 출력 [`anal_box_memory_f2x1.txt`](../debug_log/2026-10-19/outputs/anal_box_memory_f2x1.txt): `남동쪽 관측 첫(t 154 s) … 중심 Δ(+3.6, +7.3)` · `끝(t 165 s) … 중심 Δ(-0.5, +2.1)`. 가정: SLAM 상대 이동이 참. 계보: 10-15 `anal_memory_shift.py` → 이것 → 10-22 `anal_memory_shift.py`(시각 목록 판, [복귀 카드](box-return-cells.md)).

### 9.5 `depth_edge_filter.py` · `depth_turn_filter.py` — 깊이 bag 다시 쓰기 (Jetson, Python rosbag2_py)
- `depth_edge_filter.py 입력bag 출력bag [abs_m=0.05] [rel=0.04]`: 31 행 `bad |= v & nv & (np.abs(a - nb) > np.maximum(ABS, REL * a))` — 3×3 이웃 중 하나라도 깊이 차가 크면 0. 깊이 · camera_info · tf · tf_static 만 옮김. 출력 한 줄(제거 비율)은 원문 없음.
- `depth_turn_filter.py 입력bag 출력bag [thr=0.10]`: 32 · 46 행 — 깊이 시각 ±0.25 s 의 odom→base_link yaw 변화 / 0.5 s > thr 면 그 깊이 · camera_info 를 뺌(tf 는 그대로).
- 둘 다 시험 전 선언 규칙 그대로 구현. 결과 판정은 `anal_slice_box.py` 로(5 cm 척도 한계 — 실수 ①). 재사용 가능.

### 9.6 `anal_box_face_points.py` · `anal_box_static.py` — 정지 bag 점 몫 · 칸 몫 (PC, Python, 10-20)
- `anal_box_face_points.py 이름=bag …`: 점 = 깊이 → 그 순간 tf 로 지도(z 0.03~0.17). 북 면 띠 = x 1.17~1.24(모서리 제외) · y −0.20~+0.13 점의 y — 프레임마다 최댓값 · 99 · 95 %, 면보다 +1 · +2.5 cm 넘은 비율. 서 면 띠 = y −0.18~−0.04 점의 x 최솟값 · 1 · 5 %. 출력 줄 `북 면(y = −0.02) 띠 점: 프레임당 35 점(중앙) · 면 밖 최댓값 중앙 +6.2 cm · 99 % +6.2 · 95 % +5.5`.
- `anal_box_static.py 이름=bag …`: 깊이 유효 비율(전체 · 아래 절반) · 상자 부피 점 수, 마지막 5 s 조각의 상자 칸 · 북 · 서 면(`anal_slice_box` 정의) · 빈 바닥 유령 칸 · 미지 비율. 출력 [`anal_decim_static.txt`](../debug_log/2026-10-20/outputs/anal_decim_static.txt) `d4a: … 조각(마지막 5 s, 48 개) 상자 칸 9 · 북 +2.3 · 서 +3.1 cm · 빈 바닥 유령 칸 0`.
- 결함: 북 면이 거의 옆으로 보여 띠 점이 적고(10~76) 값이 세션마다 흔들림(실수 ②). 10-20 §2 의 프로젝터 켬/끔 B 시험(다른 묶음)이 이 도구를 처음 씀.

### 9.7 `run_decim_ab.sh` · `get_dc.sh` — 데시메이션 정지 A/B (Jetson · PC, bash, 로버 안 움직임)
- `run_decim_ab.sh`: D4 → D2 → D1 → D4 마다 `prep` 재기동(`decimation:=N`) → 20 s 대기 → 25 s 기록(깊이 · camera_info · tf · 조각) + 같은 창 전체 CPU · EKF 위반 누계 · nvblox 깊이 콜백 Hz, 끝에 D4 복귀. 출력 [`run_decim_ab.txt`](../debug_log/2026-10-20/outputs/run_decim_ab.txt)(첫 줄은 WSL 이진 잡음):
  ```
  ########## d1 (decimation 1) ##########
    CPU(기록 창) 56.7 % · EKF 위반 누적 20
    nvblox ros/depth_image_callback 100 14.4|ros/update_esdf 100 9.5|
  ```
- `get_dc.sh`: bag 4 개를 PC 로 회수. 결함: map→odom 을 찍지 않아 d4b −41° 를 이 출력으로 확인할 수 없음(§5 어긋남 3).

## 10. 용어
- **nvblox 조각(static_map_slice)**: nvblox 가 3D TSDF/ESDF 에서 높이 띠(z 0.06~0.30)를 잘라 낸 2D 거리 지도(odom 좌표, 5 cm 칸). 거리 ≤ 0 = 표면 안 = 장애물 칸. Nav2 nvblox 층이 이것을 이진 치명 칸으로 옮긴다.
- **재생 A/B · R0**: 기록한 깊이 bag 을 nvblox 에 다시 넣어 설정만 바꾼 비교. R0 = 같은 설정 재생이 실시간과 같은지 먼저 확인(재생 신뢰 조건).
- **기억 밀림**: nvblox 가 odom 좌표로 기억한 칸이, 그 뒤 EKF 오차를 SLAM 이 map→odom 으로 고칠 때 지도(실제 세계) 위에서 그만큼 옮겨 보이는 것. 로버 자신도 odom 위에 있으므로 로버 기준 오차 = '관측 뒤 EKF 가 잘못 센 이동'.
- **칸 반올림**: 면의 일부라도 든 5 cm 칸 전체가 장애물이 되므로 지도 면이 실제 면보다 최대 한 칸(5 cm) 바깥으로 나오는 것.
- **데시메이션(decimation_filter)**: librealsense 처리 블록 — 깊이 영상을 N×N 블록 하나로 줄임(×4 = 640×480 → 160×120). 점군 CPU 를 줄이려 09-08 에 켬, nvblox 입력에도 걸림(10-19 §1).
- **외부 보정(extrinsic)**: 카메라가 차체에 대해 어떻게 놓였는지(위치 · 각도). 1° 틀리면 1.3 m 에서 약 2.3 cm.
