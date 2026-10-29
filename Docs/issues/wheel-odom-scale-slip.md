# 휠 오도메트리 스케일 · 회전 슬립

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **우회**(09-03 시점: Jetson 쪽 보정 `VX_SCALE 0.783` · `SLIP_PTS 0.46`, 펌웨어 상수는 그대로) → 09-07 펌웨어 교정(다음 시기에서 채움) | 08-26 ~ 09-03 (이 카드가 채운 범위) | [08-26 「결과 (수치)」](../debug_log/2026-08-26/SUMMARY.md) 접지 주행 job2f | `ros2_ws/src/rover_bringup/scripts/sensor_conditioner.py`(`SLIP_PTS` 08-26 2 점 → 08-27 0.46 단일 · `VX_SCALE` 1.0 → 1.022(09-01) → **0.783**(09-01, 09-02 검증)) | [좌/우 트랙 비대칭](track-asymmetry.md) · [스크립트 주행 안전 가드](script-drive-guards.md) · 모터 PWM 50 Hz 오적용(09-07, 카드 예정) |

**한 줄**: 바퀴(FG 펄스)로 계산한 이동이 실제보다 **27.8 % 크게** 나왔다. 처음엔 이것을 '트랙이 미끄러진다(슬립)' 로 읽어 회전에만 계수(0.42/0.28 → 0.46)를 붙였고, 직진은 줄자를 잘못 재서(로버 길이 포함) 오히려 ×1.022 로 키웠다. 09-01 에 줄자 2 회 + SLAM 으로 '속도와 무관하게 1.277/1.278' 을 찾아 **펌웨어 휠 둘레 상수 오류**로 결론, Jetson 쪽 `VX_SCALE 0.783` 으로 우회했고 09-02 에 세 번째 측정(±0.25 %)과 루프 주행(드리프트 ~5 % → ~1 %)으로 확인했다. 회전 계수 0.46 은 '스케일 오류 0.782 × 실제 트랙 스크럽 0.588' 로 분해된다. 펌웨어 상수 교정은 09-03 까지 권고만 했다.

> ⚠ **이 카드의 수치는 전부 모터 PWM 50 Hz 조건**이다. CLAUDE.md: "PWM 20 kHz (2026-09-07 50Hz→20kHz 정정, 08-26~09-07 측정치는 50Hz 조건)". 09-07 이후 재실측 결과는 다음 시기에서 채운다.

## 1. 증상
- 08-26 첫 접지 주행: 0.3 rad/s 회전 3 s 에 **휠은 36°, 실제(육안) 15°**. 전진 0.05 m/s 3 s → 140 mm, 후진 복귀 오차 3 mm. 펌웨어 로그로는 '회전 시 휠 속도 목표의 52 %'. [08-26 「결과 (수치)」](../debug_log/2026-08-26/SUMMARY.md) — 출력 캡처 없음(그날은 기록 규약 채택 전).
- 08-27 W4: 같은 회전을 휠은 자이로의 1.8~2.5 배로 보고(회전 4 번의 휠/자이로, 내 계산), 좌 2 번 후 휠 누적 183° · 육안 ~70° · 자이로 79°. [`outputs/job5d_w4_external_validation.txt`](../debug_log/2026-08-27/outputs/job5d_w4_external_validation.txt)
- 08-31 첫 지도: 벽 국소밀도 평균 5.6/9, 번짐 28 % → 벽이 2~3 칸으로 번짐. [08-31 「루프클로저/드리프트 재확인 (사용자 관찰)」](../debug_log/2026-08-31/SUMMARY.md)
- 09-01 직진: odom 1.634 m 를 갔다는데 SLAM 은 1.213 m(slam/odom 0.7428). [`outputs/job18c_vxverify.txt`](../debug_log/2026-08-31/outputs/job18c_vxverify.txt)

## 2. 흐름 (시간순)
| 날짜 · 제목 | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 08-26 「결과 (수치)」 | job2f 접지 주행(0.3 rad/s · 0.05 m/s 각 3 s) | 휠 36° / 육안 15° | 회전 중 트랙이 미끄러진다(슬립) | [`jobs/job2f.sh`](../debug_log/2026-08-26/jobs/job2f.sh) · 출력 원문 없음 |
| 08-26 「판단·결정」 5 | 휠 단독 EKF(보드 자이로 무반응이라 job3j 에서 휠만 융합)에 회전 계수 2 점 보간 적용(job3o) → 검증(job3p) · 빠른 회전(job3q) | **0.42 @ 0.20 rad/s, 0.28 @ 0.57 rad/s**(육안 기준 2 점) | 슬립은 속도 의존 → 2 점 선형 보간, ≤0.4 rad/s 권장 · **틀림**(08-27 에서 '육안 + 구게이지 + 이상치 착시' 로 정정) | [`jobs/job3o.sh`](../debug_log/2026-08-26/jobs/job3o.sh) · [`job3p.sh`](../debug_log/2026-08-26/jobs/job3p.sh) · [`job3q.sh`](../debug_log/2026-08-26/jobs/job3q.sh) · 출력 원문 없음 |
| 08-27 「W 트랙」 | WT-600 게이지 0.245 를 펌웨어 `WHEEL_BASE_M` 에 반영(사용자, 이전 값 0.190 — 펌웨어 커밋 15c29b8a) → 계수 1.0 초기화 → **W4**: D455f 자이로 적분 / 휠 적분(job5b, 사용자 `!` 실행) | L-slow 0.482 · L-fast 0.402 · R-slow 0.429 · R-fast 0.553 → 평균 0.47 ± 0.06 | 속도 의존 없음, **단일 상수 0.46** | [`jobs/job5b.sh`](../debug_log/2026-08-27/jobs/job5b.sh) · [`outputs/job5b_w4_recalib.txt`](../debug_log/2026-08-27/outputs/job5b_w4_recalib.txt) |
| 08-27 「W 트랙」 | 0.46 배포(job5c) | `SLIP_PTS = ((0.20, 0.46), (0.57, 0.46))` · 정적 yaw 드리프트 0.017°/30 s | 적용 | [`outputs/job5c_slip_apply.txt`](../debug_log/2026-08-27/outputs/job5c_slip_apply.txt) |
| 08-27 「W 트랙」 외부 교차검증 | 자이로 누적 방위 vs 사용자 육안 | 좌 2 번 후 자이로 +79° / 육안 ~70° / 원본 휠 183° · 우 2 번 후 자이로 −15° / 육안 ~10° 우 | 자이로 정확, 원본 휠 ~2.3 배 과대, 0.46 타당 | [`outputs/job5d_w4_external_validation.txt`](../debug_log/2026-08-27/outputs/job5d_w4_external_validation.txt)(계산 기록, 스크립트 없음) |
| 08-27 「판단 — 캘리브레이션 정밀화 & rf2o」 | 사용자 질의 답 | — | 슬립 정밀화는 실익 적음(자이로가 heading 주도). **실익 큰 것 = ① 직진 스케일(WHEEL_RADIUS) 줄자 재실측** ② 좌/우 비대칭 ③ 자이로 스케일 | SUMMARY 만 |
| 08-28 「★ SLAM 첫 맵 완성」 | 360° 제자리 회전 지도(job7k) · 끝에 job7l 로 자세 출력 | `/odometry/filtered` x=+0.2 cm · y=+0.1 cm · yaw=+1° | "yaw·EKF·자이로융합·슬립보정 전 체인 정합 최종 증명" · **과한 결론**(아래 §5 ④ — EKF 위치는 제자리 회전 중 미끄러짐을 못 본다) | [`outputs/job7l_map_analysis.txt`](../debug_log/2026-08-28/outputs/job7l_map_analysis.txt) · [`jobs/job7l.sh`](../debug_log/2026-08-28/jobs/job7l.sh) |
| 08-31 「루프클로저/드리프트 재확인」 | 저장 지도 오프라인 분석 | 벽 국소밀도 5.6/9, 번짐 28 % | 원인 우선순위 ① 직진 스케일(WHEEL_RADIUS 0.02567, 백업 없음) ② 좌/우 비대칭 ③ 자이로 스케일 | job13 출력은 `NO_MAP`([`outputs/job13_drift_diag.txt`](../debug_log/2026-08-31/outputs/job13_drift_diag.txt)) — 분석 원문 없음 |
| 09-01 (08-31 폴더) 「결과 (수치)」 | 펌웨어 최대 속도 확인 | V_MAX 0.100 m/s, 각속도 상한 암묵 0.816 rad/s(= 0.1 / HALF_WHEEL_BASE 0.1225) | — | SUMMARY 만 |
| 09-01 「결과 (수치)」 | **job14b** 2 m 직진(0.06 m/s, VX_SCALE 1.0) + 줄자 | odom 2.005 m · 줄자 2.05 m · heading −0.1° | **×1.022**(odom 2.2 % 과소) · **틀림**(§5 ①, 줄자가 로버 길이 포함) | [`jobs/job14b_straight.sh`](../debug_log/2026-08-31/jobs/job14b_straight.sh) · 출력 원문 없음(대화에만) |
| 09-01 「결과 (수치)」 | 사각 루프 0.4 m: job14d(odom 만) → job14h(벽 기반 GT) → job14j/k(SLAM-GT) | 14d odom 닫힘 5.5 cm · −2.0° / 14h 벽 GT '94.6 cm 이동'(odom 7.0 cm) / 14k 육안 12°/14 cm ≈ slam 10.7°/16.7 cm ≈ odom 11.2°/6.2 cm | heading 0.5~1°/루프(무시), 위치 ~8~10 cm/루프. 14h 벽 GT 는 사용자가 '스캔 아티팩트' 로 기각 | [`outputs/job14d_square_loop.txt`](../debug_log/2026-08-31/outputs/job14d_square_loop.txt) · [`job14h_square_gt.txt`](../debug_log/2026-08-31/outputs/job14h_square_gt.txt) · 14k 원문 없음 |
| 09-01 「판단 (근거·기각가설)」 | 위치 ~10 cm 분해 | — | 직진 스케일 ~3.5 cm(×1.022 로 수정) + **회전 크리프 ~5~6 cm(센서 부재, 수정 불가 → SLAM 담당)** · 앞부분 **틀림**(스케일은 반대 방향이었음), 뒷부분은 09-02 에 '상당 부분이 스케일' 로 축소 | SUMMARY 만 |
| 09-01 | ×1.022 를 conditioner 에 반영(job15a) | 재빌드 · EKF/SLAM 재시작 | 적용 | [`outputs/job15a_apply.txt`](../debug_log/2026-08-31/outputs/job15a_apply.txt) |
| 09-01 세션3 | job18c ×1.022 검증(0.10 m/s, slam 을 기준으로) | odom 1.634 · slam 1.213 → **0.7428** · 직후 map→odom −0.370 m | (대화) "직진에선 slam 이 약하다(aperture)" · **틀림, 철회**(§5 ②) | [`outputs/job18c_vxverify.txt`](../debug_log/2026-08-31/outputs/job18c_vxverify.txt) · [`job18d_slamhealth.txt`](../debug_log/2026-08-31/outputs/job18d_slamhealth.txt) |
| 09-01 「★★ 중대 정정」 | job18f(후진 0.10) · job18g(전진 0.06) + 줄자 2 회 | 휠원시 1.354 / 줄자 1.06 → **1.277** · 휠원시 1.297 / 줄자 1.015 → **1.278** · slam 1.073 · 1.006 | 속도 · 방향 무관 → 슬립 아님, **스케일 상수 오류**. slam 은 줄자와 1 % 안팎 일치 → 신뢰 | [`outputs/job18f_drive_B.txt`](../debug_log/2026-08-31/outputs/job18f_drive_B.txt) · [`job18g_speed_F006.txt`](../debug_log/2026-08-31/outputs/job18g_speed_F006.txt) |
| 09-01 「★★ 중대 정정」 조치 | `VX_SCALE` 1.022 → **0.783**(= 1/1.2776) 반영(job19a) | VX_SCALE 0.783 확인 · 검증 주행 직전 배터리 방전 → Jetson 다운 | 적용(미검증). 펌웨어 권고: `WHEEL_CIRCUMFERENCE_M` 0.16130 → ≈0.1262 또는 펄스/회전 542 → ≈693, 교정 시 SLIP 0.46 → ≈0.588 | [`outputs/job19a_apply783.txt`](../debug_log/2026-08-31/outputs/job19a_apply783.txt) · [`job19b_verify783.txt`](../debug_log/2026-08-31/outputs/job19b_verify783.txt)(`No route to host`) |
| 09-02 「결과 (수치)」 | 경로 밴드 가드로 좁은 곳 1.7 m 직진(job20c) + 줄자 | 휠원시 2.177 · odom 1.708 · 줄자 1.70 → 잔여 **+0.47 %** · 세 번째 과대율 1.2806 | 3 회 평균 1.2786 ± 0.25 % → 1/1.2786 = 0.7821, **0.783 확정** | [`outputs/job20d_pathdrive_F.txt`](../debug_log/2026-09-02/outputs/job20d_pathdrive_F.txt) |
| 09-02 「판단」 | 0.46 분해 | — | **0.46 ≈ 0.782(스케일) × 0.588(실제 트랙 스크럽)**. vx 만 보정, vyaw 는 0.46 유지 = 기능상 정상 | SUMMARY 만 |
| 09-02 「A항목」 | 사각 루프 0.30 m × 4(job21d → 회전 감속 넣은 job21d_v2) + 줄자 · 육안 | v1: odom 18.0 cm · slam 46.1 cm / v2: odom 8.4 cm · +18.1° vs 줄자 6~8 cm · 육안 ~20° | 교정 후 드리프트 ~1.4 cm / 1.2 m(~1 %), 교정 전 ~5 %. "slam 은 회전 많은 구간에서 과대" · ⚠ 46.1 과 '실제 ~7' 은 서로 다른 루프(§5 ⑤) | [`outputs/job21d_loop.txt`](../debug_log/2026-09-02/outputs/job21d_loop.txt) · [`job21f_loop_v2.txt`](../debug_log/2026-09-02/outputs/job21f_loop_v2.txt) |
| 09-03 「부수 발견 (운영)」 | 데드밴드 스윕 중 관찰 | 제자리 회전 반복 시 로버가 수 회전에 10 cm+ 밀림(ICR 오프셋) | 회전 시험은 사방 55 cm+ 확보 | [`outputs/job32e_min016.txt`](../debug_log/2026-09-03/outputs/job32e_min016.txt)(시작 여유 36 cm 에서 가드로 단계가 끊김) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 회전 슬립이 속도에 따라 다르다(08-26) | 자이로 적분 / 휠 적분, 좌/우 × 0.3·0.5 rad/s(job5b) | 느림 평균 0.456 · 빠름 0.478, 방향 무의미 | **기각**(08-27). 08-26 의 2 점은 육안 + 구게이지(0.190) + 이상치 |
| 휠 직진은 실제보다 작게 보고한다(×1.022, 09-01) | 줄자 재측정 2 회(job18f/g) | 실제는 27.8 % **크게** 보고 | **기각**(측정 오류, §5 ①) |
| 직진 오차는 슬립이다 | 속도 0.06 · 0.10, 전진 · 후진에서 과대율 비교 | 1.2774 / 1.2778 / 1.2806(±0.25 %) | **기각** — 슬립이면 속도 · 하중에 따라 변해야 함. 상수 오류 **지지** |
| SLAM 은 직진(복도)에서 약하다(aperture) | 같은 주행에서 SLAM vs 줄자 | 1.073 vs 1.06 · 1.006 vs 1.015 | **기각**(철회, §5 ②) |
| SLAM 은 회전이 많으면 과대 보고한다(09-02) | job21d v1 slam 46.1 cm vs (다른 루프의) 줄자 ~7 cm | 같은 루프의 줄자 값 없음 | **미확인**(근거 약함, §5 ⑤). 회전 중 스캔 드롭 로그와 '정합' 이라는 서술만 있음 |
| 루프 위치 드리프트 ~10 cm 의 대부분은 제자리 회전 크리프(수정 불가) | 스케일 교정 뒤 같은 형태 루프 | ~8 cm/1.6 m → ~1.4 cm/1.2 m | **대부분 기각** — 상당 부분이 스케일 오류였다(09-02). 회전 중 실제 밀림 자체는 09-03 에 별도 관찰(10 cm+/수 회전) — 이후 시기에서 정량 |
| 0.46 은 순수 트랙 스크럽이다 | vyaw 도 같은 둘레 상수로 계산되므로 스케일 오류가 섞임 | 0.46 / 0.782 = 0.588 | **분해**(09-02) — 실측 아님, 계산. 펌웨어 교정 뒤 재측정 필요(09-07 에 0.600, 다음 시기) |

## 4. 조치와 효과
- `SLIP_PTS`: 08-26 2 점(0.42 · 0.28 근처, job3q 머리말은 '0.43') → 08-27 **0.46 단일**. 효과: 정적 yaw 드리프트 0.017°/30 s. 단 08-27 부터 EKF yaw 는 D455f 자이로가 주도(분산비 25 배)하므로 이 계수는 휠 vyaw 가 자이로와 다투지 않게 하는 보조.
- `VX_SCALE`: 1.0 → 1.022(09-01, 잘못) → **0.783**(09-01 적용, 09-02 확인). 효과: 직진 잔여 +0.47 %, 0.30 m 사각 루프 드리프트 ~1.4 cm(측정 오차 수준).
- 펌웨어 상수는 09-03 까지 **안 바꿈**(권고만: `WHEEL_CIRCUMFERENCE_M` 0.16130 → ≈0.1262 = 휠반경 25.67 → ≈20.1 mm, 또는 FG 펄스/회전 542 → ≈693; 교정 시 VX_SCALE 제거 + SLIP 0.46 → ≈0.588 재산정). 근거: 스프로킷/트랙 피치 실측으로 확정 권장.
- 한계: ① 모두 PWM 50 Hz 조건 ② 제자리 회전 중 차체 병진은 휠도 자이로도 못 봄(vx≈0) — 09-01 표현 '센서 부재 → SLAM 담당' ③ 0.46 의 산포 ±13 % 는 스키드 물리 산포로 판단(측정 오차 아님이라는 근거: 휠 적분은 대칭 · 일관, 변동은 자이로 쪽).
- **이후(09-04 ~): 다음 시기에서 채움** — 포인터만:
  - 09-07 펌웨어 `WHEEL_CIRCUMFERENCE_M` 0.16130 → **0.12533**(라이다 전방벽 GT 3 회 평균 1.2870), conditioner `VX_SCALE` 1.0 으로 복귀 — 근거 `sensor_conditioner.py` 머리 주석 · `firmware/rover_jupiter_fw/App/app/rover_platform.h` · 커밋 50444d56 · 3b192df1.
  - 09-07 회전: 자이로 기준 SLIP 평균 0.600 → 유효 게이지 `WHEEL_BASE_M` 0.245 → 0.409 → 0.443, `SLIP_PTS` 1.0 — 커밋 bd3e2deb · bccf6194, `sensor_conditioner.py` 주석('구 0.46 은 직진 스케일 오차 0.777 을 포함한 값').
  - 09-07 모터 PWM 50 Hz → 20 kHz(그 이전 캘리브 수치 재실측 대상) — CLAUDE.md 하드웨어 요약.
  - 제자리 회전 중 실제 미끄러짐(09-28 '180° 당 10~27 cm', 10-02 '회전 중 37 cm 를 EKF 가 못 봄' → rf2o · cuVSLAM) — 메모리 '회전 미끄러짐·rf2o', CLAUDE.md §6 오도메트리.

## 5. 내 실수
### ① 줄자 직진 보정 ×1.022(로버 길이 포함)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 휠 직진 스케일 보정. `job14b_straight.sh`(0.06 m/s, odom 2.0 m 도달 시 정지) 뒤 사용자가 줄자로 이동 거리를 잼 |
| 본 것 | odom(EKF) 2.005 m, 줄자 2.05 m, heading −0.1° |
| 처음 추론 | odom 이 2.2 % 과소 → `VX_SCALE` ×1.022 (job15a 로 배포) |
| 의심한 이유 | job18c(×1.022 적용 뒤 0.10 m/s 직진)에서 slam/odom = 0.7428 — 보정이 맞다면 1.00 근처여야 함. 25 % 차이는 '2 % 보정 오차' 로는 설명 불가 |
| 판별 시험 | 같은 바닥에서 줄자 2 회 + SLAM + 휠원시를 한 주행에 함께 기록(job18f 후진 0.10, job18g 전진 0.06) |
| 결론 | 휠원시/줄자 = 1.277 · 1.278 → 실제는 27.8 % **과대**. job14b 는 실제 이동 ≈1.55 m 에 로버 길이 0.5 m 를 더한 거리(≈2.05)를 잰 것으로 판단(측정 방법 자체는 기록 없음 — 이 판단은 수치 정합에 근거한 **추정**). 오차는 08-26 부터 있었음 |
| 다음에 알아보는 법 | 줄자 기준점을 **차체의 같은 점**(예: 앞 범퍼 끝 → 앞 범퍼 끝)으로 명시하고 기록에 적는다. 보정값은 독립 기준 2 개(줄자 + SLAM)로 교차 확인한 뒤 배포. 보정 크기가 작아도(2 %) 다른 지표와 25 % 어긋나면 측정부터 의심 |
| 데이터 | job14b 출력 원천 소실(대화에만) · [`job18c_vxverify.txt`](../debug_log/2026-08-31/outputs/job18c_vxverify.txt) · [`job18f_drive_B.txt`](../debug_log/2026-08-31/outputs/job18f_drive_B.txt) · [`job18g_speed_F006.txt`](../debug_log/2026-08-31/outputs/job18g_speed_F006.txt) · 정정 원문 [08-31 「★★ 중대 정정」](../debug_log/2026-08-31/SUMMARY.md) |

### ② "직진에서는 SLAM 이 약하다(aperture)" 주장 · 철회
| 칸 | 내용 |
|---|---|
| 하려 한 것 | job18c 의 slam/odom 0.7428 을 해석 |
| 본 것 | slam 1.213 m vs odom 1.634 m, 이어서 job18d 에서 map→odom −0.370 m, slam 로그 'queue is full' 드롭 |
| 처음 추론 | (대화) 복도처럼 앞뒤 특징이 적은 직진에서는 스캔 정합이 이동 방향을 덜 잡는다(aperture 문제) → slam 이 짧게 본다. 이 추론 원문은 SUMMARY 에 '철회' 로만 남음 |
| 의심한 이유 | 줄자라는 제3의 기준이 없었다. 'slam 이 틀렸다' 와 '휠이 틀렸다' 를 같은 데이터로 가를 수 없음 |
| 판별 시험 | job18f/18g — 줄자와 slam 을 같은 주행에서 비교 |
| 결론 | slam 1.073 vs 줄자 1.06(+1.2 %), slam 1.006 vs 줄자 1.015(−0.9 %) → **SLAM 은 직진에서 신뢰 가능**, 주장 철회 |
| 다음에 알아보는 법 | 두 측정이 어긋날 때 한쪽의 약점 이론을 세우기 전에 **세 번째 독립 기준**을 먼저 붙인다. 'X 는 이런 상황에서 약하다' 는 일반론은 그 상황의 실측 없이 쓰지 않는다 |
| 데이터 | 위 ①과 같음 |

### ③ 08-26 '속도 의존 슬립'(0.42/0.28)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 휠 단독 EKF(보드 자이로 무반응)의 회전 과대 보정 |
| 본 것 | 0.3 rad/s 3 s: 휠 36° / 육안 15°(job2f, job3p). 0.6 rad/s 3 s(job3q) |
| 처음 추론 | 0.42 @ 0.20 rad/s, 0.28 @ 0.57 rad/s → 빠를수록 더 미끄러짐 → 2 점 선형 보간 |
| 의심한 이유 | 기준이 육안 2 점뿐. 그날 펌웨어 게이지는 WT-600 이전 값(0.190) |
| 판별 시험 | D455f 자이로를 기준으로 좌/우 × 2 속도(job5b) |
| 결론 | 0.482 / 0.402 / 0.429 / 0.553 — 속도 의존 없음. 08-27 SUMMARY: "오전의 속도 의존은 육안+구게이지+이상치 착시" |
| 다음에 알아보는 법 | 계수를 '속도 함수' 로 만들기 전에 각 속도에서 반복(좌/우)으로 산포부터 본다. 산포(±13 %)가 속도 간 차이보다 크면 단일 상수 |
| 데이터 | [`outputs/job5b_w4_recalib.txt`](../debug_log/2026-08-27/outputs/job5b_w4_recalib.txt) · 08-26 원문 소실(규약 이전) |

### ④ (이번 정리에서 발견 — 기록에 정정 없음) 08-28 '360° 후 0.2 cm 복귀 = 전 체인 정합 증명'
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 360° 제자리 회전 지도 뒤 자세가 시작점으로 돌아왔는지 확인 |
| 본 것 | job7l 출력 `360도 후 pose: x=+0.2cm y=+0.1cm yaw=+1deg` |
| 처음 추론 | "yaw(π)·EKF·자이로융합·슬립보정 전 체인 정합 최종 증명" |
| 의심한 이유 | job7l 은 이 값을 **`/odometry/filtered`(EKF)** 에서 읽는다. EKF 위치는 휠 vx 로만 움직이는데 제자리 회전에서 vx≈0 → 차체가 실제로 밀려도 위치는 그대로다(09-01 SUMMARY 스스로 '제자리회전 시 vx≈0 이라 odom 이 못 봄'). 또 회전 누적이 +353°(job7j3)인데 yaw 가 +1° 인 것은 시작 yaw 가 0 이 아니었다는 뜻이고, 시작 yaw 는 기록에 없다 |
| 판별 시험 | 하지 않음. 09-03 에 '제자리 회전 반복 시 수 회전에 10 cm+ 밀림' 이 관찰됨 |
| 결론 | 위치 복귀 0.2 cm 는 **증명이 아니라 측정 구조상 당연한 값**. yaw 정합 주장도 시작 yaw 미기록으로 **미확인** |
| 다음에 알아보는 법 | '복귀' 판정은 그 운동을 볼 수 있는 센서(SLAM map→base 또는 바닥 표시)로 한다. 판정에 쓴 값이 어느 토픽인지 출력에 찍는다 |
| 데이터 | [`outputs/job7l_map_analysis.txt`](../debug_log/2026-08-28/outputs/job7l_map_analysis.txt) · [`job7j3_spin_final.txt`](../debug_log/2026-08-28/outputs/job7j3_spin_final.txt) · [`jobs/job7l.sh`](../debug_log/2026-08-28/jobs/job7l.sh) 19 · 30~32 행 |

### ⑤ (이번 정리에서 발견) 09-02 'slam 46.1 cm 과대 → 실제 ~7 cm'
| 칸 | 내용 |
|---|---|
| 본 것 | job21d(v1) 출력: odom 18.0 cm · slam 46.1 cm. job21d_v2 출력: odom 8.4 cm, slam 'TF 미확보'. 줄자 6~8 cm · 육안 ~20° 는 v2 표에 붙어 있음 |
| 기록의 추론 | "회전이 많은 구간에서는 부정확(오늘 첫 루프에서 46.1cm 로 과대 보고 → 실제 ~7cm)" |
| 의심한 이유 | 46.1 은 **v1 루프**, ~7 cm 은 **v2 루프**의 줄자다. v1 의 줄자 값은 SUMMARY 어디에도 없다 |
| 결론 | 'SLAM 이 회전 많은 구간에서 과대 보고' 는 **미확인**(근거가 다른 주행끼리의 비교). v1 실제 이동이 46 cm 였을 가능성도 배제 못 함 |
| 다음에 알아보는 법 | 비교하는 두 값이 **같은 주행 이름**에서 나왔는지 표 머리에 주행 이름을 적어 확인 |
| 데이터 | [`job21d_loop.txt`](../debug_log/2026-09-02/outputs/job21d_loop.txt) · [`job21f_loop_v2.txt`](../debug_log/2026-09-02/outputs/job21f_loop_v2.txt) |

## 6. 남은 것(09-03 시점)
- 펌웨어 상수 교정 결정(사용자) — 09-07 에 실행됨(다음 시기).
- 0.588(실제 스크럽)은 계산값. 교정 펌웨어에서 직접 재측정 필요.
- 제자리 회전 중 차체 병진(ICR 이동)을 보는 센서 없음 — SLAM 만 봄.
- 09-02 'slam 회전 과대' 주장의 같은-주행 근거.
- 표현 주의: 09-02 총괄의 "'회전 슬립 0.46'의 78% 는 스케일 버그" 는 비율의 몫이 아니라 곱셈 인수(0.46 = 0.782 × 0.588)를 뜻한다.

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| job2f | 첫 접지 주행(휠 36° / 육안 15°) | 08-26 |
| job3m · 3n | EKF 주행 검증(IMU 포함 → 휠 단독) | 08-26 |
| job3o · 3p · 3q | 슬립 2 점 반영 · 검증 · 빠른 회전 | 08-26 |
| job4z → job5b | 자이로 기준 슬립 캘리브(1 회 → W4 4 회) | 08-27 |
| job5c · job5d | 0.46 배포 · 외부 육안 교차검증 | 08-27 |
| job7l | 360° 지도 저장 + EKF 자세 | 08-28 |
| job14b | 줄자 2 m 직진(×1.022, 잘못) | 09-01(08-31 폴더) |
| job14c → 14d → 14h → 14i · 14j → 14k | 사각 루프 드리프트(odom → 벽 GT → SLAM-GT) | 09-01 |
| job14e | 라이다 프레임 판정(드리프트 원인 후보 배제) | 09-01 |
| job15a | ×1.022 배포 | 09-01 |
| job18a · 18c · 18d · 18f · 18g | 사전점검 · ×1.022 검증 · SLAM 상태 · 직진 재측정 2 회 | 09-01 |
| job19a | 0.783 배포 | 09-01 |
| job20c | 0.783 검증 직진(경로 밴드 가드) | 09-02 |
| job21a · 21d · 21d_v2 | 초기화 · 사각 루프(교정 후) | 09-02 |

## 8. 도구 해설
공통 사항(08-26 ~ 09-03 의 모든 job): **실행 위치 = Jetson**. PC 의 WSL 에서 sshpass 로 스크립트를 `/tmp` 에 올려 `bash /tmp/jobXX.sh` 로 부른다(접속 형태는 메모리 '[Jetson 접속 경로·명령 형태]'). 모터를 돌리는 스크립트는 Claude Code 분류기가 막아 **사용자가 `!` 접두어로 직접 실행**했다(08-26 「판단·결정」 7). 많은 `outputs/*.txt` 첫 줄의 깨진 `wsl: ...` 은 WSL localhostForwarding 경고(한글 깨짐)로 내용과 무관. 08-26 은 기록 규약 채택 전이라 출력 원문이 하나도 없다. 대부분 스크립트는 bash 안에 `python3 - << 'PY'` 로 rclpy 노드를 띄우는 형태이고, 지령은 `/cmd_vel`(Twist) 직접 발행, 끝에 0 지령을 10~15 번 보내 멈춘다(펌웨어 `/cmd_vel` 500 ms 워치독이 2 차 안전).

공통 좌표 상수(08-28 job7d 부터 거의 모든 주행 스크립트): `LX,LYAW = 0.152, π`(라이다가 base_link 앞 15.2 cm, 180° 뒤집혀 장착) · 풋프린트 `XMIN,XMAX = −0.25, 0.25`, `YMIN,YMAX = −0.165, 0.165`(0.50 × 0.33 m). 스캔 점 (r, a) → base_link 좌표 `px = LX + r·cos(a+π)`, `py = r·sin(a+π)`. 이 카드의 가드 규칙 자세한 해설은 [스크립트 주행 안전 가드](script-drive-guards.md).

### job2f.sh — 첫 접지 주행 (08-26)
- 부른 형태: 인자 없음. 사용자 승인 하 접지.
- 왜: Step 2 끝, 보드 ↔ ROS 경로로 실제 바퀴가 도는지 · 오도가 나오는지 첫 확인. 한계는 지시서 §3(linear ≤0.08, angular ≤0.8) 안에서 0.05 / 0.3.
- 하는 일: ① `/wheel_odom` pose 1 회 출력 ② `ros2 topic pub -r 10 -t 30 /cmd_vel {angular.z: 0.3}`(30 개 × 10 Hz = 3 s) 백그라운드, 1.5 s 에 twist 1 회 출력 ③ 0 지령 5 개 ④ pose 출력 ⑤ 같은 방식 전진 0.05 m/s 3 s, 후진 −0.05 m/s 3 s. 라이다 · 거리 가드 없음(그때 라이다 없음).
- 출력: `===ODOM_BEFORE===` 등 단계 머리 + `ros2 topic echo` 원문. 원천 소실.
- 결과가 쓰인 곳: 08-26 「결과 (수치)」 '전진 140 mm, 후진 복귀 오차 3 mm, 회전 휠 36°/실 15°'. 실 15° 는 육안.
- 계보: `ros2 topic pub` 열린 루프 패턴 → job3m/3n/3p/3q 가 같은 틀. 08-27 job4z 부터 rclpy 노드 + 적분으로 바뀜.
- 결함 · 재사용: 회전량을 재지 않고 시간으로만 돌림 → 실제 각은 육안. 지금 쓰지 않음.

### job3m.sh · job3n.sh — EKF 주행 검증 (08-26)
- 부른 형태: 인자 없음.
- 왜: robot_localization EKF 를 얹은 뒤 회전 · 직진에서 `/odometry/filtered` 가 발산하지 않는지. 3m 은 IMU(보드 ICM-20948) 포함 구성, 3n 은 '휠 단독 EKF'(보드 자이로가 회전에 무반응이라 job3j 에서 휠만 남김) 구성.
- 하는 일: job2f 와 같은 3 s 회전(0.3) · 전진(0.05) · 후진(−0.05). 각 단계 뒤 `snap()` 이 `/wheel_odom` 과 `/odometry/filtered` 의 pose(x,y,z,w 줄만 grep)를 나란히 출력. 3m 은 회전 중 `/odometry/filtered` vyaw 와 `/imu/data` z 를 함께 출력.
- 출력: 원천 소실. 결과는 08-26 「판단·결정」 3 (보드 자이로 융합 제외)로 이어짐.
- 계보: 3m → 3n(IMU 제거). 재사용 안 함.

### job3o.sh · job3p.sh · job3q.sh — 슬립 2 점 반영 · 검증 · 빠른 회전 (08-26)
- 부른 형태: 인자 없음. 3o 는 로버 정지(무주행), 3p · 3q 는 회전.
- 왜: 휠 단독 EKF 에서 heading 은 휠 vyaw 그 자체 → 회전 과대(36° vs 15°)를 conditioner 에서 줄이려고.
- 하는 일:
  - 3o: PC 에서 올린 `/tmp/rover_src/rover_bringup` 을 워크스페이스에 복사 → `colcon build --symlink-install --packages-select rover_bringup` → 기존 ekf · conditioner `pkill` → `ekf.launch.py` 를 `setsid nohup` 기동 → 15 s 뒤 로그의 error/died, `/odometry/filtered` hz, 정지 pose 출력.
  - 3p: 0.3 rad/s 3 s 전후로 `/wheel_odom` · `/odometry/filtered` 의 쿼터니언 z, w 출력 → 사람이 yaw 로 환산. 기대: filtered Δyaw ≈ 15°, wheel ≈ 35°(머리말).
  - 3q: 0.6 rad/s 3 s, 1.5 s 시점 wheel vyaw(원본) 와 filtered vyaw(보정 후)를 함께 출력. 머리말: '계수 0.43 의 속도 의존성 확인'(SUMMARY 는 0.42).
- 보정식(conditioner): `|vyaw_wheel|` 를 `SLIP_PTS` 두 점 사이 선형 보간, 범위 밖은 끝값으로 클램프(`yaw_slip_factor`, 현재 파일 53~60 행과 같은 형태).
- 출력: 원천 소실. 결과 = '0.42 @ 0.20, 0.28 @ 0.57'.
- 계보: → 08-27 job4z/job5b(자이로 기준). 재사용 안 함.

### job4z.sh → job5b.sh — 자이로 기준 회전 슬립 캘리브 (08-27)
- 실행: Jetson, 접지, 사용자 입회. 4z: `bash job4z.sh [각속도=0.3] [초=4]`(장착 전 준비만, 실행 기록 없음). 5b: 인자 없음, 4 회 고정(L-slow +0.3×4 s, L-fast +0.5×3 s, R-slow −0.3×4 s, R-fast −0.5×3 s).
- 왜: D455f 자이로가 살아 있음을 확인한 뒤(08-27 손 회전 ±3.0 rad/s), 육안 대신 자이로를 기준으로 계수를 다시 잼. 5b 는 WT-600 게이지 0.245 펌웨어 위에서.
- 하는 일(한 회): ① rclpy 노드가 `/imu/data`(conditioner 출력, 200 Hz) 의 **−angular_velocity.y**(카메라 광학 프레임에서 로봇 yaw = 광학 −y)와 `/wheel_odom` angular.z(**원본 · 미보정**)를 헤더 시각과 함께 쌓음 ② 정지 1.5 s 기준선 ③ `ros2 topic pub -r 10 -t (T×10)` 로 지령 ④ 0 지령 5 개 ⑤ 감속 포함 2 s 더 수집 ⑥ 각각 사다리꼴 적분 `Σ (t_i − t_{i−1})·(v_i + v_{i−1})/2` ⑦ `factor = 자이로 적분 / 휠 적분`(휠 적분 |·| < 1e-3 이면 '회전 안 됨').
- 출력: `[L-slow] cmd=+0.30 x4.0s | gyro= +32.95deg wheel= +68.36deg | factor=0.482 @wheel|vyaw|~0.30` 형식 4 줄 + 종료 정지 twist. 저장 [`outputs/job5b_w4_recalib.txt`](../debug_log/2026-08-27/outputs/job5b_w4_recalib.txt)(끝 '판단' 줄은 손으로 덧붙임).
- 결과가 쓰인 곳: 08-27 「W 트랙」 → 0.46. 4 값 평균 0.4665, 중앙값 0.4555(내 계산) — 0.46 을 고른 근거 문장은 기록에 없다(**미확인**).
- 계보: job3o~3q(육안) → 4z(1 회 · 인자) → 5b(4 회 고정). 09-07 재캘리브(7 속도, 다음 시기)로 대체.
- 결함: 시작 · 끝 정지 구간을 적분에 포함 — 자이로 바이어스가 남아 있으면 정지 3.5 s 만큼 섞임(conditioner 가 바이어스를 빼므로 작다고 봄, 미측정). 라이다 가드 없음.
- 지금 다시 쓸 수 있나: 축 규칙(−y)은 지금도 같음(`sensor_conditioner.py` 38 행). 단 펌웨어가 바뀌어 기대값이 1.0.

### job5c.sh — 0.46 배포 + 정적 확인 (08-27)
- 무주행. `/tmp/rover_src/.../sensor_conditioner.py` 복사 → 빌드 → 설치본의 `SLIP_PTS` 줄 grep → `sensors.launch.py` 재기동 → 35 s 뒤 conditioner 의 'gyro bias calibrated' 로그 → `/odometry/filtered` · `/wheel_odom/conditioned` · `/imu/data` hz → 30 s 간격 filtered 쿼터니언 z,w 두 번.
- 출력 [`outputs/job5c_slip_apply.txt`](../debug_log/2026-08-27/outputs/job5c_slip_apply.txt): `SLIP_PTS = ((0.20, 0.46), (0.57, 0.46))`, 30.0 / 50.0 / 199.5 Hz, z 0.000757 → 0.000909 → Δyaw = 2·Δz ≈ 0.017°/30 s.

### job5d(출력만) — 외부 육안 교차검증 (08-27)
- 스크립트 없음. job5b 네 회전의 자이로 각을 누적해 사용자 육안('좌 2 번 후 대략 70도', '우 2 번 후 약 10도 우측')과 대조한 계산 기록. [`outputs/job5d_w4_external_validation.txt`](../debug_log/2026-08-27/outputs/job5d_w4_external_validation.txt). 원본 휠 누적 +68.36 → +183.44 → +113.10 → −2.38.

### job7l.sh — 360° 지도 저장 + 자세 (08-28)
- 무주행. `map_saver_cli` 로 저장 → `/map` 에서 점유 · 자유 · 미탐사 셀 수 → ASCII 미리보기 → `/odometry/filtered` pose 1 회.
- 출력 [`outputs/job7l_map_analysis.txt`](../debug_log/2026-08-28/outputs/job7l_map_analysis.txt): 215×225 @5 cm, 벽 492 셀, `360도 후 pose: x=+0.2cm y=+0.1cm yaw=+1deg`.
- 결함: 자세를 EKF 에서 읽음 — 제자리 회전 미끄러짐을 볼 수 없음(§5 ④).

### job14b_straight.sh — 줄자 직진 보정 (09-01)
- 부른 형태: 인자 없음. V 0.06 m/s, TARGET 2.0 m(odom 유클리드 거리), 가드 SAFE 0.05 m, TIMEOUT 60 s.
- 왜: 08-31 지도 번짐의 1 순위 후보 '직진 스케일' 을 줄자로.
- 하는 일: `/scan` → 풋프린트 직사각형까지 거리의 **전체 최솟값**(전역 최소) → 5 cm 미만이면 정지 · 시작 시 7 cm 미만이면 거부. `/odometry/filtered`(x, y, yaw) · `/wheel_odom`(x, y) 시작값 저장 → 전진 → odom 이동 ≥ 2.0 이면 정지 → EKF 이동, wheel 이동, heading 변화, '줄자로 실제 이동거리 측정 → 스케일 = 실제/odom' 출력.
- 출력: `정지: TARGET` · `odom(EKF) 이동거리 = 2.005 m` 등(SUMMARY 수치). **출력 원문 없음(대화에만)**.
- 결과가 쓰인 곳: ×1.022 → job15a. 09-01 세션3 에 무효.
- 결함: 줄자 기준점을 출력이 안내하지 않음(§5 ①). 전역 최소 가드라 옆이 좁으면 못 달림(→ job20c).
- 계보: → job18c(slam 비교 · 목표 자동) → job18f/18g(휠원시 · 방향 · 속도) → job20c(경로 밴드 가드).

### job14c_square.sh → job14d_square.sh — 사각 루프(odom 만) (09-01)
- 부른 형태: 14c `[변=0.35] [방향 L|R]`, 14d `[변=0.30] [방향] [가드 m=0.03]`. 실제 실행 출력은 변 0.4 m(14d).
- 왜: 루프 한 바퀴 뒤 '시작 표시에서 얼마나 벗어났나' 를 줄자로 재 드리프트를 보려고.
- 하는 일: 4 번 반복 { 0.06 m/s 로 odom 거리 SIDE 만큼 직진(각 20 s 제한) → ±0.3 rad/s 로 odom yaw 변화 ≥ 88° 까지 회전(15 s 제한) }. 가드: 14c 는 전역 최소 < 5 cm, 시작 < 10 cm 거부. 14d 는 가드 문턱을 인자(기본 3 cm)로, 시작 거부 삭제, 시작 시 앞(±45°)/좌/우/뒤 방향별 여유 출력. 끝에 odom 닫힘 오차(시작 ↔ 끝 거리)와 heading 오차.
- 출력: 14d [`outputs/job14d_square_loop.txt`](../debug_log/2026-08-31/outputs/job14d_square_loop.txt) — 앞 160 · 뒤 154 · 좌 105 · 우 113 cm, odom 닫힘 5.5 cm · −2.0°. 14c 출력 없음. 시작 거부를 뺀 이유는 기록 없음(**미확인**).
- 결함: odom 은 자기 자신을 기준으로 닫힘을 재므로 휠이 틀리면 닫힘 오차가 작아 보일 수 있다 → 실제 드리프트는 줄자 · GT 가 필요(머리말이 그렇게 안내).
- 계보: → job14h(벽 GT) → job14j/k(SLAM GT) → job21d(교정 후).

### job14e_framecheck.sh — 라이다 프레임 판정 (09-01)
- 무주행. 사용자 '180° 뒤집힘' 가설 판별. `tf2_echo base_link lidar_link` + `/scan_raw` 1 장에서 최근접점 raw 각을 yaw=π / yaw=0 두 해석으로 base_link 방위(앞 · 좌 · 뒤 · 우)로 바꿔 출력, raw 0/±90/180 ±20° 창 최소거리.
- 결과: 손을 물리 정면에 대니 raw 180° 가 150 → 28 cm → yaw=π 재확정, 프레임 버그 배제(09-01 「결과 (수치)」). 출력 원문 없음(대화에만).
- 이 카드와의 관계: 드리프트 원인 후보 '라이다 프레임 180° 오류' 기각에 씀.

### job14h_square_gt.sh — 사각 루프 + 벽 기반 GT (09-01, 실패)
- 부른 형태: `[변=0.40] [방향=L] [가드=0.03]`.
- 왜: 사람 줄자 없이 '실제 이동' 을 스캔으로 자동 계산하려고.
- 하는 일: 정지 1.5 s 동안 스캔마다 로버 중심 기준 앞 0° · 좌 90° · 뒤 180° · 우 −90° 의 ±10° 점 거리 **중앙값**, 그것들의 중앙값을 시작 · 끝에 잼. 루프(회전 목표 89°). 실제 이동 ≈ 전진 = ((앞₀ − 앞₁) + (뒤₁ − 뒤₀))/2, 좌 = ((좌₀ − 좌₁) + (우₁ − 우₀))/2 — **시작 · 끝 heading 이 같다고 가정**.
- 출력 [`outputs/job14h_square_gt.txt`](../debug_log/2026-08-31/outputs/job14h_square_gt.txt): 시작 벽 앞 457 · 뒤 522 · 좌 518 · 우 211 → 끝 앞 285 · 뒤 539 · 좌 380 · 우 78 cm, odom 7.0 cm · +8.5°, 벽 기반 94.6 cm → '드리프트 87.6 cm 이상'.
- 결과: 사용자가 '스캔에 잡힌 아티팩트' 로 기각(09-01 기각가설 ③). 내 보충(코드 기준 **추정**): heading 이 +8.5° 바뀌면 ±10° 창이 다른 물체를 집고, 벽이 2~5 m 떨어져 있어 각 오차가 큰 거리 차가 된다(5 m × sin 8.5° ≈ 0.74 m, 내 계산).
- 계보: 폐기 → SLAM-GT(14j/k).

### job14i_slamstart.sh — SLAM 기동 · 확인 (09-01)
- 무주행. slam_toolbox 가 없으면 `slam.launch.py` 기동 후 15 s 대기 → `/map` hz → `tf2_echo map odom` · `map base_link`. SLAM-GT 의 준비.

### job14j_slamdrift.sh → job14k_slamdrift2.sh — 사각 루프 + SLAM-GT (09-01)
- 부른 형태: `[변=0.40] [방향=L] [가드=0.03]`.
- 왜: 벽 GT 실패 뒤 slam_toolbox 의 map→base 를 '실제' 로 삼음.
- 하는 일: tf2 Buffer 로 `map→odom`, `map→base_link` 조회(`Time()` = 가장 최근). 시작 값 저장 → 루프(회전 목표 89°) 동안 매 주기 map→odom 이동량의 최대값 기록 → 끝에 1 s 대기 + spin 20 번(TF 최신화) → odom 이동(추측항법) · slam 이동(map→base) · Δ(map→odom) = 'slam 이 보정한 드리프트' 출력. 14k 는 시작 여유 < 20 cm 면 '사용자님 1.5 m 떨어지세요' 로 거부, 통과 시 3 s 대기.
- 출력: 14j [`outputs/job14j_slamdrift.txt`](../debug_log/2026-08-31/outputs/job14j_slamdrift.txt) — 첫 변에서 바로 '가드정지', 이동 0. 14k: 출력 원문 없음(대화에만), 결과는 SUMMARY '육안 12°/14 cm ≈ slam 10.7°/16.7 cm ≈ odom 11.2°/6.2 cm'.
- 결과가 쓰인 곳: 09-01 '드리프트 heading ~0.5~1°/루프, 위치 ~8~10 cm/루프' · 09-02 '교정 전 ~8 cm/1.6 m(~5 %)'.
- 계보: 14j → 14k(시작 게이트 — 14j 가 사람이 가까이 있어 바로 멈춘 것으로 보임, 14k 머리말 '사용자 근처면 중단') → job21d.
- 결함: '드리프트' 를 위치 크기의 차(|odom| − |slam|)가 아니라 Δ(map→odom) 로 잼 — 이건 벡터라 옳다. 다만 SLAM 이 회전 중 스캔을 버리면 SLAM 쪽도 틀림(09-02 주장, 미확인).

### job15a_apply.sh — ×1.022 배포 (09-01)
- 무주행. `/tmp/sensor_conditioner.py` 복사 → 빌드 → conditioner · ekf · slam 종료 → EKF 재기동(자이로 캘리브 10 s, 정지 필수) → SLAM 재기동 → 노드 · hz · map→odom · VX_SCALE 줄 확인. [`outputs/job15a_apply.txt`](../debug_log/2026-08-31/outputs/job15a_apply.txt). job19a 가 같은 틀.

### job18a_precheck.sh — 무동작 사전점검 (09-01)
- joy 노드 종료(스크립트 주행 시 joy teleop 이 `/cmd_vel` 을 이중 발행하던 문제, 09-01 「부수 발견」) → 배터리 → 노드 · TF → 방향별 여유(±45° 4 섹터) → '직진 2 m 판정(전방 ≥ 230 cm)'.
- 출력 [`outputs/job18a_precheck.txt`](../debug_log/2026-08-31/outputs/job18a_precheck.txt): 12.07 V, 앞 157 · 뒤 152 · 좌 86 · 우 136 cm → '전방 부족'.

### job18c_vxverify.sh — ×1.022 검증 (09-01)
- 인자 없음. V 0.10, 가드 0.05(전역 최소). 전방 ±30° 섹터 여유 f 로 `TARGET = min(2.0, f − 0.5)`, 1.0 m 미만이면 거부.
- 하는 일: odom(EKF) 시작 + `map→base_link` 시작 → 전진 → 정지 후 1.2 s + spin → `ratio = slam 이동 / odom 이동`. |오차| < 1 % 면 '보정 성공' 등 판정 문구.
- 출력: [`outputs/job18c_vxverify.txt`](../debug_log/2026-08-31/outputs/job18c_vxverify.txt) — 전방 207 cm → 목표 1.57, odom 1.634, slam 1.213, 0.7428 → '−25.7 % 과대보고 — 과보정'. 참고(내 계산): 1.634/1.022 = 1.599 를 휠원시로 보면 slam/휠 = 0.759.
- 계보 · 결함: slam 을 기준으로 삼았으나 slam 신뢰가 그때 미확인 → §5 ②. 이어서 job18f/g.

### job18d_slamhealth.sh — SLAM 상태 (09-01)
- 무주행. `/tmp/slam.log` 에서 drop/queue/warn 줄, map→odom, odom · map→base · wheel_odom x, `/map` hz.
- 출력 [`outputs/job18d_slamhealth.txt`](../debug_log/2026-08-31/outputs/job18d_slamhealth.txt): 'Message Filter dropping message ... queue is full' 3 줄, map→odom (−0.370, 0.072) −1.2°, odom x 1.633, map→base x 1.263, wheel x 1.596.

### job18f_drive.sh → job18g_speed.sh — 직진 스케일 재측정 (09-01)
- 부른 형태: 18f `[F|B]`(기본 B, 0.10 m/s 고정), 18g `[F|B] [속도]`(기본 F 0.06). 가드 0.06(전역 최소). 진행 방향 섹터(F: ±30°, B: |각| ≥ 150°) 여유 d 로 `TARGET = min(2.0, d − 0.5)`, < 1.0 m 거부. 18g TIMEOUT 70 s.
- 하는 일: `/wheel_odom`(휠원시) · `/odometry/filtered`(EKF, 그때 ×1.022) · `map→base_link`(slam) 세 개의 시작 · 끝 위치 차를 모두 출력 → 사용자 줄자.
- 출력: [`job18f_drive_B.txt`](../debug_log/2026-08-31/outputs/job18f_drive_B.txt) 후진 182 cm → 1.32 m, 휠원시 1.354 · odom 1.386 · slam 1.073 · [`job18g_speed_F006.txt`](../debug_log/2026-08-31/outputs/job18g_speed_F006.txt) 전진 178 cm → 1.28 m, 1.297 · 1.321 · 1.006. 줄자 1.06 · 1.015 는 사용자 → SUMMARY.
- 결과: 1.277 · 1.278 → VX_SCALE 0.783. 18f 출력 끝 문구 '실제≈odom → vx 보정 정확 / 실제≈slam → 슬립 실재' 의 두 번째 해석은 틀린 이분법(실제는 '휠 상수 오류' 였다) — 출력 문구가 판단을 미리 좁힌 사례.
- 결함: odom 이 목표 1.32 에서 정지 지령을 냈는데 1.386 까지 감 — 정지 지연 · 관성 6 cm(비율 계산에는 무관).
- 계보: → job20c(경로 밴드 가드로 좁은 곳에서도).

### job19a_apply783.sh — 0.783 배포 (09-01)
- 무주행. job15a 와 같은 순서 + 끝에 전방(±30°) / 후방(|각| ≥ 150°) 여유로 다음 주행 방향 추천.
- 출력 [`outputs/job19a_apply783.txt`](../debug_log/2026-08-31/outputs/job19a_apply783.txt): bias (−0.00962, …), `VX_SCALE = 0.783`, 30.0 Hz, 전방 151 / 후방 64 → F. 검증(job19b)은 `No route to host`(배터리 방전).

### job20c_pathdrive.sh — 0.783 검증 직진 (09-02)
- 부른 형태: `[F|B] [속도=0.06]`. 경로 밴드 가드 8 cm, 목표 = 경로 여유 − 0.35 m(최대 2.0, 0.20 미만 거부). 가드 상세는 [가드 카드](script-drive-guards.md).
- 출력: [`job20d_pathdrive_F.txt`](../debug_log/2026-09-02/outputs/job20d_pathdrive_F.txt) — 경로 여유 203 cm(전역 최소 5 cm) → 1.68 m, 휠원시 2.177 · odom 1.708 · slam `nan`(map→base 미확보). 줄자 1.70 → +0.47 %.

### job21a_reset.sh — 손으로 옮긴 뒤 초기화 (09-02)
- 무주행. agent 확인 → conditioner · ekf · slam 재기동(자이로 캘리브 정지 필수) → odom 원점 · map→odom · map→base 확인 → 회전 공간 판정(중심 기준 최근접 vs 스윕 반경 30 cm) · 직진 경로 여유(밴드) · 최근접 측면.
- 출력: [`job21a_reset.txt`](../debug_log/2026-09-02/outputs/job21a_reset.txt)(최근접 16 cm → 회전 불가) · `job21b_reset2.txt` · [`job21e_reset3.txt`](../debug_log/2026-09-02/outputs/job21e_reset3.txt)(57 cm → 가능) · `job22a_reset.txt`.

### job21d_loop.sh → job21d_loop_v2.sh — 교정 후 사각 루프 (09-02)
- 부른 형태: `[변=0.30] [방향=L] [속도=0.06]`. 회전 ±0.3 rad/s.
- 왜: '루프 ~10 cm' 는 틀린 스케일 위의 값이라 0.783 으로 다시.
- 하는 일: 가드 = 직진 경로 밴드 8 cm · 회전 스윕 반경(중심 기준 34 cm), 둘 다 **0.5 백분위**. 4 × { 변 직진(30 s 제한) → 회전(20 s 제한) }. v1 회전 목표 89°, v2 목표 90° + **남은 각 15° 이하에서 ω × 0.35**. 끝에 1.5 s 대기 + spin 25 번 → odom 이동 · heading, (가능하면) slam 이동 · heading, '드리프트 = |odom 이동 − slam 이동| 이상'.
- 출력: [`job21d_loop.txt`](../debug_log/2026-09-02/outputs/job21d_loop.txt) 시작 최근접 65 cm, 4 변 hd 87.9 → −178.9 → −74.9 → 31.9, odom 18.0 cm · +38.7°, slam 46.1 cm · +33.9°. [`job21f_loop_v2.txt`](../debug_log/2026-09-02/outputs/job21f_loop_v2.txt) 시작 58 cm, hd 90.6 → −167.4 → −76.1 → 16.8, odom 8.4 cm · +18.1°, 'slam TF 미확보'.
- 결과: 4 회전 합 392° → 377°(시작 hd 0 에서 4 번째 끝 hd 31.9 · 16.8 에 360 을 더한 값과 일치), 교정 후 드리프트 ~1.4 cm.
- **알려진 결함**: 시작 대기 루프가 `st['o']` · `st['cen']` 만 기다리고 `map→base` TF 를 안 기다림 → v2 는 SLAM 재기동(job21e) 직후라 TF 가 없어 slam 비교 실패(09-02 「판단」 '스크립트 버그'). 드리프트를 크기 차로 계산 — 방향이 다르면 과소(그래서 '이상' 이라 표기).
- 지금 다시 쓸 수 있나: 구조는 참고용. 펌웨어 · 오도 구성이 바뀌어 수치 기대값이 다름.

## 9. 용어
- **FG 펄스**: 통합 드라이버 모터가 내는 속도 펄스(3 상 홀 → 펄스, 방향 정보 없음). 휠 1 회전당 542 펄스(실측, CLAUDE.md). 이동 = 펄스 × `WHEEL_CIRCUMFERENCE_M / 542`.
- **스케일 오류**: 둘레 상수가 실제보다 커서 모든 이동 · 회전이 같은 비율(여기 1.278 배)로 크게 나오는 것. 속도 · 방향과 무관한 것이 슬립과의 구별점.
- **스키드 스티어 스크럽**: 궤도(트랙) 차량이 제자리 · 곡선 회전할 때 트랙이 옆으로 끌리며(scrub) 바퀴 회전만큼 차체가 돌지 않는 현상. 그래서 '휠이 계산한 회전 > 실제 회전'.
- **SLIP_PTS / 회전 슬립 계수**: conditioner 가 휠 vyaw 에 곱하는 값(실제 회전 / 휠 회전). 2 점 보간 형식이라 이름이 PTS.
- **VX_SCALE**: conditioner 가 휠 vx 에 곱하는 값(09-01 0.783).
- **ICR(순간 회전 중심)**: 차체가 그 순간 도는 중심. 스키드 스티어에서는 접지 · 하중에 따라 base_link 중심에서 벗어나 제자리 회전에서도 차체가 밀린다(09-03 '수 회전에 10 cm+').
- **유효 게이지(B_eff)**: 스크럽을 포함해 '실제 회전 = (v_R − v_L)/B_eff' 가 되도록 맞춘 좌우 간격. 기하 간격보다 크다(09-07, 다음 시기).
- **SLAM-GT**: slam_toolbox 의 map→base_link 를 '실제 위치' 기준으로 쓰는 방법. 직진에서는 줄자와 1 % 안팎(09-01).
- **벽 기반 GT**: 정지 상태의 사방 벽 거리 변화로 이동을 역산(job14h). heading 이 바뀌면 깨짐.
- **along-track / cross-track**: 진행 방향 성분 / 옆 성분 오차. 09-01 루프 드리프트는 '주로 along-track(전진)'.
- **aperture 문제**: 특징이 한 방향으로만 늘어선 곳(긴 복도)에서 스캔 정합이 그 방향 이동을 못 잡는 현상. 여기서는 근거 없이 끌어왔다가 철회.
- **사다리꼴 적분**: 샘플 사이를 직선으로 보고 면적을 더하는 적분(job4z/5b).
