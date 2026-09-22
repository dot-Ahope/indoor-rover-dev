# Phase N 결과 — nvblox 이전 N0~N5 (2026-09-21 ~ 09-22)

**결정(2026-09-22, 사용자)**: **로컬 코스트맵의 카메라 층을 nvblox 로 채택**한다(절단 2.0 복셀·감쇠 0.99, 이진 층 + 기존 inflation). 전역 코스트맵·릴레이·STVL 은 아직 그대로이며, 다음 단계 **N6 = 전역 코스트맵 이전**(릴레이·STVL 제거)이다. 채택은 결정이고, 구성 전환(launch 통합)은 N6-0 에서 한다 — 그 전까지 `nav2_params.yaml` 로컬 `plugins` 기본값은 STVL, 모드 N 은 절차 v2.0 의 job488/job508 로 전환한다.

원문은 `Docs/debug_log/2026-09-21/SUMMARY.md §9~10`, `Docs/debug_log/2026-09-22/SUMMARY.md §0~3.1`, 기준선 `Docs/debug_log/2026-09-21/BASELINE_STVL.md`. 이 문서는 요약과 그림 색인이다.

## 1. 단계별 결과
| 단계 | 내용 | 결과 | 근거 |
|---|---|---|---|
| N0 | Isaac ROS 3.2 Dev 컨테이너(상주형, 레거시 GPU 지정)에서 nvblox 3.2.5 깊이 전용 정지 측정 | 4 게이트 통과: 상자 앞면 +0.4 셀(0.05)/+0.1 셀(0.03), 근거리 자취 0/311, 깊이 15 Hz·ESDF 9.5 Hz·지연 0.065/0.10 s, GPU ≤10 %·CPU 16~21 % | 09-21 §9 |
| N2~N3 | 호스트 `nvblox_nav2` 층 빌드(`isaac_ros_common` 빈 스텁으로 CUDA 회피), 로컬 코스트맵 이진 층 연결, 정지 A/B | 플러그인 연결 OK. 층이 슬라이스보다 −1 셀 평행이동 → **`lookupInSlice()` 의 round → floor 결함**(origin 은 픽셀 모서리) 발견·포크 수정·재캡처로 확정(층 외곽 = 슬라이스 외곽, 통과 측 가장자리 0.00 vs 물리 +0.011) | 09-21 §10.2~10.5, 그림 1·2 |
| N3-절단 | TSDF 절단 4 → 2 복셀 정지 A/B | 표면 뒤 띠 0.20 → 0.10 m(띠 셀 73 → 25, 상자 뒤끝 1.40 → 1.30, 물리 1.26), N0 게이트 유지. 선언 기준 T3·T6 는 전제 오류로 문구상 불합격(좌측 가구 차이는 STVL 범위 1.2 m 밖, 구멍은 1.7 m 스침각 5 cm 1 개) | 09-22 §1, 그림 3 |
| N3-감쇠 | 감쇠값 검토(사용자 질의 "속도에 맞춰 계산했나" → 아니었음, 벤더 기본) | 정지 측정: 0.95 → 관측 끊김 17 s 뒤 ESDF 소실(코스 필요 ≥ 60 s 미달), **0.99 → 81 s 유지** 채택 | 09-22 §2.1 |
| N4 | 주행 A/B, 같은 코스 S(STVL) 2 회 / N2(nvblox) 3 회, 절차 v2.0 | **5/5 성공, 중단·미달 0**. N2 코스트맵 상자 여유 12.3·13.4·14.6 cm(S 9.3·11.7, 기준선 8.4~12.9), 복귀 자리 8.3·9.7·13.5(S 9.1·8.3), 상자 기억 유지 3/3, CPU 합 330~337 vs 315~318(nvblox +18~20 %p, 릴레이·전역 STVL 잔존), GPU 3 %, 전력 +0.2 W, tj +1~2 °C | 09-22 §3~3.1, 그림 4 |
| N5 | 채택 판정(`BASELINE_STVL.md §4`) | CPU 기준만 불합격(구조적), 나머지 통과 → **결정 (a) 로컬 층 채택, N6 전역 이전** | 09-22 §3.1 |

## 2. 무엇이 달라졌고 무엇이 같은가 (측정으로 확인)
- **같은 것**: 관측된 표면(상자 앞면·왼쪽 가장자리)의 위치는 STVL 과 한 셀(5 cm) 안에서 같다. 통과 폭(감사 기준1 0.35~0.40)도 같다. 주행 성공률·중단·미달·좌우 전환은 두 층 모두 0.
- **다른 것**: (1) nvblox 는 관측면 뒤에 절단 띠(2.0 복셀 = 0.10 m)를 치명으로 두어 상자 뒤끝이 물리(1.26)에 가장 가깝다(STVL 1.25 는 뒤를 못 봄, 4.0 은 1.40). 뒤 모서리에서 원경로보다 +2.5~3.0 cm 밖으로 도는 경향은 이 때문으로 추정. (2) 기억: STVL 은 감쇠 120 s, nvblox 는 0.99 로 81 s(벤더 0.95 는 17 s). (3) 범위: nvblox 통합 2.0 m > STVL 카메라 1.2 m — 좌측 가구를 nvblox 만 본다. (4) 높이: nvblox 슬라이스 0.03~0.30 < STVL 0.06~0.40 — 가구 윗부분을 STVL 만 본다(후속 항목). (5) 부하: nvblox 노드 18~20 % CPU + GPU 3 %.
- **추정(측정 아님)**: 근거리 자취(STVL 의 min_range 0.45 사각)는 정지 게이트에서 0 이었고 주행 중 지표는 아직 없다 — bag 의 슬라이스로 후속 확인 가능.

## 3. 그림 (`Docs/05_nvblox/figures/`, 자체 완결 HTML — 브라우저로 열면 됨; 원본 아티팩트는 비공개 링크)
| # | 파일 | 내용 | 생성 스크립트 · 원자료 |
|---|---|---|---|
| 1 | `2026-09-21_costmap_stvl_vs_nvblox_v1_before_fix.html` | 로컬 코스트맵 정지 비교 v1 — STVL 층 / nvblox 층 / 차이 / 슬라이스. 층이 슬라이스보다 −1 셀 밀린 상태(결함 발견 전) | `debug_log/2026-09-21/jobs/job491_vizgen.py` · `outputs/grid_{stvl,nvblox}_costmap.json`, `grid_nvblox_slice.json` |
| 2 | `2026-09-21_costmap_stvl_vs_nvblox_v2_floor_fix.html` | 같은 비교 v2 — round→floor 수정 후. 판 E(층 vs 슬라이스 정렬 검증), V1~V4 판정표, v1 대비 | `job494_vizgen2.py` · `grid_stvl2_costmap.json`, `grid_nvfix_*.json` |
| 3 | `2026-09-22_truncation_4_vs_2.html` | 절단 4.0 vs 2.0 — STVL / t4 / t2 층, 차이 2 장, t2 슬라이스, T1~T6 판정과 정정표 | `debug_log/2026-09-22/jobs/job503_vizgen3.py` · `grid_stvl3_costmap.json`, `grid_t{4,2}_*.json` |
| 4 | `2026-09-22_n4_trajectories_stvl_vs_nvblox.html` | N4 주행 5 회 평면 궤적(base_link·차체 오른쪽 변)과 여유·CPU 표 | `job512_trajviz.py` · `outputs/n4{s1,s2,n1,n2,n3}.csv`(러너 0.1 s 계측) |
- 아티팩트 링크(비공개): v2 https://claude.ai/artifact/PRgdLzWzj1gWXvRhqwFchT · 절단 https://claude.ai/artifact/AGgeiror4K5zxVCv8RZxch · 궤적 https://claude.ai/artifact/Erz879XtFW9HVQDsgZgC9S
- bag(로컬만, git 제외): `debug_log/2026-09-22/bags/bag_n4*.tgz` — 모드 N 은 `BAG_PROFILE=nvblox`(슬라이스·점유 격자·깊이 160×120 포함, 14.5~15.2 MB), 모드 S 2.7 MB. 각 bag 폴더에 `run_meta.txt`·`params.txt`.

## 4. 채택 구성 (재현 정보)
- nvblox: 컨테이너 `isaac_ros_dev-aarch64-container`(NGC 프리빌드 이미지, `docker start` 로 복구), `ros2 run nvblox_ros nvblox_node --params-file /tmp/nvblox_n0_t2d99.yaml` — 채택본은 리포 `ros2_ws/src/rover_navigation/config/nvblox_local.yaml`. 깊이 입력 `/camera/camera/depth/image_rect_raw`(디시메이션 4, 160×120), global_frame odom, 슬라이스 z 0.03~0.30, 통합 2.0 m, 소거 반경 3 m.
- 층: 호스트 `~/ros2_ws/src/nvblox_nav2`(isaac_ros_nvblox release-3.2 + `lookupInSlice` floor 수정, Jetson 포크 미커밋 diff — `debug_log/2026-09-21/jobs/job493_fixfloor.sh` 로 재적용), `nav2_params.yaml` 로컬 `nvblox_layer`(이진, `max_obstacle_distance 0.40`, `inflation_distance 0.175`) + 기존 inflation_layer 0.40/2.5.
- 절차: `Docs/04_navigation/TEST_COURSE_AND_GATES.md` v2.1(게이트 J·K·L, `BAG_PROFILE=nvblox`).
- **bringup(N6-0, 09-22)**: `navigation.launch.py camera_layer:=nvblox|stvl`(기본 nvblox) → `/tmp/nav2_params_active.yaml` 생성 + `nvblox.launch.py`(`scripts/nvblox_up.sh`: 컨테이너 `docker start` 복구, 노드 기동, launch 종료·부모 소멸 시 2 s 안에 정리, SIGPIPE 안전). prep 만으로 모드 N 이 뜬다.

## 5. 남은 항목 (N6 이전에 또는 N6 에서)
1. ~~N6-0 bringup 통합~~ **완료(09-22 §4)**: launch 인자 `camera_layer`(기본 nvblox), 래퍼 `nvblox_up.sh`, 게이트 J 자동, V1~V5 통과. 남은 것: 실제 재부팅 뒤 prep 한 번으로 모드 N 게이트 통과 확인(컨테이너 정지 모사 V4 는 통과).
2. **N6 전역 코스트맵 이전**: 전역의 `stvl_layer` → `nvblox_layer`(map 프레임으로 TF 변환은 플러그인이 처리), `depth_relay`·STVL 제거 → CPU −40 %p 기대(릴레이 19 + STVL). 판정은 같은 코스 A/B + CPU 합.
3. 슬라이스 최대 높이 0.30 → 0.40(STVL 과 맞춤, 차체 높이 기준) 정지 A/B.
4. 러너 `job125_avoid3.py` 재고정에 위치 조건(|전면−hint|·|중심−hint| ≤ 0.06) 추가 — n4n3 ① 무효 원인.
5. 상류 보고 후보: `nvblox_nav2` `lookupInSlice` round→floor(isaac_ros_nvblox release-3.2).
6. 주행 중 근거리 자취 지표(bag 슬라이스) 추가, 게이트 job248 기준1 의 모드 N 과도값(클리어 직후 0.10) 처리.
