# '후진하고 멈췄다' — 위치 추정 정지와 CPU 부족(그리고 그 원인 판정의 두 번 정정)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **우회**(깨끗한 기동 · Foxglove 클라이언트 끊기 · 이후 컨디셔너 C++ 이식으로 증상 0) · 원인 판정은 두 번 바뀜: 09-09 '구조적 CPU 부족' → 09-10 §1 '긴 세션 열화' → 09-10 §4 'Foxglove 클라이언트 연결이 1 코어'. 각 판정의 몫은 나눠 재지 않음 | 09-09 오후 ~ 09-10 (이후 09-21 기준선 · 09-28 C++ 이식 · 09-30 · 10-27 같은 서명 재등장) | [09-09 §8.13 · §8.14](../debug_log/2026-09-09/SUMMARY.md) — `job170` '로버가 안 움직인다' | `ros2_ws/src/rover_bringup/launch/camera.launch.py`(`accel_fps` 200 → 100, `gyro_fps` 는 200 유지 + 주석) · `Docs/05_nvblox/NVBLOX_MIGRATION_PLAN.md`(S6 항목 신설) · 운용 규칙(측정 주행 중 Foxglove 끄기 — [Foxglove 카드](foxglove-snap-cpu.md)) | [DDS 공유메모리 사고](dds-shm-incident.md)(같은 '위치 고정' 서명의 다른 원인) · [Foxglove 4 초 스냅 · 브리지 부하](foxglove-snap-cpu.md) · [SLAM map→odom 시각 정체](slam-stamp-freeze.md)(10-27, 같은 '조회 실패' 를 다른 기전으로) · [micro-ROS 보드율 회귀](microros-baud-regression.md)(같은 날) · [배터리 · 전원 운용](battery-power-ops.md)(처음 오판한 원인) · [SLAM 데드락(09-17)](slam-dds-deadlock.md)(전력 모드를 잘못 꺼낸 날의 실제 원인) |

**한 줄**: 09-09 저녁 `job170`(STVL 검증 주행)에서 로버가 t = 5 s 부터 안 움직이는 것처럼 보였고, 나는 같은 '무이동' 이 12.0 V 부근에서만 났다는 이유로 **배터리**를 지목했다. 사용자가 "왜 후진하고 멈췄나" 를 묻자 CSV 를 전체 정밀도로 보니 위치가 9.90 s 동안 소수점 17 자리까지 똑같다가 조회가 실패했다 — tf2 버퍼 10 s 와 일치. 로버가 아니라 **`map→base_link` 갱신이 멈춘 것**이었다. 그 원인 하나(slam 의 SHM 고아 → [DDS 카드](dds-shm-incident.md))를 지운 뒤에도 `job175` 에서 같은 정지가 났고, 이번엔 EKF 가 30 Hz 주기를 91 번 놓치고(평균 0.055 s, 최대 0.197 s) slam 이 스캔을 한 번도 처리하지 못했다(load 9.01 / 6 코어). 'CPU 부족 → EKF 지연 → odom→base TF 지연 → slam 메시지 필터가 스캔 전량 폐기 → map→odom 미발행' 연쇄로 판정했다. 카메라 자이로를 100 Hz 로 낮추려다 D455 가 지원하지 않아 실패, CPU 절감 과제(S6)로 넘겼다. 다음 날 재부팅 직후엔 같은 스택이 EKF 위반 0 · load 2.10 이었고(§1 '열화' 로 정정), 같은 날 Foxglove Studio 클라이언트가 붙자 브리지 69.6 %, 끊자 EKF 위반 86 → 0 이 나왔다(§4 '진짜 병목'). 다만 그 '열화' 판정의 근거 한 줄(python3 14.7 %)은 이름별 평균이라 컨디셔너를 낮춰 보였을 가능성이 있다(§6 모순 1).

## 1. 증상
- `job170`(voxel_decay 30 · min_z 0.55, STVL 기능 확인은 성공): t = 5 s 부터 전진 0.240 m 고정, 후진 지령 −0.050 m/s 를 8 s 넘게 받고도 무이동 → `behavior_server: backup failed` → TIMEOUT. [09-09 §8.13](../debug_log/2026-09-09/SUMMARY.md)
- 같은 시각 보드 `cmd_vel timeout — motors stopped`, 스톨 카운터 `sc=0`(래치 아님). 배터리 11.96 → 11.94 V(그날 시작 12.23 V). TF · EKF 정상(`/tf` 29.9 Hz, `/odometry/filtered` 29.7 Hz 퍼블리셔 1, DDS 이상 없음) — 이 확인은 주행이 끝난 뒤 `job171_chk.sh` 시점 값.
- 같은 '무이동' 이 job141 · 169 · 170 에서 반복, 모두 12.0 V 부근. 12.2 V 대에서는 정상 주행.
- `job175`(UDP 전용 뒤): t = 3 s 동결, 9.7 s 뒤 조회 실패(§8.16).
- 출력 원문 · CSV: 09-09 `outputs/` 는 비어 있다. CSV(`/tmp/job170.csv` · `job175.csv`)는 Jetson `/tmp` 에만 있었다 → **원천 소실**. 수치는 SUMMARY 서술뿐.

## 2. 흐름 (시간순)
jobs 는 [2026-09-09/jobs/](../debug_log/2026-09-09/jobs/) · [2026-09-10/jobs/](../debug_log/2026-09-10/jobs/). 주행 이름 job141 · 169 · 170 · 175 는 스크립트가 아니라 `job125_avoid3.py` 의 실행(CSV 이름 인자)이다.

| 곳 | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 도구 |
|---|---|---|---|---|
| 09-09 §8.13 | STVL S1 확정 주행 job167 · 169 · 170 | job170: 상자 비용 로컬 · 전역 최소 99(기억 성공) — 그러나 t = 5 s 부터 무이동, TIMEOUT | — | `job125_avoid3.py` |
| §8.13 | 보드 · 배터리 · TF 생존 · nav2 로그 · load | `sc=0`, 11.96 → 11.94 V, `/tf` 29.9 Hz, filtered 29.7 Hz, fastrtps 잔재 수 | '**배터리가 공통 인자로 가장 유력**'(데드존 0.34 / KV 5.8 이 12.2 V 에서 캘리브된 값이라 전압 강하 시 토크 부족) — **틀림(§5.1)** | `job171_chk.sh` |
| §8.14 | 사용자 질의 "왜 후진하고 멈췄나" → CSV 전체 정밀도 | 마지막 위치 변화 t = 4.01, 이후 **99 샘플** `fwd=0.24011390390417972 lat=0.05075221739488888`, 기록 종료 t = 13.91 = **9.90 s 뒤** | '**로버가 안 움직인 게 아니라 `map→base_link` 갱신이 멈춤**' — 낡은 캐시 변환이 10 s 버퍼에서 만료되며 실패. 후진 중 실제 이동은 관측 불가 | (CSV 직접 읽기, 스크립트 없음) |
| §8.14 | 정지 시각 전후 nav2 · sensors · slam 로그, 지금 `/tf` 발행 주체, EKF 1 초 버킷 20 s | t ≈ 4.0 `map→odom` 발행 정지 → t = 4.5 자세 무변화 → 컨트롤러 v = 0 → t = 5.5 낡은 자세로 재계획(계획 횡 +0.39 → +0.068) → t = 6.0 `Running backup` → t ≈ 14 TF 만료 → `Goal canceled` | §8.13 배터리 판정 **정정**. job141 · 169 도 같은 서명일 가능성 | `job172_freeze.sh` |
| §8.15 | slam 프로세스 · 발행 · 고아 SHM | slam 살아 있음 · `/map` 퍼블리셔 0 · 고아 `fastrtps_port7425` | SHM 2 회차 → UDP 전용(→ [DDS 카드](dds-shm-incident.md)) | `job173_slam.sh` → `job174_dds.sh` |
| §8.16 | UDP 전용 **뒤** 다시 주행 job175 | t = 3 s 동결, 9.7 s 뒤 조회 실패, SHM 오류 0 | 다른 원인 | `job125_avoid3.py`(run job175) |
| §8.16 | 누가 발행 중인가 · 프로세스 · 로그 끝 · top | (원문 없음) | — | `job176_who.sh` |
| §8.16 | 프로파일 적용 · slam 상세 · EKF 위반 통계 · IMU 입력 Hz | EKF `Failed to meet update rate!` **91 회**, 평균 **0.055 s**, 최대 **0.197 s**(목표 0.033 s). slam 로그 **INFO 30 + WARN 1** — 마지막 정상 로그가 기동 때 'Registering sensor', 그 뒤엔 `Message Filter dropping message: frame 'lidar_link'` 뿐 = **스캔을 한 번도 처리 못 함**. load **9.01 / 6 코어**, sensor_conditioner **35~37 %**, `/imu/data` 200 Hz | **연쇄**: CPU 부족 → EKF 주기 미달 → odom→base TF 늦음 → slam 메시지 필터가 스캔 stamp 에 맞는 TF 를 못 찾아 전량 폐기 → map→odom 미발행 → 10 s 뒤 조회 실패 | `job177_env.sh` |
| §8.16 시도 | 카메라 `gyro_fps` 200 → 100, `accel_fps` 200 → 100 배포 · 재기동 · 효과 검증 | (원문 없음) | — | `job178_imu.sh` |
| §8.16 내 오류 1 | 정리 · 재기동 · 검증 | `n=$((n+$(pgrep -fc …)))` 산술 오류 → '잔존 0' 이 거짓, 오래된 프로세스가 산 채로 측정 | 측정 무효 → 카운트 함수 따로 | `job179_clean.sh` |
| §8.16 | 배포 파일 · 실행 중 카메라 파라미터 · 로그의 IMU 프로파일 | `Open profile: Gyro FPS: 200` · `Accel FPS: 100` — **D455 자이로는 100 Hz 미지원**, 드라이버가 200 으로 되돌림. `unite_imu_method 1(copy)` 이라 `/camera/camera/imu` 는 자이로 속도 = 여전히 200 Hz | 지원 프로파일 확인 없이 값을 넣은 실수 → gyro 200 복귀. CPU 절감은 **conditioner 쪽**(S6) | `job180_imuparam.sh` |
| §8.16 내 오류 2 | `/tf --verbose` 노드 목록 → 'slam 중복' → 정리 · 재기동 | 발행자 + 구독자 함께 나열한 것 | 판단 취소(→ [DDS 카드 §5.3](dds-shm-incident.md)) | `job180_imuparam.sh` → `job181_dedup.sh` |
| 커밋 `2a4092b2` · 계획서 | Phase S 에 **S6 CPU 여유 확보** 추가 | 종료 조건: 주행 30 s 동안 `Failed to meet update rate` 0 회 · `Message Filter dropping` 0 회 · load < 6 | '우선순위 높음' | `NVBLOX_MIGRATION_PLAN.md` S6 |
| 09-10 §1 | Jetson 재부팅 직후 Nav2 포함 30 s S6 기준선 | EKF 위반 **0 회 / 30 s** · slam 폐기 **0 회** · load **2.10**. CPU rplidar 19.5 / realsense 15.3 / controller 14.8 / python3 14.7 / ekf 12.7 | **'09-09 의 CPU 부족이 구조적이라는 결론은 틀렸다'** — load 8~9 · 위반 91 · python3 44 % 는 재기동 수십 번이 쌓인 **열화**. S6 우선순위 하향 | `job182_s6base.sh`(⚠ python3 값은 이름별 평균, §6 모순 1) |
| 09-10 §4 | stuck_monitor 수정 뒤 Nav2 재기동 → **기동 실패** | `lifecycle_manager: Failed to change state for node: planner_server … async_send_request failed` — 설정은 성공했는데 부하로 서비스 응답 타임아웃. load **6.35**, EKF 위반 **86**, slam 폐기 **28**. top 에 `foxglove_bridge` **69.6 %** | — | `job189_wait.sh` · `job190_err.sh` |
| 09-10 §4 | 8765 포트 연결 확인 → 브리지 정지 → 30 s 재측정 | `ESTAB 192.168.0.101:8765 ← 192.168.0.6:65351`(사용자 PC Foxglove Studio). 정지 뒤 EKF 위반 **0**(직전 86) · slam 폐기 **0**(직전 28) · Nav2 전 노드 active | **★ 진짜 병목 = Foxglove 클라이언트 연결**(`viz:=lean` 이어도 붙으면 1 코어 가까이). '09-09 주행 중 Foxglove 로 경로를 보던 것이 EKF 를 굶겨 TF 를 끊었다' — 09-09 쪽은 **추정**(그날 연결 기록 없음) | `job191_nofg.sh` |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 배터리 전압 강하로 토크 부족 → 무이동 | 전압 비교(12.0 vs 12.2 V), 보드 스톨 카운터 | `sc=0`(래치 아님), 전압은 상관만 | **기각**(§8.14 정정) — 로버가 안 움직였다는 전제부터 관측 불가였다 |
| 로버가 물리적으로 멈췄다 | CSV 전체 정밀도 · 기록 종료 시각 | 17 자리 같은 값 99 샘플 → 9.90 s 뒤 조회 실패 = 캐시 + 버퍼 10 s | **기각** — 갱신이 멈춘 것(측정 도구의 서명) |
| `map→odom` 이 멈췄다(slam 이 스캔을 처리 못 함) | job172 로그 시각, job177 slam 로그 수준별 건수 | t ≈ 4.0 정지, slam 은 스캔을 한 번도 처리 못 함(job175) | **지지** |
| slam 이 그래프에서 사라졌다(SHM) | job173 | job170 쪽: 고아 7425 · `/map` 퍼블리셔 0 | job170 의 원인으로 **지지**(XML 주석 · 커밋 기준, SUMMARY 본문엔 연결 없음 — [DDS 카드 §6](dds-shm-incident.md)) |
| job175 도 SHM | job174 검증 · job176 · 177 | SHM 오류 0, 프로파일 적용 | **기각** |
| CPU 부족 → EKF 지연 → slam 메시지 필터 전량 폐기 | job177 위반 통계 · load | 91 회 · 평균 0.055 s · load 9.01 | **지지**(job175). 메시지 필터가 '맞는 TF 를 못 찾아 버린다' 는 연결은 로그 문구 + 순서로 읽은 것 — TF 도착 지연을 직접 잰 값은 없음 |
| 자이로 200 → 100 Hz 로 conditioner 부하 절반 | job178 → job180 | D455 자이로 100 Hz 미지원, 200 유지 | **실행 불가** |
| CPU 부족이 스택 구조상 상시 | 09-10 재부팅 직후 30 s | 위반 0 · load 2.10 | **기각**(09-10 §1) — 단 근거 줄 하나가 약함(§6 모순 1) |
| 긴 세션 · 재기동 반복의 '열화' | 09-10 §1 의 대비 | 재부팅 직후 정상 vs 09-09 저녁 비정상 | **추정** — 무엇이 쌓였는지(고아 프로세스 · 잔재 · 카메라 스트림 열화 등)는 재지 않음 |
| Foxglove 클라이언트 연결이 1 코어를 먹어 EKF 를 굶김 | 09-10 §4 연결 확인 → 브리지 정지 → 같은 30 s 창 | 86 → 0, 28 → 0 | **지지**(09-10 당일). 09-09 job175 시점에도 연결돼 있었는지는 **미확인** |

## 4. 조치와 효과
- **`camera.launch.py`**: `accel_fps` 100(적용됨), `gyro_fps` 200(되돌림), 주석에 'D455 자이로 100 미지원 · `unite_imu_method 1` 이라 IMU 토픽은 자이로 속도' · '되돌릴 땐 conditioner CPU 와 EKF 위반 수를 함께'. CPU 효과 측정치는 없다.
- **S6 신설**(`NVBLOX_MIGRATION_PLAN.md`): 최대 소비원 conditioner 35~37 % — '컨디셔너에서 다운샘플하거나 C++ 로'. 종료 조건 위 표. 09-10 §1 로 '우선순위 하향'.
- **운용 규칙**(09-10 §4): 측정 주행 중 Foxglove Studio 창을 닫거나 브리지를 내린다. 경로 · 코스트맵은 rosbag 으로 남겨 사후에 본다(09-10 §0 · §6).
- **깨끗한 기동**: 09-10 §1 · §12 '측정 주행 전에는 스택을 깨끗이 재기동하고 Foxglove 를 끈다', 09-11 `job240_clean.sh`(→ [보드 카드](board-link-microros-session.md) · [DDS 카드](dds-shm-incident.md)).
- 효과: 09-10 §4 이후 S1 완주(job192) 등 주행 재개. 정지 원인별 몫(열화 · Foxglove · conditioner)은 나눠 재지 않았다.
- 이후(09-17): 전력 모드가 **nvpmodel 15 W**(ID 0, CPU 최대 1497 MHz; 하드웨어 최대 1728)임을 처음 기록. 사용자 승인으로 25 W 로 바꿨더니 CPU 상한이 **1344 MHz 로 오히려 낮아져** 같은 승인 범위에서 15 W 로 되돌렸다(내 추정 오류). CPU 를 늘리는 모드는 MAXN_SUPER 뿐(전력 대가) — 아래 §4.1 · §5.5 · [09-17 §5 · §6.2](../debug_log/2026-09-17/SUMMARY.md). 09-09 job101 이 `nvpmodel -q` 를 찍었지만 값은 기록되지 않았다.
- 이후(09-21): Phase S 기준선 — CPU 합 ≈ 320 %, conditioner ≈ 43 %(`BASELINE_STVL.md` — python3 108~110 % 의 내역). 09-23 사용자 결정: 카메라 IMU 200 Hz 유지, 다운샘플 금지 · 로직만 C++ 이식.
- 이후(09-28): conditioner C++ 이식 — **42.2 → 7.1 %**(−35 %p, [09-28 SUMMARY](../debug_log/2026-09-28/SUMMARY.md)).
- 이후(09-30): 매핑 중 Foxglove(lean) 연결 시 EKF 위반 12 회 / 30 s · EKF CPU 49 % → 끊으면 0 회 · 12 % → `viz:=map` 세트([Foxglove 카드](foxglove-snap-cpu.md)).
- 이후(10-27): 같은 'map→base 조회 실패 → 컨트롤러 중단' 서명이 이번엔 slam 위치 추정 정합(LinkNearChains) 동안 map→odom stamp 정체로 다시 나옴 → `transform_timeout 1.5`([SLAM 시각 정체 카드](slam-stamp-freeze.md)).

### 4.1 09-17 — 'CPU 를 더 주자' 와 전력 모드 (09-17 §5 · §6.2)
배경: 09-17 mp7 에서 SLAM 이 주행 중 수 초씩 멈추고 끝내 정지했다. 제어 루프 미달이 mp5 0 → mp6 9 → mp7 60+ 로 같은 설정에서 늘었고, slam.log 엔 기동부터 'queue is full' 28 회. 나는 처음에 'CPU 굶주림' 을 세우고 전력 모드를 손잡이로 봤다. 최종 정지는 Fast DDS 데드락으로 밝혀졌다(→ [SLAM 데드락 카드](slam-dds-deadlock.md)) — 이 절은 그 과정 중 전력 모드 부분만.

| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-17 §5 | `job384_power.sh` · `job385_pmhist.sh`(로버 정지) | `nvpmodel -q` = **15 W(ID 0)**, CPU `scaling_max_freq` 1497 MHz, `cpuinfo_max_freq` **1728 MHz**. `/etc/nvpmodel.conf` 의 `PM_CONFIG DEFAULT` = 25 W. 상태 파일(`/var/lib/nvpmodel/status`)은 부팅 때 다시 쓰여 어제와 같았는지 확인 불가 | '15 W 로 돌고 있다 → 25 W 면 **CPU +15 %**'(계산 근거 없음) — **❌ 추정, §6.2 에서 틀림**. 사용자 결정 항목으로 올림('로버 배터리 · Jetson 전원 회로 허용 전력 확인 필요') | 두 출력 **원천 소실**(SUMMARY §5 서술) |
| 09-17 §6.2(사용자 승인) | `run_pm25.sh` → `job388_pm25.sh`: `sudo nvpmodel -m 1` | 전 '15W · cpu0 max 1497 MHz' → 후 '**25W · cpu max 1344 ×6 MHz** · online 0-5', 온도 cpu 47 · gpu 47 °C, 배터리 12.12 V | CPU 상한이 **낮아졌다** — 승인 목적(CPU 여유)과 반대 | [`outputs/j388_pm25.txt`](../debug_log/2026-09-17/outputs/j388_pm25.txt) |
| §6.2 | `job389_pmconf.sh`: conf 의 POWER_MODEL 블록 · 10 s 뒤 cur/max/min · 가능 주파수 · `nvpmodel -q --verbose` | (원문 없음) | 모드별 표를 만들기 위한 조회 | **원천 소실** |
| §6.2 | `run_pmrevert.sh` → `job390_pmrevert.sh`: conf 의 모드별 CPU0 MAX · GPU MAX · EMC MAX 를 찍고 `sudo nvpmodel -m 0` | 15 W: CPU 1 497 600 kHz · GPU 612 MHz · EMC 2 133 MHz / 25 W: CPU **1 344 000** · GPU 918 MHz · EMC 3 199 MHz / MAXN_SUPER: 셋 다 −1(제한 없음). 원복 뒤 '15W · cpu max 1497 ×6' | **이 JetPack 의 25 W 는 전력 예산을 GPU · 메모리에 주고 CPU 를 낮춘다**. CPU 를 늘리는 유일한 모드는 MAXN_SUPER(무제한, 전력 최대) — 로버 전원 회로 허용 전력 확인 뒤 사용자 결정 | [`outputs/j390_pmrevert.txt`](../debug_log/2026-09-17/outputs/j390_pmrevert.txt) |
| 09-17 §7 mp8(15 W 그대로) | 다른 조치(Fast DDS 2.6.12 · visualize off · BT 100 ms) 뒤 주행 + top 기록 | 루프 미달 **0**, BT 타임아웃 0. top 50 샘플 load 평균 8.5, controller 36 %(최대 70), python 노드 합 121 % | 전력 모드를 안 바꿔도 루프 미달이 사라짐 → mp7 의 악화는 CPU 상한 문제가 아니었다(시각화 · bag · 데드락 쪽, 몫은 안 나눔) | `j379_mp8_events.txt` · 09-17 §7 |
| 이후(09-21) | Phase S 기준선 | 'Jetson Orin Nano **15 W**, 클럭 최대 1497 MHz' 를 운용점으로 명시 · nvblox 계획서에 'MAXN_SUPER 는 CPU 상한을 올리지만 배터리 · 열(기준선 6.6 W) 대가 — 별도 측정 항목' | 15 W 유지 | [`2026-09-21/BASELINE_STVL.md`](../debug_log/2026-09-21/BASELINE_STVL.md) L10 · `Docs/05_nvblox/NVBLOX_MIGRATION_PLAN.md` |

- **지금(10-30 저장소 기준)**: 운용 모드를 15 W 에서 바꿨다는 기록은 없다. MAXN_SUPER 측정도 기록 없음(09-21 SUMMARY '필요 시 MAXN 비교' 로 남음). Jetson 의 실제 현재 모드는 이 카드 작성 중 확인하지 않았다(로봇 접속 안 함).
- 사실 정리(측정 · conf 원문): 모드 0 = 15 W(CPU 1497.6 / GPU 612 / EMC 2133 MHz) · 모드 1 = 25 W(CPU **1344** / GPU 918 / EMC 3199) · 모드 2 = MAXN_SUPER(제한 없음, CPU 하드웨어 최대 1728). conf 에서 찍은 것은 코어 5 줄뿐이고 세 모드 다 `CPU_ONLINE CORE_5 1`, 25 W 전환 뒤 실측 `online 0-5`(6 코어) — 코어 수는 모드와 무관한 것으로 보인다(15 W · MAXN 의 0~4 번 줄은 안 찍음).

## 5. 내 실수
### 5.1 '배터리 때문에 안 움직였다' — 측정 도구의 정지를 로버의 정지로 읽음
| 칸 | 내용 |
|---|---|
| 하려 한 것 | job170 의 TIMEOUT 원인 찾기(§8.13) |
| 본 것 | 러너 1 초 출력에서 t = 5 s 부터 전진 0.240 고정, 후진 지령 −0.050 을 8 s, `backup failed`. 보드 `cmd_vel timeout`, `sc=0`, 11.96 → 11.94 V. job141 · 169 · 170 모두 12.0 V 부근 |
| 처음 추론 | 같은 '무이동' 이 전압이 낮을 때만 난다 → 배터리가 공통 인자, 데드존 · KV 캘리브가 12.2 V 기준이라 토크 부족. '충전 후 같은 시험 반복' 계획 |
| 의심한 이유 | 사용자 질문 "왜 후진하고 멈췄나" — 실제로 멈춘 것인지부터 다시 봄 |
| 판별 | CSV 를 전체 정밀도로: 99 샘플이 17 자리까지 동일 → 실제 로버라면 센서 잡음 때문에 불가능. 기록 종료 = 마지막 변화 + 9.90 s = tf2 버퍼 기본 보관 10 s. 러너의 `pose()` 는 `lookup_transform('map','base_link', Time())` = '가장 최근 변환' 이라 새 변환이 안 오면 같은 값을 계속 주다가 버퍼에서 만료되면 예외 → `None` → 그 샘플은 기록하지 않음 |
| 결론 | 갱신 정지(map→odom). 배터리 판정 근거 없음. 보드 `cmd_vel timeout` 은 컨트롤러가 지령을 끊은 결과(원인이 아님). 스톨 래치도 아님 |
| 다음에 알아보는 법 | 서명: **값이 소수점 끝자리까지 같은 연속 샘플 + 끝이 '마지막 변화 + 버퍼 시간' 에서 끊김** = 측정 대상이 아니라 입력이 멈춘 것. 러너는 변환 stamp 를 함께 기록하고 'stamp 가 0.5 s 이상 안 바뀜' 을 따로 표시해야 한다. 상관(전압)과 원인을 구분 — 다른 날 같은 전압에서 정상인 표본이 있는지 먼저 |
| 데이터 | SUMMARY §8.13 · §8.14, 커밋 `2a4092b2`, 도구 `jobs/job125_avoid3.py`(`pose()` · 기록 루프) · `job171_chk.sh` · `job172_freeze.sh`. CSV `/tmp/job170.csv` **원천 소실** |

### 5.2 지원 프로파일을 확인하지 않고 `gyro_fps` 100 을 넣음
| 칸 | 내용 |
|---|---|
| 하려 한 것 | conditioner(200 Hz IMU 를 Python 으로 중계) 부하를 반으로 — 카메라 IMU 를 100 Hz 로(`job178_imu.sh`) |
| 본 것 | (job180) 배포 파일은 100, 카메라 로그 `Open profile: … Gyro FPS: 200` · `Accel FPS: 100` |
| 처음 추론 | (배포만으로 적용됐다고 가정 — job178 의 '효과 검증' 은 Hz 측정) |
| 의심한 이유 | `/camera/camera/imu` 가 여전히 200 Hz |
| 판별 | 로그의 실제 열린 프로파일: 자이로는 드라이버가 200 으로 되돌림(D455 자이로 미지원), 가속도는 100 적용. `unite_imu_method 1(copy)` 은 자이로 속도를 따름 |
| 결론 | gyro 200 복귀, accel 100 유지. CPU 절감은 conditioner 다운샘플 · C++ 로(이후 09-23 사용자 결정: 다운샘플 금지, C++ 이식만) |
| 다음에 알아보는 법 | 센서 주기 · 해상도를 바꾸기 전에 드라이버 로그의 지원 프로파일(또는 `rs-enumerate-devices`)을 먼저 본다. 바꾼 뒤엔 '배포 값' 이 아니라 '열린 프로파일' 줄로 확인 |
| 데이터 | SUMMARY §8.16 '시도와 결과', `camera.launch.py` 주석(커밋 `2a4092b2`), 도구 `jobs/job178_imu.sh` · `job180_imuparam.sh` |

### 5.3 `pgrep -fc … || echo 0` 의 두 줄 — '잔존 0' 이 거짓
| 칸 | 내용 |
|---|---|
| 하려 한 것 | gyro 변경 뒤 깨끗하게 정리하고 재기동해 효과 측정(`job179_clean.sh`) |
| 본 것 | 산술 오류, '15 초 후 잔존' 판정이 맞지 않음 → 오래된 프로세스가 산 채로 측정 |
| 처음 추론 | (SUMMARY 서술) 'pgrep -fc 가 여러 줄을 반환' |
| 의심한 이유 | 산술 오류 메시지 · 측정 결과가 정리 전과 비슷 |
| 판별 | (코드 읽기) `pgrep -c` 는 일치 0 개일 때도 '0' 을 찍고 종료 코드 1 을 낸다 → `\|\| echo 0` 이 한 번 더 '0' → 치환 결과가 두 줄 `0\n0` → `$((n+0\n0))` 산술 문법 오류. 즉 '여러 줄' 은 pgrep 이 아니라 **대체값과 겹친 것**(SUMMARY 표현보다 좁은 기전, **추정** — 오류 원문 없음) |
| 결론 | 그 측정 폐기. `job181` 의 `cnt()` = `c=$(pgrep -fc "$p" \| head -1); c=${c:-0}` 로 고침 — 09-11 `job240` · `job249` 도 같은 형태 |
| 다음에 알아보는 법 | 셸에서 숫자를 받는 치환은 `\| head -1` 과 기본값(`${c:-0}`)으로 **한 줄 · 숫자** 를 보장. '잔존 0' 같은 판정 줄은 실제 남은 이름을 함께 찍는다(job179 의 '남음: …' 줄처럼) |
| 데이터 | SUMMARY §8.16 '내가 낸 오류 2건' 첫째, `jobs/job179_clean.sh` · `job181_dedup.sh` |

### 5.4 '구조적 CPU 부족' → '열화' → 'Foxglove' — 판정을 한 표본으로 뒤집기
| 칸 | 내용 |
|---|---|
| 하려 한 것 | S6 종료 조건(위반 0 · 폐기 0 · load < 6) 기준선 측정(09-10 `job182_s6base.sh`) |
| 본 것 | 재부팅 직후 위반 0 · 폐기 0 · load 2.10, python3 14.7 % |
| 처음 추론 | 09-09 의 load 8~9 · 위반 91 · python3 44 % 는 구조가 아니라 열화 → '결론은 틀렸다', S6 하향 |
| 의심한 이유 | 같은 날 §4 에서 Foxglove 클라이언트 하나로 위반 86 이 나왔다 — '열화' 말고도 같은 증상을 만드는 원인이 있다. 그리고 이 카드 작성 중 도구를 다시 읽으니 python3 14.7 % 는 이름별 평균이다(§6 모순 1). 09-21 기준선에서도 conditioner 는 ≈ 43 %(구조적으로 큰 소비자) |
| 판별 | (이 카드에서 한 것은 기록 · 코드 대조뿐 — 새 측정 없음) |
| 결론 | 09-09 의 정지는 'CPU 부족' 까지는 측정, 그 CPU 를 누가 먹었는지(conditioner 의 상시 몫 · 긴 세션 잔존 · Foxglove 연결)는 **나눠 재지 않음**. 09-10 §1 의 '구조적이라는 결론은 틀렸다' 는 conditioner 몫에 대해선 과했다(**추정**) |
| 다음에 알아보는 법 | 판정을 뒤집는 표본이 하나면 그 표본의 측정 조건(재부팅 직후 · 클라이언트 없음 · 주행 없음)을 함께 적고, 뒤집기 전에 같은 조건 차이로 원래 표본을 재현해 본다. CPU 표는 이름이 아니라 pid → 명령줄 단위로([Foxglove 카드 §5.1](foxglove-snap-cpu.md) 와 같은 교훈) |
| 데이터 | 09-10 SUMMARY §1 · §4, `2026-09-10/jobs/job182_s6base.sh`(awk 집계식), [`BASELINE_STVL.md`](../debug_log/2026-09-21/BASELINE_STVL.md) 37 행 |

### 5.5 '25 W 면 CPU +15 %' — 모드 이름만 보고 효과를 추정해 사용자 승인까지 받음 (09-17 §5 → §6.2)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | mp7 의 SLAM 굶주림(그때의 가설)에 CPU 여유를 더 주기 |
| 본 것 | `job384`: 15 W · CPU 상한 1497 MHz · 하드웨어 최대 1728 MHz. conf 기본은 25 W |
| 처음 추론 | '15 W → 25 W 면 클럭이 올라간다 → **CPU +15 %**'. conf 의 25 W 블록을 열어 보지 않고 '전력이 크면 CPU 도 빠르다' 로 계산. 사용자 결정 항목으로 '배터리 · 전원 회로 허용 전력 확인 필요' 와 함께 올렸고 사용자가 승인 |
| 의심한 이유 | 전환 직후 `job388` 이 찍은 `scaling_max_freq` 가 6 코어 모두 **1344** — 1497 보다 낮다 |
| 판별 | `job390`: conf 원문의 모드별 상한 — 25 W 는 CPU 1344 · GPU 918 · EMC 3199(15 W 는 1497.6 · 612 · 2133) |
| 결론 | 이 JetPack 의 25 W 는 CPU 가 아니라 GPU · 메모리 쪽에 예산을 준다. 승인 목적과 반대라 같은 승인 범위에서 즉시 15 W 로 원복(1497 MHz 확인). 그리고 그날 mp7 의 최종 정지는 CPU 가 아니라 Fast DDS 데드락이었다(→ [SLAM 데드락 카드 실수 ①](slam-dds-deadlock.md)) — 전력 모드는 애초에 틀린 손잡이였다 |
| 다음에 알아보는 법 | 설정의 '효과' 는 이름이 아니라 **그 설정 파일의 수치**로 본다(`/etc/nvpmodel.conf` 의 `CPU_A78_0 MAX_FREQ` 등). 사용자에게 승인을 청하는 변경은 예상 효과의 출처(파일 · 측정)를 함께 적는다 — 출처 없는 수치는 쓰지 않는다(메모 '사양 수치 출처 의무' 와 같은 원칙). 바꾼 직후 같은 지표(여기선 `scaling_max_freq`)를 다시 읽는 확인을 스크립트에 넣는다(`job388` 이 그랬기 때문에 바로 잡혔다) |
| 데이터 | [`2026-09-17/outputs/j388_pm25.txt`](../debug_log/2026-09-17/outputs/j388_pm25.txt) · [`j390_pmrevert.txt`](../debug_log/2026-09-17/outputs/j390_pmrevert.txt) · 도구 [`jobs/job384_power.sh`](../debug_log/2026-09-17/jobs/job384_power.sh) · `job385_pmhist.sh` · `job388_pm25.sh` · `job389_pmconf.sh` · `job390_pmrevert.sh`(`job384` · `job385` · `job389` 출력은 원천 소실) · [09-17 §5 · §6.2](../debug_log/2026-09-17/SUMMARY.md) |

## 6. 기록 사이 모순 (원문 대조)
1. **09-10 §1 의 'python3 14.7 %' 는 이름별 평균.** `job182_s6base.sh` 는 `top -b -n 30 -d 1` 30 화면을 파일로 받아 `awk '/^ *[0-9]+ / {cpu[$12]+=$9; n[$12]++} END {… cpu[c]/n[c]}'` 로 **COMMAND 이름마다** 평균을 낸다. `top -b` 는 모든 프로세스를 찍으므로 python3 는 conditioner · deskew · stuck_monitor · 기타 python 노드 줄이 한 이름으로 묶여 '줄 하나당 평균' 이 된다 — conditioner 하나가 40 % 여도 0 % 근처 python 줄들이 있으면 크게 낮아진다. 같은 이유로 09-09 의 'python3 44 %'(job177 등의 1 초 top, 줄 하나)와 직접 비교할 수 없다. 09-21 기준선(pid 별): conditioner ≈ 43 %. → '09-09 python3 44 % 는 열화' 의 근거는 약하다(새 측정 없이 코드 · 기록 대조로 낸 판단, **추정**). 또 `top -b` 첫 화면은 직전 구간이 아닌 값이라 평균에 섞인다(작은 영향, **추정**).
2. **'09-09 주행 중 Foxglove 로 경로를 보고 있던 것'**(09-10 §0 · §4): 09-09 SUMMARY 에는 job170 · 175 때 클라이언트 연결 기록이 없다. 같은 날 §8.12 는 lean 적용 뒤 top 에서 브리지가 '사라졌다' 고 쓴다 — 그때는 연결이 없었을 수 있다([Foxglove 카드](foxglove-snap-cpu.md)). 인과 포함은 **추정**.
3. **§8.14 제목의 '(job170, 175)'**: 본문은 job170 만 다루고 job175 는 §8.16 에서 나온다. job170 정지의 원인은 SUMMARY 본문에 없고(§8.15 의 2 회차 SHM 과의 연결은 XML 주석 · 커밋에만), job175 는 SHM 0 · CPU. 같은 서명이 두 원인에서 나왔다는 점이 이 카드의 핵심이라 섞어 읽지 않도록 표에서 나눴다.
4. **conditioner '35~37 %'(09-09 §8.16)와 '44 %'(09-10 §1 이 인용한 09-09 값)**: 09-09 SUMMARY 에서 python3 44 % 를 직접 적은 줄은 없다 — 가장 가까운 것은 §8.12 'lean 이후' 표의 1 위 `python3 39.2 %`(1 초 top 의 한 줄, 정체는 conditioner 로 **추정**)이고, 44.1 % 는 08-31 · 09-01 의 conditioner 값이다([Foxglove 카드](foxglove-snap-cpu.md)). 09-10 이 어느 측정을 인용했는지 **미확인**.
5. **'TF/EKF 정상'(§8.13)**: job171 은 주행이 **끝난 뒤** 값이다. 정지 중(t ≈ 4~14)의 TF 상태가 아니므로 'DDS 이상 없음' 은 정지 시각의 근거가 못 된다 — 바로 다음 job173 이 slam 고아를 찾았다.
6. **(09-17) '25W → CPU 가 오히려 느려져'**(§6 제목): 잰 것은 `scaling_max_freq`(**상한**) 1344 MHz 이고, 25 W 상태로 부하를 걸어 실제 처리 속도 · 루프 미달을 잰 적은 없다(전환 몇 분 만에 원복). '느려진다' 는 상한에서 낸 결론(타당한 추론이지만 측정은 아님). 또 §5 의 '하드웨어 최대 1728' 은 `cpuinfo_max_freq` 값으로 `job384` 출력이 없어(원천 소실) SUMMARY 서술이 유일하다.
7. **(09-17) '루프 미달 mp5 0 → mp6 9 → mp7 60+'**: 같은 15 W 에서 늘었다 — 즉 전력 모드는 이 악화의 변수가 아니었다. mp8 에서 15 W 그대로 0 이 됐으므로 원인은 그 사이 바꾼 것(visualize off · bag `/trajectories` 제외 · BT 100 ms · Fast DDS 2.6.12) 쪽이다(**어느 것인지 미분리**).

## 7. 남은 것
- 09-09 저녁 CPU 의 몫 나누기(conditioner 상시 · 고아/중복 프로세스 · Foxglove 연결) — 재현 시험 없음. 이후 conditioner C++ 이식(09-28)으로 가장 큰 몫은 사라졌다.
- '긴 세션 열화' 의 정체(무엇이 쌓이나) — 09-10 §1 은 이름만 붙였다. 09-11 §5.4 의 '깨끗한 기동' 절차가 운용 대책.
- 러너가 '갱신 정지' 를 스스로 표시하는 기능 — 이후 시기 러너(`job125_avoid3.py` 후속 · `stuck_monitor` · `nav_guard`) 카드에서 확인.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| job167 · 169 · 170 · 175(run) | STVL 확정 주행 · 정지 재현 | `2026-09-09/jobs/job125_avoid3.py`, CSV 원천 소실 |
| job171 · 172 | 주행 뒤 상태 · 정지 시각 로그 · EKF 1 초 버킷 | `2026-09-09/jobs/` |
| job176 · 177 | 발행 주체 · 프로파일 · EKF 위반 통계 | 같은 곳 |
| job178 · 179 · 180 · 181 | 카메라 IMU fps 시도 · 정리(오류) · 프로파일 확인 · 중복 정리 | 같은 곳 |
| job182 | S6 기준선 30 s | `2026-09-10/jobs/` |
| job189 · 190 · 191 | Nav2 기동 대기 · lifecycle 오류 · Foxglove 끄고 30 s | 같은 곳 |
| (09-17) job384 · 385 | 전력 모드 · 클럭 · conf 기본값 조회 | `2026-09-17/jobs/`, 출력 원천 소실 |
| (09-17) job388 · 389 · 390 (+ run_pm25 · run_pmrevert) | 25 W 전환 · conf 표 · 15 W 원복 | `2026-09-17/jobs/`, `j388_pm25.txt` · `j390_pmrevert.txt` |

## 9. 도구 해설
**공통**: Jetson 실행(PC WSL → `run_j.sh`, [보드율 카드 §9](microros-baud-regression.md) 공통 항목). 출력 원문 없음(09-09 · 09-10 `outputs/` 에 해당 파일 없음 — 09-10 은 job205 · 216 CSV 만). 'EKF 위반' = `/tmp/sensors.log` 의 `Failed to meet update rate` 줄 수, 'slam 폐기' = `/tmp/slam.log` 의 `Message Filter dropping` 줄 수. 로그를 비우지 않으면 누계라 09-10 도구들은 측정 전후 차분을 쓴다.

**도구 계보**
- 주행 계측: `job92_avoid.py`(깊이점 여유, 결함) → **`job125_avoid3.py`**(기하 여유 · 계획 여유 · 상자 자리 비용 · 깊이점 수 ⑤, 09-09 오후~) → 09-10 · 09-11 판(같은 이름, 상자 재고정 · 클러스터링 수정) — 이후 러너 계보는 다른 카드
- 정지 진단: job171(주행 뒤 상태) → job172(정지 시각 로그 + EKF 버킷) → job173(slam · SHM) → job176(누가) → job177(EKF 위반 통계 · 프로파일)
- 위반 · 폐기 측정: job177(누계) → job178 · 179 · 181(로그 비우고 재기동 뒤 누계) → 09-10 job182 · 191(30 s 창 차분) — 이후 `chk_prep.py` · `Docs/tools/anal_top.py` · `anal_proc_cpu.py`(10-12, pid 단위)
- 정리: job179(두 줄 결함) → job181(`cnt()` 수정) → 09-11 job240 · 249
- (09-17) 전력 모드: `job384_power.sh`(현재 모드 · 클럭 · 온도) → `job385_pmhist.sh`(상태 파일 · conf 기본 · 부팅 · syslog 이력) → (승인) `job388_pm25.sh`(전환 + 전후 상한) → `job389_pmconf.sh`(conf 블록 · 가능 주파수) → `job390_pmrevert.sh`(모드별 상한 표 + 원복). 이후 고정 도구 없음.

### 9.1 `job125_avoid3.py` — 회피 주행 계측판(이 카드에서는 '정지' 를 보여 준 도구)
- 부른 형태: `python3 job125_avoid3.py [D=1.80] [timeout=90] [csv이름]` — job170 · 175 등은 이름 인자.
- 하는 일(이 카드에 관련된 부분): 시작 때 `map→base_link` · 점군 · 로컬 코스트맵이 올 때까지 20 s 대기, 카메라 정적 TF 대기, 전방 상자 검출 → NavigateToPose(정면 D m) → 0.1 s 마다 `pose()`(= `lookup_transform('map','base_link', Time())`)가 `None` 이 아니면 한 줄: t · 전진 · 횡 · 기하 여유 · 계획 여유 · 계획 횡 · 로컬/전역 상자 자리 비용 · v · ω · 상자 안 깊이점 수 → 1 초마다 화면 → 끝에 CSV `/tmp/<이름>.csv` 와 ①~⑥ 요약.
- 이 카드의 서명이 생기는 곳: `Time()` 조회는 '버퍼의 최신 변환' 이라 새 TF 가 안 오면 같은 값을 돌려준다 → 같은 값 줄이 쌓인다 → 버퍼 보관 10 s 가 지나면 예외 → `None` → 그 뒤로 줄이 안 생김(루프는 목표 결과 · 시간 제한까지 계속 돎). 그래서 '17 자리 같은 99 샘플 + 9.90 s 뒤 기록 끝' 이 나왔다.
- 결함(이 카드 관점): 변환 stamp 를 기록하지 않아 '정지' 와 '갱신 정지' 를 실시간으로 구분 못 함. 상자 검출은 09-10 §9 에서 벽을 상자로 보는 결함이 드러남(다른 카드).
- 출력: CSV 원천 소실, 화면 출력은 SUMMARY 인용만.

### 9.2 `job171_chk.sh` — 주행 뒤 상태
- 하는 일: `/rover/status` level · message · 값 6 줄(스톨 카운터 `sc`) → 배터리 5 회 → `/tf` · `/odometry/filtered` · `/wheel_odom` · `/map` hz · filtered 퍼블리셔 수 · fastrtps 잔재 수 → nav2 로그 cancel|abort|stuck|backup|recovery|fail 6 줄 → load.
- 쓰인 곳: §8.13 의 '래치 아님 · 전압 · TF 정상' — 주행 **뒤** 시점(§6 모순 5).

### 9.3 `job172_freeze.sh` — 정지 시각 전후 로그 ★
- 하는 일: nav2 로그에서 대괄호 안 epoch 시각이 `17889432[3-6]x.` 인 줄(= job170 정지 시각 ≈ 1788943244 의 앞뒤 약 25 s, 숫자를 손으로 넣음) 25 줄 → sensors 로그의 ekf · conditioner warn|error|update rate|died 10 줄 → slam warn|error 5 줄 → `/tf --verbose` 발행 주체 → `/odometry/filtered` 1 초 버킷 20 개(20 개 미만이면 '← 이상').
- 출력: §2 의 t ≈ 4.0 ~ 14 시각표(SUMMARY §8.14 표). 원문 없음.
- 결함: 시각 범위가 하드코딩(다른 주행엔 고쳐 써야 함). `/tf --verbose` 집계 함정([DDS 카드 §5.3](dds-shm-incident.md)).
- 지금: 'stamp 로 로그를 자르기' 형태는 유효 — 이후 bag 기반 분석으로 대체.

### 9.4 `job176_who.sh` · `job177_env.sh` — 재발 뒤 진단
- [DDS 카드 §9.12](dds-shm-incident.md) 에 상세. 이 카드에 쓰인 값: job177 의 `grep -a 'Failed to meet update rate' | grep -aoE "Took [0-9.]+"` → awk 로 평균 · 최대 · n = **91 회 · 0.055 s · 0.197 s**, slam 로그 수준별 건수(INFO 30 · WARN 1), 'dropping 이 아닌 마지막 로그'(= 'Registering sensor').
- 읽는 법: EKF `frequency` 30 Hz → 목표 주기 0.033 s. `Took` 은 그 주기 한 번의 실제 소요. 평균 0.055 s 면 평균적으로 18 Hz 쯤으로 밀린 것(계산).

### 9.5 `job178_imu.sh` — 카메라 IMU fps 배포 · 검증
- 하는 일: `/tmp/camera.launch.py` CR 제거 · src · install 복사 · `'gyro_fps': N` 확인 → Nav2 · slam · 센서 노드 TERM → launch 3 개 TERM → 최대 15 s 대기 → 잔존 → **로그 비움**(`: > /tmp/sensors.log` 등) → sensors(28 s) → slam(14 s) → nav2(30 s) → 효과 검증: `/camera/camera/imu` · `/imu/data` · filtered · `/map` · `/tf` hz, `/tf` 퍼블리셔('3 이 정상'), slam 노드, EKF 위반 · slam 폐기 누계, conditioner CPU(`ps -p <첫 pid> -o %cpu`), load, top 상위 5.
- 결함: `pgrep -fc … || echo 0` 두 줄(대기 루프만 영향). conditioner CPU 는 첫 pid — 감싸개일 수 있음. `ps %cpu` 는 프로세스 생애 평균(직전 구간 아님) — 기동 30 s 뒤면 초기 부하가 섞인다(**추정**).

### 9.6 `job179_clean.sh` → `job181_dedup.sh` — 정리 · 재기동 · 검증(결함판 → 수정판)
- job179: 패턴 21 개 TERM → 1 s 간격 최대 15 회 `n=$((n+$(pgrep -fc "$p" 2>/dev/null || echo 0)))` 로 합계 → 0 아니면 `-9`('SHM 비활성이라 잔재 위험 없음') → 재기동(로그 비움) → job178 과 같은 검증.
- job181: 같은 흐름에 `cnt()` 함수(`pgrep -fc | head -1`, 빈 값 0)로 합계, 정리 전 · TERM 뒤 · KILL 뒤 합계를 찍음 → 재기동 → slam 인스턴스 수('1 이 정상'), `/tf` 발행 노드별 수(여전히 `--verbose` 전체), 5 토픽 hz, 위반 · 폐기, 열린 Accel/Gyro 프로파일(`stream_type: (Accel|Gyro)(0)Format: MOTION_XYZ32F, FPS: N`), load, top.
- 결함: §5.3(job179). job181 의 `/tf` 집계는 §5.3([DDS 카드](dds-shm-incident.md)) 함정 그대로.
- 지금: `cnt()` 형태가 09-11 job240 · 249 로 계승. 이후 prep 스크립트로 흡수.

### 9.7 `job180_imuparam.sh` — 배포값 vs 실제 열린 프로파일
- 하는 일: 설치본 camera.launch 의 `gyro_fps|accel_fps|unite_imu` 줄 → `ros2 param get /camera/camera` 로 gyro_fps · accel_fps · unite_imu_method · enable_gyro · enable_accel → sensors.log 의 `Open profile … (Accel|Gyro)` 4 줄 → FPS 가 든 Gyro/Accel 줄 6 개 → `/tf --verbose` 의 Node name 을 `sort | uniq -c`.
- 출력: `Gyro FPS: 200` · `Accel FPS: 100`(§5.2). 원문 없음.
- 읽는 법: ROS 파라미터 값(요청)과 드라이버 로그의 열린 프로파일(실제)이 다를 수 있다 — 판정은 로그 쪽.
- 결함: 마지막 `/tf` 집계가 'slam 중복' 오독을 낳음.

### 9.8 `job182_s6base.sh` — S6 기준선(09-10) ★(단, CPU 칸 주의)
- 하는 일: nav2 로그 비우고 navigation.launch(32 s) → lifecycle 4 개 · 로컬 레이어 목록 → 측정 시작 시점 EKF 위반 · slam 폐기 누계 기록 → `top -b -n 30 -d 1 -o %CPU > /tmp/s6top.txt` 백그라운드 → 31 s → 끝 누계 → 차분 '/ 30초 ← 종료조건 0' · load '< 6' → awk 이름별 평균 CPU 상위 10 → 6 토픽 hz · 배터리.
- 출력: §2 의 09-10 §1 줄. 원문 없음(`/tmp/s6top.txt` 원천 소실).
- 결함: CPU 칸이 이름별 '줄당 평균'(§6 모순 1) — 같은 이름 프로세스가 여럿이면 낮게 나온다(python3 가 대표). 위반 · 폐기 차분은 정확.
- 지금: 위반 · 폐기 30 s 차분 방식은 유효. CPU 는 pid 단위 도구(10-12 `Docs/tools/anal_proc_cpu.py`)로.

### 9.9 `job189_wait.sh` · `job190_err.sh` · `job191_nofg.sh` — Nav2 기동 실패 → Foxglove 판별(09-10 §4)
- job189: 20 s 기다린 뒤 lifecycle 5 개 · 코스트맵 2 개 hz · nav2 오류 3 줄 · EKF 위반 · slam 폐기 누계 · load 한 줄.
- job190: nav2 로그에서 `Failed to change state|Exception|Timed out|planner_server` 8 줄 + planner_server 관련 10 줄(200 자).
- job191: `ss -tn | grep :8765`(브리지 웹소켓에 붙은 클라이언트) → `pkill -TERM -f foxglove_bridge` → 3 s → 남은 수 → job182 와 같은 30 s 창(위반 · 폐기 차분 · load · 이름별 CPU 상위 7) → lifecycle 5 개.
- 출력: load 6.35 · 위반 86 · 폐기 28 · `foxglove_bridge` 69.6 % · `ESTAB … ← 192.168.0.6:65351` · 정지 뒤 0 · 0 · active(09-10 §4). 원문 없음. 69.6 % 가 어느 도구의 top 인지는 SUMMARY 미표기.
- 결함: '정지 전' 창(86 · 28)은 job189 의 기동 이후 **누계**이고 '정지 뒤' 창(0 · 0)은 30 s **차분** — 창 길이가 달라 수치를 그대로 비교할 수 없다(방향은 분명, **추정** — job189 시점 누계 창 길이는 기동부터 약 50 s+). 브리지를 껐을 때 클라이언트 끊김과 브리지 자체 부하 제거가 함께 일어나 둘을 가르지 않음(09-30 측정은 '연결 vs 끊김' 으로 다시 함).
- 지금: `ss -tn | grep :8765` 는 '누가 보고 있나' 를 확인하는 가장 싼 방법 — 계속 유효.

### 9.10 (09-17) `job384_power.sh` — 지금 전력 모드 · 클럭 · 온도
- 실행 위치 · 형태: Jetson, 인자 없음(sudo 불필요). 로버 안 움직임. 감싸개 `run_j.sh`(PC WSL, 스크래치패드 — 소실).
- 왜: mp7 의 루프 미달 60+ 가 '클럭이 낮게 잡혀서' 인지 보려고.
- 하는 일: `nvpmodel -q` → `/sys/devices/system/cpu/online` · cpu0 governor → 코어마다 `scaling_cur_freq/scaling_max_freq`(MHz) → `cpuinfo_max_freq`(하드웨어 상한) → `jetson-clocks` · `nvfancontrol` 서비스 활성 여부 → syslog 의 9/16 · 9/17 nvpmodel 줄 → thermal zone 온도 → cpufreq `time_in_state` 상위 3(있으면) → load · uptime.
- 출력: **원천 소실**(대화에만). SUMMARY §5 에 '15W(ID 0), CPU 최대 1497 MHz, 하드웨어 최대 1728' 로 옮겨 적힘.
- 결과가 쓰인 곳: §5 '사용자 결정 필요 — 15 W → 25 W' 제안(근거 수치는 이 도구가 아니라 내 추정).
- 알려진 결함: 모드별 상한(conf)을 읽지 않는다 — 이것이 §5.5 실수의 빈칸이었다.
- 지금 다시 쓸 수 있나: 예(읽기만).

### 9.11 (09-17) `job385_pmhist.sh` — 모드 이력을 찾을 수 있나
- 하는 일: `/var/lib/nvpmodel/status` 내용 · 수정 시각 → `/etc/nvpmodel.conf` 의 `PM_CONFIG DEFAULT` 줄 · `POWER_MODEL ID` 줄들 → `last -x reboot` 4 줄 → syslog(.1 포함)의 nvpmodel · Power Mode 줄 6 개 → `/var/log/nvpmodel*`.
- 출력: **원천 소실**. SUMMARY §5: 'conf 기본은 25W', '상태 파일은 부팅 때 다시 쓰여 어제와 달라졌는지는 확인 불가'.
- 읽는 법: conf 기본이 25 W 인데 운용은 15 W 였다 → 누군가(언제?) 15 W 로 바꿔 두었다는 뜻. 그 시점 · 이유는 **미확인**.
- 지금 다시 쓸 수 있나: 예.

### 9.12 (09-17) `job388_pm25.sh`(+ `run_pm25.sh`) — 15 W → 25 W 전환 (사용자 승인)
- 실행 위치 · 형태: Jetson, sudo. 감싸개 `run_pm25.sh`(PC WSL)가 `__PW__` 를 `sed` 로 넣어 올리고 실행 뒤 원격 파일 삭제(저장소 사본은 `<PW>`).
- 하는 일: ① DDS 패키지 5 종 설치 · 후보 버전(이 부분은 [SLAM 데드락 카드 §9.8](slam-dds-deadlock.md)) ② 전: `nvpmodel -q` 첫 줄 · cpu0 상한 → `nvpmodel -m 1` → 3 s → 후: 모드 · 6 코어 상한 · online → 온도 2 개 → 배터리 한 번.
- 출력: [`outputs/j388_pm25.txt`](../debug_log/2026-09-17/outputs/j388_pm25.txt) — '전: NV Power Mode: 15W cpu0 max 1497 MHz' · '후: NV Power Mode: 25W cpu max: 1344 1344 1344 1344 1344 1344 MHz online 0-5' · 47 °C · 12.12 V.
- 결과가 쓰인 곳: §6.2 '추정 오류' 판정 — 전후 상한을 같은 스크립트에서 찍은 덕에 바로 드러남.
- 알려진 결함: 전환 전에 conf 의 25 W 블록을 보지 않았다(스크립트 순서상 '먼저 바꾸고 나중에 본다'). 실제 처리 속도는 재지 않음(§6 ⑥).
- 지금 다시 쓸 수 있나: 모드 바꾸는 일은 사용자 결정 사항 — 쓰려면 conf 확인을 앞에 넣는다.

### 9.13 (09-17) `job389_pmconf.sh` · `job390_pmrevert.sh`(+ `run_pmrevert.sh`) — conf 표와 원복
- `job389`(sudo 불필요): conf 의 `POWER_MODEL ID=` 블록마다 CPU_ONLINE · FREQ · EMC · GPU_POWER · CPU_A78 줄(최대 60 줄) → 10 s 뒤 6 코어 cur/max/min → `scaling_available_frequencies` → `nvpmodel -q --verbose` 의 cpu · freq 줄. 출력 **원천 소실**.
- `job390`(sudo): conf 에서 모드별 `CPU_A78_0 MAX_FREQ` · `GPU MAX_FREQ` · `EMC MAX_FREQ` · `CPU_ONLINE CORE_5` 를 'ID=… NAME=… :: 줄' 로 → `nvpmodel -m 0` → 3 s → 원복 뒤 모드 · 6 코어 상한.
- 출력: [`outputs/j390_pmrevert.txt`](../debug_log/2026-09-17/outputs/j390_pmrevert.txt) — §4.1 의 모드별 표 원천(15W CPU 1497600 · GPU 612000000 · EMC 2133000000 / 25W 1344000 · 918000000 · 3199000000 / MAXN_SUPER −1 · −1 · −1, 원복 뒤 1497 ×6).
- 단위 주의: conf 의 CPU 값은 kHz(1497600 = 1497.6 MHz), GPU · EMC 는 Hz.
- 지금 다시 쓸 수 있나: `job390` 의 앞부분(모드별 상한 표)은 모드를 고민할 때 먼저 볼 표 — 그대로 유효.

## 10. 용어
- **tf2 버퍼 · `Time()` 조회**: TF 리스너는 받은 변환을 시간순으로 보관(기본 10 s)한다. `lookup_transform(목표, 원천, Time())` 의 `Time()`(0)은 '가장 최근 것' 을 뜻한다 — 새 변환이 안 와도 보관 기간 동안은 낡은 값을 그대로 준다.
- **EKF 주기 위반(`Failed to meet update rate`)**: robot_localization 이 설정 주기(30 Hz = 0.033 s) 안에 한 번의 예측 · 갱신을 못 끝냈다는 경고. 'Took 0.14s' 는 그 회차 소요.
- **메시지 필터(message filter) 폐기**: slam_toolbox 는 스캔마다 '스캔 stamp 시각의 odom→base_link' 를 TF 에서 찾아야 한다. 그 시각의 변환이 아직 없으면 큐에 두고 기다리다, 큐가 차거나 시간이 지나면 `Message Filter dropping message` 로 버린다. odom TF 가 늦게 오면 전부 버려질 수 있다.
- **load average**: 실행 중 + 실행 대기 작업 수의 1 · 5 · 15 분 평균. 코어 수(이 Jetson 6)를 넘으면 대기가 생긴다 — 9.01 / 6 은 포화.
- **top %CPU · 이름별 집계**: %CPU 는 직전 구간 사용률(코어 1 개 = 100 %). `top -b` 는 모든 프로세스를 찍으므로 이름으로 묶어 평균하면 같은 이름 다수 프로세스(python3)가 희석된다.
- **nvpmodel · 전력 모드**: Jetson 의 전력 · 클럭 상한 모드(`nvpmodel -q` 로 조회, `sudo nvpmodel -m N` 으로 변경, 정의는 `/etc/nvpmodel.conf` 의 `POWER_MODEL ID=N NAME=…` 블록). 이 장비는 15 W(ID 0, CPU 최대 1497 MHz)가 운용점이었고(09-17 기록), 25 W(ID 1)는 CPU 상한이 1344 MHz 로 **오히려 낮고** GPU 918 · 메모리(EMC) 3199 MHz 로 높으며, MAXN_SUPER(ID 2)만 상한 없음(CPU 하드웨어 최대 1728 MHz). 모드 이름의 W 는 전력 예산이지 CPU 속도가 아니다.
- **`scaling_max_freq` · `cpuinfo_max_freq` · `scaling_cur_freq`**: 리눅스 cpufreq 의 '지금 허용된 최대 클럭'(nvpmodel 이 정함) · '하드웨어가 낼 수 있는 최대' · '지금 클럭'(kHz). 모드 효과를 볼 때는 `scaling_max_freq` 를 바꾸기 전 · 후로 읽는다.
- **EMC**: Jetson 의 외부 메모리 컨트롤러(메모리 클럭). 모드마다 상한이 다르다.
- **`unite_imu_method 1(copy)`**: realsense 드라이버가 자이로 · 가속도를 한 IMU 토픽으로 합칠 때, 자이로 샘플마다 가장 최근 가속도를 복사해 붙이는 방식. 토픽 주기는 자이로 주기를 따른다.
- **S6(Phase S)**: `NVBLOX_MIGRATION_PLAN.md` 의 'CPU 여유 확보' 항목. 09-21 Phase S 종료 때 기준선 수치로 대체됐다.
- **열화(이 카드에서)**: 긴 세션 · 재기동 반복 뒤 같은 스택이 재부팅 직후보다 무거워지는 현상에 09-10 이 붙인 이름. 무엇이 쌓이는지는 재지 않았다.
