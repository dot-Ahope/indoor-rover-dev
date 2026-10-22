# 2026-10-22 — 유령 칸 대응: 깊이 프리셋 주행 f2pr1 · nvblox 최소 가중치

## §0 하루 시작 (사용자: "오늘 진행 뭘 해야 하는가." → 순서 0 점검 → 1 f2pr1 → 2 min_weight → "진행하라")
- 본 것(`outputs/chk_day_start_1022.txt`, 도구 `jobs/chk_day_start_1022.sh`):
  - PC 핑: 192.168.0.110 응답(TTL 63), 172.30.1.8 무응답 → Jetson 이 WEB_DEV_5G 로 돌아옴. 접속해 신원 `jetson-desktop` 확인.
  - **10:30:23 재부팅**(가동 47 분) → `/tmp` prep 5 개 없음. Isaac 컨테이너 · 시험 컨테이너 `Exited (255)`(nvblox_up.sh 가 docker start), 스택 없음, base active, 에이전트 컨테이너 떠 있음.
  - `camera.launch.py` = 어제 배포한 depth_preset 판(sha 95fe7b16a70f).
  - 디스크 여유 124 GB, 메모리 사용 881 MB.
- prep 스크립트 재전송(`jobs/up_prep_1022.sh` — 저장소 `Docs/tools` 판을 그대로): prep_fast.sh c636f4060d · prep_patrol.sh 6bdd126a30 · chk_prep.py d06751ab73, 저장소와 해시 일치. pad_relief.py · prep_patrol_pad.sh 는 지금 구성에서 안 씀(올리지 않음).
- 스크래치패드 `tools/` 폴더와 `job240 · 440 · 451 · 453 · 956` 원본이 또 사라짐(자동 삭제 추정). 주행 러너 묶음(run_f0 · run_f2c · put_one · job550 · job551 · job613 · rescued_jetson_tmp/)은 남아 있고 10-21 jobs 사본과 해시 일치(run_f0 은 사본이 비밀번호를 가려서 다름, run_f2c 는 어제 `home` 추가 판).

## §1 f2pr1 구성 prep — PREP_OK (`outputs/prep_pr_1022_1.txt`, 도구 `jobs/prep_pr_1022.sh`)
- 구성 = 10-21 §21.2 선언 그대로: 프로젝터 상시 끔 · vslam:=shadow · dds_shm:=true + `depth_preset:=3`.
- 위치 추정 검사 0.005 m · −0.1° 통과, `/wheel_odom 25.0 Hz`(재부팅 뒤에도 보드 세션 살아 있음 — 보드 리셋 불필요) · `/odometry/filtered 30.0` · `/tf 49.7` · 배터리 12.36 V, nvblox · cuVSLAM · vslam_twist · ekf_vslam 각 1. 64 s.
- 프리셋 적용 확인(`jobs/chk_preset_1022.sh`): 운용 카메라 `depth_module.visual_preset = 3`.
- 판정 기준은 10-21 §21.2(주행 전 선언). 주행은 사용자 "시작" 뒤.

## §2 f2pr1 주행 시작 (사용자: "1. 시험 상자 제자리에 있다. 2. 사람들이 돌아다니고 있다. 문제 발생시 여부 확인. 시작.")
- 러너 `run_f2c.sh f2pr1 … b910`(STAGE F2pr, LOAD_MAX 65, JETSON_HOST 192.168.0.110, GIT_HEAD 426a08c3). NOTE 에 '사람들이 돌아다님' 기록.
- **기준 3 해석(결과 보기 전, 주행 중 적음)**: 로버는 상자를 등지고(≈ −166°) 1.2 m 거리에서 출발하므로 '1.4 m 안에 들어온 뒤' 는 출발 즉시가 된다. → 시작 시각 t0 = 상자 중심 (1.25, −0.075) 이 **로버 1.4 m 안 그리고 진행 방향 ±40°(D455 깊이 수평 시야 ≈ 87° 의 안쪽)** 에 처음 든 시각. 판정: t0 + 2 s 안에 상자 영역 (1.15~1.35, −0.20~0.05) 로컬 LETHAL ≥ 8 칸. 같은 도구로 f2sm1(프리셋 없음) 도 잼(비교 기준). 도구 `jobs/anal_box_detect.py`.
- 사람 영향 확인: 문제(중단 · 긴 정지 · 유령 기준 미달)가 나오면 그 시각 라이다 점에 사람 크기 물체가 있었는지 bag 으로 확인.

## §3 f2pr1 결과 — 기준 1 · 2 통과, **기준 3(낮은 상자 2 s 안 ≥ 8 칸) 미달** (주행 11:34~11:38)
| 기준(10-21 §21.2 · §2 해석) | f2pr1(프리셋 3) | 비교: f2sm1(프리셋 없음) | 판정 |
|---|---|---|---|
| 1. 목표 | 3/3 (51.7 · 51.8 · 110.0 s, 총 213.7 s) | 3/3 | ✔ |
| 2. 유령 — 상자 너머 맨바닥 A · 문 사이 B (t 10~60 s) | **A 0 · B 0** | A 50 · B 0 (10-21 §15, 끔 주행 28~99 · 켬 0~3) | ✔ |
| 3. 낮은 상자 (t0 = 4.0 s, 출발 자세에서 이미 1.26 m · 방위 −4°) | 출발부터 **7 칸**, 처음 ≥ 8 은 t0 + 10.8 s | 출발부터 15~16 칸, t0 + 0.55 s | ✘ (7 < 8) |
| 4. 끝 상태 지도 · 라이다 근거 없는 LETHAL (기록) | 110 칸(그중 nvblox 슬라이스 77) | 253 칸(nvblox 244) | nvblox 몫 −68 % |

- 주행 전체 상자 칸(10 s 묶음, `outputs/anal_box_series_*.txt`):
  - 나가는 길(t 0~60, 로버-상자 최소 0.44 m): f2pr1 6~9 칸 · f2sm1 15~17 칸 — **절반**.
  - 돌아오는 길(t 170~220, 최소 0.35 m): f2pr1 **1~2 칸** · f2sm1 3~7 칸. 프리셋 없이도 복귀 쪽에선 상자가 작게 보임(반대편 면을 비스듬히 봄으로 추정), 프리셋 3 에선 거의 사라짐.
  - 그래도 로버는 상자 중심에서 0.35 m(차체 중심 기준) 밖으로 지나갔고 stuck 진단 0. 접촉 여부는 사용자 확인 필요.
- 기타: 누적 회전 휠 −79.5° vs EKF −161.7°(차 82.2°, f2sm1 11.3° · f2sm2 44.3°) — 미끄러짐이 컸다. 사람 통행(사용자)과 관련 있는지는 미분석.
- 읽기:
  1. 프리셋 3 은 **맨바닥 유령을 없앴다**(A 0, 끝 상태 nvblox 칸 −68 %). 정지 pr1 의 결과가 주행에서도 재현.
  2. 대가로 **라이다 아래 낮은 물체가 절반 이하로 보인다** — 나가는 길 7 칸은 여전히 LETHAL 이라 MPPI 가 피했지만, 복귀 쪽 1~2 칸은 '거의 못 봄'. 상자가 더 작거나 더 비스듬하면 놓칠 수 있다(추정).
  3. 따라서 프리셋 3 을 그대로 기본값으로 넣는 것은 선언 기준상 불합격. 남은 길(추정, 시험 전): (가) 중간 프리셋(5 Medium Density 등) 또는 고급 모드 개별 값(신뢰도 문턱)을 낮춰 절충점 찾기, (나) 프리셋 0 유지 + 2번(nvblox 최소 가중치)으로 깜빡이는 유령만 거르기, (다) 둘 조합.
- ⚠ 2번 준비 사항: 지금 러너 bag 에는 **깊이 영상이 없다**(nvblox 출력 슬라이스 · 코스트맵만) → 최소 가중치를 bag 재생으로 A/B 하려면 깊이(`/camera/camera/depth/image_rect_raw` + camera_info, 160×120 ≈ 38 kB × 15 Hz)를 함께 기록한 주행이 먼저 필요.
- 데이터: 러너 `outputs/run_f2pr1.txt` · bag `bags/bag_f2pr1.tgz`(PC 스크래치패드 `f0_f2pr1/` 에서 복사; /local_costmap/costmap · /global_costmap/costmap · /nvblox_node/static_map_slice · /map · /scan · /tf) · 유령 `outputs/anal_zone_ghosts_f2pr1.txt`(도구 `2026-10-21/jobs/anal_zone_ghosts.py`) · 상자 `outputs/anal_box_detect_f2pr1.txt` · `anal_box_detect_f2sm1.txt`(도구 `jobs/anal_box_detect.py`) · `outputs/anal_box_series_f2pr1.txt` · `anal_box_series_f2sm1.txt`(도구 `jobs/anal_box_series.py`) · 끝 상태 `outputs/anal_phantom_f2pr1_end.txt` · `anal_phantom_f2sm1_end_check.txt`(도구 `2026-10-21/jobs/anal_phantom_cells.py`, 그림 `figures/phantom_f2pr1_end.png`). f2sm1 입력 = `2026-10-21/bags/bag_f2sm1.tgz`.
