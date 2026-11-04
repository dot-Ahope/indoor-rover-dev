# 남서 구석 방향 맞춤 정체 — 도착 직전 '움찔' 과 nav_guard 취소 (6 기: 10-07 §2 · §2.1~§2.6 · §3.3~§3.5 · §6~§7.2 · 7 기: 10-14 §13.1 · §13.3 · §16 · §17)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **우회**(10-07 §7: 러너 yaw 모드 `f` '위치만' — map 위치가 0.15 m 안이면 러너가 취소하고 SUCCEEDED_XY. f2d2 남서 **SUCCEEDED_XY 59.6 s, 1 회 확인**). 원인: 10-07 의 해석('뒤 4.5 cm 치명 칸 때문에 −109° 로 못 돎')은 **판별 없이 남은 추정**이고, 같은 날 기록만으로도 '컨트롤러가 받은 목표 방향이 보낸 방향이 아니었다(≈ 0°)' 는 정황이 있다(§3 · §5 실수 6 — 11-02 카드 작성 중 기록 대조, 같은 추론을 10-14 §16 이 먼저 함). **7 기(10-14) — 원인 거의 확정 · 결함은 고침**: TruncatePath 시절 남서 'f' 목표의 컨트롤러 끝 방향이 목표 0.26 m 앞까지 **0.0°**(계획기 −101.3°, f2s2 bag 11-03 재실행 — §7), CopyPath 뒤엔 0.87 m 안부터 −107.8 = −107.8°(f2t1). 남서 도착 방향도 고치기 전 −0.3 · +0.5 · −1.6° → 고친 뒤 −110.6 · −106.6 · −108.9°. `f` 우회는 그대로이고 `p` 재시험은 안 함(§7.2) | 10-07 (앞: 10-02 f2b3 목표 6) | [10-02 §6.4](../debug_log/2026-10-02/SUMMARY.md)(f2b3 목표 6 — [F2 순회와 위치 점프](f2-patrol-loc-jump.md)) → [10-07 §2.2](../debug_log/2026-10-07/SUMMARY.md) 재현 | 러너 `job550_f0run.py` yaw 모드 `f`(커밋 `0bbd8326`, 사본 [`2026-10-07/jobs/job550_f0run.py`](../debug_log/2026-10-07/jobs/job550_f0run.py) 10 · 34 · 134~135 행) · 래퍼 [`run_f2c.sh`](../debug_log/2026-10-07/jobs/run_f2c.sh) `REST5F`. 그 밖 이날 바꾼 것(이 문제와 무관 판정): G4 휠 잔차 · MPPI `transform_tolerance` 0.2 → 0.5(§6). **지금**: [`places.yaml`](../../ros2_ws/src/rover_navigation/config/places.yaml) 46 행 남서 `yaw_mode: f`(47 행 `min_clear: 0.0`) · [`place_server.py`](../../ros2_ws/src/rover_navigation/scripts/place_server.py) 251~254 행 | [F2 순회와 위치 점프](f2-patrol-loc-jump.md)(같은 순회 · 10-02 첫 사례) · [회전 중 장애물 번짐](rotation-obstacle-smear.md)(10-02 f2b3 정체의 기전 후보) · [온보드 정지 수단 · nav_guard](onboard-stop-nav-guard.md)(취소 주체) · [rf2o 도입](rf2o-introduction.md)(이날 주행 구성) · [Jetson Wi-Fi](jetson-wifi-link.md)(§2.1) · [제자리 회전 옆 밀림 F0-a](f0-rotation-side-slip.md)(5 cm 격자 풋프린트 판정 전례) · [MPPI 상자 옆 통로 튜닝](mppi-passage-tuning.md)(GoalCritic 10 근거) · [정체 감시 stuck_monitor](stuck-monitor.md)(관찰 모드 진단) · [BT 끝 방향 0° 결함 · CopyPath](bt-copypath-end-yaw.md)(7 기 — 원인과 수정) · [F2 기준선 no5](f2-baseline-no5.md)(남서 = 기준선 코스 목표 4) · [상자 옆 정지 기전](box-side-stall-cause.md) (7 기) · [F2.5 장소 이름 이동](f25-place-navigation.md) (9 기) |

**한 줄**: rf2o 를 켠 F2 순회 비교(f2c1)에서 목표 4 = 남서 구석 (−1.6, −5.5) 에 0.165 m 까지 온 로버가 목표 방향(−109°)과 **반대쪽으로** 돌며 물러나 동쪽(+3°)을 보고 선 뒤, 33 s 동안 ±0.01 m/s 수준의 지령만 냈다(사용자: "움찔대기만 한다"). 라이다 기준 접촉은 없었고(12.2 cm), Nav2 진행 검사 실패 뒤 11 s 만에 nav_guard 가 '45 s 동안 0.24 m' 로 취소했다. 10-02 f2b3 · 10-07 f2c1 · f2d1 로 **3/3 재현**, G4 · transform_tolerance 를 바꿔도 같아 사용자 지시("방향을 크게 바꾸라는 명령 제거")로 러너에 '위치만(f)' 을 넣었고 f2d2 에서 남서를 59.6 s 에 넘겼다. 그날 해석은 '뒤 4.5 cm 치명 칸 + 5 cm 격자로 회전을 못 고름' 이었지만, 세 번 모두 로버가 **0° 쪽으로** 돌았고 방향 차 63 · 130° 로 Nav2 가 'SUCCEEDED' 를 낸 목표가 같은 날 두 번(10-02 f2b3 남서 89° 까지 세 번) 있어 — 컨트롤러가 비교한 목표 방향이 러너가 보낸 방향과 달랐다는 것은 설정상 거의 확실하고, 그것이 BT `TruncatePath` 의 끝 방향 0° 였다는 것은 정황이다(§3).

## 1. 증상
- f2c1(10-07 10:58:16 출발, 10 목표, 속도 0.07, `GOAL_FRAME=map`, rf2o + G4 + 그림자 EKF A): 목표 1~3 SUCCEEDED, 목표 4 남서 CANCELED 71.2 s — [`f0_f2c1_runner.log`](../debug_log/2026-10-07/outputs/f0_f2c1_runner.log):
  ```
    경로 자동 yaw: 경로 77 점, 끝 0.307 m 구간 방향 -109.4° (직선 방향 -88.4°, 차 -21.0°)
  목표 4 출발: map (-1.60, -5.50, -109°), 거리 1.80 m, 한도 81 s
    목표 4 CANCELED 71.2 s | 도착 map (-1.475, -5.392, -0.3°) 목표 대비 0.165 m, 109.0°
  ```
- Nav2 로그(같은 목표) — [`j908_g4log.txt`](../debug_log/2026-10-07/outputs/j908_g4log.txt)(도구 [`job908_g4log.sh`](../debug_log/2026-10-07/jobs/job908_g4log.sh)):
  ```
  11:00:57 [ERROR] ... [smoother_server]: Smoothed path leads to a collision at x: -1.529915, y: -5.368849, theta: 1.176065
  11:00:57 [nav_guard.py-2] ... 목표 63a1677d: 남은 거리 2.06 m → 시간 한도 89 s (시작 뒤 0.0 s)
  11:01:57 [ERROR] ... [controller_server]: Failed to make progress
  11:02:08 [nav_guard.py-2] [ERROR] ... nav_guard 개입 — 무진행: 45 s 동안 최대 0.24 m 이동 < 0.25 m → 모든 목표 취소·정지
  ```
- 사용자(주행 중): "현재 위치에서 움직이지 못하고 움찔대기만 한다 — 충돌인지 분석" → 1 s 표본(odom, EKF B) — [`j910_g4cost.txt`](../debug_log/2026-10-07/outputs/j910_g4cost.txt)(도구 [`job910_g4cost.py`](../debug_log/2026-10-07/jobs/job910_g4cost.py), 창 시작 11:00:50 = +0 s, 목표 4 시작 ≈ +7 s):
  ```
   +36.0 s  odom(-1.22,-5.41, -88°) | 외곽 안 치명 0·내접 3 | 치명 최근접 0.142(오, 차체 +0.00,-0.31) | 라이다 최근접 0.195(차체 -0.17,-0.36) | cmd 20개 v +0.030~+0.080 w -0.36~+0.23 | B−A 3.2 cm
   +39.0 s  odom(-1.20,-5.52, -63°) | 외곽 안 치명 0·내접 5 | 치명 최근접 0.083(오, 차체 -0.23,-0.25) | 라이다 최근접 0.137(차체 -0.30,-0.29) | cmd 20개 v +0.051~+0.075 w +0.38~+0.38 | B−A 2.9 cm
   +43.0 s  odom(-1.20,-5.55,  -2°) | 외곽 안 치명 0·내접 7 | 치명 최근접 0.086(뒤, 차체 -0.33,+0.12) | 라이다 최근접 0.143(차체 -0.39,-0.18) | cmd 20개 v -0.037~-0.023 w +0.15~+0.38 | B−A 2.7 cm
   +45.0 s  odom(-1.22,-5.55,  +3°) | 외곽 안 치명 0·내접 11 | 치명 최근접 0.046(뒤, 차체 -0.29,+0.14) | 라이다 최근접 0.125(차체 -0.37,-0.11) | cmd 20개 v -0.013~-0.003 w -0.00~+0.03 | B−A 2.6 cm
   +79.0 s  odom(-1.22,-5.55,  +3°) | 외곽 안 치명 0·내접 11 | 치명 최근접 0.046(뒤, 차체 -0.29,+0.14) | 라이다 최근접 0.123(차체 -0.37,-0.12) | cmd 29개 v -0.005~+0.003 w +0.00~+0.01 | B−A 2.6 cm
  ```
  +45~+79 s 의 지령 범위는 v −0.006~+0.012 m/s · ω −0.05~+0.03 rad/s(출력 전 줄, 측정). '움찔' = 이 지령이 펌웨어에서 짧은 PWM 떨림이 된 것(추정, 펌웨어 쪽 기록 없음).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-07 §2 선언 | 계획 ③ rf2o 켠 F2 순회 비교. 10-02 f2b 와 같은 구성(office_v3 · 위치 추정 · 전역 = 저장 지도 + 라이다 + 카메라 점군 · 로컬 nvblox + 라이다 · MPPI · stuck 관찰 · nav_guard · PathBlockedAhead) + `ekf.launch.py rf2o:=true gate_v:=on shadow:=true` | 비교 기준(10-02 f2b): 시도 7 · 성공 6 · 실패 1(남서 방향 맞추기 정체) · 측면 접촉 2 · 점프 최대 0.184 m | 판정 ③-a 10 목표 · 사람 도움 0 · 접촉 0 · 복귀 줄자 ≤ 5 cm, ③-b 번짐 B < A · ≤ 5 cm, ③-c G4 버림 ≤ 5 %, ③-d 부하 기록 | [10-07 SUMMARY §2](../debug_log/2026-10-07/SUMMARY.md) · prep [`job903_prep_rf2o_g4.sh`](../debug_log/2026-10-07/jobs/job903_prep_rf2o_g4.sh) |
| 10-07 §2.1 | prep 전송(scp) 'lost connection' → 네트워크 확인 | WEB_DEV_5G 에 −54 dBm 으로 붙었는데 IP 없음(10:42~10:44), 재부팅 뒤 22 s 만에 끊기고 ALOPS_ROBOTICS_5G(−57 dBm) 172.30.1.8 | 09-23 과 같은 'AP 연결 OK · DHCP 무응답'(측정), 라우터 원인은 미확인 → `JETSON_HOST=172.30.1.8` 로 진행. prep 통과(원점 0.55 cm · /odom_rf2o 7.8 Hz 는 CLI 한계 — §3.1 bag 9.6~9.7 Hz) | [`job906_net.sh`](../debug_log/2026-10-07/jobs/job906_net.sh)(출력 **원천 소실** — 수치는 SUMMARY 뿐) · [`j903_prep.txt`](../debug_log/2026-10-07/outputs/j903_prep.txt) · [`job907_postchk.sh`](../debug_log/2026-10-07/jobs/job907_postchk.sh) · [`up904.sh`](../debug_log/2026-10-07/jobs/up904.sh) → [Jetson Wi-Fi](jetson-wifi-link.md) |
| 10-07 §2.2 | f2c1 출발 — 출발 전 중단 2 회(로버 안 움직임): ① `run_f2c.sh` CRLF ② 게이트 A 가 그림자 `ekf_shadow_a` 때문에 ekf_node 2 개를 중복으로 봄 → 허용 수 = 1 + 그림자 수 | 게이트 A · B · J 15.1 Hz · C · G2 0.362 · P 52 % 통과. 목표 1 B 52.5 s · 2 (−1.6, −2.0) 59.8 s · 3 서쪽 통로 26.8 s SUCCEEDED, **4 남서 CANCELED 71.2 s**(§1) | '목표 근처 끝점이 충돌 칸 · 벽에 가까운 공간 문제일 가능성'(추정). ⚠ SUMMARY '위치는 0.165 m 안' — Nav2 허용 0.15 m 를 **넘은** 값(§5 실수 4) | [`f0_f2c1_runner.log`](../debug_log/2026-10-07/outputs/f0_f2c1_runner.log) · [`j908_g4log.txt`](../debug_log/2026-10-07/outputs/j908_g4log.txt) · [`job551_f0drive.sh`](../debug_log/2026-10-07/jobs/job551_f0drive.sh) 9~10 행 · bag `2026-10-07/bags/bag_f2c1.tgz`(run_meta `git_head_pc 0cd25aa`) |
| 10-07 §2.3 | 사용자 '움찔' → 지금 지령 확인(11:03:40) → bag 1 s 표본 | 지금은 `/cmd_vel` 없음(취소 뒤 정지). bag: +8~+38 s 남쪽 통로 진입(오른쪽 치명 8~15 cm) · +39~+44 s **왼쪽(+0.38 rad/s)으로 돌며** +39~+41 전진 · +42 부터 후진, 방향 −63° → +3° · +45~+79 s 자세 고정, 미세 지령. 외곽 안 치명 0 · 내접 11, 치명 최근접 뒤 4.5 cm, 라이다 최근접 뒤 12.2 cm, B − A 2.3~3.2 cm | **접촉 아님**(라이다 기준). 해석(추정): '−109° 로 돌려면 뒤 모서리(중심에서 0.298 m)가 그 칸(0.32 m) 근처를 쓸어 5 cm 격자 판정으로 충돌 → MPPI 가 회전도 전진도 못 고름'. 왜 반대로 돌았는지는 미확인 — **이 해석은 이후 정황과 맞지 않음**(§3 · 실수 6). 첫 계산은 코스트맵 척도 실수(실수 3) | [`job909_cmdnow.sh`](../debug_log/2026-10-07/jobs/job909_cmdnow.sh)(출력 **원천 소실**) · [`job910_run.sh`](../debug_log/2026-10-07/jobs/job910_run.sh) · [`job910_g4cost.py`](../debug_log/2026-10-07/jobs/job910_g4cost.py) · [`j910_g4cost.txt`](../debug_log/2026-10-07/outputs/j910_g4cost.txt) |
| 10-07 §2.4 | f2c2 = 목표 5~10 이어 가기(남서 구석에서 출발, 사용자 "시작") | G2 0.104 m(뒤 벽 12 cm) · P 50 % 통과, 11:08:14 출발, `git_head_pc 64aa041`. 주행 중 사용자 '전진하며 이상하게 움직인다' → 로그만 읽음(DDS 참여자 안 만듦) | '목표 5(D) 4 분 넘게 결과 없음 · 7.26 m 는 먼 우회로' — **내 오독**(실수 2): 실제 D 41.3 s 성공, 7.26 m 는 W3 정상 경로. ⚠ 제목의 출발 자세 (−1.22, −5.55, +3°) 는 **odom** 좌표(러너 map (−1.476, −5.392, −0.4°), 실수 7) | [`f0_f2c2_runner.log`](../debug_log/2026-10-07/outputs/f0_f2c2_runner.log) · [`job911_navtail.sh`](../debug_log/2026-10-07/jobs/job911_navtail.sh) · [`j911_navtail_1112.txt`](../debug_log/2026-10-07/outputs/j911_navtail_1112.txt) |
| 10-07 §2.5 | f2c2 결과 | 6/6 SUCCEEDED(f2c 합계 9/10). **목표 6 = 남서(경로 끝 149°) SUCCEEDED 58.5 s, 도착 (−1.450, −5.689, 18.8°) 목표 대비 0.242 m · −129.8°**. map→odom 누적 Δ(0.422, 0.265) m · −9.65° | SUMMARY '성공 판정은 위치만' — **설정과 모순**(yaw 허용 0.35 rad 가 실행 중 값, §5 실수 5). 이 'SUCCEEDED' 가 컨트롤러 목표 방향 ≠ 149° 의 증거(§3) | [`f0_f2c2_runner.log`](../debug_log/2026-10-07/outputs/f0_f2c2_runner.log) · bag `bag_f2c2.tgz` 의 `params.txt` |
| 10-07 §2.6 | 사용자 '복귀 때 상자 쪽으로 다시 몸을 틀었다' | 상자 칸까지 최소 7.3 cm(+106 s), 사용자 '상자를 밀면서 왔다' | 접촉 1 → ③-a 불합격. §7.1 에서 민 것은 통로 가운데 상자 ② 로 다시 읽힘(이 카드 밖 — 상자 줄기, 카드 미작성) | [`f2c2_boxgap.txt`](../debug_log/2026-10-07/outputs/f2c2_boxgap.txt) · 그림 [`2026-10-07_f2c2_return_box.png`](../04_navigation/figures/2026-10-07_f2c2_return_box.png) |
| 10-07 §3.3 | ③-b 번짐(제자리 회전 구간 B · A 대 SLAM) | f2c1 2 구간 B 4.2 · 3.8 / A 4.6 · 4.3 cm, f2c2 B 10.3 · 6.6 / A 11.8 · 7.3 cm — B < A 4/4, 최대 10.3 > 5 | '판정 불가에 가까움'(제자리 회전 4 번뿐 · 기준 SLAM 오차 수 cm · G4 몫 섞임). 남서 구석 정체와는 무관(f2c1 남서 구간 B − A 2.3~3.2 cm) → [rf2o 도입](rf2o-introduction.md) | [`f2c_anal.txt`](../debug_log/2026-10-07/outputs/f2c_anal.txt) · [`f2c_anal.py`](../debug_log/2026-10-07/jobs/f2c_anal.py) · [`job913_extract.py`](../debug_log/2026-10-07/jobs/job913_extract.py) |
| 10-07 §3.4 | map→odom 0.42 m · −9.7° 가 이상치인가 | f2b3 Δ(0.393, 0.137) · −5.70° vs f2c2 Δ(0.422, 0.265) · −9.65°. f2c1 은 남서 접근 중 **≈ 11:01:17 8.1 cm · ≈ 11:01:27 14.4 cm** 의 한 번 보정 2 회(bag +181 · +191 s) | 이상치 아님 → [F2 순회와 위치 점프 §7](f2-patrol-loc-jump.md). 남서 구석 보정 2 회와 정체의 관계는 **미확인**(§3) | [`f2c_anal.txt`](../debug_log/2026-10-07/outputs/f2c_anal.txt) |
| 10-07 §3.5 · §5 | W3 통로 저속 떨림(러너 t 188~236) | ω 부호 6 s 에 21~34 회 · v 0.035 m/s, t 235 'Exception in transformPose … extrapolation' → 재계획 뒤 매끄러움. §5: map→odom stamp 1.49 s 멈춤 | 떨림의 TF 가설 기각, t 235 중단은 TF(→ §6 `transform_tolerance` 0.5). 떨림 원인 미확정 — 이 카드 밖([SLAM map→odom 시각 정체](slam-stamp-freeze.md) 와 같은 계열) | [`f2c2_w3cost.txt`](../debug_log/2026-10-07/outputs/f2c2_w3cost.txt) · [`f2c2_w3ahead.txt`](../debug_log/2026-10-07/outputs/f2c2_w3ahead.txt) · [`j914_w3log.txt`](../debug_log/2026-10-07/outputs/j914_w3log.txt) · [`j917_tflag.txt`](../debug_log/2026-10-07/outputs/j917_tflag.txt) · [`f2c2_w3lat.txt`](../debug_log/2026-10-07/outputs/f2c2_w3lat.txt) |
| 10-07 §6 · §6.1 | 재주행 준비: ① G4 휠 잔차 ② MPPI `transform_tolerance` 0.2 → 0.5. **남서 목표 자세 · 상자 여유는 손대지 않음**(같은 코스 비교) | prep 원점 1.62 cm, 실행 중 값 v_ref wheel · `FollowPathMPPI.transform_tolerance` 0.5(RPP `FollowPath` 0.2 는 안 쓰임 — 첫 확인에서 잘못 읽음) | BT RateController 는 첫 틱 · 목표 변경 · 주행 실패 때만 재계획(주석 확인) | [`j918_prep.txt`](../debug_log/2026-10-07/outputs/j918_prep.txt) · [`job919_chk.sh`](../debug_log/2026-10-07/jobs/job919_chk.sh) · [`job920_chk.sh`](../debug_log/2026-10-07/jobs/job920_chk.sh) · bag `bag_f2d1.tgz` `params.txt`(`FollowPathMPPI.transform_tolerance: 0.5`) |
| 10-07 §6.2 | f2d1(같은 10 목표, `git_head_pc 5fabfd7`) | 1~3 SUCCEEDED 51.2 / 52.9 / 28.3 s, **목표 4 남서(−108°) CANCELED 69.4 s, 도착 (−1.483, −5.341, +0.5°) 0.197 m · 108.7°** — f2c1 과 거의 같은 자리 · 방향 | **3/3 재현**(f2b3 목표 6 · f2c1 · f2d1), 바꾼 G4 · tolerance 와 무관. 사용자: "방향을 크게 바꾸라는 명령 제거 및 비슷한 상황의 해결책 찾기. 일단은 현재 단계에서 주행 시작." 취소 주체 nav_guard 는 SUMMARY 서술 — 이 목표의 nav2 로그 발췌는 **원천 소실**(러너 한도 81 s 전이라 러너 취소는 아님) | [`f0_f2d1_runner.log`](../debug_log/2026-10-07/outputs/f0_f2d1_runner.log) · bag `bag_f2d1.tgz` |
| 10-07 §7 선언 | 러너 yaw 모드 `f` 추가: 경로 끝 방향으로 보내되 map 위치 ≤ 0.15 m(= `xy_goal_tolerance`)면 러너가 취소 → SUCCEEDED_XY. f2d2 = 목표 5~10, 남서(6 번째)만 `f` | 첫 시도 G2 불합격 0.066 m(라이다 0.083 m @ 차체 (−0.33, +0.12)) → 사용자 "뒤 왼쪽 부딪힐 것 아무것도 없다" → `G2_SKIP=1` | 일반 해결책 후보(다음): `f` 일반 규칙화 · 목표점을 벽에서 띄우기 · 정체 감지 시 방향 목표 해제. 판단 근거는 'f2c1 · f2d1 bag 분석 뒤' 로 미룸 | [`job550_f0run.py`](../debug_log/2026-10-07/jobs/job550_f0run.py) 134~135 행 · [`run_f2c.sh`](../debug_log/2026-10-07/jobs/run_f2c.sh) `REST5F` · [`f0_f2d2_runner.log`](../debug_log/2026-10-07/outputs/f0_f2d2_runner.log) 1~9 행 |
| 10-07 §7.1 | f2d2(`git_head_pc 0bbd832`) | 5/6: **남서 '위치 도달(0.148 m ≤ 0.15)' → SUCCEEDED_XY 59.6 s, 도착 (−1.457, −5.541, 133.4°)**. 목표 10(출발) 상자 앞 정지 → nav_guard 취소 123.2 s | `f` 모드 작동(1 회). 목표 10 은 상자 ②(실제 낮은 상자, 사용자 확인) 앞 — 이 카드 밖 | [`f0_f2d2_runner.log`](../debug_log/2026-10-07/outputs/f0_f2d2_runner.log) · [`j921_f2d2_g10.txt`](../debug_log/2026-10-07/outputs/j921_f2d2_g10.txt) · 그림 [`2026-10-07_f2d2_box_stop.png`](../04_navigation/figures/2026-10-07_f2d2_box_stop.png) |
| 10-07 §7.2 | '재계획 때 돌아갈 길이 있었나' — 전역 코스트맵 단면(x 1.0~1.6) | +380 s 재계획 시점: 가운데 99(상자 ②) · 남쪽 y −0.35~−0.25 비용 80~88 · **북쪽 y +0.30~+0.40 비용 70~80** — 계획기는 남쪽을 고름. +399 s 상자 ② 가 전역에서 사라짐 | 해결 과제 ⓐ 낮은 물체 기억 ⓑ 넓은 우회로 선호 ⓒ **남서 같은 방향 맞춤 정체는 `f` 기본화 또는 정체 감지 시 방향 목표 해제** | 단면 계산 스크립트 · 출력 **원천 소실**(입력 `x921_f2d2.npz` 도 PC 스크래치패드에서 소실 — bag `bag_f2d2.tgz` + [`job912_extract.py`](../debug_log/2026-10-07/jobs/job912_extract.py) 로 재생성 가능) |
| 10-08 §3 · §3.1 | 전역 nvblox A/B 선언에 '남서 두 번 모두 위치만(f)'(`run_f2c.sh … fullf`) | 사용자가 코스를 '1 · 9 · 10 번만'(B → W3 → 출발)으로 줄임 | 남서는 10-08 에 **시험 안 됨** | [10-08 SUMMARY §3](../debug_log/2026-10-08/SUMMARY.md) · [`2026-10-08/jobs/run_f2c.sh`](../debug_log/2026-10-08/jobs/run_f2c.sh) 10 행 |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 벽 · 물체에 물리 접촉해 못 움직임 | 라이다 최근접(차체 외곽 기준) | 정체 내내 뒤 12.2~12.5 cm(`j910` +45~+79 s) | **기각**(라이다 기준). 라이다 아래 낮은 물체는 못 봄 |
| 10-02 f2b3 와 같은 '회전 중 odom 벽 번짐' 만의 문제 | 다른 목표 방향(−109°) · rf2o 켬 · B − A | f2c1 · f2d1 도 정체, 남서 구간 B − A 2.3~3.2 cm | **그것만은 아님**(10-07 §2.2 추정과 같음) |
| G4 · `transform_tolerance` 와 관련 | f2d1 에서 둘을 바꾸고 같은 코스 | 같은 자리 · 같은 방향(+0.5°)으로 정체 | **기각** |
| 뒤 4.5 cm 치명 칸 + 5 cm 격자 풋프린트 판정 때문에 MPPI 가 −109° 회전을 못 고름(10-07 §2.3) | 직접 판별 없음(MPPI 후보 · 비용은 bag 에 없음 — `bag_topics` 에 `/trajectories` 없음) | 회전 방향이 −109° 쪽(시계)이 아니라 **반대(반시계, 0° 쪽)** — 같은 표본 +39~+44 s | **미확인 · 정황상 약함**. −109° 를 요구받았다면 시계로 약 20° 만 돌면 될 것을 반시계로 91°(−88° → +3°) 돈 것이 설명 안 됨 |
| 컨트롤러가 받은 목표 방향이 러너가 보낸 방향과 다름 | ① Nav2 'SUCCEEDED' 는 `SimpleGoalChecker`(stateful, `yaw_goal_tolerance` 0.35 rad = 20.05°)가 **컨트롤러 목표 방향** 기준 20° 안일 때만 — 실행 중 값 `params.txt`(bag_f2c1 · f2d1) ② 같은 날 SUCCEEDED 인데 러너 방향 차가 20° 를 넘은 목표 | f2c2 목표 6(남서, 보낸 149°) 도착 18.8° · −129.8° / f2d2 목표 3(서쪽 통로, 보낸 82°) 도착 19.2° · −62.9° — 둘 다 SUCCEEDED. 10-02 f2b3 목표 3(남서, 보낸 −107°)도 SUCCEEDED · 도착 −18.0° · 89.4°([`f0_f2b3_runner.log`](../debug_log/2026-10-02/outputs/f0_f2b3_runner.log) 18~19 행) — 러너는 경로 끝 방향으로 바꾼 **뒤의** 값으로 차를 출력(10-01 판도 같음, `job550` `gyaw = path_end_yaw(...)` 가 출력보다 앞) | **지지(설정 + 러너 로그)** — 적어도 이 세 목표에서 컨트롤러 목표 방향 ≠ 보낸 방향 |
| 그 방향은 BT 스무딩 실패 → `TruncatePath` 가 덮어쓴 끝 방향 0°(커밋 `64aa041` BT 80~85 행 `TODO(improve)` 원문) | ① 목표 시작 직후 스무더 실패 로그 ② 회전 방향 · 멈춘 방향 ③ SUCCEEDED 도착 방향 | ① f2b3 13:25:08 · f2c1 11:00:57 '스무딩 충돌'(f2d1 · f2c2 목표 6 · f2d2 목표 3 은 로그 원천 소실) ② f2b3 113° → 54° 시계(0° 쪽, 10-02 §6.4) · f2c1 −88° → +3° 반시계(0° 쪽) · 멈춘 방향 f2c1 −0.3° · f2d1 +0.5° ③ 18.8° · 19.2° · −18.0° = 0° 기준 허용 20.05° 안(같은 남서 자리에서 f2b3 목표 3 은 성공, 목표 6 은 실패 — 0° 로 돌 공간이 접근 방향에 따라 달랐을 것, 추정) | **지지(정황)** — 컨트롤러가 받은 경로(`/transformed_global_plan`)가 bag 에 없어 직접은 못 봄. 같은 추론을 10-14 §16 이 f2c1 에 대해 함(→ '이후'). 재계획이 목표당 1 회(RateController 0.01 Hz)라 첫 스무딩 실패 경로가 목표 내내 쓰였다는 것은 BT 구조로 맞음 |
| 남서 접근 중 map→odom 한 번 보정(8.1 · 14.4 cm)이 odom 좌표 목표를 옮겨 마지막 1.5 cm 를 못 들어감 | 보정 시각 vs 정체 시작 | 보정 ≈ 11:01:17 · ≈ 11:01:27(bag 시작 10:58:16 + 181 · 191 s), 정체 시작 11:01:35(+45 s) | **미확인** — '5 cm 넘는 보정' 은 변환의 병진 변화라 로버 위치 변화와 같지 않음(원점에서 5.6 m 떨어진 곳에선 yaw 1° 보정만으로 ≈ 10 cm — 정의상 계산) |
| '위치만(f)' 이 남서 정체를 피한다 | f2d2 | 0.148 m 에서 취소 · SUCCEEDED_XY 59.6 s | **지지(1 회)**. 단 f2c1(0.165) · f2d1(0.197)은 끝내 0.15 m 안에 못 들어왔으므로 그 주행에 `f` 가 있었어도 안 끝났을 수 있음 — 그때 0.15 m 안을 지났는지는 러너 csv 가 PC 스크래치패드에서 소실돼 **미확인** |

## 4. 조치와 효과
- **러너 `f` 모드**(10-07 §7, 커밋 `0bbd8326`) — [`2026-10-07/jobs/job550_f0run.py`](../debug_log/2026-10-07/jobs/job550_f0run.py) 34 · 134~135 행:
  ```python
  XY_DONE = 0.15   # 'f' 목표의 위치 도달 판정(m) = nav2 xy_goal_tolerance
  ...
                      if free and math.hypot(M[0] - gx, M[1] - gy) <= XY_DONE:
                          gh.cancel_goal_async(); xy_done = True; print('  목표 %d 위치 도달(%.3f m ≤ %.2f) — 방향 맞춤 없이 끝냄' % ...
  ```
  10 Hz 루프에서 TF map→base_link 위치를 보고, 0.15 m 안이면 NavigateToPose 를 취소하고 결과 이름을 SUCCEEDED_XY 로 바꾼다(취소 응답을 5 s 까지 기다린 뒤 다음 목표). 보내는 방향은 `p` 와 같은 경로 끝 0.3 m 방향 — 즉 Nav2 의 '위치 통과 뒤 방향만 맞추는' 단계(stateful)를 러너가 잘라 낸다.
  - 효과: f2d2 남서 — [`f0_f2d2_runner.log`](../debug_log/2026-10-07/outputs/f0_f2d2_runner.log):
    ```
      목표 2 위치 도달(0.148 m ≤ 0.15) — 방향 맞춤 없이 끝냄
      목표 2 SUCCEEDED_XY 59.6 s | 도착 map (-1.457, -5.541, 133.4°) 목표 대비 0.148 m, -19.3°
    ```
  - 한계: ① 원인을 고치지 않음(§3) ② 0.15 m 경계 2 mm 차로 끝난 1 회 ③ 위치 접근 자체에서 멈추면(f2c1 0.165 m) 효과 없음 ④ 러너(PC → Jetson)에만 있어 Nav2 를 직접 쓰는 다른 경로엔 없음 — 이후 F2.5 `place_server` 에 같은 규칙이 들어감(지금 코드, 아래).
- 같은 날 바꿨지만 남서와 무관했던 것: G4 휠 잔차(→ [rf2o 도입](rf2o-introduction.md)) · `FollowPathMPPI.transform_tolerance` 0.5(§5 TF 중단 대책).
- **지금 코드 확인(11-02)**:
  - `places.yaml` 46 행 남서 `yaw_mode: f`, 47 행 `min_clear: 0.0`(주석: 10-28 §7 등록 좌표에 차체를 놓으면 벽 칸에 닿음, f2tf1 · f2tt1 · f2tt2 반복 도착).
  - `place_server.py` 15 행(모드 설명) · 56 행(파라미터 `xy_done` 0.15) · 214 행(`f` 면 목표 여유 부족 때 방향을 고쳐 보내는 단계를 건너뜀) · 250~256 행 `tick`(`f` 목표면 xy < 0.15 에서 `cancel_goal_async` → arrived) — 러너 `f`(≤ 0.15)와 같은 규칙. 207 행은 '이미 그 자리' 검사로 별개.
  - 러너 `f` 는 저장소 상시 도구에 없음 — 마지막 사본 [`2026-10-21/jobs/job550_f0run.py`](../debug_log/2026-10-21/jobs/job550_f0run.py) 34 · 165~166 행(실행본은 PC 스크래치패드, `Docs/tools/README.md` 54 행).
  - BT: [`nav_to_pose_no_spin.xml`](../../ros2_ws/src/rover_navigation/config/nav_to_pose_no_spin.xml) 85 행 `CopyPath`(10-14, `TruncatePath` 대체 — 80 행 주석에 옛 TODO 원문). 10-07 판(커밋 `64aa041`) 85 행은 `<TruncatePath input_path="{raw_path}" output_path="{path}" distance="0.0"/>`.
  - [`nav2_params.yaml`](../../ros2_ws/src/rover_navigation/config/nav2_params.yaml) 101~115 행 goal checker(stateful · xy 0.15 · yaw 0.35 — 10-07 과 같음), 92~99 행 진행 검사기(PoseProgressChecker 0.25 m · 0.5 rad · 25 s — 같음), 260~261 행 GoalCritic(10, 1.0 m) · GoalAngleCritic(3, 0.4 m) — 같음, 264 행 PreferForwardCritic **15**(10-07 은 5 — 10-08 §6 변경), 255 행 크리틱 목록에 ClearanceBandCritic 추가됨(10-07 엔 없음).

## 5. 내 실수 · 기록 어긋남
1. **CRLF 로 출발 중단**(10-07 §2.2 ①) — 하려 한 것: `run_f2c.sh` 를 python 으로 고쳐 저장 · 본 것: 경로 끝 `\r` 로 "No such file" · 결론: 로버 안 움직임 · 다음에 알아보는 법: WSL 로 보내는 래퍼는 `tr -d '\r'`(`run_f0.sh` 가 보조 파일엔 이미 함) · 데이터: 출력 원문 없음(SUMMARY 서술뿐).
2. **러너 출력 지연을 '결과 없음' 으로 오독**(§2.4 정정) — 본 것: `j911_navtail_1112.txt` 첫 줄 11:12:27 · `tail -4` 에 목표 5 결과 없음 · 처음 추론: D 4 분째 · 7.26 m 는 먼 우회로 · 의심한 이유: 주행 뒤 러너 로그 · 판별: [`f0_f2c2_runner.log`](../debug_log/2026-10-07/outputs/f0_f2c2_runner.log) '목표 1 SUCCEEDED 41.3 s' · nav_guard '목표 ed69588c: 남은 거리 7.26 m → 시간 한도 237 s'([`j914_w3log.txt`](../debug_log/2026-10-07/outputs/j914_w3log.txt) 45 행 = W3 목표 시작) · 다음에 알아보는 법: PC 쪽 러너 출력은 2 s 폴링 · 회수 전이라 늦다 — Jetson `/tmp/f0_<이름>.log` 를 직접 tail.
3. **코스트맵 척도**(§2.3) — 첫 계산이 OccupancyGrid(0~100) 를 0~255 로 봐 치명 칸 0 → 정정. 흔적: [`job910_g4cost.py`](../debug_log/2026-10-07/jobs/job910_g4cost.py) 31 행 주석 '첫 판은 253 으로 잘못 셈'. 첫 판 출력은 **원천 소실**. 다음에 알아보는 법: `nav_msgs/OccupancyGrid` 코스트맵은 100 = 치명(254) · 99 = 내접(253) · −1 = 미지. ⚠ 같은 파일 머리 주석은 아직 '치명(≥253)' 이라 적혀 있음(코드는 맞음).
4. **'위치는 0.165 m 안'**(§2.2) — Nav2 `xy_goal_tolerance` 0.15 를 1.5 cm 넘은 값이다. '위치는 됐고 방향만 못 맞춤' 이라는 읽기는 이 숫자로 지지되지 않는다(f2d1 0.197 도 같음). 다음에 알아보는 법: 러너 '목표 대비' 거리를 허용값과 먼저 비교.
5. **'성공 판정은 위치만'**(§2.5 f2c2 목표 6) — 실행 중 `general_goal_checker.yaw_goal_tolerance: 0.35`(bag `params.txt`)와 모순. 처음 추론: 방향 차 130° 인데 SUCCEEDED 니 방향을 안 본다 · 의심한 이유(11-02): 설정은 방향을 본다 · 결론: 컨트롤러 목표 방향이 149° 가 아니었다(§3) · 다음에 알아보는 법: 'SUCCEEDED 인데 러너 방향 차 > 20°' 는 BT 가 경로 끝 방향을 바꾼 서명.
6. **'−109° 로 못 돈다' 해석**(§2.3) — 같은 출력에 회전이 반대쪽(0° 쪽)이었다는 값이 있었는데 '미확인' 으로만 두고 해석을 유지했다. 판별 시험은 10-07 에 없음(10-14 §16 재해석 → '이후'). 다음에 알아보는 법: 정체 직전 회전 방향이 목표 방향과 반대면 '컨트롤러가 받은 목표' 부터 확인(`/transformed_global_plan` 기록, 지금은 `LONG_REC` 때만).
7. **§2.4 제목의 출발 자세는 odom 좌표** — (−1.22, −5.55, +3°) 는 `j910` 의 odom 값, 러너 map 은 (−1.476, −5.392, −0.4°)([`f0_f2c2_runner.log`](../debug_log/2026-10-07/outputs/f0_f2c2_runner.log) 11 행). 좌표계 표시 누락.
8. **목표 이름 'W3' 이중 사용** — 10-07 §2 · §2.2 표의 '2 W3' 는 (−1.6, −2.0)(10-01 §8.1 · `places.yaml` 의 C). 10-02 §6 코스 줄의 'W3 (−1.6, −2.0)' 를 이어 쓴 것. 진짜 W3 = (5.5, −2.2). 이 카드는 좌표로 적음.
9. 경미: §2.3 '+39~+44 s 돌며 후진(v −0.03)' — 표본상 +39~+41 은 전진(v +0.010~+0.075)하며 돌고 +42~+44 후진. '뒤왼쪽 4.5 cm' — 도구 표기는 '뒤'(차체 y +0.14 < 반폭 0.165).
10. §2.1 '`up904.sh` 호스트 인자화' — 저장 사본 [`up904.sh`](../debug_log/2026-10-07/jobs/up904.sh) 는 `192.168.0.101` 하드코딩(인자화 전 판이 남았거나 서술이 틀림 — 미확인).
11. 저장된 [`run_f2c.sh`](../debug_log/2026-10-07/jobs/run_f2c.sh) 는 하루 끝 판(커밋 `e3e1fe88` — `LONG_REC` 기본 1 · `REST5F`). f2c1 · f2c2 · f2d1 때 판은 커밋돼 있지 않다(첫 커밋 `0cd25aa1` 의 판은 `git show` 로 볼 수 있음). bag `bag_topics` 에 `/trajectories` 가 없는 것이 그때 `LONG_REC` 가 없었다는 증거.

## 6. 남은 것 (10-08 시점 — 7 기 결과는 §7)
- 원인 확정 안 됨: 컨트롤러 목표 방향을 직접 본 기록이 없다(§3). 확인 방법 = 같은 남서 목표를 `/transformed_global_plan` 기록과 함께 `p` 로.
- 일반 해결책(§7 · §7.2 ⓒ) 미결정 — `f` 는 러너 한 곳의 우회.
- 남서 접근 중 map→odom 보정 2 회(8.1 · 14.4 cm)의 의미 · f2c1 · f2d1 이 0.15 m 안을 지났는지 — 미확인.
- 목표 좌표 자체가 벽에 가까움(10-02 §7.1 (B) '경유점 (−1.35, −5.55)' 제안) — 시험 안 함.

## 7. 7 기 (10-12 ~ 10-15) — BT 끝 방향 0° 결함으로 다시 읽기
10-14 에 서쪽 통로(f2s1)에서 같은 모양의 정지가 나와 직접 측정으로 원인을 찾았고([BT 끝 방향 0° 결함 · CopyPath](bt-copypath-end-yaw.md)), 남서 정체를 그 관점으로 다시 봤다.

| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-14 §13.1 | f2s1 서쪽 통로 목표 3 정지 분석 | 스무딩이 목표 자세에서 매번 실패, 컨트롤러 끝 방향 odom +4.5~+5.2°(지도 +0.0°) vs 계획기 −56.2° | `TruncatePath` 가 끝 방향 0° 로 덮음(측정). '10-02 · 10-07 남서 구석 정체도 같은 원인이었을 수 있다(그때 로그를 이 관점으로 다시 보지는 않았다)' | [`2026-10-14/outputs/navlog_f2s1.txt`](../debug_log/2026-10-14/outputs/navlog_f2s1.txt) · bag `2026-10-14/bags/bag_f2s1.tgz` |
| 10-14 §13.3 | f2s2 이어 가기 — 남서 `f` 포함, 아직 TruncatePath | 남서 **Nav2 SUCCEEDED 36.7 s** · 도착 (−1.499, −5.374, **−1.6°**) · 목표 대비 0.161 m · 99.8°(보낸 방향 −101°) | SUMMARY 는 '남서 SUCCEEDED 36.7 s' 만 적음. 이 카드(11-03): 러너 `f` 취소(≤ 0.15 m)가 아니라 Nav2 자체 성공 — 방향 차 99.8° 로 성공 = 컨트롤러 목표 방향이 −101° 가 아니었다는 서명(§3 의 f2c2 · f2d2 와 같은 모양) | [`2026-10-14/outputs/run_f2s2.txt`](../debug_log/2026-10-14/outputs/run_f2s2.txt) 14~15 행 |
| 10-14 §16 | 10-07 f2c1 재확인(주행 없음, §15 권고 2) | bag 에 `/transformed_global_plan` 없음 → `anal_path_endyaw.py` 실패. Nav2 로그: 목표 시작 직후 스무딩 실패 1 회(재계획 목표당 1 회 시절 — 그 경로가 목표 내내). 멈춘 방향 −0.3° · 0.165 m | '같은 결함일 가능성 높음(추정, 측정과 맞음)' — 10-07 '−109° 로 못 돎' 해석은 재검토. 10-02 f2b3 은 bag 이 PC 에 없어 미확인. 남서도 p 로 되돌려 볼 수 있다(제안) | [`2026-10-07/outputs/j908_g4log.txt`](../debug_log/2026-10-07/outputs/j908_g4log.txt) · [`f0_f2c1_runner.log`](../debug_log/2026-10-07/outputs/f0_f2c1_runner.log) |
| 10-14 §17 | f2t1(CopyPath 뒤) — 남서 `f` | 남서 SUCCEEDED_XY 65.0 s(러너 0.143 m 취소) · 도착 −110.6°(보낸 −108°). 출발 직후 갇힘 → pad_relief 첫 작동(서쪽 통로 남쪽 출구 — 남서 구석 자체가 아님) | CopyPath 검증 통과(서쪽 통로). 남서는 여전히 `f` | [`2026-10-14/outputs/run_f2t1.txt`](../debug_log/2026-10-14/outputs/run_f2t1.txt) · [`navlog_f2t1.txt`](../debug_log/2026-10-14/outputs/navlog_f2t1.txt) |
| 10-15 §15 · §29.6 | f2v2 · f2w2(같은 BT) — 남서 `f` | f2v2 **Nav2 SUCCEEDED 28.8 s** · −106.6°(보낸 −107°, 차 0.6°) · f2w2 SUCCEEDED_XY 28.8 s · −108.9°(보낸 −109°). f2v1 · f2v3 은 남서 전에 서쪽 통로 남쪽에서 중단(다른 기전 — [F2 기준선](f2-baseline-no5.md)) | 남서 정체 재발 0(2/2 도착). 도착 방향 = 보낸 방향 | [`2026-10-15/outputs/run_f2v2.txt`](../debug_log/2026-10-15/outputs/run_f2v2.txt) · [`run_f2w2.txt`](../debug_log/2026-10-15/outputs/run_f2w2.txt) |

### 7.1 직접 증거 — 남서 목표에서 컨트롤러가 받은 끝 방향(11-03 재실행)
10-14 bag 은 `LONG_REC=1` 이라 `/transformed_global_plan` 이 있다. 10-14 에 쓰인 [`anal_path_endyaw.py`](../debug_log/2026-10-14/jobs/anal_path_endyaw.py) 를 같은 bag 의 **남서 구간**에 다시 돌렸다(그날은 서쪽 통로 구간만 봄). 결과 원문 파일 없음 — 발췌가 전부.
```python
# anal_path_endyaw.py — 4 s 마다: /plan 끝 방향 · /transformed_global_plan 끝 방향(odom 값 + map→odom yaw) · 차이 · 로버 방향 · 로버→목표
cyaw = q[3] + m[3]
```
```
f2s2 목표 1 남서(TruncatePath, 10-14 13:54)      계획기   컨트롤러(지도로)   차이     로버     로버→목표
13:54:26                                       -101.3°   +0.0°           +101.3°   -62.4°   0.94 m
13:54:34                                       -101.3°   +0.0°           +101.3°   -82.5°   0.44 m
13:54:38                                       -101.3°   +0.0°           +101.3°   -86.5°   0.26 m
f2t1 목표 4 남서(CopyPath, 10-14 15:24)
15:24:06                                       -107.8°   -0.0°           +107.8°   -74.6°   0.95 m   ← 창 밖: 끝 = 중간 점
15:24:10                                       -107.8°  -107.8°            -0.0°   -77.9°   0.87 m
15:24:22                                       -107.8°  -107.8°            +0.0°   -87.5°   0.43 m
```
- 읽기(측정): TruncatePath 시절엔 목표가 컨트롤러 창 안(0.26~0.94 m)에 들어온 뒤에도 끝 방향이 0° 였다 → 남서 목표에서도 컨트롤러는 0° 를 목표 방향으로 받았다. f2s2 에서 로버가 0° 쪽(−1.6°)으로 서서 Nav2 가 'SUCCEEDED'(0° 기준 20° 안)를 낸 것과 맞다. CopyPath 뒤엔 창 안에서 끝 = 목표 방향.
- 10-07 f2c1 · f2d1 · f2c2 와 10-02 f2b3 의 컨트롤러 끝 방향은 기록이 없어 **여전히 직접 증거 없음** — 다만 같은 BT · 같은 남서 목표 · 같은 '0° 쪽으로 돌아 섬 / 큰 방향 차로 SUCCEEDED' 서명이라, §3 의 '그 방향은 TruncatePath 의 0°' 는 **정황 → 같은 자리 직접 측정 1 건으로 강화**(10-07 당일 값은 미측정).
- 남는 물음(§3 마지막 줄 · §6): 0° 로 돌 공간이 있으면 SUCCEEDED(f2b3 목표 3 · f2c2 · f2s2), 없으면 정체(f2b3 목표 6 · f2c1 · f2d1) — 접근 방향에 따라 갈렸다는 것은 추정 그대로.

### 7.2 '위치만(f)' 모드가 아직 필요한가 — 열린 항목
- 지금: [`places.yaml`](../../ros2_ws/src/rover_navigation/config/places.yaml) 46 행 남서 `yaw_mode: f` · 47 행 `min_clear: 0.0`, [`place_server.py`](../../ros2_ws/src/rover_navigation/scripts/place_server.py) 206~214 · 251~254 행(`f` 면 xy < `xy_done` 0.15 에서 취소 → arrived_xy), 러너 `no5` 문자열의 남서 `f`([`2026-10-15/jobs/run_f2c.sh`](../debug_log/2026-10-15/jobs/run_f2c.sh) 8 행).
- `f` 를 만든 이유(방향 0° 요구)는 10-14 CopyPath 로 사라졌다. 고친 뒤 남서는 3/3 도착(f2t1 · f2v2 · f2w2)했지만 **세 번 모두 `f` 였다** — `p` 로 되돌린 시험(10-14 §16 제안)은 10-15 까지 없다. f2v2 는 Nav2 가 스스로 방향까지 맞춰 성공(0.6°)했으므로 `p` 로도 될 가능성이 있다(1 회, 추정).
- `f` 를 없애면 생길 수 있는 것(추정): 남서 구석은 등록 좌표에서 차체가 벽 칸에 닿는 자리(`places.yaml` 47 행 주석 '여유 0.000 m') — 방향을 맞추려 제자리 회전하면 칸 검사에 걸릴 수 있다. 즉 `f` 의 지금 이유는 'BT 결함' 이 아니라 '좁은 구석에서의 불필요한 방향 맞춤 회피' 로 바뀌었다. 결정은 `p` 시험 뒤(사용자).
- 이후(10-19 ~): 다음 시기에서 채움 — 10-28 F2.5 `places.yaml` 남서 `f` · `min_clear 0.0`(f2tf1 · f2tt1 · f2tt2 도착 xy 0.18~0.23 m).

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2c1 | 10-07 rf2o 켠 순회 1~4, 남서 CANCELED 71.2 s | `outputs/f0_f2c1_runner.log` · `j908_g4log.txt` · `j910_g4cost.txt` · bag `2026-10-07/bags/bag_f2c1.tgz` |
| f2c2 | 목표 5~10, 남서(149°) SUCCEEDED · 방향 차 130° | `outputs/f0_f2c2_runner.log` · `j911_navtail_1112.txt` · `j914_w3log.txt` · `f2c_anal.txt` · bag `bag_f2c2.tgz` |
| f2d1 | G4 잔차 · tol 0.5, 남서 CANCELED 69.4 s | `outputs/f0_f2d1_runner.log` · bag `bag_f2d1.tgz`(nav2 로그 원천 소실) |
| f2d2 | 남서 `f` → SUCCEEDED_XY 59.6 s · 상자 앞 정지 | `outputs/f0_f2d2_runner.log` · `j921_f2d2_g10.txt` · bag `bag_f2d2.tgz` |
| `job908_g4log.sh` · `job909_cmdnow.sh` · `job910_g4cost.py` · `job910_run.sh` · `job911_navtail.sh` | 남서 정체 분석 | `2026-10-07/jobs/` |
| `job550_f0run.py` · `job551_f0drive.sh` · `run_f2c.sh` · `run_f0.sh` · `job613_pathyaw.py`(09-28) | 러너 | `2026-10-07/jobs/` · `2026-09-28/jobs/` |
| `job906_net.sh` · `up904.sh` · `job903_prep_rf2o_g4.sh` · `job907_postchk.sh` · `job918_prep.sh` · `job919/920_chk.sh` | 네트워크 · prep · 확인 | `2026-10-07/jobs/` |
| f2s2 · f2t1(10-14) · f2v2 · f2w2(10-15) | 7 기 남서 도착 — 고치기 전 1 · 고친 뒤 3 | `2026-10-14/outputs/run_f2s2.txt` · `run_f2t1.txt` · `2026-10-15/outputs/run_f2v2.txt` · `run_f2w2.txt` · bag `2026-10-14/bags/bag_f2s2.tgz` · `bag_f2t1.tgz` |
| `anal_path_endyaw.py`(10-14) | 계획기 끝 vs 컨트롤러 끝 방향 — 11-03 남서 구간 재실행(§7.1) | `2026-10-14/jobs/` · 해설 [BT 끝 방향 카드 §9](bt-copypath-end-yaw.md) |
| `job913_extract.py` · `f2c_anal.py` · `job921_run.sh` · `job912_extract.py` · `render_f2d2_box2.py` | 보정량 · f2d2 추출 · 그림 | `2026-10-07/jobs/` |

## 9. 도구 해설
공통: Jetson 쪽은 PC(WSL)에서 `sshpass -p <PW> ssh jetson@<주소>`(이날 172.30.1.8 — §2.1)로 스크래치패드 → `/tmp` 로 올려 실행. 분석용 npz(`x913_*` · `x921_*`)와 러너 csv 는 PC 스크래치패드에만 있었고 **지금 소실**(같은 세션 폴더에 `run_f2c.sh` 만 남음, 11-02 확인) — 출력 txt 와 bag 만 남았다. 이날은 `TOOLS.md` 규약 전(10-12 결정).

### job550_f0run.py — F0/F2 러너 (Jetson, Python rclpy) · 이날 판의 차이
- 해설 본체는 [제자리 회전 옆 밀림 F0-a §9](f0-rotation-side-slip.md) · [F2 순회와 위치 점프 §9](f2-patrol-loc-jump.md). 부른 형태: `run_f2c.sh NAME NOTE GIT_HEAD [rest5|rest5f]` → `run_f0.sh NAME "$G" 0.07` → Jetson `job551_f0drive.sh` → `python3 job550_f0run.py NAME GOALS 0.07`.
- 목표 방향 `p`: 보내기 직전 별도 프로세스 `job613_pathyaw.py` 가 `compute_path_to_pose`(GridBased, `use_start False`)로 **원경로**를 받아, 마지막 점에서 0.30 m 이상 떨어진 첫 점 → 끝점 방향을 목표 yaw 로(실패면 직선 방향). ⚠ 이 경로는 스무딩 전 원경로라, BT 안에서 스무딩이 실패해 `TruncatePath` 가 끝 방향을 바꿔도 러너는 모른다 — 러너가 출력하는 '목표 대비 °' 는 **러너가 보낸 방향 기준**(141 행).
- 한도: `lim = 직선 거리 / 0.07 × 2 + 30`(108 행) — 남서 목표 81 s. f2c1 은 71.2 s 에 nav_guard 가 먼저 취소.
- `f` 모드(10-07 §7 추가): §4 발췌. `GOALS` 에서 yaw 자리에 'f' 면 `(from_path=True, free=True)`(103 행). 10-07 저장본은 `f` 추가 뒤 판이고, f2c1 · f2c2 · f2d1 은 그 전 판(Jetson `/tmp`, 커밋 없음 — 10-02 판과 같음).
- 출력: 화면(→ `/tmp/f0_<이름>.log` → PC 회수 → `outputs/f0_<이름>_runner.log`), csv `/tmp/<이름>.csv`(10 Hz, **outputs 에 없음**).
- 지금: 상시 도구 아님(최신 사본 10-21 jobs).

### job551_f0drive.sh — 게이트 · 녹화 래퍼 (Jetson, bash) · 이날 차이
- 10-02 판 대비([`2026-10-07/jobs/job551_f0drive.sh`](../debug_log/2026-10-07/jobs/job551_f0drive.sh) diff): ① 게이트 A — `ekf_node` 허용 수 = 1 + `__node:=ekf_shadow_a` 프로세스 수(9~10 행) ② 녹화 토픽에 `EXTRA_TOPICS`(이날 `/odometry/ekf_a /odom_rf2o /odom_rf2o/gated`) ③ `LONG_REC=1` 이면 `/trajectories /transformed_global_plan`(§11 추가 — 이 카드의 주행엔 없었음).
- G2(출발 자세 여유 ≥ 0.10 m, 23~24 행) · P(정지 10 s CPU ≤ 60 %, 30 행)는 10-02 와 같음. f2d1 의 '라이다 점 ↔ 차체 외곽 최소 9.900 m'(가까운 라이다 점이 하나도 안 잡힌 기본값으로 보임)인데 G2 0.133 이 나온 것은 코스트맵 칸 쪽 값 — 그 순간 스캔을 못 받았는지는 미확인.

### run_f2c.sh — 목표 문자열 래퍼 (PC/WSL, bash)
- 인자 `NAME NOTE GIT_HEAD [rest5|rest5f]`. `FULL`(10 목표) · `REST5`(목표 5~10) · `REST5F`(남서만 f)를 파일 안에 두고 `LONG_REC` · `JETSON_HOST=172.30.1.8` · `BAG_PROFILE=nvblox` · `G2_SKIP` · `GOAL_FRAME=map` · `STAGE=F2c` · `EXTRA_TOPICS` 를 export. 10-08 판은 `FULLF` · `B910` 추가(10 행).
- 왜: 10-02 §6.2 의 wsl 인자 분리 실수 재발 방지(목표 문자열을 인자로 넘기지 않음).

### job908_g4log.sh — 목표 4 nav2 로그 발췌 (Jetson, Python 인라인)
- `/tmp/nav2.log` 의 `[epoch.ns]` 가 2026-10-07 11:00:30 이후이고 'Message Filter' 가 아닌 줄 중 정규식 `PathBlocked|nav_guard|Fail|Abort|Cancel|Received|Recovery|clear|BackUp|Wait|Goal|collision|Optimizer|Stuck` 에 맞는 줄을 'HH:MM:SS 내용(190 자)' 으로. 끝에 러너 로그의 nav_guard · stuck 줄과 `/tmp/*.log` 목록. 10-02 `job816_g5log.sh` 와 같은 본문(시각만 다름).
- 출력 [`j908_g4log.txt`](../debug_log/2026-10-07/outputs/j908_g4log.txt). 쓰인 곳 §2.2 경과 · §3 스무딩 실패 증거. 결함: 시각 하드코딩 · 'Received' 가 스무더 수신까지 잡아 줄이 많음. 같은 발췌를 f2d1 엔 안 남김(원천 소실의 원인).

### job909_cmdnow.sh — 지금 지령 확인 (Jetson, bash)
- `ros2 topic info /cmd_vel -v`(발행자) · `topic echo --once` · `topic hz` · nav2 로그 끝 8 줄 · 러너 프로세스. 정지 상태에서 DDS 참여자를 만드는 확인이라 주행 중엔 쓰지 않음(규칙 — [주행 직전 DDS 참여자 금지](pre-drive-dds-participants.md)).
- 출력: **원천 소실**(SUMMARY '11:03:40 /cmd_vel 메시지 없음' 만).

### job910_g4cost.py · job910_run.sh — 정체 구간 1 s 표본 (Jetson, Python rosbag2_py)
- 부른 형태: `job910_run.sh` 가 `/tmp/bag_f2c1`(없으면 tgz 를 `/tmp/x910` 에 풀어)로 `python3 job910_g4cost.py BAG 1791338450 1791338535`(11:00:50~11:02:15).
- 왜: 사용자 '움찔 — 충돌인지'.
- 하는 일: bag 을 순서대로 읽어 `/odometry/filtered`(EKF B) · `/odometry/ekf_a`(그림자 A) · `/cmd_vel` 은 모두 모으고 `/local_costmap/costmap` · `/scan` 은 최신 한 장만 보관 → 1 s 마다: ① 코스트맵 값 ≥ 99 칸 중심을 EKF B 자세로 차체 좌표로 ② `gap()` = 차체 외곽(x −0.248~+0.262, y ±0.165) 까지 거리(안이면 0) ③ 값 ≥ 100 = 치명, 99 = 내접 — 외곽 안 치명 · 내접 개수, 치명 최근접의 거리 · 방향(앞/뒤 · 왼/오, 외곽 안이면 '안') ④ 라이다: `ranges` 유한 · > 0.05 m 를 라이다 위치 x 0.152 · yaw π − 0.04677 로 차체 좌표 → 외곽 거리 최소 ⑤ 직전 1 s 지령 개수 · v · ω 범위 ⑥ B − A 위치 차(cm).
  ```python
  def gap(px, py):   # 차체 좌표 점 → 외곽까지 거리(안이면 0)
      dx = np.where(px > XF, px - XF, np.where(px < XB, XB - px, 0)); dy = np.maximum(np.abs(py) - HW, 0); return np.hypot(dx, dy)
  ...  leth = g[iy, ix] >= 100   # OccupancyGrid 0~100 척도: 100 = 치명(254), 99 = 내접(253) — 첫 판은 253 으로 잘못 셈
  ```
  (14~15 · 31 행)
- 출력 [`j910_g4cost.txt`](../debug_log/2026-10-07/outputs/j910_g4cost.txt)(81 줄 — 머리 1 줄 + 80 표본). 쓰인 곳 §2.3.
- 결함 · 한계: 자세가 odom(코스트맵과 같은 좌표)이라 map 좌표 목표와의 관계는 안 보임(실수 7 의 원인) · 내접 칸은 거리 대신 개수만 · 머리 주석 '치명(≥253)' 낡음 · 시각 창 epoch 하드코딩.
- 계보: 10-02 `job814_nearcells.py`(정지 한 장) → 이것(시계열) → 10-23 `Docs/tools/fig_drive_video.py`(영상).

### job911_navtail.sh — 주행 중 로그 엿보기 (Jetson, bash)
- `date` · `/tmp/f0_f2c2.log` 끝 4 줄 · nav2 로그에서 `PathBlocked|nav_guard|Fail|…|stuck` 끝 14 줄 · csv 끝 3 줄. **DDS 참여자를 만들지 않는** 확인(주행 중 허용).
- 출력 [`j911_navtail_1112.txt`](../debug_log/2026-10-07/outputs/j911_navtail_1112.txt). 쓰인 곳 §2.4(오독 — 실수 2).

### job906_net.sh — 연결 끊김 진단 (Jetson, bash)
- `uptime` · `nmcli` 활성 연결 · WEB_DEV/ALOPS 신호 · `ip -4 -br addr` · `/var/log/wifi_mon/` 최신 파일 끝 25 줄 · NetworkManager journal 에서 WEB_DEV · deauth · dhcp 실패 줄. 출력 **원천 소실**. 해설은 [Jetson Wi-Fi](jetson-wifi-link.md) 로.

### job913_extract.py · f2c_anal.py — 보정량 · 번짐 (Jetson → PC, Python)
- `job913_extract.py BAG OUT`: bag 전체에서 `/tf` 의 map→odom · odom→base_link, 그림자 A 자세, EKF B 속도, rf2o 원 · 게이트 출력(공분산 [0] · [7]), cmd_vel, `/plan` 점 수 → npz(`x913_*`, **원천 소실**).
- `f2c_anal.py`(PC): ③-c 회전(|ω| > 0.15) 표본의 게이트 통과 · σ 키움(공분산 > 0.03² × 1.5) · ③-b 제자리 회전 구간(|ω| > 0.15 · |v| < 0.03 이 1.5 s 넘게)마다 SLAM 이동(map→odom ∘ odom→base, 끝은 +2 s 보정 뒤) vs B · A 이동 · map→odom 병진 변화 합(회전 중 / 밖) · **한 번에 5 cm 넘는 변화**(연속 두 map→odom 사이 병진 차).
  ```python
  big = np.flatnonzero(dm > 0.05); print('  한 번에 5 cm 넘는 보정 %d 회: %s' % (len(big), ' '.join('%.0fs/%.1fcm' % (tm[i] - t[0], 100 * dm[i]) for i in big[:12])))
  ```
  (31 행) — ⚠ 앞 12 개만 출력(f2c2 15 회 중 3 회 미출력, 최대값 미상). `dm` 은 **변환의 병진 변화**라 로버 위치 변화와 다르다(yaw 보정이 원점에서 먼 곳에선 큰 병진으로 보임).
- 출력 [`f2c_anal.txt`](../debug_log/2026-10-07/outputs/f2c_anal.txt). 쓰인 곳 §3.1~§3.4.

### job921_run.sh · job912_extract.py · render_f2d2_box2.py — f2d2 복귀 (Jetson → PC)
- `job921_run.sh`: nav2 로그 epoch 1791346600~1791346730 을 목표 시작(1791346297) 기준 '+초' 로 발췌(정규식에 `extrapolation|Begin navigating|Reached` 추가) → [`j921_f2d2_g10.txt`](../debug_log/2026-10-07/outputs/j921_f2d2_g10.txt), 이어 `job912_extract.py BAG TA TB OUT`(map 자세 궤적 · 그림자 A · `/plan` 전부 · 전역 코스트맵 2 s · 로컬 1 s · 스캔 1 s · cmd_vel → `x921_f2d2.npz`, 원천 소실).
- `render_f2d2_box2.py`(PC): 목표 6 시작 +60 s 뒤 로컬 치명 칸을 그 시각 map→odom 으로 map 좌표에 놓고, 라이다 점(cKDTree)에서 7.5 cm 넘게 떨어진 칸 = '카메라만 본 칸' 으로 색칠 · 계획 경로 · 2 s 마다 차체 외곽 → 그림 [`2026-10-07_f2d2_box_stop.png`](../04_navigation/figures/2026-10-07_f2d2_box_stop.png) · 화면에 카메라만 치명 칸 상위 15(출력 원문 없음).
- §7.2 단면(x 1.0~1.6 전역 비용)을 낸 계산은 저장된 스크립트가 없다(**원천 소실**).

### job903_prep_rf2o_g4.sh · job907_postchk.sh · job918_prep.sh · job919/920_chk.sh — prep · 확인 (Jetson)
- `job903`: `EXTRA_SENSORS="rf2o:=true shadow:=true gate_v:=on"` 로 `job780_prep_navmap.sh`(office_v3 위치 추정 + Nav2) → sensors 인자 · `/rf2o_gate v_mode`. `job907`: Nav2 3 노드 lifecycle · rf2o 원/게이트/EKF A `topic hz` · `top` 2 회 중 rf2o_gate · rf2o_laser · ekf_node CPU. 출력 [`j903_prep.txt`](../debug_log/2026-10-07/outputs/j903_prep.txt) · [`j918_prep.txt`](../debug_log/2026-10-07/outputs/j918_prep.txt). 계보: 10-12 이후 `Docs/tools/prep_patrol.sh` → `prep_fast.sh`.

## 10. 용어
- **방향 맞춤(stateful goal checker)**: Nav2 `SimpleGoalChecker` 가 `stateful: True` 면 위치가 `xy_goal_tolerance`(0.15 m) 안에 한 번 들어온 뒤로는 위치를 다시 보지 않고 방향(`yaw_goal_tolerance` 0.35 rad)만 맞추면 성공. 비교 대상은 **컨트롤러가 받은 경로의 마지막 자세**다(러너가 보낸 목표가 아님).
- **GoalCritic · GoalAngleCritic**: MPPI 크리틱. 목표까지 1.0 m(위치) · 0.4 m(방향) 안에서 켜져, 후보 궤적 끝이 목표 위치 · 방향에 가까울수록 비용을 낮춘다(가중 10 · 3). 방향 기준도 경로 마지막 자세.
- **스무딩 실패 → TruncatePath(10-07 BT)**: `SmoothPath` 가 '스무딩 경로가 충돌' 로 실패하면 원경로를 `TruncatePath(distance 0)` 로 `{path}` 에 복사 — 이 노드가 마지막 점 방향을 atan2(0, 0) = 0 으로 덮어씀(09-17 `TODO(improve)`, 10-14 `CopyPath` 로 대체).
- **SUCCEEDED_XY**: 러너 `f` 모드가 위치만으로 끝낸 목표의 결과 이름(Nav2 상태는 CANCELED).
- **움찔(사용자 표현)**: 정체 중 MPPI 가 ±0.01 m/s · ±0.05 rad/s 수준의 지령을 20 Hz 로 계속 내는 상태. 펌웨어 최소 휠 속도(0.020 m/s) 근처라 바퀴가 짧게 떨림(추정).
