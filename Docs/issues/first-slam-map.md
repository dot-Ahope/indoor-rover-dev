# 첫 SLAM 지도 — 스모크 → 360° 제자리 회전 지도 → 조이스틱 병진 지도

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **해결**(첫 지도 2 장 확보) · 단 '복귀 자세 0.2 cm' 근거는 약함(§5) · 이후 F1 매핑으로 이어짐 | 08-27 ~ 09-01 (이 카드는 09-03 까지만) | [08-27 '결과 (수치)' 통합 launch + SLAM 스모크](../debug_log/2026-08-27/SUMMARY.md) | `ros2_ws/src/rover_bringup/config/slam.yaml`(minimum_travel_heading 0.08 → 0.03, minimum_time_interval 0.3 → 0.1 — 08-28) · `launch/slam.launch.py` · 지도 `ros2_ws/maps/rover_map.*`(08-28) · `rover_map_drive.*`(08-31) | [Jetson Wi-Fi 간헐 무응답](jetson-wifi-link.md)(회전을 detach 로 돌린 이유) · [조이스틱 teleop](joystick-teleop.md)(병진 지도의 조종 수단) · [배터리 · 전원 운용](battery-power-ops.md)(세션마다 끊긴 이유) · 스캔 끌림(scan_restamp · deskew, 카드 예정) · 휠 오도 스케일 27.8 %(카드 예정) |

**한 줄**: 08-27 에 slam_toolbox 가 뜨는지만 본 스모크(지도 171×85) → 08-28 에 라이다 yaw(π) 확정 뒤 제자리 360° 회전으로 첫 지도(215×225, 벽 492 칸)를 저장하고 → 08-31 에 조이스틱으로 끌고 다니며 병진 지도(318×220, 벽 3190 칸, 자유 공간 ≈ 58.8 m²)를 저장했다. 중간에 Wi-Fi 끊김 때문에 회전 스크립트를 'Jetson 에서 독립 실행(detach)' 하는 방식이 생겼고, 회전 지도에서 본 '스캔 끌림' 때문에 slam 파라미터를 바꿨다. 병진 지도의 벽은 2~3 칸으로 번져 있었고(벽 칸 28 % 가 이웃 7 칸 이상), 그 원인은 뒤에 **휠 오도메트리 스케일 27.8 % 과대**로 드러났다(09-01, 별도 카드 예정).

> 읽는 법: 08 월 기록은 § 번호가 없다. 인용은 '날짜 + 제목 글자' 로 한다(예: [08-28 '★ SLAM 첫 맵 완성'](../debug_log/2026-08-28/SUMMARY.md)). 측정은 출력 파일 원문이 있는 값, **추정** 은 그렇게 표시, '미확인' 은 기록이 없는 것. **(10-29 재계산)** 은 이 카드를 쓰며 저장된 지도 파일로 다시 계산한 값.

## 1. 증상 · 목표
- 이 줄기는 '문제' 라기보다 '첫 지도를 얻기까지' 이다. 막힌 곳은 셋:
  1. 회전 중 PC↔Jetson 연결이 끊겨 회전 스크립트가 중간에 죽음 → detach 실행으로 해결([08-28 '★ SLAM 첫 맵 완성'](../debug_log/2026-08-28/SUMMARY.md) "detach 실행 → WiFi 무관").
  2. 회전 중 라이다 점이 회전 방향으로 끌려가다 특징점에 '스냅'(사용자 관찰) → scan_restamp + slam 파라미터 변경([08-28 '스캔 포인트 끌림 진단·수정'](../debug_log/2026-08-28/SUMMARY.md)).
  3. 병진 지도 벽이 두꺼움 → '오도메트리 드리프트 + slam 보정' 으로 진단(사용자 정정), 원인 우선순위 ① 직진 스케일([08-31 '루프클로저/드리프트 재확인'](../debug_log/2026-08-31/SUMMARY.md)).

## 2. 흐름 (시간순)
| 날짜 · 제목 | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 08-27 '결과 (수치)' 통합 launch + SLAM 스모크 | sensors.launch 로 전환 뒤 slam.launch 15 s 기동 | scan 9.99 · imu 199.6 · depth 30.0 · filtered 30.0 · wheel_odom 50.0 Hz. `/map` 0.5 Hz, 171×85 @ 5 cm, map→odom (0,0,0), map→lidar_link z 0.286. 경고 1 줄 'minimum laser range 0.0 > 0.2' | slam 동작 확인, 경고 무해 | [`job4x.sh`](../debug_log/2026-08-27/jobs/job4x.sh) · [`outputs/job4x_sensors_slam.txt`](../debug_log/2026-08-27/outputs/job4x_sensors_slam.txt) |
| 08-28 'LiDAR yaw 최종 확정' | 라이다 yaw 판정(종이 흔들기 → 코너 → 두 벽) | yaw = π, 혼선 원인은 Foxglove fixed frame = map(사용자 발견) | 지도 만들 준비 완료 | `outputs/job6*` · `lidar_yaw_CONFIRMED.txt` (라이다 yaw 카드 예정) |
| 08-28 (시각 미기록, 오전) | slam 기동 확인 | `/map` 아직 미발행, `/wheel_odom` **없음**, 지도 87×119 | 보드 세션 끊김 → 보드 리셋 | [`job7a.sh`](../debug_log/2026-08-28/jobs/job7a.sh) · [`job7a_slam_ready.txt`](../debug_log/2026-08-28/outputs/job7a_slam_ready.txt) · [`job7b_board_session.txt`](../debug_log/2026-08-28/outputs/job7b_board_session.txt) → [`job7b_after_reset.txt`](../debug_log/2026-08-28/outputs/job7b_after_reset.txt)(wheel_odom 48.6 Hz, 배터리 11.96 V) |
| 08-28 (출력 없음) | 회전 v1 `job7c`(원거리 가드) → v2 `job7d`(풋프린트 가드, 0.18 rad/s) → slam 재시작 `job7d1` → 리셋 뒤 여유 측정 `job7e`(94.2 cm) → v3 `job7f`(0.28 rad/s) | 7c · 7d · 7f 의 실행 결과 원문 없음. `job7d1`: wheel_odom 49.7 Hz · 11.90 V | — | [`job7d1_session_slam.txt`](../debug_log/2026-08-28/outputs/job7d1_session_slam.txt) · [`job7e_reset_clearance.txt`](../debug_log/2026-08-28/outputs/job7e_reset_clearance.txt) |
| 08-28 11:23 | 연결 끊김 뒤 '재부팅인가 Wi-Fi 인가' 판별 | uptime 2:32(부팅 08:51:45) → **재부팅 아님**, ROS 노드 · agent 생존, 신호 −44 dBm | Wi-Fi(또는 경로) 단절로 판단 | [`job7g.sh`](../debug_log/2026-08-28/jobs/job7g.sh) · [`job7g_reboot_check.txt`](../debug_log/2026-08-28/outputs/job7g_reboot_check.txt) |
| 08-28 (11:23~11:28) | 잔존 회전 프로세스 정리 + 정지 지령 | 잔존 없음, ω −0.0005 rad/s, `/cmd_vel` 무발행, 지도 215×195 | 안전 정지 확인 | [`job7h.sh`](../debug_log/2026-08-28/jobs/job7h.sh) · [`job7h_safety_cleanup.txt`](../debug_log/2026-08-28/outputs/job7h_safety_cleanup.txt) |
| 08-28 11:28 | detach v1(`job7i_launch` → job7f) 결과 확인 | `spin.log` **비어 있음**, ω 0.0009, 지도 215×195 그대로 | 회전이 안 돌았거나 기록이 안 남음 — 원인 **미확인**(§8 job7i 결함) | [`job7j.sh`](../debug_log/2026-08-28/jobs/job7j.sh) · [`job7j_spin_log.txt`](../debug_log/2026-08-28/outputs/job7j_spin_log.txt) |
| 08-28 (11:28~11:42) | 리셋 뒤 slam 재시작 + 시작 여유 | 여유 88.9 cm, 배터리 **11.71 V** | 회전 가능 | [`job7e2_reset_slam.txt`](../debug_log/2026-08-28/outputs/job7e2_reset_slam.txt)(스크립트는 `job7e.sh` 재실행) |
| 08-28 11:42:20~11:43:19 | detach v2(`job7k_launch` → `job7k`) 360° 회전 | `SPIN_END reason=DONE_360 acc=+353deg minclr=16.4cm`, 가드(3 cm) 미발동, 59 s | 360° 완주 | [`job7k.sh`](../debug_log/2026-08-28/jobs/job7k.sh) · [`job7j2_spin_result.txt`](../debug_log/2026-08-28/outputs/job7j2_spin_result.txt) · [`job7j3_spin_final.txt`](../debug_log/2026-08-28/outputs/job7j3_spin_final.txt) |
| 08-28 11:44 | 지도 저장 + 통계 | 215×225 @ 5 cm = 10.8×11.3 m, 벽 492 · 자유 11895 · 미탐사 35988 칸, 'pose x=+0.2cm y=+0.1cm yaw=+1deg' | "360° 후 복귀 자세 0.2 cm/1° → yaw(π)·EKF·자이로·슬립보정 전 체인 정합 최종 증명" — **과한 결론**(§5 실수 1) | [`job7l.sh`](../debug_log/2026-08-28/jobs/job7l.sh) · [`job7l_map_analysis.txt`](../debug_log/2026-08-28/outputs/job7l_map_analysis.txt) · [`ros2_ws/maps/rover_map.yaml`](../../ros2_ws/maps/rover_map.yaml) · `rover_map.png` |
| 08-28 '스캔 포인트 끌림 진단·수정' | 회전 중 점 끌림 → 정적 타이밍 측정 | /scan now−stamp +112 ms, scan_time 95 ms, scan−odom −160 ms → 0.28 rad/s 에서 ≈ 1.8° | scan_restamp(스윕 중앙) + **slam minimum_travel_heading 0.08 → 0.03 · minimum_time_interval 0.3 → 0.1** | [`job8a.sh`](../debug_log/2026-08-28/jobs/job8a.sh) · [`job8a_scan_timing.txt`](../debug_log/2026-08-28/outputs/job8a_scan_timing.txt) · [`job8b.sh`](../debug_log/2026-08-28/jobs/job8b.sh) · [`job8b_restamp.txt`](../debug_log/2026-08-28/outputs/job8b_restamp.txt) |
| 08-31 '결과 (수치)' · '판단·결정' | 충전 뒤 재기동, 끌림 수정 회전 검증, deskew 추가 | 회전 0.22 rad/s 에서 /scan_raw 1.27° → restamp 0.68° → deskew 0.12° | deskew 활성, restamp 는 폴백 | `outputs/job8d~8k` (스캔 끌림 카드 예정) |
| 08-31 16:46~16:56 | 병진 지도 준비: 보드 리셋 전후 확인 → slam 재시작 → EKF 재시작으로 odom 원점 0 | 리셋 뒤 odom (−1.715, −1.736) **0 아님** → EKF 재시작 뒤 (0, 0), map→odom 0 | 보드 리셋은 EKF odom 을 안 지움 → EKF 를 따로 재시작 | [`job10a`](../debug_log/2026-08-31/jobs/job10a.sh) · [`job10b`](../debug_log/2026-08-31/jobs/job10b.sh) · [`job10c`](../debug_log/2026-08-31/jobs/job10c.sh) · `outputs/job10a_prereset.txt` · [`job10b_reset_slam.txt`](../debug_log/2026-08-31/outputs/job10b_reset_slam.txt) · [`job10c_clean_odom.txt`](../debug_log/2026-08-31/outputs/job10c_clean_odom.txt) |
| 08-31 ≈ 17:08~17:22 | 조이스틱 주행 매핑(조종 절차는 [조이스틱 카드](joystick-teleop.md)) | 주행 끝 odom (4.489, −0.713) | — | [`job11_map_save.txt`](../debug_log/2026-08-31/outputs/job11_map_save.txt) |
| 08-31 17:22 | 지도 저장 + 통계 | 318×220 @ 5 cm = 15.9×11.0 m, 벽 3190 · 자유 23514 칸, 자유 공간 ≈ 58.8 m² | "deskew 로 이동 중 스캔 선명" | [`job11.sh`](../debug_log/2026-08-31/jobs/job11.sh) · [`ros2_ws/maps/rover_map_drive.yaml`](../../ros2_ws/maps/rover_map_drive.yaml) · `rover_map_drive.png` |
| 08-31 '루프클로저/드리프트 재확인' | 사용자: 남은 '따라감→스냅' 은 스캔 지연이 아니라 오도 드리프트 + slam 보정 | 저장 지도 오프라인 분석: 벽 국소 밀도 평균 5.6/9(중앙 6), 번짐 28 % | 중간 정도 드리프트. 원인 순위 ① 직진 스케일 ② 좌우 트랙 비대칭 ③ 자이로 스케일 | 분석 도구 · 출력 원문 없음(대화에만). **(10-29 재계산)** 같은 정의로 재현됨 — §8 '벽 번짐 분석' |
| 08-31 (밤) | 라이브 드리프트 진단 시도(`job13`) | `NO_MAP`, 파라미터 전부 빈 값 | 배터리 완전 방전으로 Jetson 다운 → 스택 없음 | [`job13_drift_diag.txt`](../debug_log/2026-08-31/outputs/job13_drift_diag.txt)(스크립트 원천 소실) |
| 09-01 '★★ 중대 정정' | 줄자 재측정 | 휠 원시 / 줄자 = 1.277 · 1.278 | 휠 오도 27.8 % 과대 → VX_SCALE 0.783(09-02 검증 +0.47 %) — 08-31 병진 지도의 벽 번짐 1 순위 원인이 이것(**추정**, 같은 경로 재매핑으로 확인한 기록 없음) | 휠 오도 스케일 카드(예정) |

이후(09-04 ~): 다음 시기에서 채움 — F1 매핑(09-30 ~ 10-02, `office_v2` · `office_v3`, 루프 오정합으로 `loop_search_space_dimension` 8 → 3, [09-30 §14](../debug_log/2026-09-30/SUMMARY.md)), 회전 중 스캔 처리 포크([`Docs/04_navigation/SLAM_FORK_ROTATION.md`](../04_navigation/SLAM_FORK_ROTATION.md)), 위치 추정 모드의 stamp 정체([SLAM map→odom 시각 정체](slam-stamp-freeze.md)).

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 회전 스크립트가 죽은 건 Jetson 재부팅 때문 | `job7g`: uptime · 부팅 이력 · 노드 생존 | uptime 2:32, 마지막 부팅 08:51:45, 노드 · agent 생존 | **기각** — PC↔Jetson 연결 단절 쪽(Wi-Fi 카드) |
| 360° 회전 뒤 자세가 처음으로 돌아왔다 → 전 체인 정합 | `job7l` 의 '360도 후 pose' | `/odometry/filtered`(odom 좌표) x +0.2 cm · yaw +1°. 회전 시작 자세는 기록 안 됨, 누적 회전은 +353° | **미확인**(근거 부족) — §5 실수 1 |
| 회전 중 점 끌림 = 루프 클로저 | 끌림 양상(밀리다 특징점에 스냅) + 정적 타이밍(`job8a`) | 스캔 스탬프가 스윕 시작 · 처리 지연 112 ms | **기각** — 스캔 시간 지연 + 스캔 매칭 보정(08-28) |
| 병진 지도 벽 번짐 = 스캔 지연 | deskew 로 회전 끌림 0.12° 까지 줄인 뒤에도 번짐 남음 | 벽 국소 밀도 평균 5.6/9, 28 % | **기각**(사용자 정정) — 오도 드리프트 + slam 보정 |
| 벽 번짐의 1 순위 = 직진 스케일 | 09-01 줄자 2 회 + 09-02 1 회 | 과대율 1.2774 · 1.2778 · 1.2806 | **지지**(스케일 오류는 확정). 이 지도 번짐에 대한 기여량은 **미확인**(재매핑 비교 없음) |

## 4. 조치와 효과
- **detach 실행**(`setsid` + `nohup`/`disown` + 로그 파일, `python3 -u` + `flush=True`): 회전이 SSH 세션과 무관하게 완주(08-28 11:42, 59 s). 이후 모든 주행 러너의 기본 형태가 됨(→ 10 월 `run_jn.sh` 계열).
- **풋프린트 가드**(`job7d` 이후): 라이다 점을 차체 직사각형(0.50×0.33 m) 둘레까지의 거리로 바꿔 판정. 원거리 가드(`job7c`)는 차체 모양을 몰라 앞뒤 비대칭을 못 봄.
- **slam 파라미터**(08-28, `config/slam.yaml`): minimum_travel_heading 0.08 → **0.03 rad**, minimum_time_interval 0.3 → **0.1 s**(스캔 매칭을 약 3 배 자주). 효과는 restamp 와 함께 '밀림 ≈ 1.8° → ≈ 0.85°' 로 적혀 있으나(08-28) 이것은 계산 예상치이고, 실측은 08-31 회전 시험(restamp 0.68°)이다. 두 변경의 몫을 나눈 측정은 없음.
- 저장 지도: `rover_map.*`(08-28, 회전) · `rover_map_drive.*`(08-31, 병진). git 첫 반영은 커밋 `76c08343`(09-02). 그때의 `slam.yaml` 은 `git show 76c08343:ros2_ws/src/rover_bringup/config/slam.yaml` — mapping 모드, resolution 0.05, max_laser_range 12.0, transform_timeout 0.2, minimum_travel_distance 0.05, do_loop_closing true, loop_search_space_dimension 8.0(09-30 에 3.0 으로).
- 한계: 회전 지도는 한 지점에서 본 별 모양(`job7l` ASCII 미리보기) — 방 전체가 아님. 병진 지도는 휠 스케일 오류 아래에서 만든 것이라 벽이 번짐. 두 지도 모두 이후 운용에 쓰이지 않았다(F1 의 `office_v2/v3` 로 대체).

## 5. 내 실수
### 실수 1 — '360° 후 복귀 자세 0.2 cm · 1°' 를 전 체인 정합의 증명으로 적음
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 360° 제자리 회전 지도를 저장하고(`job7l.sh`), 회전 뒤 로버 자세가 시작 자세로 돌아왔는지로 라이다 yaw · EKF · 자이로 융합 · 슬립 보정을 한 번에 검증 |
| 본 것 | [`job7l_map_analysis.txt`](../debug_log/2026-08-28/outputs/job7l_map_analysis.txt) `360도 후 pose: x=+0.2cm y=+0.1cm yaw=+1deg`, 같은 회전의 [`job7j3_spin_final.txt`](../debug_log/2026-08-28/outputs/job7j3_spin_final.txt) `acc=+353deg` |
| 처음 추론 | "결정적 성공 지표 … 전 체인 정합 최종 증명"([08-28 '★ SLAM 첫 맵 완성'](../debug_log/2026-08-28/SUMMARY.md)) |
| 의심한 이유(이 카드를 쓰며) | ① `job7l` 이 읽은 것은 `/odometry/filtered` — **EKF 의 odom 좌표**이지 SLAM(map) 자세가 아니다. ② 제자리 회전에서 휠 vx ≈ 0 이라 EKF 위치는 구조상 거의 안 변한다 → 0.2 cm 는 '안 밀렸다' 의 증거가 될 수 없다. 09-03 에 '제자리 회전 반복 시 수 회전에 10 cm+ 밀림'([09-03 '부수 발견 (운영)'](../debug_log/2026-09-03/SUMMARY.md)), 09-01 에 '제자리 회전 시 vx≈0 이라 odom 이 못 봄'([08-31 파일의 09-01 '판단'](../debug_log/2026-08-31/SUMMARY.md)) 이 이미 기록됨. ③ 회전 시작 yaw 를 기록하지 않았고 누적은 +353°(98 % 정지 조건) 인데 끝 yaw 가 +1° — 시작이 0° 였다면 −7° 근처여야 한다. 즉 '시작 = 0' 가정 자체가 확인 안 됨 |
| 판별 시험 | 그때 한 것 없음. 이후 09-28 회전 시험(180° 당 10~27 cm 밀림, SLAM 도 못 봄)이 '제자리 회전은 실제로 밀린다' 를 측정으로 보였다(다음 시기에서 채움) |
| 결론 | 이 수치가 보여 주는 것은 'EKF yaw 가 자이로를 따라 약 353° 를 적분했다' 까지다. 라이다 yaw = π 의 근거는 08-28 '두 벽 배치'(`job6n` · `job6o`) 쪽이고, 복귀 자세 근거로는 **미확인** |
| 다음에 알아보는 법 | 회전 · 왕복 '복귀 오차' 를 말할 때 ① 어느 프레임(odom / map / 줄자)인지 ② 시작 자세를 같은 도구로 기록했는지 ③ 그 센서가 그 오차를 원리상 볼 수 있는지(제자리 회전의 휠 vx) 셋을 먼저 적는다 |

### 실수 2 — 병진 지도 궤적 '(0,0)→(4.49,−0.71)' 을 실제 이동처럼 적음
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 지도 저장 때 주행 궤적 범위를 함께 기록(`job11.sh` 의 '현재 로버 위치') |
| 본 것 | [`job11_map_save.txt`](../debug_log/2026-08-31/outputs/job11_map_save.txt) x 4.489 · y −0.713 — `/odometry/filtered` 값 |
| 처음 추론 | "궤적 (0,0)→(4.49,−0.71)"([08-31 '조이스틱 teleop + 병진 주행 맵핑'](../debug_log/2026-08-31/SUMMARY.md)) |
| 의심한 이유 | 이 시각의 EKF 는 VX_SCALE 보정 전(09-01 ×1.022 → 09-01 밤 0.783) — 휠 원시가 27.8 % 과대였다 |
| 판별 | 하지 않음. 실제 끝점은 SLAM 자세(map→base_link)로 읽었어야 하나 그 값은 남지 않았다 |
| 결론 | 4.49 m 는 '과대 보고된 odom 좌표' 이고 실제 변위는 더 작다(**추정**: 전 구간 비슷한 방향이면 약 1/1.278 배). 실제 값은 **미확인** |
| 다음에 알아보는 법 | 위치를 기록할 때 프레임 이름을 값 옆에 적고, 주행 거리 · 범위는 map 프레임(또는 줄자)으로 |

## 6. 남은 것
- 병진 지도 벽 번짐에 대한 휠 스케일 오류의 몫 — 같은 경로 재매핑 비교가 없어 미확인(지도 자체가 더 쓰이지 않아 우선순위 낮음).
- detach v1(`job7i_launch`)이 왜 아무 기록도 남기지 않았는지 — 미확인(§8 job7i).
- 'minimum laser range 0.0 > 0.2' 경고: slam.yaml 에 `min_laser_range` 를 안 줘서 나는 것(**추정**). 무해로 두었고 고친 기록 없음.

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| 스모크 | slam 첫 기동 | 08-27, `job4x` |
| 회전 지도 | 제자리 360°, 0.28 rad/s 지령 | 08-28 11:42, `job7k` → `rover_map.*` |
| 병진 지도 | 조이스틱 주행 ≈ 14 분(17:08 무렵 ~ 17:22, 출력 파일 시각으로 **추정**) | 08-31, `job11` → `rover_map_drive.*` |
| `job4x` · `job7a~7l` · `job8a` · `job8b` · `job10a~10c` · `job11` · `job12`(소실) · `job13`(소실) | 아래 §8 | `2026-08-27/jobs` · `2026-08-28/jobs` · `2026-08-31/jobs` |

## 8. 도구 해설
공통 사항(이 시기 도구 전부):
- **실행 위치 · 부른 형태**: 전부 Jetson 에서 도는 bash(안에 python3 heredoc). PC 의 Git Bash → WSL(`Ubuntu-22.04`) → `sshpass` + `scp` 로 `/tmp/jobXX.sh` 에 올려 실행하는 러너를 거쳤다([08-26 '한 일' Step 0](../debug_log/2026-08-26/SUMMARY.md) 'WSL + sshpass 패턴'). 이 시기 러너 원본(scratchpad `run_j.sh`)은 **원천 소실** — 후손이 [`2026-10-08/jobs/run_jn.sh`](../debug_log/2026-10-08/jobs/run_jn.sh)(비밀번호 `<PW>`). 모터를 움직이는 스크립트는 사용자가 `!` 접두어로 직접 실행([08-26 '판단·결정' 7](../debug_log/2026-08-26/SUMMARY.md)). 인자는 거의 없다(값이 스크립트 안에 박혀 있음).
- **출력**: 화면 출력만. 사용자가 대화에서 `outputs/` 에 옮겨 적은 것이 남았다. 출력 파일 이름이 스크립트 이름과 다를 수 있다(`job7j2_…` · `job7e2_…` 처럼 같은 스크립트 재실행에 번호를 붙임).
- **'지금 다시 쓸 수 있나'** 판단 기준: 토픽 이름(`/scan` · `/odometry/filtered` · `/map`)은 지금도 같다. 다만 `/tmp/rover_src` 배포, 고정 대기 시간(`sleep`), 하드코딩 상수(라이다 x 0.152 · yaw π · 차체 0.50×0.33)는 지금 URDF(데크 yaw 보정 −2.68°, 09-18)와 다르다.
- **차체 여유 계산(`clearances`, 7d · 7e · 7f · 7k · 8e · 14g · 18a 공통)**: 라이다 점 (거리 r, 각 a) → base_link 좌표 `th = a + π`, `px = 0.152 + r·cos th`, `py = r·sin th`. 차체 직사각형 x ∈ [−0.25, 0.25], y ∈ [−0.165, 0.165] 바깥까지 거리 `dx = max(XMIN−px, 0, px−XMAX)`, `dy` 같은 식, `√(dx²+dy²)`. 점이 차체 안이면 0. r > 0.05 m 이고 유한한 점만 씀.
- **yaw 누적(`acc`, 7c · 7d · 7f · 7k)**: `/odometry/filtered` 쿼터니언 → `yaw = atan2(2(wz+xy), 1−2(y²+z²))`, 이전 값과의 차를 (−π, π] 로 감아 더함. EKF yaw 는 D455f 자이로가 주도(08-27) → 사실상 '자이로가 본 회전량'.

### job4x — 통합 launch 전환 + slam 스모크 (08-27)
- 왜: 센서를 launch 하나(`sensors.launch.py`)로 묶은 뒤 slam_toolbox 가 그 위에서 뜨는지 처음 확인.
- 하는 일: ① `/tmp/rover_src/rover_bringup` 을 `~/ros2_ws/src` 에 복사 · `colcon build --symlink-install --packages-select rover_bringup` ② 개별 launch(`camera` · `lidar` · `ekf` · 노드 이름 8 종) `pkill -f` ③ `setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log` 후 35 s 대기, 로그에서 'bias calibrated|not stationary' · 'error|died|failed' 1~3 줄 ④ 5 토픽 `ros2 topic hz` 6 s ⑤ `slam.launch.py` 를 같은 방식으로 띄우고 15 s 뒤 `/map` hz 8 s · `tf2_echo map odom` · `tf2_echo map lidar_link` · `/map` info(해상도 · 폭 · 높이) · slam 로그 경고 4 줄 ⑥ foxglove 8765 포트 열림과 `ws://<IP>:8765`.
- 출력: [`outputs/job4x_sensors_slam.txt`](../debug_log/2026-08-27/outputs/job4x_sensors_slam.txt) — 위 §2 첫 줄의 수치.
- 쓰인 곳: [08-27 '결과 (수치)' 통합 launch + SLAM 스모크](../debug_log/2026-08-27/SUMMARY.md). 08-27 의 2 Mbps 50 Hz 기준선(CLAUDE.md 통신 항목)도 이 출력이다.
- 계보: SLAM 기동 확인 부분 → `job7a`(08-28). 스택 전체 기동 → `job8d`(08-31) → `job20a_boot`(09-02) → 10 월 `prep_fast.sh`.
- 결함: 고정 sleep(35 · 15 s)라 늦게 뜨면 'does not appear' 로 나옴. map→odom (0,0,0) 은 '정상' 이 아니라 '아직 보정 없음' 일 뿐.
- 지금 다시: 그대로는 안 씀(`/tmp/rover_src` 배포 방식 폐기, foxglove 상시 기동 안 함).

### job7a — slam 준비 확인 (08-28)
- 왜: 재부팅(08:51) 뒤 slam 이 떠 있는지, 지도 · TF 가 나오는지.
- 하는 일: `pgrep -f slam_toolbox` 로 없으면 `slam.launch.py` detach 기동 후 12 s. 노드 목록, `/map` hz 8 s, `tf2_echo map odom`(Translation · RPY), `map base_link` Translation, `/map` info(+origin), `/tmp/slam.log` 경고 3 줄, `/scan` · `/wheel_odom` · `/odometry/filtered` hz 5 s.
- 출력: [`job7a_slam_ready.txt`](../debug_log/2026-08-28/outputs/job7a_slam_ready.txt) — `/map` 미발행, 87×119, **`/wheel_odom` does not appear**, `/odometry/filtered` 30.03 Hz.
- 쓰인 곳: 보드 세션이 없다는 첫 단서 → `job7b`.
- 결함: 지도가 '아직 미발행' 이어도 info 를 읽으면 그 직전 지도 크기가 나온다(87×119). `/odometry/filtered` 30 Hz 는 휠 입력이 없어도 EKF 가 예측만으로 내보내므로 '오도 정상' 의 증거가 아님.
- 지금 다시: 지금은 `chk_prep.py` 가 같은 역할.

### job7b — 보드(micro-ROS) 세션 진단 (08-28)
- 왜: `/wheel_odom` 이 없을 때 agent 문제인지 보드 세션 문제인지.
- 하는 일: `docker ps` 에서 microros 컨테이너 상태, `docker logs --tail 3`, `ros2 topic list` 에서 wheel_odom · battery · heartbeat · rover, `/wheel_odom` hz 10 s, `/battery` voltage 1 회, `/rover/f5b_heartbeat` 1 회, `/imu/data_raw` hz 5 s.
- 출력: 리셋 전 [`job7b_board_session.txt`](../debug_log/2026-08-28/outputs/job7b_board_session.txt)(agent 'Up About an hour', 보드 토픽 전무) → 리셋 뒤 [`job7b_after_reset.txt`](../debug_log/2026-08-28/outputs/job7b_after_reset.txt)(wheel_odom 48.6 Hz, battery 11.96 V, heartbeat 105, imu 50.0 Hz).
- 쓰인 곳: '재부팅 뒤엔 보드 리셋 필요'(08-26 판단 2 '펌웨어는 부팅 시 1 회만 세션 수립')의 재확인. SUMMARY 에 별도 문장 없음.
- 계보: → `chk_board.sh`(09-03) → 10 월 `chk_prep.py` 의 보드 항목.
- 결함: `/wheel_odom/conditioned` 는 Jetson 쪽 컨디셔너가 내는 토픽이라 보드가 없어도 목록에 남는다(출력의 첫 줄) — 토픽 '존재' 로 세션을 판정하면 안 됨.
- 지금 다시: 개념은 유효(agent + 토픽 주기). 이름 `f5b_heartbeat` 는 당시 펌웨어 것.

### job7c — 360° 회전 v1, 원거리 가드 (08-28)
- 왜: 제자리 360° 로 첫 지도를 그리되 벽에 닿으면 멈추게.
- 하는 일: `/scan` 에서 r > 0.05 인 점의 **최소 거리**(`minr`, 라이다 중심 기준), `/odometry/filtered` 로 yaw 누적. 시작 `minr < 0.28 m` 면 거부. `angular.z = 0.22 rad/s` 를 루프마다 발행(`spin_once` 0.05 s → 약 20 Hz). 멈춤 조건: `minr < 0.22`(가드) · `|acc| ≥ 360°×0.98` · 45 s. 멈출 때 빈 Twist 10 회 × 20 ms. 끝에 `/map` hz · 폭 · 높이.
- 출력: 원문 없음(대화에만).
- 계보: v1(이것) → v2 `job7d`(차체 모양 가드) → v3 `job7f`(빠르게) → detach 코어 `job7k`.
- 결함: 라이다는 차체 앞쪽(x 0.152)에 있어 같은 0.22 m 라도 앞과 뒤의 실제 여유가 다르다(뒤 끝까지 0.40 m). 회전 중 모서리가 그리는 원(반경 ≈ 0.30 m)을 고려 안 함 → v2 로 교체.
- 지금 다시: 쓰지 않음.

### job7d — 360° 회전 v2, 풋프린트 가드 (08-28)
- 왜: v1 의 거리 가드가 차체 모양을 몰라서.
- 하는 일: 위 공통 `clearances` 로 '차체 외곽 ↔ 벽' 최소 실거리 `clr`. 시작 `clr < 0.03` 이면 거부. 0.18 rad/s, 멈춤: `clr < 0.03` · 360°×0.98 · 55 s. 정지 Twist 12 회. 출력 줄 '정지. 사유: … 누적회전 … 최소 로버-벽거리'.
- 출력: 원문 없음.
- 쓰인 곳: 이 방식(차체 직사각형 거리)이 이후 모든 '사방 여유' 도구의 원형 — `job7e` · `job8e` · `job14g_health` · `job18a_precheck` → 9 월 게이트(`job248_audit` 등, 다음 시기).
- 결함: 가드 3 cm 는 '이미 닿기 직전' 수준 — 회전은 관성 · 슬립으로 더 돈다. 라이다 높이(바닥 + 18.5 cm) 아래 물체는 못 봄.
- 지금 다시: 쓰지 않음(라이다 yaw 상수가 지금 URDF 와 다름).

### job7d1 — 세션 확인 + slam 재시작(지도 초기화) (08-28)
- 하는 일: `/wheel_odom` hz 6 s, `/battery` 1 회, `pkill -f slam_toolbox` → 2 s → slam.launch detach → 12 s → slam 노드 존재, map→odom Translation, `/scan` hz 5 s, `READY`.
- 출력: [`job7d1_session_slam.txt`](../debug_log/2026-08-28/outputs/job7d1_session_slam.txt) — 49.68 Hz · 11.90 V · map→odom 0 · scan 10.01 Hz.
- 왜 지도를 지웠나: 앞 회전 시도로 지도에 흔적이 남아 '깨끗한 360° 한 번' 으로 다시 그리려고(스크립트 주석 '깨끗한 맵').
- 지금 다시: 지금은 slam 재기동이 prep 안에 들어 있음.

### job7e — 리셋 후 세션 + slam 재시작 + 시작 여유 (08-28, 두 번 실행)
- 하는 일: `job7d1` 과 같은 세션 확인(+ `/imu/data_raw` hz) · slam 재시작, 그다음 `/scan` 한 장으로 `clearances` 최소값과 그 점의 raw 각 · 거리. '360도 안전 기준: 시작 여유 ≥ 30 cm 권장' 을 고정 문구로 출력(판정은 하지 않음).
- 출력: 1 회차 [`job7e_reset_clearance.txt`](../debug_log/2026-08-28/outputs/job7e_reset_clearance.txt)(94.2 cm, θ +10°, 1.36 m, 11.84 V) · 2 회차 [`job7e2_reset_slam.txt`](../debug_log/2026-08-28/outputs/job7e2_reset_slam.txt)(88.9 cm, θ +3°, 1.29 m, **11.71 V**).
- 쓰인 곳: 회전 시작 여유 확인 · 배터리 11.71 V 는 [08-28 '★ SLAM 첫 맵 완성'](../debug_log/2026-08-28/SUMMARY.md) '배터리 11.71V — 충전 필요' 의 출처.
- 결함: '30 cm 권장' 근거('모서리 반경 0.30 m, 라이다 스윙 0.15 m')는 주석의 어림 — 측정 아님. 시작 한 장의 최소 여유는 회전 중 최소(16.4 cm, `job7k`)와 다르다.
- 계보: 사방 여유만 떼어 → `job8e`(08-31) → `job14g_health`(4 방향) → `job18a_precheck`(직진 판정).

### job7f — 360° 회전 v3 (08-28)
- 차이(v2 대비): 0.18 → **0.28 rad/s**, 제한 55 → 70 s. 나머지 같음.
- 실행: 처음엔 SSH 전경 실행 → 도중 연결 끊김(**추정**: `job7g` 의 질문과 `job7h` 의 '잔존 회전 프로세스 정리' 로 미루어. 끊긴 시각 · 그때 회전량 원문 없음). 두 번째는 `job7i_launch` 로 detach.
- 출력: 원문 없음.
- 결함: python 출력이 파일로 갈 때 버퍼링됨(`-u` 없음) → detach 로 돌리면 끝날 때까지 로그가 비어 보임(`job7j` 에서 그대로 겪음). SSH 세션에 묶여 있어 연결이 끊기면 SIGHUP 으로 같이 죽는다(그때 마지막 `/cmd_vel` 뒤 500 ms 펌웨어 watchdog 이 모터를 세운다 — 설계상 동작, 08-28 에 확인한 기록은 없음).

### job7g — 재부팅인가 Wi-Fi 단절인가 (08-28 11:23)
- 하는 일: `uptime`/`uptime -s`/`date`, `sudo dmesg | tail -6`(비밀번호 `<PW>` 로 가림), `last -x` 재부팅 3 줄, ROS 노드 프로세스 수(`pgrep -af` 6 종)와 `ros2 node list`, agent 컨테이너 Up 시간, `/wheel_odom` hz, `/battery`, `lsmod | grep -c hid_sensor`(재부팅 시 HID 모듈 자동 로드 확인 겸), `iwconfig wlP1p1s0` 신호.
- 출력: [`job7g_reboot_check.txt`](../debug_log/2026-08-28/outputs/job7g_reboot_check.txt) — up 2:32 · 부팅 08:51:45 · 프로세스 6 · agent 'Up 2 hours' · 49.99 Hz · 11.80 V · HID 6 · Link Quality 66/70, −44 dBm. dmesg 마지막 6 줄은 카메라 UVC GET_CUR 오류(이 질문과 무관).
- 판정 논리: 재부팅이면 uptime 이 짧고 노드 · agent 가 사라졌어야 함 → 둘 다 아님 → 연결 단절. 신호가 좋다는 것은 '끊긴 순간' 이 아니라 '지금' 값이라 원인 판정에는 못 씀.
- 계보: 재부팅 · 네트워크 판별 → 9 월 `chk_jetson_state.sh`(10-13, 재부팅 여부 · IP · 스택).
- 지금 다시: 개념 유효. `last -x` 는 'still running' 이 여러 줄 나와 읽기 어렵다(출력 참조).

### job7h — 잔존 회전 정리 + 정지 확인 (08-28)
- 하는 일: `pgrep -af "map_spin|job7f|job7d|topic pub.*cmd_vel"` → 같은 패턴 `pkill -f` → `ros2 topic pub -t 8 -r 10 -w 1 /cmd_vel Twist '{}'`(빈 지령 8 회) → `/odometry/filtered` 의 angular.z · linear.x 1 회 → `/cmd_vel` 을 4 s 동안 1 회라도 받으면 '!! 계속 발행중' → `/map` 폭 · 높이.
- 출력: [`job7h_safety_cleanup.txt`](../debug_log/2026-08-28/outputs/job7h_safety_cleanup.txt) — 잔존 없음 · ω −0.00045 · 무발행 · 215×195.
- 결함: 자기가 방금 낸 정지 지령 뒤 1 s 만에 `/cmd_vel` 을 듣기 때문에, `-t 8 -r 10`(0.8 s) 이 끝나기 전이면 자기 지령을 '계속 발행' 으로 오판할 수 있다(이번엔 안 걸림). 노드 이름 `map_spin` 은 회전 스크립트들이 공유.
- 계보: → `job9stop` · `job10stop`(조이스틱 정지) → `job15c_shutdown` · `job31_shutdown`(전체 종료).

### job7i_launch — detach v1 (08-28)
- 하는 일: `pkill -f map_spin|job7f` → `rm -f /tmp/spin.log` → `setsid nohup bash /tmp/job7f.sh > /tmp/spin.log 2>&1 &` → 5 s 뒤 로그 3 줄.
- 출력: 실행 직후 출력 원문 없음. 결과는 `job7j`(11:28): 로그 비어 있음 · ω 0.0009 · 지도 그대로.
- 알려진 결함: ① job7f 안의 python 이 `-u` 없이 파일로 출력 → 끝날 때까지 로그가 비어 보임 ② stdin 을 끊지 않음(`</dev/null` 없음) · `disown` 없음. 다만 지도 크기도 그대로였으므로 '버퍼링으로 안 보였을 뿐' 이 아니라 '회전이 실제로 안 돌았음' 쪽이다(**추정**). 왜 안 돌았는지는 **미확인**(판별 안 함).
- 계보: v1(이것) → v2 `job7k_launch` + `job7k`.

### job7j — detach 결과 확인 (08-28, 세 번 실행)
- 하는 일: `/tmp/spin.log` 전체, `pgrep -af map_spin`, 현재 ω, `/map` 폭 · 높이 · 해상도, `uptime`, `/wheel_odom` hz.
- 출력: 11:28 [`job7j_spin_log.txt`](../debug_log/2026-08-28/outputs/job7j_spin_log.txt)(로그 없음) · 11:42:57 [`job7j2_spin_result.txt`](../debug_log/2026-08-28/outputs/job7j2_spin_result.txt)(+182° 진행 중) · 11:43:42 [`job7j3_spin_final.txt`](../debug_log/2026-08-28/outputs/job7j3_spin_final.txt)(DONE_360).
- 의의: '네트워크와 무관하게 돌고, 나중에 로그로 확인' 하는 패턴의 첫 확인 도구.

### job7k — detach 회전 코어 (08-28) ★ 첫 지도를 만든 실행
- 하는 일: 맨 앞 `exec >>/tmp/spin.log 2>&1`(스크립트 전체 출력을 로그로), `SPIN_START 시각`, `python3 -u`, 모든 print 에 `flush=True`. 회전 로직은 v3(`job7f`)와 같음: 0.28 rad/s, 풋프린트 가드 3 cm, 360°×0.98, 제한 75 s. **2 s 마다** `...누적deg minclr=..cm` 진행 줄. 끝 `SPIN_END reason=… acc=… minclr=…` · `SPIN_EXIT 시각`.
- 출력: 로그 원문이 `job7j2` · `job7j3` 에 그대로 실림 — START clr 88.7 cm, +94° 까지 75.6 cm, +111° 에서 21.9 cm, +297° 에서 16.4 cm, `DONE_360 acc=+353deg`. 11:42:20 → 11:43:19.
- 이 출력으로 계산할 수 있는 것 **(10-29 계산)**: 353° 를 약 56 s(전후 기동 · 정지 몇 초 제외, **추정**)에 돌았으니 실제 회전 ≈ 6.3 °/s ≈ 0.11 rad/s — 지령 0.28 의 약 0.39 배. 진행 줄 간격(2 s 에 11~15°)과도 맞다. 08-26 의 '회전 시 실제 15°/휠 36°'(08-26 '결과') · 회전 슬립과 같은 방향의 관찰이다. 당시 SUMMARY 에는 이 비교가 없다.
- 쓰인 곳: [08-28 '★ SLAM 첫 맵 완성'](../debug_log/2026-08-28/SUMMARY.md) '59s, 최소 여유 16.4cm 가드 미발동'.
- 결함: 시작 yaw 를 출력하지 않음 → §5 실수 1 의 판별을 못 하게 만든 원인. 2 s 진행 줄의 minclr 는 '지금까지 최소' 라 언제 가장 가까웠는지 시각은 모름.
- 계보: 이 detach 형태(`exec >> log` · `-u` · flush · `setsid … </dev/null` · `disown`) → 08-31 이후 러너 → 9 월 `run_detached`/`run_jn.sh`(다음 시기).

### job7k_launch — detach v2 실행기 (08-28)
- 하는 일: `pkill -f map_spin` → `rm -f /tmp/spin.log` → `setsid bash /tmp/job7k.sh </dev/null >/dev/null 2>&1 &` → `disown` → 6 s 뒤 `pgrep -f map_spin | wc -l` 과 로그 5 줄 → '40초 뒤 로그 재확인' 안내.
- v1 과의 차이: stdin 끊기(`</dev/null`), 출력은 코어가 스스로 로그로(`exec`), `disown`, 6 s 뒤 프로세스 수까지 확인.
- 출력: 실행 직후 출력 원문 없음(결과는 `job7j2` · `job7j3`).

### job7l — 지도 저장 + 통계 + PNG + 회전 뒤 자세 (08-28)
- 하는 일: ① `ros2 run nav2_map_server map_saver_cli -f ~/ros2_ws/maps/rover_map --ros-args -p save_map_timeout:=10.0` ② python: `/map` 을 TRANSIENT_LOCAL(depth 1)로 1 장, `/odometry/filtered` 1 장. 값 ≥ 65 = 벽, 0~24 = 자유, < 0 = 미탐사 칸 수. ③ 'pose x · y · yaw' (odom 프레임) ④ 다운샘플(긴 변 / 60) ASCII 미리보기 `#` 벽 · `.` 자유 ⑤ matplotlib 로 `/tmp/rover_map.png`(미탐사 회색 127 · 벽 0 · 자유 255).
- 출력: [`job7l_map_analysis.txt`](../debug_log/2026-08-28/outputs/job7l_map_analysis.txt) · 지도 [`ros2_ws/maps/rover_map.yaml`](../../ros2_ws/maps/rover_map.yaml)(origin −5.9, −5.75, trinary, occupied 0.65 · free 0.25) · `rover_map.pgm` · `rover_map.png`(PC 로 복사본).
- 결함: §5 실수 1 — 'pose' 가 odom 프레임. '1.0 % 벽' 은 지도 전체(미탐사 포함) 대비라 의미 작음. 지도 크기 10.8×11.3 m 는 방 크기가 아니라 가장 먼 빔(최대 12 m 설정)까지의 경계.
- 계보: → `job11`(같은 골격, 병진 지도) → 09-30 F1 의 지도 저장 스크립트(다음 시기).
- 지금 다시: `map_saver_cli` 부분은 유효. pose 는 map→base_link 로 바꿔야 함.

### job8a — 스캔 · 오도 타이밍 정적 분석 (08-28) — slam 파라미터 변경의 근거
- 왜: 회전 중 '점 끌림'(사용자 관찰)의 원인을 주행 없이 특정.
- 하는 일: 6 s 동안 `/scan` · `/odometry/filtered` 수신마다 `now − header.stamp`(ms) 평균 · 최대 · 최소. 마지막 스캔의 `scan_time` · `time_increment` · 점 수. '0.28 rad/s 에서 스윕당 왜곡 = 0.28 × scan_time', '스탬프가 스윕 시작이면 반 스윕 지연'(° 환산) 출력. 마지막 scan stamp − odom stamp. 이어 `ros2 param get /slam_toolbox` 8 개(minimum_travel_heading · distance · minimum_time_interval · transform_timeout · tf_buffer_duration · use_scan_matching · scan_buffer_size · resolution), rplidar 3 개.
- 출력: [`job8a_scan_timing.txt`](../debug_log/2026-08-28/outputs/job8a_scan_timing.txt) — [08-28 '스캔 포인트 끌림'](../debug_log/2026-08-28/SUMMARY.md) 의 +112 ms · 95 ms · −160 ms.
- 쓰인 곳: scan_restamp 노드 작성 + slam `minimum_travel_heading 0.08 → 0.03`, `minimum_time_interval 0.3 → 0.1`.
- 결함: 'now − stamp' 는 수신 지연 + 스탬프 정의를 섞어 잰다(둘을 못 나눔). 정지 상태 측정이라 회전 중 slam 처리 지연은 안 잼.
- 계보: → `job8b` · `job8c` · `job8e` · `job8h~8k`(deskew 측정, 08-31) — 스캔 끌림 카드(예정)에서 자세히.

### job8b — restamp + slam 파라미터 배포 · 재측정 (08-28)
- 하는 일: `/tmp/rover_src/rover_bringup` 복사 · 빌드 → rplidar · scan_restamp · lidar.launch · slam 종료 → lidar.launch(8 s) · slam.launch(10 s) detach 기동 → 노드 · `/scan_raw` · `/scan` hz → 6 s 동안 두 토픽의 now−stamp 평균 → map→odom → `minimum_travel_heading` · `minimum_time_interval` 실제 값.
- 출력: [`job8b_restamp.txt`](../debug_log/2026-08-28/outputs/job8b_restamp.txt) · [`job8b2_restamp.txt`](../debug_log/2026-08-28/outputs/job8b2_restamp.txt)(재실행) — 지연 100.6 → 52.8 ms.
- 의의(이 카드): slam 파라미터가 실제 노드에 0.03 · 0.1 로 들어갔음을 `ros2 param get` 으로 확인한 출처.

### job10a · job10b · job10c — 병진 지도 직전 '깨끗한 출발' (08-31 16:46~16:56)
- 왜: 오후 내내 조이스틱 시험으로 odom 이 원점에서 멀어졌고 지도에도 흔적이 있어, 지도용 주행 전에 보드 · EKF · slam 을 원점으로.
- `job10a`(리셋 전): agent 컨테이너 Up 시간, `/wheel_odom` hz, 주요 노드 7 종, teleop/joy `pkill -9`. 출력 `job10a_prereset.txt`(agent Up 7 hours, 50.03 Hz).
- `job10b`(보드 RESET 뒤): `/wheel_odom` hz 8 s · `/battery` · `/imu/data_raw` hz, **odom 위치가 0 근처인지**, slam 재시작(12 s) · map→odom, `/scan` · `/scan_raw` · `/odometry/filtered` · `/camera/camera/imu` hz, `scan_deskew` 노드. 출력 [`job10b_reset_slam.txt`](../debug_log/2026-08-31/outputs/job10b_reset_slam.txt) — 12.20 V, **odom (−1.715, −1.736)**, camera imu 150 Hz(평소 200).
- `job10c`: '로버를 15초간 가만히' 안내 → `ekf.launch` · ekf_node · sensor_conditioner · slam 종료 → `ekf.launch.py` detach → 16 s → 'bias calibrated' 줄 → odom 위치 → slam 재시작 → 노드 · `/odometry/filtered` hz. 출력 [`job10c_clean_odom.txt`](../debug_log/2026-08-31/outputs/job10c_clean_odom.txt) — 바이어스 (0.00032, 0.00027, −0.00004), odom (0, 0), map→odom 0, 30.02 Hz.
- 배운 것: **보드 리셋은 EKF 의 odom 을 지우지 않는다**(EKF 는 Jetson 프로세스) — 원점은 EKF 재시작으로만. 자이로 바이어스 보정이 EKF launch 안의 컨디셔너 기동 때 10 s 정지로 이뤄진다.
- 결함: `job10b` 의 '0 근처여야' 는 기대가 틀린 검사(보드 리셋 뒤에 0 이 될 이유가 없음). camera imu 150 Hz 는 기록만 되고 따지지 않음.
- 계보: → 09-02 `job21a_reset` · 09-03 `job33a_reset_noagent`(손으로 옮긴 뒤 EKF · slam 재시작) → 10 월 prep.

### job11 — teleop 정지 + 병진 지도 저장 (08-31 17:22)
- 하는 일: ① teleop · joy_linux `pkill -9`, 빈 `/cmd_vel` 5 회 ② `/odometry/filtered` x · y ③ `map_saver_cli -f ~/ros2_ws/maps/rover_map_drive` ④ `/map` 1 장으로 크기 · 벽 · 자유 칸, **자유 칸 × 0.05² = 탐사 면적** ⑤ `/tmp/rover_map_drive.png`.
- 출력: [`job11_map_save.txt`](../debug_log/2026-08-31/outputs/job11_map_save.txt) · [`rover_map_drive.yaml`](../../ros2_ws/maps/rover_map_drive.yaml)(origin −5.16, −6.11).
- 결함: §5 실수 2(위치가 보정 전 odom). '탐사 면적' 은 자유 칸 면적이라 레이저가 지나간 바닥(문 너머 포함)까지 센다.
- 계보: `job7l` 의 병진판. 이후 F1 지도 저장 스크립트(다음 시기).

### job12 — teleop 속도 상향 배포 확인 (08-31 마무리) — 스크립트 원천 소실
- 출력만 남음: [`job12_speed_change.txt`](../debug_log/2026-08-31/outputs/job12_speed_change.txt) — 빌드 1 줄, 배포된 `scale_linear.x 0.10` · `scale_angular.yaw 0.8` 주석 줄, teleop 정리, 배터리 12.17 V. 자세한 것은 [조이스틱 카드](joystick-teleop.md).

### job13 — 라이브 드리프트 진단 (08-31 밤) — 스크립트 원천 소실
- 출력 제목으로 본 의도: ① map→odom 누적 보정량(= slam 이 고친 드리프트) ② slam 루프 클로저 · 스캔 매칭 파라미터 11 개 ③ '맵 벽 두께 분석(두꺼우면 드리프트로 번진 것)'.
- 출력: [`job13_drift_diag.txt`](../debug_log/2026-08-31/outputs/job13_drift_diag.txt) — 전부 빈 값 · `NO_MAP`. 배터리 방전으로 스택이 내려간 뒤였다([08-31 '루프클로저/드리프트 재확인'](../debug_log/2026-08-31/SUMMARY.md) '⚠ 배터리 완전방전').
- 그래서 벽 두께 분석은 PC 에서 저장 지도로 따로 했다(아래).

### 벽 번짐 분석 (08-31 밤, 오프라인) — 도구 · 출력 원문 없음(대화에만)
- SUMMARY 수치: '벽 국소밀도 평균 5.6/9(중앙 6), 번짐 28 %'.
- **(10-29 재계산)** `ros2_ws/maps/rover_map_drive.pgm` 을 읽어 벽 칸(픽셀 ≤ 50, 즉 0)마다 3×3 이웃(자기 포함) 중 벽 칸 수를 세면 평균 **5.61** · 중앙 **6** · 7 이상 비율 **0.28** — SUMMARY 와 일치. 따라서 당시 정의는 '국소 밀도 = 3×3 안 벽 칸 수(최대 9)', '번짐 = 7 이상인 벽 칸 비율' 이었을 것(**추정**, 원 도구 없음). 같은 계산을 회전 지도 `rover_map.pgm` 에 하면 평균 3.04 · 중앙 3 · 7 이상 0 %(회전 지도는 벽이 얇고 성김).
- 읽는 법: 깨끗한 1 칸 두께 직선 벽은 3×3 안에 3 칸(자기 + 양옆)이다. 평균 5.6 · 중앙 6 은 대략 2 칸 두께. 이 지표는 모서리 · 가구처럼 원래 두꺼운 물체에서도 크게 나오므로 '드리프트 양' 의 근사일 뿐이다. 10 월의 '벽 번짐 읽는 법'(EKF − SLAM 차이, 10-02 §19)과는 다른 지표.
- 재계산 코드(PC, numpy): `occ = (pgm <= 50); n = sliding_window_view(np.pad(occ,1),(3,3)).sum((2,3)); v = n[occ]; v.mean(), np.median(v), (v>=7).mean()`.

## 9. 용어
- **slam_toolbox mapping vs localization**: `mode: mapping` 은 스캔으로 지도를 새로 만들며 자기 위치도 같이 고친다(이 시기 전부). `localization` 은 저장된 지도(pose graph)에 맞춰 위치만 고친다(10 월 순회 운용). 둘 다 `map→odom` 변환을 낸다.
- **map→odom**: SLAM 이 내는 '보정' 변환. EKF 는 `odom→base_link`(휠 + 자이로로 이어 붙인 연속 자세, 시간이 갈수록 어긋남)를 내고, SLAM 이 스캔을 지도에 맞춰 본 차이를 `map→odom` 으로 얹는다. 둘을 곱한 `map→base_link` 가 지도 위 자세. 스냅(점프)은 이 보정이 한 번에 크게 바뀔 때 보인다.
- **odom 프레임 / map 프레임 값**: `/odometry/filtered` 의 pose 는 odom 프레임 — 제자리 회전에서 차체가 옆으로 밀려도 휠이 그 움직임을 안 보면 바뀌지 않는다.
- **detach(setsid · nohup · disown)**: SSH 로 띄운 프로세스는 세션이 끊기면 SIGHUP 을 받아 같이 죽는다. `setsid` 는 새 세션(제어 터미널 없음)으로 띄우고, `nohup` 은 SIGHUP 을 무시하게 하고, `disown` 은 셸의 작업 목록에서 빼 셸 종료 때 신호를 안 보내게 한다. `</dev/null` 은 끊긴 SSH 의 입력에 묶이지 않게, `python3 -u` · `flush=True` 는 파일로 갈 때의 출력 버퍼링을 꺼 로그가 바로 보이게 한다.
- **풋프린트 여유(clearance)**: 라이다 점에서 '라이다까지' 가 아니라 '차체 직사각형 외곽까지' 의 거리. 회전하는 직사각 차체는 모서리가 가장 먼저 닿는다.
- **map_saver_cli · trinary**: `/map` 을 받아 `.pgm`(흰 254 자유 · 검정 0 벽 · 회색 205 미탐사)과 `.yaml`(해상도 · origin · 문턱)로 저장. occupied_thresh 0.65 · free_thresh 0.25.
- **minimum_travel_heading / minimum_time_interval**: slam_toolbox 가 새 스캔을 지도에 넣는(스캔 매칭하는) 조건 — 마지막 처리 이후 이만큼 돌았거나(rad) 이만큼 시간이 지나야(s). 작게 하면 더 자주 고치지만 CPU 를 더 쓴다.
- **스캔 매칭 vs 루프 클로저**: 스캔 매칭은 새 스캔을 '가까운 최근 스캔들' 에 맞추는 것(매번), 루프 클로저는 한참 전에 지나간 곳을 알아보고 그래프 전체를 다시 푸는 것(드묾).
