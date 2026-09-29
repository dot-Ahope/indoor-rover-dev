# slam_toolbox 포크 — 제자리 회전 중 스캔 처리 (회전 밀림을 지도 층에서 보정)

작성 2026-09-29. 근거 기록: `Docs/debug_log/2026-09-28/SUMMARY.md` §3·§6·§8·§9·§13, `Docs/debug_log/2026-09-29/SUMMARY.md` §3.1·§5·§12.
패치 원문: `Docs/debug_log/2026-09-28/jobs/slam_toolbox_rover_fork.patch`.

## 1. 한 줄 요약
SLAM 에 "오차 감지" 기능을 새로 넣은 것이 아니다. slam_toolbox 가 **제자리 회전 중에는 스캔을 버리던 조건**을 "이동 거리 **또는** 회전각이 문턱을 넘으면 처리" 로 한 줄 바꿨다. 그 결과 회전하는 동안에도 스캔 정합이 돌아, 로봇이 실제로 밀려난 위치를 지도(map) 좌표에서 따라가게 됐다.

## 2. 문제 — 왜 원본은 회전 밀림을 못 봤나
- 스키드스티어(트랙) 로버는 제자리 회전할 때 차체 중심이 **180° 당 10~27 cm 옆으로 밀린다**(09-28 §6, 스캔 직접 정합 16 회 측정).
- EKF 는 이 밀림을 볼 수 없다. 휠 오도메트리는 옆 속도 0 을 σ 0.01 로 보고하고, 자이로는 회전만 잰다. 그래서 odom 에서는 "제자리에서 돌았다" 로만 나온다.
- slam_toolbox 는 새 스캔을 쓸지 `shouldProcessScan()` 에서 정한다. 원본 조건은 **odom 기준 이동 거리만** 봤다:
  `if (dist² < 0.8 × minimum_travel_distance²) return false;` (회전각은 보지 않음)
- 제자리 회전 중 odom 이동 거리 ≈ 0 → **스캔이 전부 버려짐** → 스캔 정합이 한 번도 안 돌아 map→odom 보정이 0.
- 측정 확인(09-28 §8, bag 재생): 원본(apt) 설정으로 회전 11 회 중 **0 회 포착**, 본 이동 0.1~0.2 cm(실제 10~27 cm).

## 3. 고친 것 — `shouldProcessScan()` 한 조건
```cpp
// 원본
if (dist2 < 0.8 * min_dist2 || scan_ctr < 5) return false;
// 포크: 거리도 작고 "그리고" 회전각도 작을 때만 버림
const double dheading = fabs(NormalizeAngle(pose.GetHeading() - last_pose.GetHeading()));
const double min_heading = DegreesToRadians(getParamMinimumTravelHeading());
if ((dist2 < 0.8 * min_dist2 && dheading < 0.8 * min_heading) || scan_ctr < 5) return false;
```
- 문턱은 기존 설정값 그대로: `minimum_travel_distance 0.05 m`, `minimum_travel_heading 0.03 rad(≈1.7°)` (`rover_bringup/config/slam.yaml`).
- 회전 중에는 약 1.7° 마다 스캔을 정합해 포즈 그래프에 노드를 추가한다. 스캔 정합이 "실제로 어디에 있는지" 를 벽·가구 모양으로 맞추므로, 밀림이 map 포즈에 반영되고 그 차이가 map→odom 보정으로 나타난다.
- 정지·직진 중 동작은 원본과 같다(거리 조건이 그대로라서).

### 만들며 생긴 버그(기록)
Karto 의 `getParamMinimumTravelHeading()` 은 내부 라디안 값을 **도(degree)로 바꿔** 돌려준다. 첫 빌드는 이를 라디안으로 착각해 문턱이 1.72 rad(≈98°)가 됐고, 회전당 2 번만 처리되어 오차가 5~26 cm 였다(09-28 §9.1). `DegreesToRadians` 로 고쳤다.

## 4. 측정 근거
| 확인 | 데이터 | 결과 |
|---|---|---|
| 재생 A/B (09-28 §9.2) | 회전 bag 11 회전, 정답 = 정지 스캔 직접 정합 | 원본 0/11 포착 → **포크 11/11, 오차 평균 1.1·최대 2.1 cm** |
| 대안 비교 (같은 표) | "거리 0 + 시간 0.5 s" 설정만 바꾸기 | 정확도는 같지만 **정지 중에도 CPU 21 %**(노드 2 개/s 누적) → 기각 |
| 문턱 비교 (같은 표) | 회전 문턱 0.03 / 0.10 / 0.20 rad | 오차 1.1 / 2.4 / 4.8 cm → 0.03 유지 |
| 새 회전 실주행 (09-29 §3.1) | 시계·반시계 0.38 rad/s 완전 회전 4 회 | SLAM 오차 중앙값 **1.3 cm**(최대 1.6), 93° 부분 회전 3.5 cm |
| Nav2 주행 (09-29 §5·§12) | f0a7·f0b1·f0b2 | 회전 구간에서 SLAM 이 odom 을 5~10 cm 씩 되돌림, 복귀 오차는 줄자 ±5 cm 안 |

## 5. 한계·미확인 (추정은 추정으로)
- **09-29 새 회전 실주행(1.3 cm)은 B2 를 켠 상태**였다. B2 가 odom 초기값을 실제에 가깝게 만들어 정합 수렴을 도왔을 수 있다 → 포크 단독 효과와 섞여 있다(분리 시험 미실시). 다만 09-28 재생 A/B(11/11, 1.1 cm)는 B2 없이 포크만의 결과다.
- **CPU**: 재생에서 회전하는 동안만 slam 42~52 %(정지 중 4.5~5.5 %, 원본과 같음). 호를 그리며 도는 일반 주행에서 노드가 얼마나 더 쌓이는지·전체 CPU 는 라이브로 따로 재지 않았다.
- 이 보정은 **지도(map) 층**에서만 일어난다. EKF(odom) 는 여전히 회전 밀림을 못 보므로 로컬 코스트맵(odom 기준)은 회전 직후 잠깐 어긋날 수 있다(09-28 f0a3 관찰). odom 층까지 고치려면 rf2o 같은 스캔 기반 속도 입력이 필요 — JetPack 7.2 이전 단계로 미룸(로드맵 §7.4).
- 스캔 정합이 기댈 구조가 없는 곳(넓은 빈 공간)이나 사람이 많은 곳에서는 정합 자체가 약해진다(일반 원리, 미측정).

## 6. 운용
- 설치: Jetson `~/slam_ws` 오버레이(slam_toolbox 2.6.10 = apt 판과 같은 태그 + 위 패치), Release 빌드.
- 선택: `ros2 launch rover_bringup slam.launch.py slam_build:=fork|apt` (기본 **fork**). 되돌리기 = `slam_build:=apt`.
- 확인 방법: 제자리 회전 뒤 map→odom 이 움직이면 포크가 작동하는 것(원본은 0).
