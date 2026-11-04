# slam_toolbox 포크 — 제자리 회전 중에도 스캔 처리 (5 시기: 09-28 B1 · 09-29 문서화)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **해결(지도 층)** · 운용 중 — 원본이 순수 회전 스캔을 버리는 것은 소스 + 재생으로 **확인**, 포크가 회전 밀림을 map 에서 따라가는 것은 bag 재생 11/11(오차 평균 1.1 · 최대 2.1 cm)과 실주행 줄자(≈ 2 · 4 cm)로 **측정**. 한계: odom 층은 그대로 · 주행 중(호 회전) CPU 증가는 미측정 · 지금 운용(위치 추정 모드)의 회전 문턱 0.15 rad 에서의 포착 정확도는 미측정(§8) | 09-28 ~ (09-29 문서화, 10-27 계측 사본) | [09-28 §3.1](../debug_log/2026-09-28/SUMMARY.md) — S1 순수 회전 3 회 동안 map→odom 0 | Jetson `~/slam_ws`(slam_toolbox 2.6.10 + 패치 [`slam_toolbox_rover_fork.patch`](../debug_log/2026-09-28/jobs/slam_toolbox_rover_fork.patch)) · [`slam.launch.py`](../../ros2_ws/src/rover_bringup/launch/slam.launch.py)(`slam_build:=fork\|apt`, 기본 fork) · 설명 [`SLAM_FORK_ROTATION.md`](../04_navigation/SLAM_FORK_ROTATION.md) | [제자리 회전 옆 밀림 F0-a](f0-rotation-side-slip.md)(문제의 본줄기 — 이 카드는 그 B1) · [SLAM map→odom 시각 정체](slam-stamp-freeze.md)(같은 포크의 위치 추정 정합 비용) · [센서 컨디셔너](sensor-conditioner.md)(B2 · B3 — odom 층 쪽 대책) · [SLAM Fast DDS 데드락](slam-dds-deadlock.md)(같은 노드의 다른 문제) · [휠 오도 스케일 · 회전 슬립](wheel-odom-scale-slip.md) · [정지 중 방향 드리프트](stationary-yaw-drift.md) (9 기) |

**한 줄**: 스키드스티어 로버가 제자리 180° 돌 때마다 중심이 10~27 cm 옆으로 밀리는데(스캔 직접 정합 16 회), 원본 slam_toolbox 는 '새 스캔을 쓸지' 정하는 `shouldProcessScan()` 이 **odom 병진 거리만** 봐서 순수 회전 중 스캔을 전부 버렸고, 그래서 map→odom 이 0 그대로였다. 설정만 바꾸는 안(거리 0 + 시간 간격 0.5 s)은 맞았지만 정지 중에도 CPU 21 % 를 썼다. 그 조건 한 줄을 **'거리 또는 회전각이 문턱을 넘으면 처리'** 로 바꾼 포크를 빌드했고(첫 빌드는 Karto 가 회전 문턱을 **도(degree)** 로 돌려주는 걸 몰라 문턱이 ≈ 79° 가 되는 버그), 재생 11/11 · 평균 1.1 cm · 정지 CPU 원본과 같음을 확인한 뒤 사용자 결정으로 라이브 기본이 됐다. '오차를 감지하는 기능' 을 넣은 것이 아니다 — 회전 중에도 평소의 스캔 정합이 돌게 했을 뿐이다(09-29 §14).

## 1. 증상
- 09-28 S1(0.38 rad/s 시계 × 3, v = 0): 3 회(−176° × 3) 내내 **map→odom = (0.0000, 0.0000, 0.000°)**, 포즈 그래프 마커 4 개, slam CPU 3.9 %. 회전 러너가 잰 'SLAM 이동' 과 'EKF 이동' 이 둘 다 0.002 m 로 같았다([`j566_s1.txt`](../debug_log/2026-09-28/outputs/j566_s1.txt), [09-28 §3.1](../debug_log/2026-09-28/SUMMARY.md)). 같은 회전의 스캔 직접 정합은 17.0 · 15.7 · 10.5 cm([`j567_s1_scanmatch.txt`](../debug_log/2026-09-28/outputs/j567_s1_scanmatch.txt)).
- 같은 날 R1b · R2b · R3 러너도 전부 SLAM = EKF = 0.000~0.002 m([`j573`](../debug_log/2026-09-28/outputs/j573_r1b.txt) · [`j576`](../debug_log/2026-09-28/outputs/j576_r2b.txt) · [`j578`](../debug_log/2026-09-28/outputs/j578_r3.txt) 앞부분).
- 반대로 09-23 f0a2 에서는 SLAM 이 회전 중 +0.20 m 를 잡았다 — MPPI 가 회전 중 후진을 섞어 odom 병진이 문턱(4.47 cm)을 넘은 순간 몰아서 처리한 것(09-28 §3.1 ②, [F0-a 카드 실수 4](f0-rotation-side-slip.md)).

## 2. 무엇을 고쳤나 — `shouldProcessScan()` 한 조건 (코드 기준)
**원본의 흐름**(slam_toolbox 2.6.10 `src/slam_toolbox_common.cpp`). 저장소에는 함수 전체 사본이 없고 패치 문맥(537~543 행)만 있다 — 아래 ①~④ 는 그 계열 소스에 대한 내 기억이라 **원문 미대조**, ⑤ 는 패치 문맥으로 확인:
1. 첫 스캔은 무조건 처리(그때 자세 · 시각을 `last_pose` · `last_scan_time` 에 저장).
2. 일시정지 상태면 버림.
3. `throttle_scans`(1) 배수가 아니면 버림.
4. 직전 처리 스캔 뒤 `minimum_time_interval`(0.1 s) 이 안 지났으면 버림.
5. **`dist2 = last_pose.SquaredDistance(pose)`** — `pose` 는 laserCallback 이 그 스캔 시각의 **odom→base 자세**로 넘긴 값. `if (dist2 < 0.8 * min_dist2 || scan_ctr < 5) return false;` — 0.8 은 '보정 오차 10 % 여유' 주석. 통과하면 `last_pose` 갱신 후 처리(→ addScan → 스캔 정합 → 포즈 그래프 노드 추가 → map→odom 갱신).
- 제자리 회전에서 휠 오도는 옆 이동 0 을 보고하므로 odom 병진 ≈ 0 → ⑤ 에서 영원히 버림 → 스캔 정합이 한 번도 안 돌아 map→odom 이 안 바뀐다. `minimum_travel_heading` 은 이 관문에 **없다**(`slam.yaml` 38 행 주석 '~1.7° 마다 (회전 시 스캔매칭 보정 잦게)' 는 원본에선 거짓 — 지금도 주석 그대로).

**포크**(패치 원문, 2026-09-28):
```cpp
const double dist2 = last_pose.SquaredDistance(pose);
const double dheading = std::fabs(karto::math::NormalizeAngle(pose.GetHeading() - last_pose.GetHeading()));
// Karto 의 getParamMinimumTravelHeading() 은 도(degree)로 돌려준다(내부는 라디안) → 라디안으로 변환
const double min_heading = karto::math::DegreesToRadians(smapper_->getMapper()->getParamMinimumTravelHeading());
if ((dist2 < 0.8 * min_dist2 && dheading < 0.8 * min_heading) || scan_ctr < 5) {
  return false;
}
```
- 의미: '거리도 작고 **그리고** 회전각도 작을 때만 버림' = '거리 **또는** 회전각이 넘으면 처리'. `dheading` 은 **마지막으로 처리된 스캔의 odom yaw** 와의 차(−π~π 정규화 뒤 절댓값) — 회전이 쌓여 문턱을 넘는 순간 처리되고 기준이 갱신된다.
- 정지 · 직진 중에는 원본과 같다: 정지면 둘 다 작아 버림, 직진은 거리 조건이 원래대로 통과.
- 실제 문턱(0.8 배 포함 — 계산):

| 구성 | minimum_travel_distance / heading | 버리는 조건(병진 · 회전 둘 다 미만) | 출처 |
|---|---|---|---|
| 매핑 모드(09-28 시험 · 09-28 ~ 09-30 운용) | 0.05 m / 0.03 rad | < 0.0447 m · < 0.024 rad(**1.375°**) | `slam.yaml` 37~38 행 |
| 첫 빌드 버그(변환 없음) | 0.03 rad 가 1.7189 '라디안' 으로 비교됨 | < 1.375 rad(**≈ 79°**) → 180° 당 2 번 처리 | `j588` `minh 1.7189 … pass 1` at `dhead 1.3996` |
| **위치 추정 모드(10-01 ~ 지금 운용)** | 0.30 m / 0.15 rad | < 0.268 m · < 0.12 rad(**≈ 6.9°**) | `slam.launch.py` 위치 추정 파라미터(10-01 §9) |

- 회전 중 실제 처리 간격(추정): 0.38 rad/s 면 스캔 한 장(라이다 주기 ≈ 0.1 s 가정) 사이 0.038 rad 로 0.024 문턱을 넘으므로 사실상 시간 간격(0.1 s)마다 처리 — s1 재생에서 회전당 map→odom 갱신 38~43 회, 마커 145 개(3 회전, `j589_b1_s1_b2.txt`). 이것이 회전 중 CPU 42~52 % 의 이유로 보인다(분리 측정 안 함).
- 왜 map 만 고쳐지나: 처리된 스캔은 스캔 정합으로 **map 기준 자세**가 정해지고 slam_toolbox 는 `map→odom = map 자세 ∘ (odom 자세)⁻¹` 을 발행한다. 밀림은 map 자세에 들어가고 그 차이가 map→odom 으로 드러난다. EKF(odom→base)는 그대로다.
- 원문 메모 1 — `SLAM_FORK_ROTATION.md` §3 '회전 중에는 약 1.7° 마다' 는 0.8 배를 뺀 값이다(실제 1.375°). §3 의 첫 빌드 '1.72 rad(≈ 98°)' 도 0.8 배 전 값(실제 버림 문턱 ≈ 79°) — 회전당 2 번이라는 관측과는 둘 다 맞는다.

## 3. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-23 §20.4 | 슬립 보정안 비교 | `slam.yaml` minimum_travel 0.05 m · heading 0.03 rad · 주석 '회전 시 보정 잦게' | 'SLAM 갱신 간격은 이미 촘촘 — 주기 문제 아님' — **틀림**(09-28 §3.1, F0-a 카드 실수 4) | `slam.yaml` 37~38 행 |
| 09-28 §3.1 | S1 순수 회전 · 소스 읽기(slam_toolbox humble) | map→odom 0 · 마커 4 · CPU 3.9 %. 관문 ⑤ 가 거리만 봄 | 순수 회전 슬립은 원본 SLAM 도 못 본다. 설치본(apt 바이너리)이 같은 줄인지는 **미확인** — 관측과는 일치 | [`j566_s1.txt`](../debug_log/2026-09-28/outputs/j566_s1.txt) |
| 09-28 §7.1 · §7.2 | 방안 B1 정의 · 충돌 검토 | (a) 설정만: 거리 0 + 시간 간격 0.5 s / (b) 소스 한 줄(nvblox_nav2 포크와 같은 운용) | 오늘 bag 7 개 재생으로 주행 없이 검증 가능. B1 ↔ B2 · B4 는 층이 달라(map→odom vs odom→base) 이중 계산 없음. B1 ↔ rf2o 는 같은 라이다라 실패가 동시(밋밋한 벽) → cuVSLAM 이 독립 백업. (a) 는 정지 중 노드 누적 → (b) 우선 | [09-28 §7](../debug_log/2026-09-28/SUMMARY.md) |
| 09-28 §7.3 | 순서 1 = B1 오프라인(사용자 확정) | — | — | — |
| 09-28 §8(무효 묶음) | 첫 재생 묶음 | `j582_*` · `j583_*`: 설정 이름 빈칸(인자 전달 실패) · 앞 실행의 slam 노드가 안 죽어 도메인 42 에 SLAM 둘 | **결과 폐기**(실수 2). 래퍼에 시작 · 끝 pkill 과 '남은 재생용 slam 0' 확인 추가 | `outputs/j582_b1_s1*.txt` · `j583_*` |
| 09-28 §8 | 재생 A/B: base vs (a) | base: r2b 4 회 0.1~0.2 cm, map→odom 변화 0, 갱신 0. (a): s1 · r2b · r3 **11/11 포착, 오차 평균 1.2 · 최대 2.0 cm**, 회전당 갱신 16~33 회, 회전각 ±1.4° 안. CPU base 3.4 % → (a) 19.2~21.5 % | B1 개념 **확인**. (a) 의 CPU 증가 상당 부분이 정지 구간 몫(**추정** — §9.2 에서 측정으로 확인), 정지 중 노드 2 개/s(1 시간 7 200 개 — 계산) → (b) 권장 | [`job580`](../debug_log/2026-09-28/jobs/job580_slamreplay.py) · [`job581`](../debug_log/2026-09-28/jobs/job581_b1.sh) · `j584_b1_*` · [`j585_b1_compare.txt`](../debug_log/2026-09-28/outputs/j585_b1_compare.txt) · `j587_b1_s1_base.txt` |
| 09-28 §9 | 포크 빌드 | `~/slam_ws` 에 slam_toolbox **2.6.10**(apt 판과 같은 태그, 8293d21), Release · MAKEFLAGS −j3, 첫 6 분 57 초 · 증분 1 분 40 초. 라이브는 계속 apt | — | [`slam_toolbox_rover_fork.patch`](../debug_log/2026-09-28/jobs/slam_toolbox_rover_fork.patch) |
| 09-28 §9.1 | 첫 (b) 재생 | 회전당 map→odom 갱신 **2 회**, 마커 10~13, 오차 크고 R3 회전 3 · 4 는 옆 방향 부호까지 틀림. 진단 로그 `minh 1.7189` | Karto `getParamMinimumTravelHeading()` 이 **도로 돌려줌**(`Mapper.cpp:2333 return math::RadiansToDegrees(...)`) → `DegreesToRadians` 로 수정, 진단 로그 제거 뒤 재빌드(실수 1) | `j586_b1_*` · [`j588_b1_diag.txt`](../debug_log/2026-09-28/outputs/j588_b1_diag.txt) |
| 09-28 §9.2 | 수정판 · 문턱 비교 | 아래 §5 표 — (b) 0.03 = 11/11 · 1.1/2.1 cm · 회전 중 42~52 % · 정지 4.8~5.5 %(`j591`). 0.10 → 2.4/4.5 cm, 0.20 → 4.8/10.3 cm | **제안: (b) + 0.03 유지**. 미확인: 이동하며 도는 일반 주행에서 노드가 더 자주 쌓여 CPU · 그래프 크기가 얼마나 늘지(라이브 A/B 필요) | `j589_b1_*_b2.txt` · `j590_b1_*_b10/b20.txt` · [`j591_b1_compare2.txt`](../debug_log/2026-09-28/outputs/j591_b1_compare2.txt) · `j592_b1_s1_final.txt`(= j589 같은 값) |
| 09-28 §13 | **라이브 적용(사용자 결정)** | `slam.launch.py` 에 `slam_build:=fork\|apt`(기본 fork). prep: 실행 파일 · `libtoolbox_common.so` 모두 `~/slam_ws` 포크 | 되돌리기 = `slam_build:=apt` | [`j600_prep_f0a3.txt`](../debug_log/2026-09-28/outputs/j600_prep_f0a3.txt) · `slam.launch.py` 17~34 행 |
| 09-28 §14 · §15 | f0a3(첫 라이브) | 목표 2 방향 전환 중 map→odom 변화 **56 회**(원본이었으면 0 이었을 구간 — 추정). 줄자 가로 3 · 세로 2 cm vs map 복귀 2.1 cm | 포크 SLAM 위치가 물리와 ≈ 2 cm(한 값 · 눈대중). 동시에 **odom 층 어긋남**이 드러남 — 포크가 슬립을 잡아 map→odom 보정이 커지자 odom 고정 로컬 지도가 map 에서 16 cm 옮겨 보임([F0-a 카드](f0-rotation-side-slip.md) §7) | [`j602_f0a3_csv.txt`](../debug_log/2026-09-28/outputs/j602_f0a3_csv.txt) · [`j604_f0a3_boxdrift.txt`](../debug_log/2026-09-28/outputs/j604_f0a3_boxdrift.txt) |
| 09-28 §20 · §22 | f0a5 · f0a6 줄자 대조 | f0a5 정지 위치: SLAM 오차 ≈ **12 cm**(세로 11 · 가로 5 cm 차). f0a6: ≈ **4 cm**(세로 3.6 · 가로 1.6) | f0a5 의 12 cm 원인 미확인(목표 2 부근 150° 회전 + 후진이 다 보정 안 됐거나 출발점 뒤쪽 정합 기하 — 추정) | [`j612_f0a5.txt`](../debug_log/2026-09-28/outputs/j612_f0a5.txt) · [`j617_f0a6_csv.txt`](../debug_log/2026-09-28/outputs/j617_f0a6_csv.txt) · 줄자 = 대화 |
| 09-29 §14 | 사용자 질문 'SLAM 에서 무엇을 고쳤길래 이동 중 오차를 감지한다고 했나' | — | 오차 감지 기능을 넣은 게 아니라 버리던 회전 스캔을 정합하게 한 것. '1~2 cm 로 따라간다' = map 포즈의 스캔 직접 정합 대비 오차. 정리 문서 [`SLAM_FORK_ROTATION.md`](../04_navigation/SLAM_FORK_ROTATION.md) · CLAUDE.md §6 지도 줄에 포크 언급 | [09-29 §14](../debug_log/2026-09-29/SUMMARY.md) |
| 이후 10-27 §29 (9 기, 채움) | 위치 추정 정체 원인 계측 — 운용 `~/slam_ws` 는 그대로 두고 사본 `~/slam_dbg_ws` 에 단계별 시간 `[ROVER_T]` 출력만 넣어 Release 빌드(≈ 14 분), 재생(`Docs/tools/run_slam_replay.sh`, `SLAM_WS=~/slam_dbg_ws`) | 빌드 diff 3 파일 · 34 줄(그중 `slam_toolbox_common.cpp` 8 줄 = 이 포크의 회전 조건이 같은 diff 에 보이는 것). 처리 101 스캔 · addScan 중앙 168 / 최대 1138 ms 중 **LinkNearChains 64 %** · 순차 정합 16 % · 루프 7 %. 계측판 스캔 버림 22 · 정체 23 = 기준 재생 19~23 수준(동작 불변) | 회전 조건(이 포크)이 아니라 위치 추정 정합 안의 사슬 재정합이 무겁다 — 다만 정체 직전 1 s 에 회전이 낀 경우 39/55 · 46/56(10-27 §26.1)이라, 회전으로 정합이 더 자주 불리는 몫은 **미분리** | [`prep_slam_dbg_1027.sh`](../debug_log/2026-10-27/jobs/prep_slam_dbg_1027.sh) · [`prep_slam_dbg_1027.txt`](../debug_log/2026-10-27/outputs/slamproc/prep_slam_dbg_1027.txt) · [`anal_slam_timing_T0dbg.txt`](../debug_log/2026-10-27/outputs/slamproc/anal_slam_timing_T0dbg.txt) · → [SLAM 시각 정체 카드 §4.1 · §8.9](slam-stamp-freeze.md) |

## 4. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 원본은 순수 회전에서 스캔을 처리하지 않는다 | 라이브 S1 map→odom · 소스 · 재생 base | 0 · 거리만 보는 관문 · 11 회전 0.1~0.2 cm, 갱신 0 | **확인** |
| 스캔만 들어가면 slam_toolbox 정합이 회전 밀림을 맞힌다 | (a) 재생 vs 스캔 직접 정합 | 11/11, 1.2/2.0 cm | **지지** |
| (a) 의 CPU 부담은 정지 중 노드 누적 탓 | 회전 · 정지 구간 CPU 분리(`job580` 보강) | (a) 정지 중 21.4 % vs 원본 3.6 % | **확인**(§8 추정 → §9.2 측정) |
| 거리 OR 회전각(b) 이면 정확도는 (a) 와 같고 정지 비용은 원본과 같다 | (b) 0.03 재생 | 11/11 1.1/2.1 cm · 정지 4.8~5.5 % | **지지** |
| 회전 문턱을 키우면 CPU 를 줄이면서 정확도를 지킬 수 있다 | 0.10 · 0.20 재생 | 2.4/4.5 · 4.8/10.3 cm | **기각**(0.03 유지) |
| 라이브에서도 포크가 회전 중 보정한다 | f0a3 방향 전환 중 map→odom 변화 · 줄자 | 56 회 · 줄자와 ≈ 2 cm(f0a6 ≈ 4, f0a5 ≈ 12) | **지지**(f0a5 예외 원인 미확인) |
| 포크가 odom 층(로컬 코스트맵) 문제도 푼다 | f0a3 로컬 vs 전역 상자 | 로컬만 16 cm 옮겨 보임 | **기각** — 층이 다름(애초 기대도 아니었음, §7.1 '한계') |

## 5. 조치와 효과
| 설정(재생, 정답 = 스캔 직접 정합) | 포착 | 오차 평균 / 최대 | slam CPU 회전 중 / 정지 중 | 마커(s1) |
|---|---|---|---|---|
| 원본(apt) | 0/11 | —(0.1~0.2 cm 만 봄) | 3.8 / 3.6 %(s1, `j587`) | 4 |
| (a) 거리 0 + 간격 0.5 | 11/11 | 1.2 / 2.0 cm | 23.5 / 21.4 % | 108 |
| **(b) 포크, 회전 0.03 rad** | 11/11 | **1.1 / 2.1 cm** | **42~52 / 4.8~5.5 %** | 145 |
| (b) 포크, 회전 0.10 | 7/7 | 2.4 / 4.5 cm | 13.7~27.1 / 4.1~4.2 % | 69 |
| (b) 포크, 회전 0.20 | 7/7 | 4.8 / 10.3 cm | 8.9~13.3 / 4.0~4.1 % | 30 |
(원문 [`j591_b1_compare2.txt`](../debug_log/2026-09-28/outputs/j591_b1_compare2.txt). 0.10 · 0.20 은 s1 · r3 만(n 7).)
- 적용: `slam.launch.py` `_select_build` — `slam_build == 'fork'` 이고 `~/slam_ws/install/slam_toolbox/lib/slam_toolbox/async_slam_toolbox_node` 가 있으면 launch 프로세스의 `AMENT_PREFIX_PATH` · `LD_LIBRARY_PATH` 앞에 포크 접두를 붙여 자식 노드가 포크 실행 파일 · 라이브러리를 잡게 함, 없으면 apt 로 떨어지며 LogInfo. 위치 추정 노드(`localization_slam_toolbox_node`)도 같은 접두에서 찾으므로 포크를 탄다 — 10-27 §29 소스 원문에서 `slam_toolbox_localization.cpp` laserCallback → `shouldProcessScan(포크 수정)` → addScan 확인(`2026-10-27/outputs/slamproc/slam_src_dump.txt`).
- 효과(라이브): 회전 직후에도 map 좌표(전역 경로 · 목표)가 실제 위치를 따라감(f0a3 줄자 ≈ 2 cm, f0a6 ≈ 4 cm). 09-29 §3.1 새 회전 실주행 SLAM 오차 중앙값 1.3 cm(최대 1.6) · 93° 부분 회전 3.5 cm — 단 **B2 를 켠 상태**라 포크 단독 효과와 섞임([`SLAM_FORK_ROTATION.md`](../04_navigation/SLAM_FORK_ROTATION.md) §4 · §5 인용, 이 카드에서 09-29 원문은 대조하지 않음).
- 한계: map 층만. 회전 중 CPU 가 원본의 10 배 이상(재생). 호 회전 주행 중 비용은 라이브로 재지 않음.

## 6. 내 실수
**실수 1 — 포크 첫 빌드의 단위 버그(§9.1)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | `shouldProcessScan` 에 `dheading < 0.8 * getParamMinimumTravelHeading()` 을 더해 회전 0.03 rad 마다 처리 |
| 본 것 | 첫 (b) 재생(`j586`): 회전당 map→odom 갱신 **2 회**, 마커 10~13 개, R3 회전 3 · 4 는 옆 방향 부호까지 틀림 |
| 처음 추론 | (재생 전) getter 는 설정값(0.03 rad)을 그대로 돌려준다 |
| 의심한 이유 | 0.03 rad 문턱이면 180° 당 수십 번이어야 하는데 2 번 — 문턱이 ≈ 80° 급이라는 뜻 |
| 판별 | 비교 값을 찍는 진단 빌드(`j588`): `minh 1.7189`, `dhead 1.3996` 에서 처음 통과. Karto `Mapper.cpp:2333` 이 `RadiansToDegrees` 로 돌려줌 |
| 결론 | 0.03 rad → 1.7189 '도' 가 라디안으로 비교됨. `DegreesToRadians` 로 고쳐 재빌드 → 11/11 · 1.1 cm(`j589` · 최종판 `j592` 같은 값) |
| 다음에 알아보는 법 | 남의 라이브러리 getter 는 **단위를 소스에서 확인**한다(내부 저장 단위와 반환 단위가 다를 수 있음). 서명: 문턱을 바꿨는데 동작 횟수가 계산과 몇십 배 다름 → 문턱 값을 그 자리에서 찍어 본다 |
| 데이터 | `2026-09-28/outputs/j586_b1_{s1,r2b,r3}_b.txt` · [`j588_b1_diag.txt`](../debug_log/2026-09-28/outputs/j588_b1_diag.txt) · 패치 주석(사후 기록) · 진단 빌드의 코드는 '확인 뒤 제거' 로 남지 않음 |

**실수 2 — B1 첫 재생 묶음이 무효(§8)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 도메인 42 에서 base · (a) 설정으로 slam_toolbox 를 띄우고 회전 bag 재생 |
| 본 것 | 첫 묶음(`j582` · `j583`)의 설정 표시 줄에 설정 이름이 비어 있었고, 앞 실행의 slam 노드가 종료되지 않아 같은 도메인에 SLAM 이 둘 |
| 처음 추론 | (실행 시) 래퍼가 인자를 받고 앞 노드는 INT 로 끝난다 |
| 의심한 이유 | 출력 머리줄의 설정 이름 빈칸 · 결과가 설정과 안 맞음(SUMMARY 는 어떤 값이 이상했는지는 적지 않음 — 미확인) |
| 판별 | 프로세스 확인 — 재생용 slam 이 둘 |
| 결론 | 결과 폐기. 래퍼(`job581`)에 시작 전 `pkill -9` · 끝에 INT → 2 s → `-9` · '남은 재생용 slam: N' 출력 추가 후 다시(`j584`) |
| 다음에 알아보는 법 | 재생 · A/B 래퍼는 **시작 전에 같은 패턴 프로세스 0 을 확인하고 결과 첫 줄에 실제 적용된 파라미터를 노드에서 읽어 찍는다**(`ros2 param get`). 이 규칙은 10-27 `run_slam_replay.sh` 에서 'pkill 패턴이 본 스택 SLAM 까지 걸 수 있음' 으로 한 번 더 고쳐졌다(띄운 pid 만 죽이기) |
| 데이터 | `2026-09-28/outputs/j582_b1_s1.txt` · `j582_b1_s1_a.txt` · `j583_b1_*_a.txt` · [`job581_b1.sh`](../debug_log/2026-09-28/jobs/job581_b1.sh) 11~12 · 27~28 행 |

**실수 3 — 설정 주석을 동작 근거로 씀(09-23 §20.4)**: [F0-a 카드 실수 4](f0-rotation-side-slip.md) 에 칸 형식으로.

## 7. 기록 사이 모순 (원문 대조, 11-02)
1. **§9.1 '오차 5~26 cm'** vs 원문 대조(`j586` 의 SLAM 이동 − `j585` 정답, 내 계산): s1 2.0 · 5.1 · 5.7, r2b 1.0 · 4.3 · 5.6 · 4.0, r3 6.1 · 19.4 · **30.5 · 38.0 cm** → 실제 범위 **1.0~38.0 cm**. 또 '방향까지 틀림' 은 R3 회전 3 만이 아니라 **회전 4 도**(정답 옆 −22.8 vs SLAM +11.6 cm).
2. **§9.2 표 (b) 0.03 '정지 중 4.5~5.5 %'** vs 원문 `j589` 정지 구간 4.8 · 5.5 · 5.5 %, `j591` '4.8~5.5'. 4.5 의 출처 없음 — `SLAM_FORK_ROTATION.md` §5 도 4.5~5.5 로 옮겨 적음.
3. **§9.2 표 원본 CPU '3.8 / 3.6 %'** 는 s1(`j587`) 값. r2b base 는 평균 3.4 %(`j584_b1_r2b_base.txt`) — `j591` 의 '3.4~3.8 %' 가 전체 범위.
4. **`SLAM_FORK_ROTATION.md` §3 '약 1.7° 마다' · '1.72 rad(≈ 98°)'** — 0.8 배를 뺀 값(§2 원문 메모 1). 실제 처리 문턱 1.375° · 버그 때 ≈ 79°.
5. **§8 '(a) CPU 19.2~21.5 %'**(래퍼 전체 평균) vs §9.2 표 '(a) 회전 23.5 / 정지 21.4'(구간 분리) — 같은 설정의 다른 집계라 모순은 아니다(재생 시간 안 정지 · 회전 비율이 다름).
6. **§3.1 '설치본은 apt 바이너리라 같은 줄인지는 미확인'** — 이후 확인된 것: 포크는 apt 판과 **같은 태그 2.6.10** 소스(§9), 재생 base(apt) 가 0/11 로 관측 일치. 바이너리 디스어셈블 같은 직접 확인은 없다.

## 8. 남은 것 · 지금 구성에 걸린 것
- **지금 운용은 위치 추정 모드**(10-01 ~, `slam.launch.py` 위치 추정 파라미터 `minimum_travel_distance 0.30` · `minimum_travel_heading 0.15`): 포크의 회전 문턱이 0.12 rad(≈ 6.9°)가 된다. 09-28 에 검증한 것은 **매핑 모드 0.03 rad** 이고, 재생 비교로는 0.10 → 평균 2.4 · 최대 4.5 cm, 0.20 → 4.8 · 10.3 cm 였다 — 0.15 에서 순수 회전 밀림을 얼마나 따라가는지는 **미측정**(위치 추정 모드는 정합 대상이 저장 지도라 매핑 모드와 같다고 볼 수도 없음). 0.15 는 10-01 §9 에서 정체(map→odom 지연)를 줄이려고 고른 값이다.
- 같은 포크가 위치 추정 정합(LinkNearChains 64 %)의 정체를 만든다는 것은 [SLAM 시각 정체](slam-stamp-freeze.md) 카드. 회전 조건이 위치 추정 모드에서 정합 횟수를 얼마나 늘리는지(= 정체 기회)는 분리 측정 없음 — 10-27 §26.1 '정합 문턱(0.30 m · 0.15 rad) 이상 53/54' 는 거리 · 회전 어느 쪽으로 넘었는지 나누지 않았다(**미확인**).
- 호 회전 주행 중 CPU · 그래프 크기 — 라이브 A/B 없음(§9.2 미확인 그대로).
- odom 층 — 포크로 안 풀림. 10-02 rf2o · 10-23 cuVSLAM 주 EKF 로 넘어감([F0-a 카드](f0-rotation-side-slip.md) §7.8).
- 넓은 빈 공간 · 사람 많은 곳에서 정합 약화 — 일반 원리, 미측정(`SLAM_FORK_ROTATION.md` §5).
- `slam.yaml` 38 행 주석('~1.7° 마다 … 보정 잦게')은 포크에서만 맞고 실제는 1.375° — 주석 미수정.
- 포크 유지 비용: Jetson `~/slam_ws` 는 저장소 밖(패치만 저장소). Jetson 재설치 · apt 판 갱신 때 같은 태그로 다시 빌드해야 한다(절차 = `SLAM_FORK_ROTATION.md` §6 + 패치).

## 9. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| s1 · r2b · r3 bag | 재생 입력(회전 11 개: s1 3 · r2b 4 · r3 4) | 원천 소실(`2026-09-28/bags/` 없음) |
| 재생 base · a · b · b2 · b10 · b20 | 설정별 재생 결과 | `2026-09-28/outputs/j584` ~ `j592` |
| `job580_slamreplay.py` · `job581_b1.sh` | 도메인 42 재생기 · 래퍼 | `2026-09-28/jobs/` |
| `slam_toolbox_rover_fork.patch` | 포크 패치(최종판) | `2026-09-28/jobs/` |
| `job567_scanmatch.py` | 정답(정지 스캔 직접 정합) | [F0-a 카드 도구 해설](f0-rotation-side-slip.md) |
| f0a3 · f0a5 · f0a6 | 라이브 포크 확인(줄자 대조) | F0-a 카드 §7 |
| `slam.launch.py` `_select_build` | fork / apt 선택 | `ros2_ws/src/rover_bringup/launch/slam.launch.py` |

## 10. 도구 해설
도구 계보: (재생 A/B) **`job580` + `job581`**(09-28, 회전 bag · 매핑 모드 · `async_slam_toolbox_node`) → `Docs/tools/run_slam_replay.sh` + `slam_replay_feed.py`(10-27, 주행 bag · 위치 추정 모드 · `localization_slam_toolbox_node` · `SLAM_EXTRA` · `SLAM_WS` 환경 · 띄운 pid 만 정리 — [SLAM 시각 정체](slam-stamp-freeze.md)). (포크) `~/slam_ws` 09-28 패치 → 10-27 `~/slam_dbg_ws`(같은 소스 + 단계별 시간 '[ROVER_T]' 출력만, 운용판은 그대로, `2026-10-27/jobs/prep_slam_dbg_1027.sh`).

### job580_slamreplay.py — 회전 bag 재생기 (Jetson, Python rclpy + rosbag2_py)
- 부른 형태: `SLAM_PID=<pid> python3 /tmp/job580_slamreplay.py /tmp/bag_<NAME>` — `job581` 이 ROS_DOMAIN_ID 42 에서 부름.
- 왜: B1 이 순수 회전 밀림을 잡는지 주행 없이(그날 bag 으로) 보려고(§7.3 순서 1).
- 하는 일: ① bag 을 통째로 읽어 /scan · /tf · /tf_static · /cmd_vel 수집. /tf 에서 **기록 당시 map→odom 은 빼고** 나머지(EKF odom→base 등)만 남김, odom→base 자세 따로 저장 ② 노드(use_sim_time **False** — 스스로 시계를 냄)로 /clock(5 ms 마다) · /scan · /tf · /tf_static(transient_local, 시작 때 먼저 + 2 s 대기) 을 bag 시각 간격 그대로 **실시간 1 배속** 발행 ③ 새 SLAM 이 내는 /tf 의 map→odom 을 그때 sim 시각으로 기록, `/slam_toolbox/graph_visualization` 마커 수, `/proc/<SLAM_PID>/stat` 의 utime + stime 을 0.25 s 마다 ④ 끝에 3 s 더 시계를 흘려 마지막 보정 수신 ⑤ 회전 구간(|ω 지령| > 0.01, 0.5 s 끊김이면 새 구간, 2 s 미만 버림)마다 tA = 시작 − 0.8 s, tB = 끝 + 2.5 s 의 map→base(= map→odom ∘ odom→base, 회전 포함 합성)로 시작 차체 기준 이동(앞+/왼+) · 회전 · map→odom 변화 · 갱신 횟수(값이 바뀐 횟수, 소수 4 자리 반올림 비교) ⑥ 회전 구간(시작 −0.5 ~ 끝 +1.0 s) vs 나머지 CPU %.
- 출력: '회전 k: SLAM 중심 이동 (dx, dy) = d | 회전 | map→odom 변화 (…), 갱신 n 회', 'slam CPU: 회전 구간 % | 정지 구간 % | 마커 n'(→ `j584` ~ `j592`). 정답과의 비교표(`j585` · `j591`)는 대화 중 정리 — 그 코드는 보관 안 됨.
- 결과가 쓰인 곳: §8 · §9 의 모든 표.
- 알려진 결함: 회전 구간 경계 상수(−0.8 · +2.5 s)가 `job567` 과 같게 맞춰져 있어야 비교가 성립(같은 값). 마커 수는 마지막 메시지 기준(그래프 크기의 대용). /clock 과 데이터를 같은 노드가 내므로 Jetson 부하로 발행이 밀리면 sim 시각이 같이 밀림(측정 안 함). 매핑 모드 전용(위치 추정은 지도 파일 필요).
- 계보 → `Docs/tools/slam_replay_feed.py`(10-27). 지금 다시: bag 이 없어 이 날 재현은 불가, 형태는 후속 도구로 이어짐.

### job581_b1.sh — 재생 A/B 래퍼 (Jetson, bash)
- 부른 형태: `bash /tmp/job581_b1.sh /tmp/bag_<NAME> base|a|b|b10|b20`(`run_jn.sh` 로).
- 하는 일: ROS 환경 · UDP 전용 Fast DDS 프로필 · **ROS_DOMAIN_ID 42** → 시작 전 `pkill -9 -f "async_slam_toolbox_node.*use_sim_time:=true"` → 설정: base = 설치 `slam.yaml` 그대로 · a = `-p minimum_travel_distance:=0.0 -p minimum_time_interval:=0.5` · b* = `~/slam_ws/install/setup.bash` 를 추가 source(포크) · b10/b20 = `-p minimum_travel_heading:=0.10/0.20` → `ros2 run slam_toolbox async_slam_toolbox_node --params-file slam.yaml -p use_sim_time:=true …` 백그라운드 → `ros2 param get` 이 될 때까지 최대 15 s → 머리줄에 **실제 노드 파라미터**(거리 · 회전 · 간격 · 해상도 · 모드)와 실행 파일 경로(`readlink /proc/<pid>/exe` — 포크인지 확인) → `job580` → 전체 CPU 평균(/proc stat 틱 차 ÷ 100 Hz 가정 ÷ 경과) → INT → 2 s → −9 → '남은 재생용 slam: N'.
- 출력: `j584` ~ `j592` 머리줄 · 끝줄. 예 `j588`: '설정 b … 거리 0.05 / 회전 0.03 / 간격 0.1 / 해상도 0.05 / 모드 mapping', 'slam 실행 파일: /home/jetson/slam_ws/install/…'.
- 알려진 결함: pkill 패턴이 명령줄 일치라 같은 패턴의 다른 실행도 죽일 수 있음(라이브 스택은 `use_sim_time:=true` 가 없어 안 걸림 — 10-27 판에서 '띄운 pid 만' 으로 바뀜). CPU 틱 100 Hz 가정. 첫 묶음은 인자 전달 실패(실수 2 — 지금 보관본은 고친 판).
- 지금 다시: 형태 참고(후속 `run_slam_replay.sh`).

### slam_toolbox_rover_fork.patch + `~/slam_ws` 빌드 (Jetson)
- 형태: `src/slam_toolbox_common.cpp` 한 덩어리(537~543 행 → 13 줄) — §2. 빌드: `~/slam_ws` 에 slam_toolbox 2.6.10(8293d21) 소스 + 패치, colcon Release, MAKEFLAGS −j3(첫 6 분 57 초 · 증분 1 분 40 초).
- 진단판(09-28 §9.1): 비교 값(`dist` · `dhead` · `minh` · `pass`)을 줄마다 찍는 판 → `j588` — 확인 뒤 제거(코드 원문 없음).
- 쓰이는 곳: 매핑(`async_slam_toolbox_node`) · 위치 추정(`localization_slam_toolbox_node`) 둘 다 공통 `shouldProcessScan` 을 탄다(10-27 §29 소스 원문).
- 지금 다시: 운용 중. 되돌리기 `slam_build:=apt`.

### slam.launch.py `_select_build` (Jetson launch, 저장소 코드)
- 형태: `ros2 launch rover_bringup slam.launch.py [slam_build:=fork|apt] [slam_mode:=mapping|localization] [map_file:=…]`(prep 이 부름).
- 하는 일: `OpaqueFunction` 으로 `_select_build` 를 노드 생성 전에 실행 — fork 이고 포크 실행 파일이 있으면 `os.environ` 의 `AMENT_PREFIX_PATH` · `LD_LIBRARY_PATH` 앞에 포크 경로를 붙이고 '[slam.launch] slam_toolbox = 포크 <경로>' 로그, 없으면 '[slam.launch] ⚠ 포크 없음(…) → apt 판 사용' 로그. 환경은 launch 프로세스 전역이라 그 뒤 띄우는 slam 노드가 포크를 잡는다.
- 확인 방법: prep 출력의 실행 파일 · `libtoolbox_common.so` 경로(`j600`), 또는 제자리 회전 뒤 map→odom 이 움직이는지(원본은 0 — `SLAM_FORK_ROTATION.md` §6).
- 알려진 결함: 포크가 없으면 **조용히 apt 로** 돈다(로그 한 줄뿐) — 재설치 뒤 확인 필요. 같은 launch 프로세스에서 다른 노드를 띄우면 그 노드도 포크 접두를 본다(slam_toolbox 외 패키지는 영향 없음 — 접두에 slam_toolbox 만 있으므로, 추정).

## 11. 용어
- **shouldProcessScan**: slam_toolbox 가 들어온 스캔마다 '이걸 지도 · 위치 계산에 쓸지' 정하는 관문 함수. 여기서 버린 스캔은 정합도, 포즈 그래프 노드도, map→odom 갱신도 없다.
- **minimum_travel_distance · minimum_travel_heading**: 직전 처리 스캔 뒤 odom 기준으로 이만큼 움직여야 새 스캔을 처리한다는 문턱(Karto 파라미터). 원본 slam_toolbox 의 관문은 거리만 쓰고, heading 은 Karto 내부(다른 곳)에서만 쓰였다 — 포크가 관문에 heading 을 넣었다.
- **Karto**: slam_toolbox 안의 스캔 정합 · 포즈 그래프 라이브러리(open_karto 계열). 파라미터를 내부 라디안으로 저장하고 getter 가 도로 돌려주는 것이 있다(§6 실수 1).
- **포즈 그래프 노드 · 마커**: 처리된 스캔마다 그래프에 자세 노드가 하나 생기고, 노드 사이 정합 결과가 간선이 된다. `/slam_toolbox/graph_visualization` 의 마커 수는 그 크기의 대용(이 카드의 '마커').
- **sim time · ROS_DOMAIN_ID 42**: 재생 때 bag 시각을 /clock 으로 흘려 노드가 그 시각으로 동작하게 하는 것(use_sim_time). 도메인 42 는 라이브 스택(도메인 0)과 DDS 통신이 섞이지 않게 분리한 번호.
- **map 층 vs odom 층**: map→odom(SLAM)과 odom→base(EKF)는 다른 층이다. 포크는 앞쪽만 고친다 — odom 프레임에 장애물을 기억하는 로컬 코스트맵 · nvblox 는 그대로 어긋날 수 있다([F0-a 카드](f0-rotation-side-slip.md) 용어 'odom 층 어긋남').
