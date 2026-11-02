# 회전 중 장애물 번짐 — odom 좌표 코스트맵에 남는 옛 표시 (5 기: 10-02 §7.2 · §8.2 · §10~§12 · §19)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| 10-02 시점 **원인 확인 · 대책 미적용** — 번짐의 근원은 '어느 층' 이 아니라 **주행계(EKF)가 제자리 회전 중 실제 미끄러짐을 거의 못 보는 것**(통제 회전 rot2: SLAM 0.322 m vs EKF 0.003 m, 라이다 최근접 18.5 cm 감소 — **측정**). 대책 두 가지는 **기각**: B2 회전축 모델(짧은 회전에서 지금보다 나쁨 — 단 기준이 위치 추정 SLAM 이라 약함, §5) · 로컬 코스트맵 map 좌표(rot3 번짐 최대 9.2 cm, 불합격). 남은 길 = rf2o(→ [rf2o 도입](rf2o-introduction.md)) · 회전 줄이기. 이후 10-23 주 EKF 병진 = cuVSLAM | 10-02 (이 카드는 10-02 를 채우고, 6 시기 10-06 ~ 10-08 은 §7 에 흐름만 이어 채움) | [10-02 §7.2](../debug_log/2026-10-02/SUMMARY.md) — f2b3 남서 구석에서 사용자 '+36 s 에 x −1.8 이던 왼쪽 장애물이 회전하며 −1.73 까지 커진다' | [`navigation.launch.py`](../../ros2_ws/src/rover_navigation/launch/navigation.launch.py) 인자 **`local_frame:=odom|map`**(기본 odom — 61~68 행, 211 행 선언, 지금도 남아 있음). 스택 기본값은 바꾸지 않음. 러너 `run_f2b2.sh` 에 `BAG_PROFILE=nvblox` | [F2 순회와 위치 점프](f2-patrol-loc-jump.md)(§7 에서 갈라져 나옴) · [제자리 회전 옆 밀림 F0-a](f0-rotation-side-slip.md)(같은 미끄러짐의 첫 줄자) · [slam-fork-rotation.md](slam-fork-rotation.md)(회전 중 스캔 처리 포크 — 09-28) · [센서 컨디셔너](sensor-conditioner.md)(B2 · B3) · [rf2o 도입](rf2o-introduction.md) · [카메라 깊이 장애물](depth-obstacle-costmap.md)(nvblox 기억) · [nvblox 층 셀 인덱스 round → floor](nvblox-layer-round-floor.md) · [회전 방식 · 트랙 속도 비율 · 앞 회전 우선](rotation-method-track-ratio.md)(10-08 밀림 방향) · [남서 구석 정체](southwest-orient-stall.md) (6 기) |

**한 줄**: f2b3 남서 구석에서 로버가 방향을 맞추려 후진 · 회전하는 동안, map 좌표의 실제 벽은 그대로인데 odom 좌표에선 같은 벽이 12 cm 움직였고 로컬 코스트맵(odom 좌표)에 옛 표시가 남아 벽이 로버 쪽으로 두꺼워져 MPPI 가 '모든 궤적 충돌' 로 멈췄다. 층을 가르려 f2b4 출발 회전(nvblox 포함)을 봤지만 그 회전은 작아 번짐도 작았고(라이다 obstacle 층 몫), 출발 테이프 자리에서 ±90° × 3 통제 회전(rot2)을 하니 **번짐은 2.6 cm 로 작았지만 로버가 회전만으로 32 cm 미끄러졌고 EKF 는 0.3 cm 로 봤다** — 근원은 층이 아니라 주행계였다. 회전축 모델 B2 는 Nav2 의 짧은 회전에서 지금보다 나빴고(중앙 4.7 vs 3.1 cm), 로컬 코스트맵을 map 좌표로 그리는 A/B(rot3)는 위치 추정이 회전 중 미끄러짐을 일정하게 따라가지 못해(0.322 vs 0.114 m) 번짐이 오히려 9.2 cm 로 커져 불합격 → 사용자가 rf2o 도입을 결정했다. 실주행에서 번짐을 읽는 법은 '같은 벽을 EKF 좌표와 SLAM 좌표로 놓았을 때의 차이(오간 폭)' 로 정했다(§19).

## 1. 증상
- f2b3(10-02 13:25:30 기준 +26~49 s 남서 구석 기동 — 지령 v −0.06 과 ω −0.38 이 번갈아): 서쪽 구조물 안쪽 면이 라이다 map 좌표 −1.81~−1.86 으로 **그대로**인데 odom 좌표 **−1.40 → −1.53(12 cm)**, 로컬 치명 칸 안쪽 면(map 으로 옮김) −1.84 → **−1.72** 로 남음. 같은 구간 odom 이동 0.246 m · map 이동 0.153 m · map→odom 보정 0.263 m(csv +247~265 s). 차체 외곽 4.8 cm 안 치명 → 'Optimizer fail to compute path' 2 회 → 진행 검사 실패 → nav_guard 취소([10-02 §6.4 · §7.2](../debug_log/2026-10-02/SUMMARY.md), [`j816_g5log.txt`](../debug_log/2026-10-02/outputs/j816_g5log.txt)). 사용자 눈대중 '실제 여유 ~10 cm' 와 맞음.
- ⚠ §7.2 의 수치는 `f2b3_lviz.npz` 와 러너 csv(`f2b3.csv`)로 계산한 것인데 둘 다 스크래치패드에만 있어 **원천 소실**, 출력 원문 없음(SUMMARY 표만).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-02 §7.2 | 사용자 관찰을 측정으로 — 같은 벽의 map · odom · 로컬 치명 안쪽 면 시계열 | §1. 26~31 s(170° → 150°) odom −1.40~−1.42, 37~43 s(68° → 47° → 59°) odom −1.51~−1.53, 로컬 치명 −1.72 그대로 남음 | **확인** — EKF 가 회전 중 미끄러짐을 잘못 적분 → odom 좌표 로컬 코스트맵에 옛 표시 + 새 표시가 겹쳐 벽이 ≈ 12 cm 두꺼워짐. 어느 층이 옛 표시를 남겼는지는 bag 에 nvblox 슬라이스가 없어 분리 불가(러너가 `BAG_PROFILE` 안 넘김) | `job817_lviz.py` · `f2b3_lviz.npz`(소실) · 그림 [`2026-10-02_f2b3_corner.png`](../04_navigation/figures/2026-10-02_f2b3_corner.png) |
| 10-02 §7.2 대책 후보 | ① B2 · B3 켜기(09-29 §3 '회전 중 EKF 오차 1/3') ② 로컬 코스트맵 map 좌표 ③ nvblox 기억 단축(층 분리 뒤) | — | 결정 대기 | — |
| 10-02 §8.2 | B2 를 왜 껐나(09-29 §5) 다시 보기 — 10-01~02 F2 주행 csv 의 제자리 회전 구간(지령 \|ω\| > 0.15 · \|v\| < 0.03 이 1 s 이상) | **24 구간**, 회전 중앙 25° · 최대 57°. SLAM(map) 이동 D 기준 오차: 지금 EKF 중앙 **3.1** · 90 % 7.4 · 최대 10.8 cm / 병진 0 가정 4.0 · 8.1 · 9.9 / **B2 4.7** · 8.3 · 11.7 | Nav2 의 짧은 회전에선 B2 가 지금보다 나쁨 → **B2 켜기 근거 없음**(사용자에게 보류 권고). §7.2 의 12 cm 는 순수 회전이 아니라 후진 · 회전 섞인 기동에서 생김 → 회전 모델 하나로는 못 잡음. 해결 후보 ① rf2o ② 로컬 map 좌표 ③ 층 분리 먼저 | [`rot_models.py`](../debug_log/2026-10-02/jobs/rot_models.py) · [`rot_models.txt`](../debug_log/2026-10-02/outputs/rot_models.txt) · 입력 csv `f0_f2*/f2*.csv`(스크래치패드, **원천 소실**) |
| 10-02 §10 | 층 분리 시도 — f2b4 출발(남서 구석, 67° → 105° 회전 · 조금 이동), 이번엔 nvblox 슬라이스 있음 | 서쪽 구조물 안쪽 면: 라이다 map −1.84 → −1.81(3 cm) · odom −1.49 → −1.51, **로컬 치명 −1.846 → −1.789**, nvblox 장애 칸은 이 구역에 **없음**(전 구간 nan) | 회전이 작아 번짐도 작았고(5.7 cm) 그 몫은 nvblox 가 아니라 **라이다 obstacle 층**. f2b3 의 12 cm 층은 여전히 미분리. ⚠ 5.7 cm 는 로컬 치명의 '시작 값 대비' 이동이고, 같은 시각 라이다 면과의 차는 **≤ 2.2 cm**(t 17 · 22 · 25 s: −1.838/−1.816, −1.815/−1.795, −1.811/−1.789) — §5 모순 1 | [`job821_lviz.py`](../debug_log/2026-10-02/jobs/job821_lviz.py) · [`smear_layers.py`](../debug_log/2026-10-02/jobs/smear_layers.py) · [`smear_layers_f2b4.txt`](../debug_log/2026-10-02/outputs/smear_layers_f2b4.txt) |
| 10-02 §11 선언 | 통제 회전 — 처음 고른 벽 옆은 바닥 녹색 테이프(반사 유령 우려)로 사용자가 취소 → 출발 테이프 자리. 손으로 옮겨 위치 추정이 틀어져 prep 다시(원점 1.11 cm) | 정지 측정: 오른쪽 외곽 0.394 m · 왼쪽 0.335 m · 중심 최근접 0.584 m → 회전 여유 0.274 m | 방법: Nav2 목표 없이 `/cmd_vel` ω ±0.38 rad/s(MPPI 가 쓰던 값)로 EKF 각 기준 +90° → 2 s → −90° → 2 s, 3 회. 라이다 외곽 0.08 m 안이면 정지 · 중단. 지표(판정 아닌 기준선, 차체 기준이라 위치 추정과 무관): **번짐 = 라이다 외곽 최근접 − 로컬 치명 외곽 최근접**, 옛 칸 = 외곽 0.6 m 안 치명 칸 중 0.10 m 안에 라이다 점도 nvblox 장애도 없는 것, 누적 이동 EKF vs SLAM | [`job823_wallgap.py`](../debug_log/2026-10-02/jobs/job823_wallgap.py) · [`j826_prep.txt`](../debug_log/2026-10-02/outputs/j826_prep.txt) · [`job825_rot.py`](../debug_log/2026-10-02/jobs/job825_rot.py) |
| 10-02 §11.1 rot1 | 첫 시험 | +62° · 4.7 s 에서 안전 정지 — 원문 '외곽 최소 **0.000 m**'. 사람(사용자)이 로버를 옮기려 다가옴 | 무효. SUMMARY 의 '차체 뒤왼쪽 0.35~0.42 m 에 라이다 점 52~143 개' 는 **라이다 거리**(range)이고 외곽 여유가 아니다(§5 모순 2) | [`j825_rot1.txt`](../debug_log/2026-10-02/outputs/j825_rot1.txt) · `job827_gapchk.py`(출력 원문 없음) |
| 10-02 §11.1 rot2 | 사용자가 45 cm 앞으로 옮긴 자리, ±90° × 3 완료(회당 4.5~6.2 s) | 회마다 외곽 최소 0.335 → 0.309 → 0.268 → 0.254 → 0.204 → 0.212 m(시작 0.397). 번짐 최대 **+2.6 cm** · 끝 +0.4. nvblox 는 이 장애물을 거의 안 봄(0.33~0.66 m). 옛 칸 **4 → 95**(치명 칸 78 → 177). **누적 이동 SLAM 0.322 m vs EKF 0.003 m** | 번짐의 근원은 층이 아니라 **주행계가 회전 중 미끄러짐을 못 보는 것**. 옛 칸이 로버 쪽에 생기느냐(f2b3, 12 cm 가깝게) 반대쪽이냐(rot2, 장애물 뒤쪽 — 그래서 최근접 번짐은 작음)는 **미끄러진 방향**에 달림(추론). 540° 에 ≈ 30 cm = 09-28 '180° 당 10~27 cm' 와 같은 성질 | [`j825_rot2.txt`](../debug_log/2026-10-02/outputs/j825_rot2.txt) · [`smear_rot.py`](../debug_log/2026-10-02/jobs/smear_rot.py) · [`smear_rot2.txt`](../debug_log/2026-10-02/outputs/smear_rot2.txt) · `job828_lviz.py`(0.5 s) · bag `bag_rot2`(**소실** — 10-06 §2) |
| 10-02 §12 선언 | 대책 1 A/B: `local_frame:=map` — local_costmap `global_frame` 과 nvblox 층 `nav2_costmap_global_frame` 을 map 으로(nvblox 층은 슬라이스를 TF 로 변환하는 코드가 있음, `nvblox_costmap_layer.cpp` 236~255 행). Nav2 만 재시작(위치 추정 유지). 로버를 rot2 시작 자리로 | — | 판정(rot2 대비): ① 옛 칸 최대 95 → **≤ 30** ② 번짐 최대 **≤ 3 cm** 유지 ③ 계단식 이동 횟수 기록 | [`job830_localmap.sh`](../debug_log/2026-10-02/jobs/job830_localmap.sh) |
| 10-02 §12.1 rot3 | 같은 회전 · 같은 지표(`smear_rot.py … map`) | 외곽 최소 0.407 → 0.192 m(rot2 와 비슷한 미끄러짐). 옛 칸 최대 **59**(✗ ≤ 30) · 번짐 최대 / 끝 **9.2 / 2.9 cm**(✗ ≤ 3) · 누적 이동 SLAM **0.114** / EKF 0.003 m | **불합격, 채택 안 함** → odom 으로 되돌림(인자는 launch 에 남김). 해석: 같은 종류의 회전인데 SLAM 이 본 이동이 0.322 vs 0.114 m — **위치 추정 모드는 회전 중 미끄러짐을 일정하게 따라가지 못함**(노드 간격 0.30 m · 0.15 rad 라 갱신이 계단식) → map 좌표로 그려도 계단식으로 어긋남 | [`j825_rot3.txt`](../debug_log/2026-10-02/outputs/j825_rot3.txt) · [`smear_rot3.txt`](../debug_log/2026-10-02/outputs/smear_rot3.txt) · `job831_lviz.py` · [`job832_revert.sh`](../debug_log/2026-10-02/jobs/job832_revert.sh) · 그림 [`2026-10-02_smear_rot23.png`](../04_navigation/figures/2026-10-02_smear_rot23.png) |
| 10-02 §12.1 정리 | B2(§8.2) · map 좌표(§12) 둘 다 회전 미끄러짐을 못 풂 | — | 남은 길 ① 회전 자체 줄이기(§7.1 대책 A — 중간 목표 방향 무시) ② **rf2o**(원래 JetPack 7.2 단계) → §13 사용자 결정 | — |
| 10-02 §13.2 (rf2o 카드) | rot3 줄자 | 실제 **뒤 27.5 · 오른쪽 24.5 cm(0.368 m)** — SLAM 0.114 m 는 틀림, rf2o 0.370 m 가 맞음 | §12.1 의 'SLAM 이 회전 중 미끄러짐을 일정하게 못 따라감' 을 **줄자로 확인**. 동시에 §8.2 B2 비교의 기준(SLAM)도 같은 약점을 가짐(§5 실수 1) | [rf2o 도입](rf2o-introduction.md) |
| 10-02 §15 · §16 | 하루 마무리 그림 + rf2o 로 보정한 EKF B 의 독립 검사 | 정적 구조물을 각 EKF 자세로 odom 좌표에 놓았을 때 첫 스캔과의 어긋남 중앙: rot3 A 22.1 · **B 3.2 cm**, rot2 A 23.1 · **B 2.5 cm**. A 의 어긋남이 회전마다 커짐 = 로컬 코스트맵 번짐과 같은 현상 | rf2o 를 넣으면 '같은 벽이 odom 에서 제자리' 에 가까워짐(재생) | [`render_day1002.py`](../debug_log/2026-10-02/jobs/render_day1002.py) · [`render_ekfB_slip.py`](../debug_log/2026-10-02/jobs/render_ekfB_slip.py) · 그림 [`2026-10-02_ekfB_slip.png`](../04_navigation/figures/2026-10-02_ekfB_slip.png) — 수치는 화면 출력뿐(**출력 원문 없음**) |
| 10-02 §19 | 사용자 질의 '`f2b3_wall_AB.png` 의 EKF 곡선과 SLAM 곡선 차이를 벽 번짐으로 읽으면 되나' | f2b3 구석 기동(13:25:56~14:19) 로버 쪽 벽 면(x 95 백분위): 기동 중 \|최대\| 차 EKF A − SLAM **16.8 cm** · B − SLAM 8.4, 기동 뒤 남은 차 A **−15.2 cm**(≈ 3 칸) · B **−4.9 cm**(≈ 1 칸) | **근사적으로 그렇다(SLAM 이 맞다는 전제)** — 세 곡선은 같은 스캔 점을 각자의 자세로 옮긴 것이라 '보이는 부분이 바뀌는 몫' 이 공통 → 빼면 odom 좌표에서 벽이 밀려 보인 양만 남음. 읽는 법 ① 번짐 두께 = 차이가 **오간 폭**(표시는 지워지기 전까지 쌓임) ② SLAM 도 틀릴 수 있음(rot3 36.8 중 11 cm 만 봄) → SLAM 이 튄 순간은 과대, 안정된 끝값이 더 믿을 만함 | 그림 [`2026-10-02_f2b3_wall_AB.png`](../04_navigation/figures/2026-10-02_f2b3_wall_AB.png)(범례 범위 A 19.8 · B 9.9 · SLAM 8.4 cm) · `render_day1002.py` ③ · 차 표 수치는 **출력 원문 없음** |
| 10-02 §19 적용 | 실주행 분석 · 통제 시험 규칙 | — | 줄자 없는 실주행 = 'SLAM 과의 차이' 로 번짐을 읽음(이름도 그렇게). 통제 시험(§17 단계별) = 줄자를 정답으로, SLAM 도 비교 대상에 넣어 SLAM 자체의 회전 중 오차를 같이 재고 그 값으로 실주행 차이의 신뢰 범위를 정함 | — |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| f2b3 의 12 cm 두꺼워짐 = nvblox 기억(감쇠 느림) | f2b3 bag 에 슬라이스 없음 / f2b4 출발 회전엔 nvblox 장애 칸이 그 구역에 없음 | f2b4 번짐은 라이다 obstacle 층 몫 | f2b3 자체는 **미확인**(층 미분리), f2b4 에선 **기각** |
| 번짐 = 라이다 obstacle 층이 옛 칸을 못 지움(빔이 지나가면 지우게 돼 있는데 남음) | rot2 옛 칸 계수 | 근거 없는 치명 칸 4 → 95 로 쌓임 | 옛 칸이 남는 것은 **지지**, 지우지 못한 기전(빔이 그 칸을 지나지 않는 방향 등)은 **미확인** |
| 근원 = 주행계가 회전 중 미끄러짐을 못 봄 | 통제 회전에서 SLAM · 라이다 거리 vs EKF | SLAM 0.322 · 라이다 최근접 −18.5 cm vs EKF 0.003 m(rot2), 줄자 0.368 vs EKF 0.003(rot3) | **지지(측정)** |
| B2(회전축 고정 모델)가 짧은 회전에서도 낫다 | F2 주행 24 회전 구간, SLAM 기준 | B2 중앙 4.7 > 지금 3.1 cm | **기각** — 단 기준인 위치 추정 SLAM 이 회전 중 미끄러짐을 놓치는 것이 나중에 드러나 근거가 약함(§5 실수 1) |
| 로컬 코스트맵을 map 좌표로 그리면 번짐이 준다 | rot3 A/B | 옛 칸 95 → 59 지만 번짐 2.6 → 9.2 cm | **기각**(선언 기준 둘 다 불합격). rot2 · rot3 의 SLAM 추적량이 달라(0.322 vs 0.114) 한 변수 A/B 는 아님 |
| EKF − SLAM 차이 ≈ 벽 번짐(사용자 질의) | 같은 스캔을 세 자세로 — 공통 몫 상쇄 | A 끝 −15.2 cm ≈ 구석 정체와 부합 | **근사적으로 지지**(SLAM 이 맞을 때만) |

## 4. 조치와 효과
- **`local_frame` 인자**(10-02 §12): [`navigation.launch.py`](../../ros2_ws/src/rover_navigation/launch/navigation.launch.py) 61~68 행 — `local_frame:=map` 이면 `local_costmap.global_frame` 과 `nvblox_layer.nav2_costmap_global_frame` 을 map 으로. rot3 에서 불합격 → 기본 odom 으로 되돌림, 인자는 남김(지금도 기본 `odom`, 211 행). 효과 수치는 §2 표.
  - ⚠ rot3 은 **10-27 이전의 호스트 nvblox 층**으로 돌았다. 10-27 에 이 층이 'TF 조회 실패 시 슬라이스를 단위 변환(항등)으로 써서 odom 슬라이스를 map 에 적는' 결함이 확인돼 고쳐졌다(`Docs/05_nvblox/nvblox_nav2_rover.patch`, [10-27 SUMMARY](../debug_log/2026-10-27/SUMMARY.md) §15 이후). local_frame:=map 은 그 변환 경로를 쓰므로 rot3 에 영향이 있었는지는 **미확인**(rot 시험에서 nvblox 는 장애물을 거의 안 봐 영향은 작았을 것으로 추정).
- **B2 · B3 는 켜지 않음**(§8.2 권고 · 사용자 보류). 지금 `ekf.launch.py` 의 `icr`(B2) 기본 false · `rot_cov`(B3) 기본 false — 단 `rf2o:=true` 또는 `vslam:=on|shadow` 이면 B3 가 σ 0.3 으로 자동으로 켜진다(39~40 행, 지금 prep 기본 `vslam:=on` 이라 실주행에선 B3 켜짐 — [센서 컨디셔너](sensor-conditioner.md) §0).
- **러너 `BAG_PROFILE=nvblox`**(f2b4 부터): 층 분리가 가능해짐.
- **분석 규칙**(§19): 실주행 번짐 = EKF − SLAM 의 오간 폭으로 읽음.

## 5. 내 실수
**실수 1 — B2 를 기각한 기준이 '회전 중 SLAM' 이었다(§8.2, 이 카드 작성 중 발견)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | B2 를 왜 껐는지 다시 보고 켤지 판단 — `rot_models.py` 가 F2 주행 csv 의 제자리 회전 24 구간에서 지금 EKF · 병진 0 · B2 의 이동을 **SLAM(map) 이동 D** 와 비교 |
| 본 것 | 오차 중앙 지금 3.1 · 병진 0 4.0 · B2 4.7 cm → 'B2 켜기 근거 없음' |
| 처음 추론 | 09-29 §3.1 의 '회전 중 SLAM 오차 1~2 cm' 를 근거로 SLAM 을 기준으로 씀(도구 머리 주석) |
| 의심한 이유 | 같은 날 §12.1 에서 위치 추정 모드 SLAM 이 같은 종류의 회전에 0.322 vs 0.114 m 로 들쭉날쭉, §13.2 줄자는 rot3 의 실제 0.368 m 중 SLAM 이 0.114 m 만 봤다고 판정. 09-29 §3.1 은 **매핑 모드**(노드 간격 0.05 m · 0.03 rad) 측정이고, 10-01~02 F2 csv 는 **위치 추정 모드**(0.30 m · 0.15 rad) 주행이다 |
| 판별 | 하지 않음(이 카드 작성 중 발견). rot_models 의 24 구간을 rf2o(10-02 이후 기준) 또는 줄자 기준으로 다시 계산해야 판별 가능 |
| 결론 | 'B2 가 지금보다 나쁘다' 는 결론의 기준이 약하다 — **미확인**. 다만 B2 를 껐던 09-29 근거(부분 회전에서 옆 성분이 틀려 SLAM 이 되돌림)와 이후 rf2o · cuVSLAM 채택으로 실제 결정은 바뀌지 않았다 |
| 다음에 알아보는 법 | 'SLAM 을 정답으로' 쓸 때는 **그 SLAM 이 매핑 모드인지 위치 추정 모드인지**와 노드 간격을 같이 적는다. 위치 추정 모드의 회전 중 이동은 정답으로 쓰지 않는다 |
| 데이터 | [`rot_models.py`](../debug_log/2026-10-02/jobs/rot_models.py) · [`rot_models.txt`](../debug_log/2026-10-02/outputs/rot_models.txt) · 입력 `f0_f2*/f2*.csv`(스크래치패드, **원천 소실**) · 대조 [`smear_rot2.txt`](../debug_log/2026-10-02/outputs/smear_rot2.txt) · [`smear_rot3.txt`](../debug_log/2026-10-02/outputs/smear_rot3.txt) |

**실수 2 — 통제 회전 bag 에 `/imu/data` 를 안 넣음(§11)**: 기록 토픽 목록(`job825_rot.py` 의 `TOP`)에 `/imu/data` 가 빠져, 같은 날 R2 1 차 재생에서 rf2o 게이트의 자이로가 0 이 되어 회전 중 rf2o 를 거의 다 버렸다(→ [rf2o 도입](rf2o-introduction.md) §5). 이 카드의 번짐 지표에는 영향 없음. 알아보는 법: 시험 bag 토픽은 '나중에 재생할 노드의 입력' 기준으로 고른다. 또 rot2 · rot3 bag 은 Jetson `/tmp` 에만 있다가 재부팅으로 소실(10-06 §2 — 줄자 대조 재현 불가).

**모순 · 원문 대조(이 카드를 쓰며 찾은 것)**
1. §10 '로컬 치명 −1.846 → −1.789(최대 5.7 cm 안쪽)': [`smear_layers_f2b4.txt`](../debug_log/2026-10-02/outputs/smear_layers_f2b4.txt) 에서 이 값은 로컬 치명 면의 **시작 대비 이동**이다. 같은 시각 라이다가 본 면(−1.811~−1.838)과의 차는 2.0~2.2 cm 이고, 라이다 면 자체가 3 cm 움직였다(보이는 부분 변화). 즉 '번짐(라이다 − 로컬)' 으로 읽으면 **약 2 cm**. 또 t 28~39 s 는 라이다 점이 그 구역에 없는데(nan) 로컬 치명 면이 −1.886 · −1.905 로 바깥으로 옮겨져 있다 — 원인 미확인.
2. §11.1 rot1 '차체 뒤왼쪽 0.35~0.42 m 에 라이다 점': 원문 [`j825_rot1.txt`](../debug_log/2026-10-02/outputs/j825_rot1.txt) 는 '외곽 최소 0.000 m' 로 중단. `job827_gapchk.py` 가 찍는 '거리' 는 **라이다에서의 거리**(range)라 외곽 여유와 다른 값 — SUMMARY 문장만 읽으면 여유 35 cm 로 오해할 수 있다. 실제로는 사람이 차체 외곽에 붙어 있었다.
3. §12 A/B 는 '로컬 좌표' 하나만 바꾼 시험이지만 결과는 그 시각 위치 추정의 회전 추적량(0.322 vs 0.114)에 좌우됐다 — 같은 조건 반복이 없어 map 좌표 방식의 평균 성능은 **미확인**.

## 6. 남은 것 (10-02 시점)
- 근본 대책(주행계가 회전 중 병진을 보게) — rf2o R2 오프라인만 통과, 라이브 미적용.
- f2b3 12 cm 가 어느 층이었는지 — 미분리.
- 라이다 obstacle 층이 '빔이 지나가면 지운다' 는데 옛 칸이 남는 기전 — 미확인.
- 회전 자체 줄이기(중간 목표 방향 무시) — 결정 대기.
- 피벗 회전(한 트랙 정지 회전, 사용자 §13)이 미끄러짐을 줄이는지 — 미시험.

## 7. 6 시기 (10-06 ~ 10-08) — 이 카드에 닿는 것 (10-06 · 10-07 · 10-08 기록에서)
이 시기에 '번짐' 자체(로컬 코스트맵의 옛 칸)를 다시 잰 시험은 없다. 근원(주행계가 회전 중 미끄러짐을 못 봄)에 대한 측정과, 순회 중 번짐 판정 시도 하나가 있다.

| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-06 §4.1 | 근원 대책(rf2o 속도를 EKF 에)의 라이브 측정 — 단계별 90° × 6, 줄자 | EKF B(rf2o) 줄자 대비 평균 **1.5 cm**, 원위치 단계 0.0 · 0.1 · 0.7. 그림자 A(지금까지 구성) 원위치 단계 −10.0 · −15.5 · −17.0 cm 누적 | odom(EKF B)이 회전 중 밀림을 따라감 → odom 좌표 로컬 코스트맵에 옛 표시가 남는 근원이 줄어들 것(**추정** — 코스트맵 번짐은 이 시험에서 재지 않음. bag 에 `/local_costmap/costmap` 은 기록됨) | [F0-a 카드 §7.9](f0-rotation-side-slip.md) · [`step_state_1.json`](../debug_log/2026-10-06/outputs/step_state_1.json) · [`step_tape.csv`](../debug_log/2026-10-06/outputs/step_tape.csv) · bag `2026-10-06/bags/bag_step1.tgz`(PC 로컬) |
| 10-07 §2 선언 | rf2o 켠 F2 순회(f2c) 판정 ③-b '번짐(핵심)': 제자리 회전 구간마다 **EKF B − SLAM 위치 차(오간 폭)** 가 그림자 A 보다 작고 최대 ≤ 5 cm. 비교 기준 10-02 f2b3 실측 A 15 cm · 재생 추정 B 5 cm | — | §19 읽는 법을 판정에 씀 | [10-07 SUMMARY](../debug_log/2026-10-07/SUMMARY.md) §2 |
| 10-07 §3.3 | f2c1 · f2c2 의 제자리 회전 구간(\|ω\| > 0.15 · \|v\| < 0.03 이 1.5 s 넘게) | f2c1 2 구간(−24° · +51°): SLAM 이동 3.3 · 2.1, B − SLAM 4.2 · 3.8, A − SLAM 4.6 · 4.3 cm. f2c2 2 구간(−35° · −28°): 8.9 · 5.7 / **10.3** · 6.6 / 11.8 · 7.3 cm. B < A 4/4(차 0.4~1.5 cm) | **판정 불가에 가까움** — 최대 10.3 > 5 로 선언 기준은 불합격이지만 ① 제자리 회전이 4 번뿐(순회 회전은 대부분 곡선) ② 기준 SLAM 이 회전 직후 보정이라 그 자체 오차가 수 cm ③ G4 가 이 구간 rf2o 를 줄인 몫이 섞임. 10-06 줄자 시험이 더 직접적 근거 | [`f2c_anal.py`](../debug_log/2026-10-07/jobs/f2c_anal.py) · [`f2c_anal.txt`](../debug_log/2026-10-07/outputs/f2c_anal.txt) · 입력 `x913_f2c*.npz`(스크래치패드, **원천 소실** — bag `2026-10-07/bags/bag_f2c1 · f2c2.tgz` 는 PC 로컬) |
| 10-07 §3.2 | 같은 순회의 rf2o 게이트 G4 | 곡선 회전에서 σ 키움 43~58 %(정상 전진 속도가 문턱 0.05 에 걸림) | G4 설계 결함 → 10-07 §4 휠 잔차 기준으로 수정([rf2o 도입](rf2o-introduction.md) 이후 칸) | `f2c_anal.txt` · [`f2c_g4arc.txt`](../debug_log/2026-10-07/outputs/f2c_g4arc.txt) |
| 10-08 §4 | 순회 bag 6 개(f2c1~f2e2)의 ≥ 45° 회전 22 개를 스캔 직접 정합으로 — **실제** 미끄러짐(EKF 오차가 아님) | 90°당 중앙 제자리 9.8 · 피벗형 7.6 · 중간 2.8 cm, 범위 2.1~16.2. 앞뒤 성분이 21/22 회 **차체 뒤쪽** | 순회 회전에서도 번짐을 만들 만큼(수 cm~16 cm) 미끄러진다 — 그 밀림이 주로 '뒤' 라는 방향 정보가 새로 생김. 이 회전들에서 EKF B 가 얼마나 따라갔는지는 **재지 않음** | [회전 방식 카드](rotation-method-track-ratio.md) · [`rot2_stats.txt`](../debug_log/2026-10-08/outputs/rot2_stats.txt) · [`slip_consistency.txt`](../debug_log/2026-10-08/outputs/slip_consistency.txt) |
| 10-08 §5.6 · §6.1 · §7 | 통제 회전 40 회(트랙 비율 시험) | 방향 일정(38/40 뒤), 크기 변동계수 66 %, 시간에 따라 커짐 | 회전 방식으로 밀림(=번짐의 근원)을 줄인다는 근거 없음. 고정 보정 대신 rf2o · 가변 σ(§7 ③) | 같은 카드 |

**어긋남(원문 대조, 11-02)**
1. **10-07 §2 의 '오간 폭'** 과 §3.3 을 낸 계산이 다르다. `f2c_anal.py` 는 회전 구간 시작 · 끝 두 시각의 **변위 차의 크기** `np.linalg.norm(dB - dS)` 를 낸다(18~23 행) — 10-02 §19 의 '오간 폭'(기동 중 차이가 오간 범위)이 아니고, 벽 면 자체도 보지 않는다. 또 SLAM 끝 자세는 `comp(at(mo, te + 2.0), at(ob, te))` — map→odom 은 끝 + 2 s, odom 은 끝 시각을 섞는다(회전 직후 SLAM 보정을 기다리려는 의도로 보임, 주석 없음).
2. 같은 표에서 f2c1 −24° 구간은 **B − SLAM 4.2 cm 가 SLAM 이 본 이동 3.3 cm 보다 크다** — 두 추정이 다른 방향으로 갔거나 SLAM 이 덜 본 것. 어느 쪽인지 **미확인**(정답 없음).

**이후(10-12 ~) — 포인터(다음 시기에서 채움)**
- 10-12 PreferForward 15(앞 회전 우선, 후진 2.93 → 0.2~0.4 m) — [회전 방식 카드](rotation-method-track-ratio.md) 이후 칸.
- 10-13 · 10-15 상자 옆 정지: nvblox 가 odom 좌표라 기억된 상자가 4~5 cm 밀림 + 5 cm 칸 판정 — 같은 'odom 좌표 기억' 계열(메모리 '상자 옆 정지', [10-13 SUMMARY](../debug_log/2026-10-13/SUMMARY.md) §12.2 · §15).
- 10-20 cuVSLAM 병진 속도 융합(W3 회전 창 −12~29 %) → **10-23 §16 주 EKF 병진 = cuVSLAM**(`ekf.launch vslam:=on`, prep 기본) — [10-23 SUMMARY](../debug_log/2026-10-23/SUMMARY.md). '상자 옆 근접은 이것으로 안 풀림' 도 같은 §.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2b3 남서 구석 기동 | 번짐 첫 측정(12 cm) | `f0_f2b3_runner.log` · `j816_g5log.txt` (npz · csv 소실) |
| f2b4 출발 회전 | 층 분리 시도(nvblox 포함) | `smear_layers_f2b4.txt` |
| rot1 | 통제 회전 — 사람 접근 중단 | `j825_rot1.txt` |
| rot2 | 통제 회전 ±90° × 3, 로컬 odom | `j825_rot2.txt` · `smear_rot2.txt` (bag 소실) |
| rot3 | 같은 회전, 로컬 map | `j825_rot3.txt` · `smear_rot3.txt` (bag 소실) |
| 회전 구간 24 개 | B2 · 병진 0 · 지금 EKF 비교 | `rot_models.txt` |
| 그림 | 번짐 · 옛 칸 시계열, 구석 벽 A/B | `Docs/04_navigation/figures/2026-10-02_smear_rot23.png` · `_f2b3_wall_AB.png` · `_ekfB_slip.png` |
| 도구 | `job821_lviz.py` · `smear_layers.py` · `job823_wallgap.py` · `job825_rot.py` · `job825.sh` · `job827_gapchk.py` · `job828/831_lviz.py` · `smear_rot.py` · `job830_localmap.sh` · `job832_revert.sh` · `rot_models.py` · `render_day1002.py` | `2026-10-02/jobs/` |
| **6 시기** step1(10-06) · f2c1 · f2c2(10-07) · 주행 회전 22 개(10-08) | 근원 대책 줄자 확인 · 순회 번짐 판정 시도 · 실제 미끄러짐 방향 | [F0-a 카드 §7.9](f0-rotation-side-slip.md) · `2026-10-07/outputs/f2c_anal.txt` · [회전 방식 카드](rotation-method-track-ratio.md) |

## 9. 도구 해설
공통: bag 장면 추출은 `job8xx_lviz.py` 한 본문(해설은 [F2 순회와 위치 점프 §9](f2-patrol-loc-jump.md) 의 job817_lviz). 추출 npz · 러너 csv 는 PC 스크래치패드에 있었고 **지금은 소실** — 분석 출력 txt 만 남았다. 차체 외곽은 앞 0.262 · 뒤 0.248 · 옆 0.165 m, 라이다는 차체 x 0.152 · yaw π − 0.04677(데크 보정)로 모든 도구가 같은 상수를 직접 박아 넣었다(URDF 를 읽지 않음 — 데크를 다시 재면 이 도구들도 고쳐야 함).
도구 계보: (번짐 지표) §7.2 손 계산(map · odom 면) → §10 `smear_layers.py`(층별 면, map 좌표 구역) → §11 `smear_rot.py`(차체 기준 최근접 · 옛 칸 · 누적 이동) → §16 `render_ekfB_slip.py`(정적 구조물을 EKF 자세로 놓아 첫 스캔과의 어긋남 — 줄자 없는 독립 검사) → §19 'EKF − SLAM 면 차' → 10-07 §3.3 번짐 판정(판정 불가에 가까움).

### smear_layers.py — 층별 벽 안쪽 면 (PC, Python)
- 부른 형태: `python smear_layers.py f2b4s_lviz.npz [T0]`.
- 왜: f2b3 의 12 cm 가 nvblox 기억인지 라이다 obstacle 층인지 가르려고(§10).
- 하는 일: 표본마다(1 s) 서쪽 구조물 구역(map y −5.95~−5.35, x −2.1~−1.6)에서 ① 라이다 점의 x 95 백분위(map) 와 그 점을 map→odom 역변환한 odom 좌표 값 ② nvblox 슬라이스 중 거리 ≤ 0.05 m 칸(장애)을 map 으로 옮긴 최대 x ③ 로컬 코스트맵 값 ≥ 100 칸을 map 으로 옮긴 최대 x ④ 로컬 치명 중 0.1 m 안에 nvblox 장애가 없는 칸의 최대 x(= 라이다 층 몫 추정).
- 출력: [`smear_layers_f2b4.txt`](../debug_log/2026-10-02/outputs/smear_layers_f2b4.txt)(열: t · 로버 θ · map→odom x · 라이다 map/odom · nvblox · 로컬 치명 · 로컬 치명 중 nvblox 없음).
- 결함: 구역 · 면 정의가 이 구조물 전용. 라이다는 95 백분위, 로컬은 최대값이라 두 열의 '면' 정의가 다르다(직접 빼면 1~2 cm 는 정의 차일 수 있음). nvblox 가 이 구역을 못 봐 ④ 열이 전부 nan.
- 지금 다시: 그대로는 안 씀(구역 하드코딩).

### job823_wallgap.py — 회전 전 여유 (Jetson, rclpy)
- `/scan` 최대 10 장(4 s)을 받아 마지막 장을 차체 좌표로(0.2~3 m), 왼 · 오른 · 앞 · 뒤 방향별 외곽 최소 거리와 그 점, 중심 최근접 − 0.31(모서리 반경) = 제자리 회전 여유. 출력 원문 없음(SUMMARY §11 수치만).

### job825_rot.py · job825.sh — 통제 회전 (Jetson, rclpy + ros2 bag)
- 부른 형태: `python3 -u /tmp/job825_rot.py bag_rot2`(sh 는 rot2 용 한 줄 + bag 크기 확인).
- 왜: Nav2 · MPPI 없이 같은 회전을 반복해 번짐을 '기준선' 으로 재려고(§11).
- 하는 일: ① `ros2 bag record` 를 자식 프로세스로 — `/scan /tf /tf_static /map /local_costmap/costmap /nvblox_node/static_map_slice /odometry/filtered /wheel_odom /cmd_vel`(**/imu/data 없음** — 실수 2) ② `/odometry/filtered` 의 yaw 와 `/scan` 의 외곽 최소 거리(위 상수)를 콜백으로 갱신 ③ 4 s 대기 후 3 회 × (+, −): 매 0.05 s ω = ±0.38 발행, EKF yaw 증분의 절댓값 합이 90° 가 되거나 10 s 넘으면 정지 신호 10 회, 외곽 < 0.08 m 면 중단 ④ 각 회 사이 2 s ⑤ 끝나면 bag 기록기에 SIGINT.
- 출력: 화면 — 시작 epoch · yaw · 외곽 최소, 회마다 '각도 / 시간, 외곽 최소' → [`j825_rot1.txt`](../debug_log/2026-10-02/outputs/j825_rot1.txt) · [`_rot2.txt`](../debug_log/2026-10-02/outputs/j825_rot2.txt)(첫 줄에 WSL 깨진 문자 섞임) · [`_rot3.txt`](../debug_log/2026-10-02/outputs/j825_rot3.txt). bag `/tmp/bag_rot{1,2,3}` → **소실**(10-06 §2).
- 결함: 각도는 EKF yaw(자이로 지배)라 실제 회전과 맞음. 미끄러짐 자체는 안 재고 bag 으로 사후 분석. 안전 정지 문턱 0.08 m 는 외곽 기준이라 사람 손 · 몸이 붙어도 정지(rot1).
- 계보: 10-06 단계별 회전(한 번에 90°, 줄자 · 상태 저장) 판으로 이어짐(10-02 §17 설계 → [rf2o 도입](rf2o-introduction.md)).

### job827_gapchk.py — rot1 중단 원인 (Jetson, rosbag2_py)
- `/tmp/bag_rot1` 의 스캔마다 외곽 최소 거리 · 그 점의 차체 좌표 · **라이다 거리** · 0.08 m 안 점 수를 외곽 < 0.15 m 일 때만 출력. 출력 원문 없음. SUMMARY 의 '0.35~0.42 m' 는 이 '라이다 거리' 열(모순 2).

### smear_rot.py — 통제 회전 번짐 지표 (PC, Python)
- 부른 형태: `python smear_rot.py rot2_lviz.npz [odom|map]`(두 번째 인자 = 로컬 코스트맵이 그려진 좌표, §12 에서 추가).
- 하는 일: 표본마다(0.5 s) ① 로버 map 자세와 map→odom 으로 odom 자세 계산 ② 라이다 점 · 로컬 치명(≥ 100) 칸 · nvblox 장애(≤ 0.05 m) 칸을 모두 **차체 기준**으로(로컬은 인자에 따라 map 또는 odom 자세로, nvblox 는 항상 odom 자세로) ③ 각자의 외곽 최소 거리, **번짐 = 라이다 − 로컬**(양수 = 실제보다 가깝게 표시) ④ 외곽 0.6 m 안 로컬 치명 칸 중 0.10 m 안에 라이다 점(외곽 0.6 m 안 것)도 nvblox 장애도 없는 칸 = '옛 칸', nvblox 만 근거인 칸 ⑤ 첫 표본 대비 map · odom 누적 이동.
- 출력: [`smear_rot2.txt`](../debug_log/2026-10-02/outputs/smear_rot2.txt) · [`smear_rot3.txt`](../debug_log/2026-10-02/outputs/smear_rot3.txt)(1 s 간격 표 + 끝 요약 '번짐 최대 · 마지막 · 옛칸 최대 · 끝 누적 이동'). `render_day1002.py` 가 이 파일을 `exec` 로 다시 돌려 그림 [`2026-10-02_smear_rot23.png`](../04_navigation/figures/2026-10-02_smear_rot23.png).
- 쓰인 곳: §11.1 · §12.1 판정.
- 결함: '번짐' 은 **최근접 한 점**만 본다 — 옛 칸이 장애물 뒤쪽에 쌓이면(rot2) 0 에 가깝게 나온다(그래서 옛 칸 수를 같이 봄). '누적 이동 map' 은 위치 추정 SLAM 이라 회전 중엔 틀릴 수 있음(rot3 0.114 vs 줄자 0.368).
- 지금 다시: 같은 형식 npz 가 있으면 그대로 쓸 수 있음(상수 하드코딩).

### job830_localmap.sh · job832_revert.sh — local_frame A/B 배포 · 복귀 (Jetson, bash)
- 830: 스크래치패드 경유 `navigation.launch.py` 를 `~/ros2_ws/src/rover_navigation/launch/` 로 복사 → `colcon build --packages-select rover_navigation` → `NAV_EXTRA="local_frame:=map" bash /tmp/job760_nav2_restart.sh`(Nav2 만 재시작) → `local_costmap.global_frame` · `nvblox_layer.nav2_costmap_global_frame` · `/local_costmap/costmap` 헤더 frame_id · nav2.log 오류 확인. 832: `NAV_EXTRA=""` 로 다시 재시작 · global_frame 확인. 출력 원문 없음.
- ⚠ 실행 중 코스트맵 설정을 바꿔 Nav2 를 재시작한 뒤 이어 주행한 경우가 있다면, 10-14 에 확인된 '실행 중 패딩 변경 뒤 MPPI 멈칫' 과 같은 계열인지는 미확인(10-02 에는 재시작 방식이라 해당 없을 것으로 추정).

### rot_models.py — 회전 중 이동 모델 비교 (PC, Python)
- 부른 형태: `python rot_models.py`(스크래치패드의 `f0_f2*/f2*.csv` 를 읽음 — F2 러너 csv).
- 하는 일: csv 마다 지령 |w| > 0.15 · |v| < 0.03 이 1 s 이상 이어진 구간 → map 이동 D(정답으로 씀), odom 이동을 시작 시각 map→odom yaw 로 map 좌표로 옮긴 값(지금 EKF), 0(병진 0), B2 = 09-29 §1 의 180° 당 이동 2p(시계 (−0.059, 0.102) · 반시계 (−0.062, −0.186), 로버 시작 자세 기준)를 회전각 비례로 → 각 |모델 − D| 의 중앙 · 90 % · 최대, 회전각 구간별(0~60 · 60~120 · 120° 이상).
- 출력: [`rot_models.txt`](../debug_log/2026-10-02/outputs/rot_models.txt) — 24 구간 전부 0~60° 구간.
- 결함: 정답 D 가 위치 추정 SLAM(실수 1). 120° 이상 구간이 하나도 없어 B2 가 맞던 180° 영역은 비교되지 않음.

### render_day1002.py — 하루 그림 4 장 (PC, matplotlib)
- ① `rot3_paths.png`(줄자 대비 A · B · SLAM · rf2o 궤적 — rf2o 카드) ② `smear_rot23.png`(`smear_rot.py` 를 exec 해 줄을 정규식으로 읽음 — 번짐 · 옛 칸 시계열) ③ `f2b3_wall_AB.png`(`r2_f2b3.npz` 의 스캔 중 서쪽 구조물 점을 EKF A · B · SLAM 자세로 놓은 x 95 백분위, 13:25:30 +20~55 s, 시작 대비 cm, 범례에 범위) ④ `r2_runs.png`(R2 회차별). 화면 출력은 'ok' 뿐 — 수치는 그림 범례로만 남음.

### f2c_anal.py — 10-07 순회 번짐 판정 ③-b (PC, Python) — 6 시기
- 부른 형태: `python f2c_anal.py`(스크래치패드의 `x913_f2c1.npz` · `x913_f2c2.npz` — bag 추출물, 지금 **소실**).
- 하는 일(③-b 부분, 13~25 행): 제자리 회전 구간 = EKF B 의 `|ω| > 0.15 · |v| < 0.03` 이 1.5 s 넘게 → 시작 ts · 끝 te 에서 SLAM 자세 = map→odom ∘ EKF B(끝은 map→odom 을 **te + 2.0 s** 로), B · A 변위를 시작 map→odom yaw 로 map 방향에 맞춤 → `eB = |dB − dS|`, `eA = |dA − dS|`(cm) → 구간별 표 + 평균 · 최대 · B < A 개수. 같은 파일이 ③-c 게이트 비용 · rf2o 발행률 · map→odom 보정 누적도 낸다(→ [rf2o 도입](rf2o-introduction.md)).
- 출력: [`f2c_anal.txt`](../debug_log/2026-10-07/outputs/f2c_anal.txt) — 나온 결과 발췌: `100.7~ 103.2 s   -35° |   8.9 |  10.3 |  11.8` · `→ 회전 2 구간: B − SLAM 평균 8.5 · 최대 10.3 cm | A − SLAM 평균 9.5 · 최대 11.8 cm | B < A 인 구간 2/2`.
- 알려진 결함: 선언(10-07 §2)의 '오간 폭' 이 아니라 시작 · 끝 변위 차(§7 어긋남 1). 정답이 위치 추정 SLAM(§5 실수 1 과 같은 약점). 지금 다시: npz 를 bag 에서 다시 만들어야 함(추출 스크립트 `job913_extract.py` — 10-07 jobs).

## 10. 용어
- **번짐(smear)**: 장애물 표시가 실제보다 두껍게(특히 로버 쪽으로) 남는 것. 여기서는 odom 좌표 로컬 코스트맵에서, 주행계가 놓친 이동만큼 같은 벽의 '옛 자리' 표시와 '새 자리' 표시가 겹쳐 생긴다.
- **옛 칸(stale cell)**: 지금 라이다 점도 카메라(nvblox) 장애도 근처(0.10 m)에 없는데 치명으로 남은 로컬 코스트맵 칸.
- **odom 좌표 vs map 좌표**: odom = EKF 가 적분한 연속 좌표(튀지 않지만 미끄러짐을 놓치면 어긋남이 쌓임), map = SLAM 이 지도에 맞춘 좌표(보정 때 계단식으로 튐). Nav2 의 로컬 코스트맵 · nvblox · MPPI 는 odom, 전역 코스트맵 · 경로는 map.
- **라이다 obstacle 층의 지우기(raytrace clearing)**: 빔이 지나간 칸을 비우는 방식. 로버가 미끄러져 같은 칸을 지나는 빔이 없으면 옛 표시가 남는다.
- **B2(회전축 모델)**: 09-28 · 09-29 에 만든 컨디셔너 기능 — 제자리 회전 중 차체가 한쪽 트랙 쪽 축으로 돈다고 보고 휠 속도에 옆 이동을 더함(`ekf.launch.py icr:=`). **B3**: 회전 중 휠 병진 공분산을 키움(`rot_cov:=`).
- **위치 추정 모드 노드 간격**: localization 모드의 `minimum_travel_distance 0.30` · `minimum_travel_heading 0.15` — 이만큼 움직여야 새 스캔을 정합에 씀. 매핑 모드(0.05 · 0.03)보다 성겨서 회전 중 보정이 계단식이다.
