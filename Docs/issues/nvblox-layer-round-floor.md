# 호스트 nvblox 코스트맵 층의 셀 인덱스 결함 — `round` → `floor`

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **해결(결함 확정 · 수정 채택)** — 층이 슬라이스를 셀 단위로 그대로 옮김(V1), 상자 통과 측 가장자리 0.00 vs 물리 +0.011(V3). 단 슬라이스 픽셀 규약(모서리 기준)은 메시지 주석 · 재캡처로 판단했고 nvblox 코어 소스로는 **미확인**(§3 · §5.3). 상류 보고는 안 함 | 09-21 §10.3(관찰) → §10.4(소스 읽기) → §10.5(수정 · 재캡처), 09-22 §1.1(재부팅 뒤 정렬 유지 확인), 이후 10-27 §15~§17 같은 파일에 두 번째 수정 | [09-21 §10.3](../debug_log/2026-09-21/SUMMARY.md) 셀 단위 차이 시각화 — 층 상자가 슬라이스보다 두 축 모두 −0.05 | Jetson 호스트 포크 `~/workspaces/isaac_ros-dev/src/isaac_ros_nvblox/nvblox_nav2/src/nvblox_costmap_layer.cpp` L308 한 줄(저장소에는 원본 대비 차이만: [`Docs/05_nvblox/nvblox_nav2_rover.patch`](../05_nvblox/nvblox_nav2_rover.patch), 10-27 에 만듦). 컨테이너 쪽 nvblox 는 무변경 | [nvblox 이전 N0~N4](nvblox-migration-n0-n4.md)(이 결함이 나온 정지 A/B 의 전체 흐름) · [SLAM map→odom 시각 정체](slam-stamp-freeze.md)(10-27 같은 파일의 TF 실패 처리 결함) · `nvblox-n6-global-ghosts.md`(09-22 §4~ · 09-23 — 같은 층을 전역 코스트맵에도 씀) · [낮은 상자 기억](low-box-global-memory.md) (6 기) |

**한 줄**: 09-21 저녁, nvblox 이진 층과 STVL 층을 같은 자세에서 셀 단위로 겹쳐 보니 층의 상자가 nvblox 가 낸 원자료(ESDF 슬라이스)보다 **x · y 모두 정확히 한 칸(5 cm) 음의 방향**으로 밀려 있었다. 층 소스를 읽어 보니 `lookupInSlice()` 가 슬라이스 인덱스를 `round((pos − origin)/res)` 로 구하는데, 슬라이스 메시지 정의는 origin 을 **첫 픽셀의 모서리**로 둔다 — 모서리 기준이면 `floor` 가 맞고 `round` 는 소수부 ≥ 0.5 인 축에서 옆 픽셀을 읽는다. 한 줄 고쳐 같은 배치에서 재캡처하자(판정 기준을 캡처 전에 선언) 층 = 슬라이스 · 통과 측 가장자리 오차 −6 cm → −1 cm 가 됐다. 이 결함은 상자의 **통과 측(왼쪽) 가장자리를 물리보다 6 cm 안쪽에** 찍는 위험한 방향의 오차였고, 사용자가 본 "STVL 이 더 정확해 보인다" 의 절반이 이것이었다(나머지 절반은 표면 뒤 TSDF 절단 띠 — [N0~N4 카드](nvblox-migration-n0-n4.md) §4).

> 이 수정은 Jetson 포크의 **미커밋 diff** 로만 살아 있다(09-21 §10.5 · 절차 `TEST_COURSE_AND_GATES.md` 운영 규칙 11). 저장소에는 10-27 부터 패치 파일로 남는다. 재부팅으로는 안 사라지지만(09-22 §0 `j498_state.txt` "포크 diff 1 file changed") `git checkout` · 재클론 · 상위 버전 갱신 때 사라진다 — 그때 `git apply Docs/05_nvblox/nvblox_nav2_rover.patch` 후 `colcon build --packages-select nvblox_nav2`.

---

## 1. 증상
- 09-21 §10.3: 같은 배치(출발 테이프, 상자 앞단 +0.90 · 우 0.08)에서 로컬 코스트맵을 STVL → nvblox → STVL 로 재캡처해 5 cm 격자로 대조(사용자 질의 "치명 셀이 무엇인지, STVL 과 어떤 식으로 차이가 있는지 시각화"):

  | | STVL 층 | nvblox 층(이진) | nvblox 슬라이스(원자료) | 물리(카메라 점군) |
  |---|---|---|---|---|
  | 상자 LETHAL 범위 x / y | 1.10~1.25 / −0.20~0.00 | **1.10~1.35 / −0.30~−0.05** | **1.15~1.40 / −0.25~0.00** | 전면 1.153 · y −0.169~+0.011 |

  층과 슬라이스는 같은 nvblox 출력인데 층이 두 축 모두 정확히 −0.05. 결과적으로 층의 상자 **통과 측(왼쪽, +y) 가장자리가 −0.05** 로 물리 +0.011 보다 6 cm 안쪽이었다 — 로버가 그쪽으로 지나가므로 '실제보다 여유가 있다' 고 보는 위험한 방향.
  데이터: `../debug_log/2026-09-21/outputs/grid_{stvl,nvblox}_costmap.json` · `grid_nvblox_slice.json`(도구 `job489_gridcmp.py` JSON 판, 아래 §8), 그림 [`figures/2026-09-21_costmap_stvl_vs_nvblox_v1_before_fix.html`](../05_nvblox/figures/2026-09-21_costmap_stvl_vs_nvblox_v1_before_fix.html)(= `outputs/j491_costmap_ab.html`). 표의 범위 수치는 job491 이 화면에 찍은 값인데 그 화면 출력은 저장되지 않았다(HTML 안 표에만 있음).
- 그 전 §10.2 의 10 cm ASCII 지도(`outputs/j489_nvblox_mode.txt`)에서도 "슬라이스 자체는 x 1.2~1.4 · y −0.2~0.0 = 물리와 일치 → 층의 격자 재표본화로 ≤1 셀 번짐" 이라고 적었다. 즉 **어긋남은 §10.2 에서 이미 보였지만 '재표본화 번짐' 으로 넘겼다**(§5.1).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론 | 데이터 |
|---|---|---|---|---|
| 09-21 §10.2 | 정지 A/B 첫 관찰, 10 cm ASCII | 층 상자 x 1.1~1.3 · y −0.3~−0.1, 슬라이스 1.2~1.4 · −0.2~0.0 | "층의 격자 재표본화로 ≤1 셀 번짐" ✘(결함이었음) | `outputs/j488_layer_ab.txt` · `j489_nvblox_mode.txt` · `j489_stvl_mode.txt` |
| 09-21 §10.3 | 5 cm 셀 단위 JSON 덤프 · HTML | 층 = 슬라이스 − (0.05, 0.05) 정확히 | 차이의 기전은 '절단 띠' 로 설명(추정) — 평행이동은 아직 원인으로 안 봄 | `outputs/j490_griddump.txt` · `grid_*.json` · `j491_costmap_ab.html` |
| 09-21 §10.4 | 사용자 질의 "현재로서는 STVL 이 더 정확해 보인다. 어떻게 해결할 것인가" → 플러그인 소스 읽기(읽기 전용, DDS 참여 없음) | `lookupInSlice()` L306~308 `round()`; `DistanceMapSlice.msg` "origin … upper-left corner of the upper-left most pixel"; `esdf_slice_conversions.cu` L157~158 `origin = aabb.min()` | **(A) 층의 격자 조회 반 셀 규약 결함**(코드로 확인) + (B) 절단 띠는 이진/기울기 무관 LETHAL | `outputs/j492_layersrc.txt`(도구 `run_j492.sh` · `run_j492b.sh` · `run_j492c.sh`) |
| 09-21 §10.5 | 판정 기준 V1~V4 선언 → `round`→`floor` 한 줄 · 재빌드 38 s → 같은 배치 재캡처(stvl2 · nvfix) | V1 통과(층 외곽 = 슬라이스 외곽 1.15~1.40 / −0.25~0.00), V3 통과(통과 측 0.00), V4 0.40 유지, V2 는 선언대로 평가 불가 → 정정 후 통과 | **결함 확정 · 수정 채택** | `outputs/j493_fixcapture.txt` · `j493_ab_nvfix.txt` · `j494_viz2.txt` · `grid_stvl2_costmap.json` · `grid_nvfix_*.json` · `j494_costmap_ab_v2.html` · `j495_sochk.txt` · `j496_endstate.txt` · `j497_endstate.txt` |
| 09-22 §0 · §1.1 | 재부팅 뒤 포크 diff 유지 확인, 절단 A/B 에서 층 vs 슬라이스 재대조 | diff 1 파일 유지, 공통 영역 순수 차이 t4 0/0 | 정렬은 재부팅 뒤에도 유지 | `../debug_log/2026-09-22/outputs/j498_state.txt` · `j502_eval.txt`(층 = 슬라이스 상자 외곽 t4 · t2 동일) |
| 이후 10-27 §15~§17 | 같은 파일의 슬라이스 콜백 catch 에 `return;` 추가, 원본 대비 전체 차이를 패치 파일로 | (이 카드 §7) | | `../debug_log/2026-10-27/SUMMARY.md` §15~§17 |

## 3. 기전 — 코드로 본 것과 아직 못 본 것
### 3.1 슬라이스와 층이 하는 일
- 컨테이너의 `nvblox_node` 는 ESDF 의 한 높이 단면을 `nvblox_msgs/DistanceMapSlice` 로 낸다: `origin`(x, y) · `resolution`(0.05) · `width` × `height` · 행 우선 `data[]`(각 픽셀 = 가장 가까운 표면까지의 거리 m, 미관측은 `unknown_value`). 메시지 주석(`j492_layersrc.txt` "## msg"): *"The location of the origin of the distance map slice image. This point coincides with the upper-left corner of the upper-left most pixel."* — **origin = 첫 픽셀의 모서리**. 변환 코드 `esdf_slice_conversions.cu` L157~158 은 `map_slice->origin.x = aabb.min().x()` (블록 AABB 의 최소 모서리).
- 호스트 Nav2 의 `NvbloxCostmapLayer::updateCosts()`(L141~222)는 코스트맵 셀 (i, j) 마다 `mapToWorld` 로 셀 **중심** 좌표를 얻고 → `T_G_S_.inverse()` 로 슬라이스 프레임에 옮겨 → `lookupInSlice(pos_S)` 로 거리를 읽고 → 거리 ≤ 0 이면 LETHAL, 아니면(이진 모드) FREE.
- `lookupInSlice()`(L298~328, 수정 전):
  ```cpp
  Eigen::Vector2f scaled_position = (pos - Eigen::Vector2f(slice_->origin.x, slice_->origin.y)) / slice_->resolution;
  Eigen::Vector2i pos_index = scaled_position.array().round().cast<int>();   // ← L308
  ```

### 3.2 왜 round 가 틀렸나 — 숫자 예
- 모서리 기준이면 픽셀 k 가 덮는 구간은 `[origin + k·res, origin + (k+1)·res)` → 올바른 인덱스는 `floor(s)`, s = (pos − origin)/res.
- 예: origin.x = 0.00, res 0.05, 코스트맵 셀 중심 pos = 1.175(셀 [1.15, 1.20)). s = 23.5 → floor 23(= 픽셀 [1.15, 1.20), 맞음), **round 24**(= 픽셀 [1.20, 1.25)). 즉 층의 1.15~1.20 칸에 1.20~1.25 칸의 거리가 들어간다 → 층 그림 전체가 **−1 셀** 이동해 보인다.
- s 의 소수부는 '코스트맵 셀 중심 − 슬라이스 origin' 의 소수부라, 두 격자가 모두 5 cm 이고 슬라이스 origin 은 블록 경계(복셀 격자 위)에 있으므로 **한 Nav2 세션 안에서는 모든 셀에 같은 값**이다(이 카드 작성 때의 코드 추론). 로컬 롤링 창의 원점은 처음 기동 자세에서 정해지고 이후 정수 셀만큼 옮겨지므로, 결함은 축마다 '이번 기동에서는 전부 −1 셀' 또는 '전부 0' 으로 나타난다 — §10.3 은 두 축 모두 −1 셀인 세션이었다. job488 은 매번 Nav2 를 재기동하므로 캡처마다 유무가 달라질 수 있다.
  - 정정 메모: 09-21 §10.4 는 "세션마다 **방향** · 유무가 달라짐" 이라고 썼지만, 슬라이스 프레임 = 코스트맵 프레임(로컬 odom)일 때 round 는 언제나 +1 픽셀을 읽으므로 방향은 −x · −y 로 고정이다. 방향이 바뀔 수 있는 것은 슬라이스 프레임이 코스트맵 프레임과 회전돼 있을 때(전역 map 코스트맵, N6-1 이후)뿐이다(코드 추론, 측정 아님).

### 3.3 아직 못 본 것 — 슬라이스 픽셀 규약의 최종 확인(미확인)
- 판단 근거는 **메시지 주석 + `origin = aabb.min()` + 재캡처의 물리 대조**다. nvblox 코어 슬라이서(`esdf_slicer`)는 apt 바이너리라 소스가 컨테이너에 없었다(`run_j492c.sh` 의 `find / -name "esdf_slicer*"` 결과 비어 있음, `j492_layersrc.txt` 끝 "## slicer files:" 빈 줄).
- 같은 파일 L64~65(`j492_layersrc.txt`)는 점군 변환에서 `point.x = aabb.min().x() + voxel_size * col_idx` 로 **+0.5 없이** 점을 놓는다. 모서리 규약이 맞다면 이 점군(우리는 안 씀)은 반 칸 어긋나 있을 것이고, 반대로 중심 규약이면 층의 floor 가 틀린 것이 된다 — 이 불일치는 해소하지 않았다(**미확인**, §5.3).

## 4. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| (§10.2) 층의 −1 셀은 코스트맵 재표본화 번짐 | 번짐이면 양쪽으로 퍼져야(셀 수 증가) 하고 평행이동이 아님 | §10.3: 상자 셀 19(층) vs 20(슬라이스) — 수는 같고 **두 축 모두 정확히 −0.05 평행이동** | 기각 |
| (A) `lookupInSlice` 의 round 가 모서리 기준 origin 과 안 맞음 | 소스 읽기(§3) → 수정 뒤 **같은 배치 재캡처**에서 V1(층 외곽 = 슬라이스 외곽) · V3(통과 측 가장자리 = 물리 ±2.5 cm) | V1 1.15~1.40 / −0.25~0.00 동일, V3 0.00 vs +0.011(수정 전 −0.05) | **지지(수정 채택)** |
| (A') 슬라이서 규약이 사실은 중심 기준(round 가 맞음) | 선언: V1~V3 실패 시 이 가능성 → 원점 +0.5 셀 보정 재시도 | V1~V3 통과로 재시도 안 함. 다만 §5.3 의 반 칸 논점 | 기각(근거는 V3 · 주석; 코어 소스 미확인) |
| (B) 남은 차이(층만 LETHAL 90 셀)는 표면 뒤 TSDF 절단 띠 | 절단 4 → 2 정지 A/B(09-22 §1) | 띠 셀 73 → 25, 상자 깊이 0.25 → 0.15 | 지지 — [N0~N4 카드](nvblox-migration-n0-n4.md) §4 |

## 5. 조치와 효과
### 5.1 조치
- `job493_fixfloor.sh`(09-21 18:19~): L308 `round()` → `floor()` 를 sed 로(주석 "2026-09-21 수정: origin 은 픽셀 모서리(DistanceMapSlice.msg) → floor 가 맞음. round 는 −1 셀 평행이동을 일으킴(rover §10.4)") → `colcon build --symlink-install --packages-select nvblox_nav2` 38 s(`j493_fixcapture.txt`: Finished 35.8 s). 설치 `.so` 는 build 로의 심볼릭이고 18:20:00 갱신(`j495_sochk.txt` · `j496_endstate.txt`). 18:21 job488 이 Nav2 를 재기동하면서 새 `.so` 를 로드.
- 되돌리기: `git -C ~/workspaces/isaac_ros-dev/src/isaac_ros_nvblox checkout -- nvblox_nav2/src/nvblox_costmap_layer.cpp` + 재빌드.

### 5.2 판정 기준(캡처 전 선언, 09-21 §10.5)과 결과
| 기준 | 선언 | 결과(`j494_viz2.txt`) | 판정 |
|---|---|---|---|
| V1 | 층 상자 LETHAL 외곽 = 슬라이스 ≤0 외곽 | 층 x 1.15~1.40 · y −0.25~+0.00 (20 셀) = 슬라이스 같은 값 (20 셀) | 통과 |
| V2 | 층 vs 슬라이스 5 cm 스냅 차이 층만 · 슬라이스만 각 ≤ 5 | 전체 창: 층만 197 · 슬라이스만 75 → **평가 불가**(라이다 층 셀 · 3×3 m 창 밖 슬라이스를 셈). 정정: 공통 영역(슬라이스 기지 ∩ 반경 1.45 m) 409 셀, 둘 다 38 · 층만 1(라이다 귀속 1, 순수 0) · 슬라이스만 0 | 정정 뒤 통과 — **데이터를 본 뒤 바꾼 기준이라 선언보다 약함** |
| V3 | 상자 통과 측(왼쪽) 가장자리 = 물리 +0.011 ± 2.5 cm | +0.00(수정 전 −0.05) | 통과 |
| V4 | 감사 기준1 최소폭 0.40 m 유지 | 0.40 m(@1.20) · RPP 0.25, 3 표본 동일(`j493_ab_nvfix.txt`) | 유지 |

### 5.3 전후 수치
| | STVL(stvl2) | 층 수정 전(v1, 09-21 §10.3) | 층 수정 후(nvfix) | 슬라이스(nvfix) |
|---|---|---|---|---|
| 로컬 LETHAL(3×3 m) | 211 | 278 | 294 | ≤0 172(창 밖 포함) |
| 상자 외곽 x / y | 1.10~1.25 / −0.20~0.00 (9) | 1.10~1.35 / −0.30~−0.05 (19) | **1.15~1.40 / −0.25~0.00 (20)** | 1.15~1.40 / −0.25~0.00 (20) |
| 5 cm 스냅 둘 다 / nvblox 만 / STVL 만 | — | 189 / 89 / 12 | 204 / 90 / 7 | |
| nvblox 만: 상자 / 좌측 가구 / 우측 벽 | — | 12 / 26 / 51 | 13 / 23 / 54 | |
| LETHAL 중 센서 점 8 cm 근거 | — | 93~95 %(§10.2, 다른 표본) | 98~99 % | |

- 남은 '층만' 90 셀은 결함이 아니라 (B) 표면 뒤 절단 띠(상자 깊이 0.25 = 앞면 1.153 + 절단 0.20 + 셀 양자화). 수정은 이 띠를 줄이지 않는다.
- 효과의 범위: 이 수정은 관측된 표면의 **위치**만 바로잡는다. 통과 폭(감사 기준1 0.40)은 수정 전 두 번째 표본에서도 0.40 이었다(09-21 §10.3) — 기준1 이 재는 행(x 1.20)에서는 −1 셀이 폭을 바꾸지 않았다(좌측 가구 쪽도 같이 밀리므로). 위험이 컸던 곳은 상자 옆을 지나는 MPPI 의 상자 가장자리 여유(6 cm 과대).
- 09-22 이후 모든 nvblox 주행(N4 n4n1~3, N6, 10 월 순회)은 수정본 위에서 돌았다. 수정 전 층으로 주행한 회차는 없다.

## 6. 내 실수
### 6.1 §10.2 에서 −1 셀을 '재표본화 번짐' 으로 넘김 — 칸 형식
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 정지 A/B 첫 관찰(job488 · job489 ASCII 10 cm)에서 층과 슬라이스가 같은지 확인 |
| 본 것 | 슬라이스 상자 x 1.2~1.4 · y −0.2~0.0, 층 x 1.1~1.3 · y −0.3~−0.1(`outputs/j489_nvblox_mode.txt`) — 두 축 모두 한 칸 |
| 처음 추론 | "층의 격자 재표본화로 ≤1 셀 번짐" — 차이가 1 셀 이하라 허용 범위로 봄 |
| 의심한 이유 | 번짐이면 셀이 양쪽으로 늘어야 하는데 **한쪽으로 한 칸 평행이동**이었고, 같은 nvblox 출력을 두 번 그린 것이라 0 이어야 했다. §10.3 의 5 cm 덤프에서 −0.05 가 x · y 모두 '정확히' 였음 |
| 판별 | 소스 읽기(`run_j492*.sh`) → 수정 → 같은 배치 재캡처(V1~V4) |
| 결론 | 반 셀 규약 결함. 수정 뒤 층 = 슬라이스 |
| 다음에 알아보는 법 | **서명**: 같은 데이터의 두 표현(원자료 vs 변환 결과)이 두 축 모두 정확히 한 칸 같은 방향으로 어긋나면 '번짐' 이 아니라 인덱스 규약(round/floor · 중심/모서리) 결함. 원자료와 변환 결과의 셀 대조는 첫 연결 때 바로 한다(10 cm ASCII 는 5 cm 평행이동을 반올림으로 가린다) |
| 데이터 | `2026-09-21/outputs/j489_nvblox_mode.txt` · `j490_griddump.txt` · `grid_nvblox_{costmap,slice}.json` · `j492_layersrc.txt` |

### 6.2 V2 를 평가할 수 없는 형태로 선언 — 칸 형식
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 수정 후 '층 = 슬라이스' 를 셀 수로 판정(V2: 층만 · 슬라이스만 각 ≤ 5) |
| 본 것 | 전체 창 비교 층만 197 · 슬라이스만 75(`j494_viz2.txt` "층 vs 슬라이스: 둘 다 97 / 층만 197 / 슬라이스만 75") |
| 처음 추론 | (선언 문구대로면 불합격) |
| 의심한 이유 | V1(외곽)은 완전히 같았다. 층만 197 은 코스트맵에 **라이다 ObstacleLayer 셀**이 섞인 것이고, 슬라이스만 75 는 슬라이스(48×72)가 코스트맵 창(3×3 m) **밖까지** 이어진 것(≤0 172 중 134 가 반경 1.45 m 밖) — 기준이 다른 것을 세고 있었다 |
| 판별 | 공통 영역(슬라이스 기지 ∩ 반경 1.45 m) 으로 한정 + STVL 모드 캡처에서도 LETHAL 인 셀(공유 라이다 층) 제외 |
| 결론 | 둘 다 38 · 순수 층만 0 · 슬라이스만 0 → 통과. 단 **데이터를 본 뒤 정한 기준**이라 근거 강도는 선언보다 약하다고 기록(09-21 §10.5) |
| 다음에 알아보는 법 | 셀 수 기준을 선언할 때는 **비교 영역(두 지도가 모두 정의된 곳)과 다른 층의 기여를 빼는 규칙까지** 같이 선언한다. 이 규칙은 09-22 절단 A/B 평가(`job502`)에도 '구역별' 로 이어졌다 |
| 데이터 | `2026-09-21/outputs/j494_viz2.txt` · `grid_nvfix_{costmap,slice}.json` · `grid_stvl2_costmap.json` |

### 6.3 V1 은 슬라이스 규약을 검증하지 못한다(이 카드 작성 때 다시 본 것) — 칸 형식
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 수정이 맞음(슬라이스는 모서리 기준)을 V1~V3 으로 확정 |
| 본 것 | V1 · V3 통과 |
| 처음 추론(09-21) | "V1~V3 통과 = 결함 확정 · 수정 채택" |
| 의심한 이유 | 슬라이스 셀을 좌표로 그리는 우리 도구(job489 · job474 · job506)도 모두 `origin + (k + 0.5)·res`, 즉 **모서리 규약**을 가정한다. 그러면 floor 로 고친 층이 이 그림과 같아지는 것(V1)은 규약이 맞든 틀리든 성립한다 — V1 은 '수정이 적용됐고 두 코드 경로가 같은 규약' 이라는 확인이지 규약 자체의 증거가 아니다 |
| 판별 | 규약과 무관한 물리 기준만 본다: (a) V3 통과 측 가장자리 — 모서리 규약이면 0.00 vs 물리 +0.011(−1.1 cm), 중심 규약이었다면 슬라이스 픽셀의 실제 위치가 그려진 곳보다 반 칸 음(−)의 방향이라 가장자리 −0.025 → −3.6 cm. (b) N0 (i) 앞면 — 모서리 규약 1.175 vs 물리 1.153(+2.2 cm), 중심 규약이었다면 1.150(−0.3 cm). 두 물리 기준이 반 칸에서 서로 반대쪽을 가리킨다 |
| 결론 | 1 셀(5 cm) 평행이동 결함은 확정(수정 전 −6.1 cm → 후 −1.1 cm). **반 칸(2.5 cm) 수준의 규약은 측정으로 가르지 못했고** 메시지 주석 · `origin = aabb.min()` 에 기댄다(**미확인**). 반대 방향 힌트로 점군 변환 L64~65 의 +0.5 없음(§3.3)이 남아 있다 |
| 다음에 알아보는 법 | 두 표현을 같은 규약 가정으로 그려 비교하면 그 규약은 검증되지 않는다. 규약을 확정하려면 반 칸보다 작은 물리 기준이 필요: 예) 상자를 2.5 cm 씩 옮기며 슬라이스 앞면 셀이 바뀌는 위치를 찾거나, 복셀 0.03 · 슬라이스 셀 경계와 물리 면이 겹치지 않는 배치에서 앞면 · 옆면을 동시에 본다. 또는 nvblox 코어 소스(isaac_ros_nvblox 의 `nvblox` 서브모듈 `esdf_slicer`)를 직접 읽는다 |
| 데이터 | `2026-09-21/outputs/j494_viz2.txt`(V3) · `j474_n0a.txt`(N0 (i)) · `j492_layersrc.txt`(L64~65 · L157~158 · msg 주석) · 도구 `jobs/job474_n0_measure.py` · `job489_gridcmp.py`(09-22 판) |

### 6.4 `.so` 갱신 확인 경로 오기(같은 실수를 10-27 에 반복)
- `job493_fixfloor.sh` 는 `~/ros2_ws/install/nvblox_nav2/lib/libnvblox_costmap_layer.so` 의 수정 시각을 봤는데 실제 라이브러리 이름은 `libnvblox_nav2.so`(`j485_hostbuild2.txt` ".so: libnvblox_nav2.so"). 없는 파일이라 stat 이 0 → "**.so 갱신: NO (09:00:00)**"(`j493_fixcapture.txt`, 09:00:00 은 epoch 0 의 KST). 실제로는 `run_j495.sh` 로 build 쪽 `.so` 18:20:00 갱신 · install 은 build 로의 심볼릭임을 확인(`j495_sochk.txt` · `j496_endstate.txt`) — 결과 판단에는 영향 없음.
- 10-27 `chk_nvlayer_so.sh` 에도 같은 옛 이름 확인이 남아 NO 로 찍혔다(10-27 §17 "틀린 경로라 NO 로 찍힘 — 무시"). **알아보는 법**: 빌드 산출물 확인은 이름을 박지 말고 `find build/<pkg> install/<pkg> -name '*.so*' -printf '%T@ %p\n'` 로, 그리고 실행 중 프로세스가 연 라이브러리는 `/proc/<pid>/maps`(run_j495 방식)로 본다.

## 7. 이후 — 같은 파일의 두 번째 결함(10-27)과 패치 파일
- 10-27 §15: 주행 영상의 '문이 막혔다 풀림 · 상자가 벽 쪽으로' 가 전역 코스트맵 두 장에서만 나타났는데, 원인은 같은 `nvblox_costmap_layer.cpp` 의 `sliceCallback()` — `lookupTransform(map, odom, 슬라이스 stamp)` 가 예외를 내면 **경고만 찍고 return 하지 않아** 기본 Transform(단위)을 `T_G_S_` 로 저장, odom 슬라이스를 map 에 그대로 적어 장애물이 0.55 m · 7.5° 틀어졌다. 로컬은 슬라이스와 같은 odom 프레임이라 조회를 안 해 영향 없음. 방아쇠(TF 조회 실패)는 처음엔 부하로 추정했다가 SLAM map→odom stamp 정체로 정정(→ [SLAM map→odom 시각 정체](slam-stamp-freeze.md)).
- 10-27 §17: catch 에 `return;` 한 줄(직전 slice_ · T_G_S_ 쌍 유지) — `../debug_log/2026-10-27/jobs/prep_nvlayer_tffix_1027.sh` → `outputs/setup/prep_nvlayer_tffix_1027.txt`, 빌드 40 s. 정지 120 s 확인은 TF 실패가 한 번도 안 일어나 고친 경로 자체는 안 탔다(10-27 §17 한계).
- **패치 파일에서 보이는 모습**([`Docs/05_nvblox/nvblox_nav2_rover.patch`](../05_nvblox/nvblox_nav2_rover.patch), 상위 release-3.2 `7908a18` 기준, 커밋 `8e5ec16a` 10-27): 두 hunk —
  - `@@ -254,6 +254,7 @@ sliceCallback` : `+ return;  // 2026-10-27 수정: 조회 실패 시 이 슬라이스를 버림 …(rover 10-27 §15)`
  - `@@ -305,7 +306,7 @@ lookupInSlice` : `- …round().cast<int>();` → `+ …floor().cast<int>();  // 2026-09-21 수정: origin 은 픽셀 모서리 …(rover §10.4)`
  두 번째 hunk 의 줄 번호가 306 으로 밀린 것은 첫 hunk 의 한 줄 때문이다. 09-21 에는 패치 파일이 없었고(포크 미커밋 diff 만), 저장소에 원본 대비 차이가 남은 것은 10-27 부터다.
- 지금 상태(이 카드 작성 10-30, 저장소 기준 확인): 전역 · 로컬 코스트맵 모두 `nvblox_layer`(이진, `convert_to_binary_costmap: true`, [`nav2_params.yaml`](../../ros2_ws/src/rover_navigation/config/nav2_params.yaml) 로컬 L331~338 · 전역 L564~571) — 두 수정 모두 운용 경로에 있다. Jetson 포크에 패치가 실제로 적용돼 있는지는 이 카드에서 Jetson 을 보지 않아 **확인 안 함**(확인: `git -C ~/workspaces/isaac_ros-dev/src/isaac_ros_nvblox diff --stat` → 1 file, 2 insertions(+), 1 deletion(-) 이어야).

## 8. 남은 것
1. 슬라이서 픽셀 규약의 코어 소스 확인 또는 반 칸 물리 시험(§6.3) — 미확인.
2. 점군 변환(`esdf_slice_conversions.cu` L64~65)의 +0.5 없음이 상위의 다른 반 칸 어긋남인지 — 우리는 `static_esdf_pointcloud` 를 안 쓰지만 시각화에 쓰면 반 칸 어긋나 보일 수 있음(미확인).
3. 상류 보고: PHASE_N_RESULTS §5-5 "상류 보고 후보" 그대로 — 보고 안 함. 상위의 더 새 릴리스(4.x)가 고쳤는지는 확인 안 함(Orin Nano + JetPack 6 은 3.2 가 마지막 지원판이라 갱신 계획 없음, NVBLOX_MIGRATION_PLAN §6).
4. 이진 모드만 쓰므로 거리 → 비용 기울기(`inflation_distance` · `max_obstacle_distance`) 경로의 같은 인덱스는 검증 범위 밖이었으나 같은 `lookupInSlice` 를 쓰므로 수정 효과는 같다(코드 추론).

## 9. 실험 · 도구 색인
| 이름 | 무엇 | 데이터 |
|---|---|---|
| stvl_mode · nvblox_mode (§10.2) | 첫 정지 A/B 10 cm ASCII | `2026-09-21/outputs/j488_layer_ab.txt` · `j489_{stvl,nvblox}_mode.txt` |
| stvl · nvblox (§10.3, run_j490) | 5 cm JSON 덤프 v1 | `outputs/j490_griddump.txt` · `grid_{stvl,nvblox}_costmap.json` · `grid_nvblox_slice.json` · `j491_costmap_ab.html` |
| 소스 읽기 (§10.4) | 층 · 메시지 · 변환 코드 | `outputs/j492_layersrc.txt` |
| stvl2 · nvfix (§10.5, run_j493) | 수정 후 재캡처 | `outputs/j493_fixcapture.txt` · `j493_ab_nvfix.txt` · `grid_stvl2_costmap.json` · `grid_nvfix_{costmap,slice}.json` · `j494_viz2.txt` · `j494_costmap_ab_v2.html` |
| .so · 마감 확인 | 라이브러리 경로 · 잔존 노드 | `outputs/j495_sochk.txt` · `j496_endstate.txt` · `j497_endstate.txt` |
| 그림 | v1 · v2 자체 완결 HTML | [`figures/2026-09-21_costmap_stvl_vs_nvblox_v1_before_fix.html`](../05_nvblox/figures/2026-09-21_costmap_stvl_vs_nvblox_v1_before_fix.html) · [`…_v2_floor_fix.html`](../05_nvblox/figures/2026-09-21_costmap_stvl_vs_nvblox_v2_floor_fix.html) |

## 10. 도구 해설
도구 계보: (정지 A/B) `job488_layer_ab.sh` + `job489_gridcmp.py`(ASCII) → `job489` JSON 판 + `run_j490.sh` + `job491_vizgen.py`(v1 그림) → `run_j492*.sh`(소스 읽기) → `job493_fixfloor.sh` + `run_j493.sh` + `job494_vizgen2.py`(v2 그림 · V1~V4) → (09-22) `job501` + `job502_trunc_eval.py` + `job503_vizgen3.py`(절단 A/B, [N0~N4 카드](nvblox-migration-n0-n4.md)). `job488` · `job473` 의 자세한 해설도 그 카드에 있다. 모든 `run_*.sh` 는 PC(WSL)에서 `sshpass -p <PW> scp/ssh` 로 Jetson `/tmp` 에 올려 실행하는 래퍼이고 원본은 그날의 PC scratchpad(지금은 자동 삭제됨 — 저장소 `jobs/` 사본이 유일).

### job489_gridcmp.py — 코스트맵 · 슬라이스 격자 덤프(두 판)
- 실행: Jetson 호스트 python3(호스트에 `nvblox_msgs` 를 소스 빌드했으므로 가능), `python3 /tmp/job489_gridcmp.py NAME [SLICE=1] [TOPIC]`(TOPIC 은 09-22 판, 기본 `/local_costmap/costmap`). PC 래퍼 `run_j489.sh NAME [0|1]`.
- 왜: §10.2 "층이 무엇을 LETHAL 로 찍는가" 를 위치로 보려고. §10.3 에서 시각화용 원자료가 필요해 JSON 덤프를 붙였다.
- 하는 일: `/local_costmap/costmap`(OccupancyGrid, transient_local · reliable, depth 1) 한 장과 `/nvblox_node/static_map_slice`(sensor_data QoS) 한 장을 12 s 안에 받고, TF(코스트맵 프레임 ← base_link)를 최대 4 s 기다려 조회. 셀 중심을 `origin + (k + 0.5)·res − 로버 위치` 로 구해 로버 yaw 로 돌려 **base_link 좌표**로. 코스트맵 값 100 → '#', 99 → 'o'(내접), 1~98 → '.', 0 → ' ', −1 → '?'; 슬라이스 거리 ≤ 0 → '#', 미지 → '?'. x −0.5~2.0 · y +1.0~−1.0 의 **10 cm ASCII**(셀 우선순위 # > o > ? > . > 공백). 앞 0.3~1.6 m 의 LETHAL 을 y 0.2 m 구간별로 센다. **JSON 판**(09-22 jobs 사본)은 `/tmp/grid_<NAME>_costmap.json`(값 ≠ 0 셀만 `[x, y, 값]`) · `/tmp/grid_<NAME>_slice.json`(모든 셀 `[x, y, 거리 또는 null]`)을 쓴다.
- 출력: `==== NAME 로컬 코스트맵 60x60 @0.05: LETHAL n, 내접 n, 미지 n, 비용>0 n` · ASCII 21 줄 · `앞 0.3~1.6 m LETHAL 셀 …` · `==== NAME nvblox 슬라이스 48x72 @0.05 (odom): 장애물(≤0) n, 미지 n, 자유 n | 거리 최소 · 최대` → `2026-09-21/outputs/j489_{stvl,nvblox}_mode.txt` · `j490_griddump.txt` · `j493_fixcapture.txt`, JSON `grid_*.json`(09-21 · 09-22 outputs).
- 쓰인 곳: 09-21 §10.2 표 · §10.3 · §10.5, 09-22 §1.1, N6-1 전역 비교(09-22 §5.1, TOPIC 인자).
- 계보 · 결함: ⚠ **`2026-09-21/jobs/job489_gridcmp.py` 사본은 JSON 덤프가 없는 앞 판**이다. §10.3 · §10.5 의 JSON 을 만든 판은 `2026-09-22/jobs/job489_gridcmp.py`(JSON 2 줄 + TOPIC 인자)에만 남아 있다(이 카드 작성 때 diff 로 확인). 슬라이스 셀 좌표에 +0.5(모서리 규약)를 가정 — §6.3. 한 장 표본이라 nvblox 층 전환 직후(클리어 뒤 재적분 중)에 찍으면 과도 상태를 잡는다.
- 다시 쓸 수 있나: 예(09-22 판). 전역은 TOPIC `/global_costmap/costmap`.

### run_j490.sh — v1 원자료 캡처
- 실행: PC(WSL), 인자 없음. Jetson 에 job489 · job488 · job473 을 올리고 한 ssh 안에서: 로컬 코스트맵 클리어 → 12 s → `job489 stvl 0` → `job473 start`(nvblox 기동) → `job488 nvblox 1.153 -0.079`(Nav2 재기동 · 감사) → 5 s → `job489 nvblox 1` → `job488 stvl` 복귀 → `job473 stop` → JSON 3 개 회수.
- 왜: §10.3 사용자 질의(시각화). 출력 `outputs/j490_griddump.txt`. 감사 기준1 이 이번엔 0.40(§10.2 의 0.10 은 과도 상태였다는 정정의 근거).
- 결함: job488 이 Nav2 를 재기동하므로 STVL 캡처와 nvblox 캡처의 로컬 롤링 창 원점이 다르다 → 두 코스트맵 격자가 수 mm 어긋나 job491 이 floor 스냅으로 맞춘다. 슬라이스 '거리 최대' 가 j489(2.00)와 달리 1.00 으로 찍힌 이유는 미확인(같은 nvblox_n0.yaml 로 재시작했을 것으로 보이나 확인 안 함).

### job491_vizgen.py — v1 비교 그림
- 실행: PC python, 인자 없음(작업 폴더의 `grid_stvl_costmap.json` · `grid_nvblox_costmap.json` · `grid_nvblox_slice.json`).
- 하는 일: 세 JSON 을 공통 5 cm 격자 `floor(x/0.05)` 에 스냅(셀 중심 좌표라 floor 가 그 셀). 셀 분류 L(≥100) · I(99) · C(1~98) · F → 두 코스트맵 차이 B(둘 다 L) · N(nvblox 만) · S(STVL 만). 구역 규칙: 상자 0.9 < x < 1.5 · −0.35 < y < 0.15, 우측 벽 y < −0.5, 좌측 가구 y > 0.45, 뒤 · 옆 x < 0.3. 상자 외곽 = 구역 안 LETHAL 의 x · y 최소 ~ (최대 + 1 셀). 물리 상자 외곽 `x 1.153~1.263, y −0.169~+0.011` 은 **코드에 박힌 상수**. SVG 4 판(STVL / nvblox / 차이 / 슬라이스) + 차체 · 카메라 화각선.
- 출력: 화면 요약(공통 · nvblox 만 · STVL 만, 구역별, 상자 외곽 3 개) — **출력 원문 없음**(저장 안 함, 수치는 SUMMARY §10.3 표와 HTML 안에만) · `costmap_ab.html` → `outputs/j491_costmap_ab.html` = 그림 1.
- 결함: docstring 은 "인덱스 = round(x/0.05)" 라고 쓰지만 코드는 floor(같은 날 같은 주제의 결함이라 혼동 주의 — 셀 중심 좌표에서는 floor 가 맞음). 물리 상자 상수.
- 다시 쓸 수 있나: 입력 이름 고정 → 인자화한 job494 를 쓴다.

### run_j492.sh · run_j492b.sh · run_j492c.sh — 플러그인 소스 읽기(읽기 전용)
- 실행: PC, 인자 없음. ssh 로 Jetson 의 `~/workspaces/isaac_ros-dev/src/isaac_ros_nvblox`(release-3.2 7908a18 클론) 파일만 grep/sed — ROS · DDS 참여 없음(주행 30 s 규칙과 무관).
- 하는 일: (492) `nvblox_costmap_layer.cpp` 의 `updateBounds` 부터 끝까지 주석 · 빈 줄 빼고 120 줄, `DistanceMapSlice.msg` 전문, 변환기 origin grep(경로가 틀려 빈 결과), 절단 · ESDF 파라미터 grep. (492b) `lookupInSlice` 함수 전체, `*slice*conver*` 파일 찾기 → `esdf_slice_conversions.cu` 의 origin · aabb grep, `truncation_distance_vox` 가 있는 yaml 목록 · 값, 실행 중 `/tmp/nvblox_n0.yaml` 값. (492c) `esdf_slice_conversions.cu` 의 origin · aabb · width · 0.5 grep(L39~276), 컨테이너 호스트 쪽 `/opt/ros/humble/include/nvblox/...slice*` grep, `find / -name esdf_slicer*`.
- 출력: 세 개를 이어 붙인 `outputs/j492_layersrc.txt`(앞머리 wsl 경고 줄은 PC 쪽 잡음). 핵심 줄: L186~188 `distance <= 0 → LETHAL` 이 `convert_to_binary_costmap_` 분기 **앞**(→ 절단 띠는 이진/기울기 무관, N0~N4 카드 §4), L308 `round()`, msg "upper-left corner", .cu L157~158 `origin = aabb.min()`, 벤더 yaml 전부 `truncation_distance_vox: 4.0`.
- 결함: 492 의 변환기 경로 오기(`src/conversions/esdf_slice_converter.cpp` — 실제는 `src/lib/conversions/esdf_slice_conversions.cu`), 492c 의 코어 헤더 경로도 비어 있음 → 코어 슬라이서 규약은 못 봄(§3.3).
- 다시 쓸 수 있나: 포크 경로가 같으면 그대로. 지금은 패치가 적용된 상태라 원본을 보려면 `git show HEAD:nvblox_nav2/src/nvblox_costmap_layer.cpp`.

### job493_fixfloor.sh ★ 수정 · 재빌드
- 실행: Jetson, 인자 없음(run_j493 안에서). 
- 하는 일: 수정 전 `scaled_position.array()` 줄 출력 → `round().cast<int>();` 가 있으면 sed 로 `floor().cast<int>();  // 2026-09-21 수정: …` 로 바꿈(멱등) → 수정 후 줄 · `git diff --stat` · `-U1` 의 ± 줄 → `colcon build --symlink-install --packages-select nvblox_nav2 --cmake-args -DCMAKE_BUILD_TYPE=Release` 소요 → `.so` 수정 시각 비교 → "실행 중 Nav2 는 아직 옛 .so — job488 재기동 때 반영".
- 출력: `j493_fixcapture.txt` 앞부분('수정 전 308 … round', '수정 후 … floor', 1 file changed 1+/1−, 빌드 38 s, ".so 갱신: NO" — §6.4 경로 오기).
- 쓰인 곳: 09-21 §10.5, PHASE_N_RESULTS §4 "job493_fixfloor.sh 로 재적용", 절차 운영 규칙 11.
- 다시 쓸 수 있나: 원본 소스에는 예(sed 패턴이 정확히 맞을 때). 지금은 패치 파일(`git apply`)이 두 수정을 함께 담으므로 그쪽을 쓴다.

### run_j493.sh — 수정 후 재캡처(stvl2 · nvfix)
- 실행: PC, 인자 없음, ssh 한도 840 s. 순서: job493(수정 · 재빌드) → 로컬 클리어 12 s → `job489 stvl2 0` → `job473 start` → `job488 nvblox 1.153 -0.079 | tee /tmp/j493_ab_nvfix.txt`(Nav2 재기동으로 새 `.so` 로드 · 감사 3 표본) → 5 s → `job489 nvfix 1` → `QUICK=1 job488 stvl`(감사 생략 복귀) → `job473 stop` → JSON 3 + 감사 회수.
- 출력: `outputs/j493_fixcapture.txt` · `j493_ab_nvfix.txt` · `grid_stvl2_costmap.json` · `grid_nvfix_{costmap,slice}.json`.
- 결함: `job488` 안의 `job315_boxcells.py` 가 인자 없이 불려 **IndexError**(`j493_ab_nvfix.txt` · `j488_layer_ab.txt` 모두) — job315 의 '근거 셀' 표는 이날 한 번도 안 나왔고, '센서 점 8 cm 근거 98~99 %' 는 job248 감사의 줄이다(SUMMARY 에는 job315 실패가 안 적힘). 기능상 영향 없음.

### job494_vizgen2.py ★ v2 비교 그림 · V1~V4 판정
- 실행: PC python, `python job494_vizgen2.py <stvl.json> <nvblox.json> <slice.json> <out.html> [감사 최소폭 문자열]`.
- 하는 일: job491 을 인자화 + 판 E(층 vs 슬라이스) + V1~V4. V1 = 층 상자 외곽 == 슬라이스 ≤0 상자 외곽(구역 규칙 job491 과 같음). V2(정정판) = 공통 영역(슬라이스 기지 ∩ base_link 반경 1.45 m — 3×3 m 창의 내접원) 안에서 '층만' 에서 STVL 캡처에서도 LETHAL 인 셀(라이다 층)을 빼고 순수 층만 ≤ 5 · 슬라이스만 ≤ 5. V3 = 상자 구역 층 LETHAL 의 최대 y 셀 위쪽 경계가 물리 +0.011 ± 0.025. V4 = 인자로 받은 감사 문자열 표시만(판정 없음 '—').
- 출력: 화면 9 줄 → `outputs/j494_viz2.txt`, HTML → `outputs/j494_costmap_ab_v2.html` = 그림 2.
- 결함: 물리 상자 상수(+0.011)가 코드에 있음. V2 는 데이터를 본 뒤 고친 기준(§6.2). V1 은 규약 검증력 없음(§6.3).
- 다시 쓸 수 있나: 같은 형식 JSON 이면 그대로. 09-22 절단 A/B 는 job503 으로 이어짐.

### run_j495.sh · run_j496.sh · job497_endstate.sh(+ run_j497.sh) — 라이브러리 · 마감 확인(읽기 전용)
| 도구 | 하는 일 | 출력 | 비고 |
|---|---|---|---|
| `run_j495.sh` | build · install 의 `*.so*` 수정 시각, planner 프로세스 `/proc/<pid>/maps` 의 nvblox 라이브러리, 로컬 plugins, 컨테이너 nvblox 프로세스 수 | `j495_sochk.txt`: build `libnvblox_nav2.so` 18:20:00, install 17:21:48(심볼릭 자체의 시각), planner 는 nvblox `.so` 안 엶(전역은 STVL 이었으므로 정상), "nvblox 노드: 3"(`pgrep -fc nvblox_node` 가 `bash -lc` 래퍼까지 셈 — 실행 파일 PID 기준은 job483 방식) | job493 의 'NO' 를 반증 |
| `run_j496.sh` | install `.so` 가 build 로의 심볼릭인지(readlink), 컨테이너에 nvblox 가 남았으면 `job473 stop` | `j496_endstate.txt`: 심볼릭 → build 18:20:00, 정지 실행 | |
| `job497_endstate.sh` | 컨테이너 · 호스트 nvblox 프로세스 수(`grep 'nvblox_nod[e]'` 로 자기 자신 제외), 로컬 plugins, 스택 프로세스 수, 로드 · 온도 | `j497_endstate.txt`: nvblox 0 · 0, plugins STVL, controller/planner/slam/relay/agent 각 1, 47.4 °C | "ssh 인라인에 프로세스 이름을 두지 않기 위해" Jetson 측 파일로 — 인라인 `pgrep -f nvblox` 가 ssh 명령줄 자신을 세는 함정 회피 |

## 11. 용어
- **DistanceMapSlice**: nvblox 가 ESDF 의 한 높이 단면을 내는 메시지. 픽셀 = 가장 가까운 표면까지 거리(m), 표면 안 · 위는 ≤ 0, 미관측은 `unknown_value`. 이 로버에서는 `/nvblox_node/static_map_slice`, 0.05 m, 9.5 Hz, odom 프레임.
- **origin 규약(모서리 vs 중심)**: 격자 원점이 첫 칸의 **모서리**면 칸 k = [o + k·r, o + (k+1)·r), 인덱스 = floor((p − o)/r). **중심**이면 칸 k 의 중심 = o + k·r, 인덱스 = round((p − o)/r). 규약을 섞으면 축마다 반 칸이 평균 오차가 아니라 '이번 격자 정렬에서는 전부 한 칸 / 전부 0' 으로 나타난다(두 격자 간격이 같을 때).
- **`lookupInSlice()`**: 호스트 Nav2 의 nvblox 층(`nvblox::nav2::NvbloxCostmapLayer`)이 코스트맵 셀 중심 좌표로 슬라이스 픽셀 값을 읽는 함수. 이진 모드에서는 그 값 ≤ 0 → LETHAL.
- **`T_G_S_`**: 층이 저장하는 '코스트맵 전역 프레임 ← 슬라이스 프레임' 변환. 로컬(odom = 슬라이스 프레임)은 단위 행렬, 전역(map)은 매 슬라이스 stamp 의 map←odom. 10-27 결함은 조회 실패 때 이것을 단위 행렬로 두고 슬라이스를 쓴 것.
- **포크 미커밋 diff**: 상위 저장소를 클론해 고친 뒤 커밋하지 않은 상태. `git diff --stat` 으로 살아 있는지 본다. 이 로버는 상위 코드를 저장소에 넣지 않고 패치 파일만 둔다.
- **공통 영역 비교**: 두 지도가 모두 정의된 곳(여기선 슬라이스 기지 ∩ 코스트맵 창 내접원)으로 한정하고, 한쪽에만 있는 다른 입력(라이다 층)의 기여를 빼고 세는 것.
