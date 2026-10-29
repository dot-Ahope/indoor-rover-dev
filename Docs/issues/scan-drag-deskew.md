# 회전 중 스캔 끌림 — 스캔 시각 보정(restamp) → 점별 회전 보정(deskew)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **해결**(스캔 시각 지연 성분) · 남은 '따라감 → 스냅' 은 다른 문제(오도메트리 드리프트 + SLAM 보정)로 넘김 · deskew 의 점별 보정 정확성은 **미검증** | 08-28 ~ 09-01 | [08-28 '스캔 포인트 끌림 진단·수정 (사용자 관찰)'](../debug_log/2026-08-28/SUMMARY.md) | `ros2_ws/src/rover_bringup/scripts/scan_restamp.py`(신규) · `scripts/scan_deskew.py`(신규, 09-01 벡터화) · `launch/lidar.launch.py`(rplidar `/scan` → `/scan_raw` 재매핑, deskew 노드) · `config/slam.yaml`(minimum_travel_heading 0.08 → 0.03, minimum_time_interval 0.3 → 0.1) | [라이다 yaw](lidar-yaw-alignment.md) · [Foxglove 4초 스냅](foxglove-snap-cpu.md) · 회전 미끄러짐 · SLAM 포크(09-28, 카드 예정) |

**한 줄**: 제자리 회전 때 Foxglove 에서 라이다 점이 회전 방향으로 밀렸다가 벽에 '착' 붙는 것을 사용자가 봤다. 정지 상태 측정으로 스캔 시각(stamp)이 실제보다 약 100 ms 과거(스윕 시작 시각)에 찍혀 있음을 찾았고, ① stamp 를 스윕 중앙으로 옮기는 `scan_restamp`(지연 100 → 53 ms) ② 빔마다 취득 시각 차만큼 EKF 각속도로 각도를 되돌리고 stamp 를 스윕 끝으로 두는 `scan_deskew`(지연 101 → 9 ms)를 만들었다. 기록의 '밀림 1.27° → 0.68° → 0.12°' 는 **지연 × 명목 각속도 0.22 rad/s 로 계산한 값**이지 화면의 점 밀림을 잰 것이 아니다. 사용자는 그 뒤에도 남은 '따라감 → 스냅' 이 스캔 지연이 아니라 오도메트리 드리프트와 SLAM 보정이라고 정정했고, 그 판단이 맞았다(이후 09-28 에 회전 미끄러짐 · SLAM 이 회전 중 스캔을 버리는 문제로 이어짐).

## 1. 증상
- 08-28: "회전 시 lidar 포인트가 회전방향으로 밀리다 특징점에 스냅"(사용자 관찰). 첫 해석: 루프 클로저가 아니라 '스캔매칭 보정 + 스캔 시간지연'. [08-28 '스캔 포인트 끌림 진단·수정'](../debug_log/2026-08-28/SUMMARY.md)
- 08-31 저녁(조이스틱 병진 주행 뒤): 남은 '스캔 따라감 → 스냅'. [08-31 '루프클로저/드리프트 재확인 (사용자 관찰)'](../debug_log/2026-08-31/SUMMARY.md)
- 수치로 남은 화면 관찰은 없다(캡처 · 영상 없음). '4 초' 같은 주기가 언급된 것은 별개 문제 → [Foxglove 4초 스냅](foxglove-snap-cpu.md).

## 2. 흐름 (시간순)
| 날짜 · 곳 | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 08-28 '스캔 포인트 끌림' 진단(정적) | `job8a` 정지 상태 타이밍 · slam 파라미터 | `/scan` now − stamp 평균 **+112.0 ms**(최소 95.6 · 최대 354.4, n 60), `/odometry/filtered` +12.3 ms, scan_time **94.9 ms**, time_increment 52.8 µs × 1800 점, '마지막 scan stamp − 마지막 odom stamp' −160.7 ms. slam: heading 0.08 · distance 0.08 · time 0.3 · transform_timeout 0.2 | 지연의 대부분은 '스윕 시작에 stamp' 탓(≈ scan_time) + 전송. 0.28 rad/s 에서 0.28 × 0.112 rad ≈ **1.8°**(계산) | [job8a.sh](../debug_log/2026-08-28/jobs/job8a.sh) · [job8a_scan_timing.txt](../debug_log/2026-08-28/outputs/job8a_scan_timing.txt) |
| 08-28 수정 ① | `scan_restamp` 작성 · lidar.launch 재매핑 · slam 튜닝, `job8b` 배포 1 회차 | 1 회차: 노드 목록에 scan_restamp **없음**, `/scan` +100.7 ms, slam 파라미터 그대로(0.08 · 0.3) | 배포 실패(원인 기록 없음) | [job8b.sh](../debug_log/2026-08-28/jobs/job8b.sh) · [job8b_restamp.txt](../debug_log/2026-08-28/outputs/job8b_restamp.txt) |
| 08-28 | `job8b` 재실행 | `/scan_raw` +100.6 ms → `/scan` **+52.8 ms**(−47.8), heading **0.03** · time **0.1** 반영 | 지연 절반. '밀림 ~1.8° → ~0.85°'(0.28 rad/s × 52.8 ms, **계산**), '보정 3 배 잦게'(**틀림** — §3 마지막 두 줄) | [job8b2_restamp.txt](../debug_log/2026-08-28/outputs/job8b2_restamp.txt) · 요약 [scan_lag_FIX.txt](../debug_log/2026-08-28/outputs/scan_lag_FIX.txt) |
| 08-28 끝(**추정**) | `job8c` 상태 · 배터리 확인 | 거의 빈 출력, `/battery` 미발행 | 보드 세션 없음(방전 직전, 08-28 '★ SLAM 첫 맵' "배터리 11.71 V") — **추정** | [job8c.sh](../debug_log/2026-08-31/jobs/job8c.sh) · 출력 [2026-08-28/outputs/job8c_status.txt](../debug_log/2026-08-28/outputs/job8c_status.txt) |
| 08-31 '한 일' | 재부팅 뒤 `job8d` 전체 재시작, `job8e` 준비 확인 | scan_restamp 생존 · wheel_odom 50.013 Hz / 배터리 12.177 V, `/scan_raw` 100 → `/scan` 52 ms, 시작 여유 70 cm | 수정이 재부팅 뒤에도 유지 | [job8d_restart.txt](../debug_log/2026-08-31/outputs/job8d_restart.txt) · [job8e_prep.txt](../debug_log/2026-08-31/outputs/job8e_prep.txt) |
| 08-31 '결과 (수치)' | `job8f`(+ `_launch` · `job8g`) 0.22 rad/s 180° 회전, 회전 중 지연 | TIMEOUT(40 s), 누적 **+174°**. 회전 중 `/scan_raw` **101 ms** → `/scan` **54 ms**. 출력의 '밀림' = 지연 × 0.22 rad/s: 1.27° → 0.68° | restamp 효과가 회전 중에도 유지('약 46 % 감소'). ⚠ 실제 평균 각속도는 174° / 40 s ≈ **0.076 rad/s**(출력 진행 줄에서 계산) — 0.22 로 환산한 '밀림' 은 약 3 배 큼(비율은 그대로) | [job8f.sh](../debug_log/2026-08-31/jobs/job8f.sh) · [job8g_spin_result.txt](../debug_log/2026-08-31/outputs/job8g_spin_result.txt) |
| 08-31 수정 ② | `scan_deskew` 작성 · lidar.launch 에서 restamp 대신 deskew, `job8h` 배포 · 정지 비교 | 노드 목록 `/rplidar_node` **2 개** + `/scan_deskew`, raw 1584 점 vs deskew 1588 점, 공통 빔 최대 거리차 **3193 mm** → '점검 필요' | 옛 rplidar 가 안 죽어 두 드라이버가 섞임 | [job8h.sh](../debug_log/2026-08-31/jobs/job8h.sh) · [job8h_deskew_static.txt](../debug_log/2026-08-31/outputs/job8h_deskew_static.txt) |
| 08-31 | `job8i` 전부 `kill -9` 뒤 단일 파이프라인 | rplidar 1 · deskew 1, ω −0.0000, raw 1577 / deskew 1577, 최대 차 **0 mm** | '정지 무결성 완벽'. ⚠ 정지(|ω| < 0.02)면 deskew 는 stamp 만 옮기고 거리값을 안 건드리므로 0 mm 는 **당연한 결과**(보정 계산은 검사되지 않음) | [job8i.sh](../debug_log/2026-08-31/jobs/job8i.sh) · [job8i_deskew_clean.txt](../debug_log/2026-08-31/outputs/job8i_deskew_clean.txt) |
| 08-31 | `job8j` 정지 지연 · slam 건강성 | `/scan_raw` 101 → `/scan` **4 ms**, slam 실행 중, map→odom (0,0,0), slam 로그 'queue is full' 드롭 2 줄, `/scan` 발행 1 · 구독 2 | deskew 출력을 slam · foxglove 가 받음 | [job8j.sh](../debug_log/2026-08-31/jobs/job8j.sh) · [job8j_deskew_latency.txt](../debug_log/2026-08-31/outputs/job8j_deskew_latency.txt) |
| 08-31 '판단·결정' | `job8f` 재실행 + `job8k` 결과 | DONE_180, 누적 +177°(38 s), 회전 중 raw **101 ms** → `/scan` **9 ms** → '밀림' 1.28° → **0.12°**(@0.22 환산). 드롭 2 줄(8j 와 같은 두 줄 = 회전 중 새 드롭 0), 지도 202 × 221 | '~90 % 제거', 잔여 9 ms = 전송 지연 + ω 샘플링, '더 줄일 필요 없음'. restamp 는 경량 폴백으로 보존 | [job8k.sh](../debug_log/2026-08-31/jobs/job8k.sh) · [job8k_deskew_dynamic.txt](../debug_log/2026-08-31/outputs/job8k_deskew_dynamic.txt) |
| 08-31 '판단·결정' 주의 | ref = end 의 대가 | stamp ≈ now − 9 ms → slam 이 그 시각의 odom TF 를 잠깐 기다림(transform_timeout 0.2 s 안) | 드롭 빈발 시 ref 조정 여지 | SUMMARY 문장 |
| 08-31 저녁 | 조이스틱 병진 주행 지도 | 318 × 220 @5 cm, '이동 중 스캔 선명' | deskew 효과(육안) | `ros2_ws/maps/rover_map_drive.*` |
| 08-31 '루프클로저/드리프트 재확인' | 사용자 정정 | 남은 '따라감 → 스냅' 은 스캔 지연이 아니라 **EKF odom 누적 드리프트 → slam map→odom 주기 보정(점프)**. 저장 지도 벽 국소밀도 평균 5.6/9(중앙 6), 번짐 28 % | 사용자 진단 채택. 원인 순위: 직진 스케일 > 좌우 비대칭 > 자이로 스케일 | SUMMARY 문장(분석 스크립트 · 출력 원문 없음) |
| 09-01 세션 2 | deskew 벡터화(Python 루프 → `np.minimum.at`) | deskew CPU: 바꾸기 전 9.0 %(job17b) · 뒤 7.8 %(job17e) | '동작 동일' — **비교 시험 없음**(코드 주석 주장만) | [Foxglove 카드 §8 job17b](foxglove-snap-cpu.md) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 루프 클로저가 스냅을 만든다 | 08-28 해석 | 제자리 회전 · 짧은 시간 — 루프 아님 | **기각**(논리, 측정 없음) |
| 스캔 stamp 가 실제 취득보다 과거 → 회전 중 스캔이 틀린 자세로 그려짐 | job8a 정지 지연 | now − stamp 112 ms ≈ scan_time 95 ms + 17 ms | **지지**. 'stamp = 스윕 시작' 은 이 수치로부터의 **추정**(드라이버 소스는 안 봄) |
| 한 스윕(95 ms) 안의 점들이 서로 다른 자세에서 찍혀 스캔 모양이 휨(전단) | deskew 로 보정 | 지연은 9 ms 로 줄었으나 **모양(전단) 보정이 맞는지 따로 잰 시험은 없음** | **미확인**(§6) |
| '마지막 scan stamp − 마지막 odom stamp −160.7 ms' 가 정합 오류 | job8a 출력 줄 | 이 값은 두 토픽의 '마지막으로 받은 메시지' 시각 차 — 지연 차(≈ 100 ms) + 수신 위상이 섞인 한 표본. slam 은 scan stamp 시각의 odom TF 를 보간해 쓰므로 정합 오류 지표가 아님 | **지표 부적절**(내 판단, 이 카드 작성 시) |
| slam 정합을 잦게(heading 0.08 → 0.03, time 0.3 → 0.1) 하면 회전 중 보정이 3 배 잦아짐 | 08-28 SUMMARY 주장 | 회전 중 정합 횟수를 센 측정은 이 시기에 없음. 이후 09-28 에 apt slam_toolbox 의 스캔 처리 조건이 **odom 이동 거리만** 보고 회전각은 안 본다는 것이 확인됨(`Docs/04_navigation/SLAM_FORK_ROTATION.md` §2) → 제자리 회전에선 heading 을 바꿔도 처리 0 | **틀림**(제자리 회전에 대해) — 이후 시기에서 확인 |
| 남은 '따라감 → 스냅' 도 스캔 지연 | 사용자 정정 + 저장 지도 번짐 28 % | deskew 뒤에도 남음, 지도 벽 2~3 셀 번짐 | **기각** → 오도메트리 드리프트 + SLAM 보정(사용자). 이후 09-28 에 '회전 중 차체 옆 밀림을 EKF 가 못 보고, 원본 SLAM 은 회전 중 스캔을 버린다' 로 구체화 |

## 4. 조치와 효과
| 단계 | 바꾼 것 | 지연(정지) | 지연(회전) | 환산 '밀림'(@0.22 rad/s, 계산) |
|---|---|---|---|---|
| 원래 | rplidar → `/scan` | 112 ms(job8a) · 100.6 ms(job8b) | 101 ms(job8g) | 1.27° |
| ① restamp | stamp + scan_time × 0.5 | 52.8 ms(job8b2) · 52 ms(job8e) | 54 ms(job8g) | 0.68° |
| ② deskew | 점별 회전 보정 + stamp = 스윕 끝 | 4 ms(job8j) · 3.1 ms(09-01 job16f) | 9 ms(job8k) | 0.12° |
- 실제 회전 평균 각속도가 약 0.076 rad/s 였으므로(§2) 실제 환산값은 표의 약 1/3. 비율(약 90 % 감소)은 같다.
- 현재(이 카드 작성 시 git 기준): `lidar.launch.py` 는 09-02 첫 커밋 이후 바뀌지 않았고 deskew(ref end, deadband 0.02)가 활성, `scan_restamp.py` 는 쓰이지 않는 폴백으로 남아 있다. 10-22 기록에 scan_deskew CPU 8.7 % 로 나온다(`Docs/debug_log/2026-10-22/SUMMARY.md` 부하 표).
- slam.yaml: heading 0.03 · time 0.1 반영. 같은 시기 minimum_travel_distance 도 0.08(08-28 job8a) → **0.05**(09-01 job16i)로 바뀌었는데 **SUMMARY 에 기록이 없다**(09-02 커밋의 slam.yaml 주석 "저속 로버 — 5 cm 마다 노드" 만 있음).
- 한계: (1) 점별 보정의 부호 · 시간 순서 가정 미검증(§6) (2) 병진 왜곡 무시(코드 주석: 0.05 m/s × 0.095 s = 5 mm) (3) 회전축이 base_link 중심이라 라이다(전방 0.152 m)의 원운동 병진도 무시 — 0.08 rad/s × 0.095 s × 0.152 m ≈ 1 mm(계산) (4) ω 는 보간 없이 '마지막으로 받은 EKF 값' 하나.

## 5. 내 실수
### 5.1 '밀림 각도' 를 측정값처럼 기록 — 칸 형식
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 수정 효과를 수치로: 회전 중 화면의 점 밀림이 얼마나 줄었나 |
| 본 것 | job8f 출력 `회전중 지연: /scan_raw 101ms(밀림 1.27deg) → /scan 54ms(밀림 0.68deg @0.22rad/s)` |
| 처음 추론 | 밀림 1.27° → 0.68° → 0.12°, '~90 % 제거' 를 결과 표에 '스캔 끌림 (동적, 회전 0.22 rad/s)' 로 기록(08-31 '결과 (수치)') |
| 의심한 이유 | 코드를 보면 '밀림' = 평균 (now − stamp) × 0.22 — 화면 점 위치는 재지 않는다. 또 같은 출력의 진행 줄(2 s 마다 약 8~9°)은 실제 각속도가 0.22 가 아니라 약 0.076 rad/s 임을 보여 준다 |
| 판별 | 이 카드 작성 중 코드와 출력 재독(새 실험 없음) |
| 결론 | '지연' 감소(101 → 54 → 9 ms)는 측정. '밀림 각' 은 명목 각속도로 환산한 계산이며 실제 회전 기준으로는 약 1/3. 그리고 지연이 줄었다는 것은 stamp 가 '지금' 에 가까워졌다는 뜻일 뿐, 점이 올바른 자리에 그려진다는 증명이 아니다 |
| 다음에 알아보는 법 | 수치 옆에 '측정 / 계산(무엇 × 무엇)' 을 적는다. 효과 지표는 고치려는 증상 자체(직선 벽이 회전 중 휘는 정도 · 회전 방향을 바꿨을 때 같은 벽의 각 차)로 잡는다 |
| 데이터 | `2026-08-31/outputs/job8g_spin_result.txt` · `job8k_deskew_dynamic.txt`, 도구 `jobs/job8f.sh` |

### 5.2 '정지 무결성 완벽' 의 의미 과대
- job8i 의 0 mm 는 deskew 가 정지 때 거리값을 아예 안 건드리는 분기(`|ω| < 0.02` → `_restamp_only`)를 탔다는 확인이다. 보정 계산이 '정지 때 아무것도 안 바꾼다' 는 것 이상은 검사하지 않았다. job8h 의 3193 mm 는 rplidar 두 개가 섞인 운영 사고로, 도구 결함이 아니다.

### 5.3 slam heading 튜닝 효과 주장
- 08-28 '보정 3 배 잦게' 는 측정 없이 파라미터 비율(0.08/0.03, 0.3/0.1)로 쓴 문장. 제자리 회전에 대해서는 이후(09-28) apt slam_toolbox 가 회전각을 처리 조건에 안 쓴다는 것이 밝혀져 틀린 주장이 됐다. 칸 형식 기록은 이후 시기 카드(SLAM 포크)에서 — 이후(09-04 ~): 다음 시기에서 채움.

## 6. 남은 것
- **점별 보정의 방향 가정(미확인)**: deskew 는 '빔 번호 i 가 커질수록 나중에 찍혔다(t_i = i × time_increment)' 와 'stamp = 스윕 시작' 을 가정한다. rplidar_ros 가 빔 순서를 뒤집어 내보내는지(물리 회전은 시계 방향, 메시지는 반시계), `angle_compensate: True` 의 격자 재배치가 시간 순서를 어떻게 바꾸는지 이 저장소에서 확인된 적이 없다. 순서가 반대면 스윕 안 보정은 왜곡을 줄이는 대신 두 배로 만들고, 그래도 '지연' 지표는 똑같이 좋아진다. 판별 시험 제안: 직선 벽 옆에서 시계 · 반시계 회전 때 `/scan` 의 벽 직선 적합 잔차 비교(보정이 맞으면 두 방향 모두 정지 때와 같아야).
- 스캔 이음매 손실: 보정 뒤 각도가 `angle_max` 를 넘는 빔은 감아 돌리지 않고 버린다(`j < n` 조건). 이음매(원시 ±180°)는 yaw π 장착에서 **로버 정면**이다. 0.08 rad/s 면 약 2 빔(0.44°), 0.8 rad/s 면 약 22 빔(4.4°)이 정면에서 빈다(계산, 실측 없음).
- intensities 는 재배치하지 않고 원래 배열을 그대로 붙인다(거리와 어긋남). 현재 intensity 를 쓰는 소비자는 확인 안 함.
- 이후(09-04 ~): 다음 시기에서 채움 — 회전 미끄러짐(09-28 '180° 당 10~27 cm'), SLAM 포크(회전 중 스캔 처리), rf2o · cuVSLAM 등 '회전 중 위치' 문제 줄기.

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| job8a | 정지 타이밍 진단 | `2026-08-28/jobs/` · `outputs/job8a_scan_timing.txt` |
| job8b | restamp + slam 튜닝 배포 · 지연 비교 | `2026-08-28/jobs/` · `outputs/job8b_restamp.txt`(실패) · `job8b2_restamp.txt`(성공) |
| job8c · 8d · 8e | 상태 · 재시작 · 준비(배터리 · 지연 · 여유) | `2026-08-31/jobs/` · 출력 8c 는 `2026-08-28/outputs/`, 8d · 8e 는 `2026-08-31/outputs/` |
| job8f · 8f_launch · 8g · 8k | 180° 회전(detach) + 회전 중 지연, 결과 읽기 | `2026-08-31/jobs/` · `outputs/job8g_spin_result.txt`(restamp) · `job8k_deskew_dynamic.txt`(deskew) |
| job8h · 8i · 8j | deskew 배포 · 정지 비교 · 지연과 slam 건강성 | 같은 곳 |
| `scan_restamp.py` · `scan_deskew.py` | 노드 | `ros2_ws/src/rover_bringup/scripts/` |
| 요약 메모 | 08-28 진단 · 수정 정리 | `2026-08-28/outputs/scan_lag_FIX.txt` |

## 8. 도구 해설
공통: job 은 **Jetson** 에서 돈다(PC 에서 `/tmp` 로 보내 ssh 실행, 비밀번호 `<PW>`). 노드 소스는 PC 의 `ros2_ws/src/rover_bringup` 에서 고쳐 Jetson `/tmp/rover_src` 로 올린 뒤 job 이 워크스페이스로 복사 · 빌드한다. 지연 측정은 전부 같은 식: 구독 콜백 안에서 `node.get_clock().now() − header.stamp`(같은 Jetson 시계, use_sim_time 꺼짐 — 09-01 job16f 에서 확인).

**도구 계보**
- 지연 측정: job8a(정지, `/scan` · `/odometry/filtered`) → job8b(`/scan_raw` vs `/scan` 6 s) → job8c · 8e · 8j(같은 비교 5 s, 상태 확인 겸) → job8f(회전 중, 스크립트 안에 내장) → 09-01 job16f(토픽 5 개, 콜백 안 40 개씩 — [Foxglove 카드](foxglove-snap-cpu.md))
- 회전 시험: 08-28 job7j(360° 매핑 — [첫 SLAM 지도 카드](first-slam-map.md)) → job8f(180°, 0.22 rad/s, 여유 가드 3 cm) → 09-01 job16h · 16k · 17c(0.6 rad/s, TF 로깅 · CPU)
- 노드: scan_restamp(08-28) → scan_deskew(08-31, ref end) → 벡터화(09-01, job17b)
- 정지 비교: job8h(1 장씩, 점 수 · 최대 차) → job8i(+ ω 표시, 중복 정리)

### scan_restamp.py (노드, 08-28)
- 실행: Jetson, `lidar.launch.py` 가 띄움(08-28 ~ 08-31 오전). 지금은 launch 에서 빠진 폴백.
- 파라미터: `offset_ratio` 0.5 · `offset_fixed_s` 0.0.
- 하는 일: `/scan_raw` 구독 → `stamp += scan_time × offset_ratio + offset_fixed_s` → 같은 메시지를 `/scan` 으로 발행(QoS sensor_data). 거리 · 각도는 그대로.
- 효과의 뜻: '스캔 전체가 스윕 한가운데 순간에 찍혔다' 고 말해 주는 것. 스윕 앞쪽 점은 47 ms 늦게, 뒤쪽 점은 47 ms 이르게 여겨지는 오차(전단)는 남는다(소스 주석도 같은 말).
- 주석: `TODO(production): 드라이버가 스윕중앙 스탬프 지원하면 본 노드 제거`(레거시 라벨 = TODO(improve)).

### scan_deskew.py (노드, 08-31; 09-01 벡터화)
- 실행: Jetson, `lidar.launch.py`(파라미터 `ref: end`, `omega_deadband: 0.02`). 09-01 job17b 에서는 잠시 `ros2 run` 으로 따로 띄움.
- 입력: `/scan_raw`(LaserScan), `/odometry/filtered`(Odometry — `twist.twist.angular.z` 만 씀, 받을 때마다 덮어씀). 출력: `/scan`.
- 단계(스캔 1 장마다):
  1. n = 빔 수, ti = time_increment, st = scan_time, ω = 마지막 EKF 각속도.
  2. 기준 시각 오프셋 t_ref: `end` = (n − 1)·ti(ti ≤ 0 이면 st), `mid` = st/2, `start` = 0.
  3. |ω| < 0.02 rad/s 또는 ti ≤ 0 또는 n = 0 → **거리값 손대지 않고** stamp 만 + t_ref 해서 발행.
  4. 아니면 빔 i 의 취득 오프셋 t_i = i·ti, 보정 각 a′_i = angle_min + i·angle_increment − ω·(t_ref − t_i). 뜻: 빔 i 이후 기준 시각까지 라이다가 ω·Δt 만큼 더 돌았으므로, 고정된 점은 기준 자세에서 볼 때 그만큼 반대쪽(−)에 있다.
  5. 재배치: j = round((a′ − angle_min)/angle_increment). 유효(유한 · range_min~range_max) 이면서 0 ≤ j < n 인 빔만, 같은 칸에 둘 이상 오면 **더 가까운 거리**(`np.minimum.at(newr, j, r)`, 09-01 전에는 같은 일을 Python for 루프로). 아무것도 안 온 칸은 inf.
  6. 새 LaserScan(헤더 · 각도 · 시간 필드 복사, ranges = 재배치 결과, intensities = **원본 그대로**) → stamp + t_ref 로 발행.
- 숫자 감각: S2L 10 Hz Standard 에서 n 1800 · ti 52.8 µs · angle_increment 0.1996°(0.003484 rad). ω = 0.08 rad/s 면 스윕 첫 빔은 0.08 × 0.095 = 0.0076 rad ≈ 2.2 칸 이동, 마지막 빔은 0 칸.
- 알려진 결함 · 가정: §6(시간 순서 · stamp 가정 미검증, 이음매 빔 버림, intensities 불일치), ω 보간 없음, 순수 yaw 가정. 소스 주석 `TODO(production)`.
- 벡터화(09-01): 주석 "기존 Python 루프와 결과 동일 … deskew CPU 대폭 절감". 실측은 9.0 % → 7.8 %(측정 조건 다름) — '대폭' 은 측정으로 뒷받침되지 않는다([Foxglove 카드 §5.2](foxglove-snap-cpu.md)). 결과 동일 여부를 비교한 출력도 없다.
- 지금도 쓰인다(git: 09-02 첫 커밋 뒤 변경 없음).

### job8a.sh — 정적 타이밍 진단
- 부른 형태: 인자 없음, 로버 정지.
- 하는 일: `ros2 topic hz /scan` 1 줄 → 6 s 동안 `/scan` · `/odometry/filtered` 콜백에서 (now − stamp) ms 를 모음, 마지막 스캔의 scan_time · time_increment · 빔 수 · 각도 범위 저장 → 평균 · 최대 · 최소, '0.28 rad/s 에서 스윕당 왜곡 = 0.28 × scan_time', '반 스윕 지연 = 0.28 × scan_time / 2' 계산 줄, '마지막 scan stamp − 마지막 odom stamp' → `ros2 param get /slam_toolbox` 8 개(minimum_travel_heading · distance · time_interval · transform_timeout · tf_buffer_duration · use_scan_matching · scan_buffer_size · resolution) → rplidar 3 개(scan_frequency · angle_compensate · scan_mode).
- 출력: §2 첫 줄 수치 → [job8a_scan_timing.txt](../debug_log/2026-08-28/outputs/job8a_scan_timing.txt).
- 쓰인 곳: 08-28 진단 문단, `scan_restamp.py` 머리 주석 근거.
- 결함: 'scan − odom stamp 차' 는 한 표본이라 지표로 부적절(§3). 0.28 rad/s 는 당시 회전 지령값 기준(실제 각속도는 안 잼). 다시 쓸 수 있음(정지 지연 점검용으로는 충분).

### job8b.sh — restamp 배포 · 전후 비교
- 하는 일: `/tmp/rover_src/rover_bringup` 복사 · `chmod +x scripts/*.py` · `colcon build --symlink-install --packages-select rover_bringup` → rplidar · scan_restamp · lidar.launch · slam_toolbox pkill → `lidar.launch.py`(8 s) → `slam.launch.py`(10 s) → 노드 목록 · `/scan_raw` · `/scan` hz → 6 s 동안 두 토픽 (now − stamp) 평균 → `tf2_echo map odom` 1 줄 → slam heading · time 파라미터.
- 출력: 1 회차 [job8b_restamp.txt](../debug_log/2026-08-28/outputs/job8b_restamp.txt)(restamp 노드 없음, `/scan_raw` 무발행 — 새 launch 가 적용 안 된 상태로 보임, 원인 기록 없음), 2 회차 [job8b2_restamp.txt](../debug_log/2026-08-28/outputs/job8b2_restamp.txt)(100.6 → 52.8 ms, 0.03 · 0.1). 2 회차의 `/scan_raw` 12.932 Hz 는 `ros2 topic hz` 4 s 짧은 창의 측정 흔들림으로 보임(**추정**, `/scan` 은 10.001).
- 계보: 같은 비교 블록이 job8c · 8e · 8j 에 복사됨.

### job8c.sh — 배포 상태 · 배터리
- 하는 일: 노드 목록(scan_restamp · slam · rplidar) · 두 토픽 hz · 5 s 지연 비교 · slam 파라미터 2 개 · `/battery` 1 회 · `/wheel_odom` hz.
- 출력: [2026-08-28/outputs/job8c_status.txt](../debug_log/2026-08-28/outputs/job8c_status.txt) — 거의 전부 빈 값, `/battery` 미발행 → 'NONE'. 스크립트는 08-31 폴더, 출력은 08-28 폴더(실행 시점은 08-28 끝 배터리 방전 무렵 — **추정**).
- 다시 쓸 일 없음.

### job8d.sh — 재부팅 뒤 전체 재시작
- 하는 일: base · sensors · slam · lidar · ekf launch 와 노드들 pkill · agent 컨테이너 제거 → base.launch(10 s, agent + RSP) → sensors.launch(30 s, lidar + restamp + camera + EKF + foxglove) → slam.launch(12 s) → 노드 목록 · scan_restamp 존재 · `/scan` hz · `/wheel_odom` hz.
- 출력: [job8d_restart.txt](../debug_log/2026-08-31/outputs/job8d_restart.txt) — scan_restamp OK, wheel_odom 50.013 Hz(SUMMARY: 보드도 전원 사이클로 세션 자동 재수립), `/scan` hz 칸은 빈 값.

### job8e.sh — 회전 시험 준비 확인
- 하는 일: `/battery` → 5 s 지연 비교 → **시작 여유**: `/scan` 한 장을 로버 좌표로(LX 0.152, LYAW π: px = 0.152 + r·cos(a + π), py = r·sin(a + π)) 옮겨, 차체 사각형(x −0.25~0.25, y −0.165~0.165)까지의 거리 = sqrt(dx² + dy²)(dx = max(XMIN − px, 0, px − XMAX), dy 같음)의 최솟값.
- 출력: 12.177 V · 100 → 52 ms · 최소 여유 70 cm → [job8e_prep.txt](../debug_log/2026-08-31/outputs/job8e_prep.txt).
- 계보: 이 '차체 사각형까지 거리' 계산이 job8f · 16h · 16k · 17c 의 회전 가드로 복사되고, 이후 `stuck_monitor.py` 등의 LIDAR_YAW 상수와 같은 뿌리(라이다 yaw 를 코드에 박아 둠 — 09-18 데크 보정 때 함께 고쳐야 했던 이유).

### job8f.sh · job8f_launch.sh · job8g.sh — 180° 회전 + 회전 중 지연
- 실행: `job8f_launch.sh` 가 기존 `map_spin` 을 죽이고 `/tmp/spin.log` 를 지운 뒤 `setsid bash /tmp/job8f.sh &` 로 **분리 실행**(ssh/Wi-Fi 가 끊겨도 회전이 끝까지 감독되도록) → 5 s 뒤 로그 4 줄. `job8g.sh` 는 최대 30 s(2 s × 15) 동안 `SPIN_END` 를 기다렸다가 로그 전체 + 현재 각속도 1 회.
- job8f 하는 일: 노드 `map_spin` — `/cmd_vel` 발행, `/scan`(여유 + 지연) · `/scan_raw`(지연) · `/odometry/filtered`(yaw 적분 · 각속도) 구독. 설정 W 0.22 rad/s · 목표 180°(98 % 도달 시 종료) · TIMEOUT 40 s · 가드 SAFE 0.03 m(여유가 3 cm 미만이면 정지). 시작 여유 < 3 cm 면 시작 안 함. 2 s 마다 누적각 출력. 종료 시 0 Twist 12 회 → 두 토픽 평균 지연 × 0.22 를 '밀림' 으로.
- 출력: restamp 시험 [job8g_spin_result.txt](../debug_log/2026-08-31/outputs/job8g_spin_result.txt)(TIMEOUT · +174° · 101 → 54 ms), deskew 시험 [job8k_deskew_dynamic.txt](../debug_log/2026-08-31/outputs/job8k_deskew_dynamic.txt)(같은 job8f 재실행, DONE_180 · +177° · 101 → 9 ms).
- 결함: §5.1 — '밀림' 은 계산값이고 명목 0.22 를 씀. 실제 각속도(약 0.076 rad/s)를 이미 구독하고 있었으므로(`s.wrate`) 그것을 쓸 수 있었다. 회전 중 '지연' 평균에는 정지 구간 몇 장도 섞인다.
- 다시 쓸 수 있나: 분리 실행 + 여유 가드 틀은 이후 러너들로 발전. 이 파일 자체는 라이다 yaw · 차체 치수 상수가 박혀 있어 그대로 쓰지 않는다.

### job8h.sh — deskew 배포 · 정지 비교 v1
- 하는 일: 소스 복사 · 빌드 → lidar.launch · rplidar · scan_restamp · scan_deskew pkill(일반 SIGTERM) → lidar.launch(8 s) → 노드 · 두 토픽 hz → 두 토픽 각 1 장 → 유효 점 수, 둘 다 유효한 빔의 |raw − deskew| 최대 → '점 수 차 < 5 % 이고 최대 차 < 5 cm 면 OK' → lidar.log 의 deskew 시작 줄.
- 출력: rplidar_node 2 개 경고 · 3193 mm '점검 필요' → [job8h_deskew_static.txt](../debug_log/2026-08-31/outputs/job8h_deskew_static.txt). 원인 = 이전 rplidar 프로세스가 안 죽음(같은 이름 노드 2 개).
- 결함: 두 토픽에서 '같은 순간' 장을 맞추지 않음(각자 처음 받은 장) — 정지 상태라 문제는 작음.

### job8i.sh — 정리 후 정지 비교 v2
- 하는 일: rplidar · restamp · deskew 를 `pkill -9`, lidar.launch pkill → 잔존 수 → 단일 lidar.launch(9 s) → 프로세스 수(rplidar 1 · deskew 1 기대) · hz → `/odometry/filtered` 각속도까지 받아 정지 확인 → 점 수 차 < 20 이고 최대 차 < 5 cm 면 OK.
- 출력: 잔존 0, 각 1 개, ω −0.0000, 1577/1577 · 0 mm → [job8i_deskew_clean.txt](../debug_log/2026-08-31/outputs/job8i_deskew_clean.txt).
- 한계: §5.2 — 정지 분기만 검사.

### job8j.sh — deskew 지연 · slam 건강성
- 하는 일: 5 s 지연 비교 → slam 노드 존재 · `tf2_echo map odom` · `/tmp/slam.log` 에서 extrapolat · could not · timeout · error · drop 마지막 3 줄 → `ros2 topic info /scan` 발행 · 구독 수.
- 출력: 101 → 4 ms, map→odom (0,0,0), 'queue is full' 드롭 2 줄(시각 1788135511 · 1788136745), 발행 1 · 구독 2 → [job8j_deskew_latency.txt](../debug_log/2026-08-31/outputs/job8j_deskew_latency.txt).
- 쓰인 곳: '회전 중 slam 드롭 없음' 판정의 기준선(8k 와 같은 두 줄).

### job8k.sh — deskew 회전 결과 읽기
- 하는 일: 최대 36 s `SPIN_END` 대기 → spin.log 전체 → slam.log 'dropping message' 개수와 마지막 2 줄 → 현재 각속도 → `/map` 의 width · height.
- 출력: §2 의 deskew 회전 수치 → [job8k_deskew_dynamic.txt](../debug_log/2026-08-31/outputs/job8k_deskew_dynamic.txt).
- 한계: 드롭 '개수' 는 slam.log 전체 누계라 회전 전후를 따로 세지 않았다(8j 출력과 같은 두 줄임을 사람이 대조해 '회전 중 0' 으로 읽음).

## 9. 용어
- **스윕(sweep) · scan_time**: 회전 라이다가 한 바퀴 도는 동안 점을 차례로 찍는 것. S2L 10 Hz 면 한 스윕 약 95 ms. `scan_time` = 스윕 소요, `time_increment` = 이웃 빔 사이 시간(52.8 µs).
- **스캔 stamp 위치**: 한 장의 스캔에 붙는 시각 하나. 스윕 시작 · 중앙 · 끝 중 어디에 붙이느냐에 따라 '이 스캔은 언제의 모습인가' 가 달라진다. 여기서는 측정(now − stamp ≈ 101 ms ≈ scan_time + 전송)으로 '시작' 이라고 추정했다.
- **now − stamp(지연)**: 받는 순간의 시계와 메시지 stamp 의 차. 전송 · 처리 지연 + 'stamp 를 얼마나 과거에 찍었나'. 작다고 정확한 것은 아니다(stamp 를 미래 쪽으로 옮기면 얼마든지 작아짐).
- **restamp vs deskew**: restamp 는 stamp 만 옮긴다(스캔 모양은 그대로, 평균 시각만 맞춤). deskew 는 빔마다 다른 취득 시각을 고려해 각 점을 기준 시각의 자세로 옮긴다(모양까지 바로잡음). 여기서는 회전(yaw)만 보정.
- **전단(shear) 왜곡**: 회전 중 스윕 앞부분과 뒷부분이 서로 다른 방향에서 찍혀 직선 벽이 비틀려 보이는 것.
- **ref(end / mid / start)**: deskew 결과 스캔이 '어느 순간의 모습' 인지. end 면 가장 최신이라 지연이 최소지만, 그 시각의 odom TF 가 아직 안 왔을 수 있어 SLAM 이 TF 를 기다린다.
- **omega_deadband**: 이보다 느린 회전은 정지로 보고 보정하지 않음(0.02 rad/s). EKF 각속도 잡음이 정지 스캔을 흔들지 않게.
- **재배치(rebin) · 이음매**: 보정된 각도를 원래 각도 격자로 다시 넣는 것. 격자 양 끝(원시 ±180°)이 이음매이며, 넘어간 점은 이 구현에서 버려진다.
- **minimum_travel_heading / distance / time_interval(slam_toolbox)**: 새 스캔을 지도에 넣을지 거르는 문턱. 이 시기 apt 판은 실제로 거리 문턱만 처리 조건에 썼다(09-28 확인).
- **queue full 드롭**: slam_toolbox 의 메시지 필터가 TF 를 기다리는 스캔을 쌓아 둘 자리가 없어 버림. 스캔 stamp 가 '지금' 에 가까울수록(odom TF 가 아직 없음) 기다림이 늘어난다(**추정**, 08-31 '판단·결정' 주의 문장).
- **오도메트리 드리프트 vs SLAM 보정(스냅)**: EKF 의 odom→base_link 는 휠 · 자이로 적분이라 오차가 쌓이고, SLAM 이 스캔 정합으로 map→odom 을 가끔 고치면 화면 속 로버 · 스캔이 '착' 옮겨 간다. 스캔 시각 문제와 겉모습이 비슷하다.
