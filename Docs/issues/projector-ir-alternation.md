# 프로젝터 번갈이 · IR — cuVSLAM 용 IR 과 깊이 점 사이의 충돌, 상시 끔 결정 (8 기: 10-19 §15~§17.1 · §19 · §19.1 · §20 · §23 · §23.1 · §24 · §24.1 · §25 · §25.1, 10-20 §1 · §2 · §2.1, 10-21 §16 ~ §20)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **우회**(10-21 §20 사용자 결정 — 프로젝터 **상시 끔** 유지). 번갈이는 두 구현(우리 분리 노드 · NVIDIA 권장 구성) 모두 정지 시험에서 같은 벽에 막혔다: 자동 노출이 켠 프레임(점 무늬)에 맞춰져 끈 IR 이 어둡고(측정), 번갈이 중 실행 중 노출 · 게인 쓰기는 거부되거나 번갈이를 깬다(측정). 상시 끔이면 cuVSLAM 이 이동을 따라갔다(f2z1 1 회, 위치 오차 95 % 25.7 cm · yaw 0.8°). 대가 = 무늬 없는 바닥의 깊이 구멍 · 맨바닥 유령 칸 → [유령 칸 · 깊이 프리셋](ghost-cells-depth-preset.md). 원인이 남은 것: 메타데이터 `frame_emitter_mode` 뒤집힘(카메라 펌웨어 5.15 탓인지 미판별), 번갈이 + 기동 파라미터 수동 노출 절충(24 ms × 248)의 주행 효과(미측정) | 10-19 ~ 10-21 (앞 이력 09-29 §10 · §10.1 O1 채택) | [10-19 §15.1](../debug_log/2026-10-19/SUMMARY.md) S1 첫 시험 '반대로 나뉨'. 핵심 증상은 [10-19 §20](../debug_log/2026-10-19/SUMMARY.md) 끈 IR 어두움 · §23.1 cuVSLAM 이 이동을 못 따라감 | 새 [`emitter_splitter.cpp`](../../ros2_ws/src/rover_bringup/src/emitter_splitter.cpp)(커밋 `82eb43eb` §15 · `d1edc058` §16 · `7355c370` §17) · [`CMakeLists.txt`](../../ros2_ws/src/rover_bringup/CMakeLists.txt) 25~29 행 · [`camera.launch.py`](../../ros2_ws/src/rover_bringup/launch/camera.launch.py) 인자 `emitter_flash` · `stereo_fps` · `emitter_off`(115~117 행) · 러너 `BAG_IR`([`job551_f0drive.sh`](../debug_log/2026-10-27/jobs/job551_f0drive.sh) 38 · 70 · 95 행) · [`prep_patrol.sh`](../tools/prep_patrol.sh) `SENSORS_ADD`(16 행). 저장소 밖(Jetson): 이미지 `isaac_ros_dev-aarch64-rs:{latest,apt}` · 시험 컨테이너 `isaac_rs_test`(10-21 §17 · §18, 남겨 둠) | [Isaac · cuVSLAM 평가](isaac-cuvslam-evaluation.md)(09-29 O1 채택 · O2 기각 — 이 카드의 앞 이력) · [유령 칸 · 깊이 프리셋](ghost-cells-depth-preset.md)(상시 끔의 대가, 10-21 §13~§15 · §21~) · [cuVSLAM 속도 융합](cuvslam-velocity-fusion.md)(상시 끔 위에서 10-23 기본 채택) · [카메라 ↔ 컨테이너 SHM](camera-container-shm.md)(§16.1 의 'UDP 로 큰 영상' 손실이 10-20 §7 로 이어짐) · [상자 과장 출처](box-exaggeration-source.md)(§15 의 투입 근거 = 10-19 §14 기억 밀림, 10-20 §2 북 면 과장) · [주행 운용 10-19~23](drive-ops-1019-1023.md)(f2y1 · f2z1 게이트) · [DDS 공유메모리 사고](dds-shm-incident.md) · [CPU 부하](cpu-load-stalls.md)(§16.1 CPU 77 %) · [로그 · 산출물 정리 보류](storage-housekeeping.md)(GB 급 IR bag, 10-19 §18 · §18.1) · [깊이 점군 아티팩트 · depth_relay](depth-relay-artifacts.md)(10-21 §20: nvblox 깊이엔 필터 없음) |

**한 줄**: 같은 D455f 를 nvblox(점 무늬 켠 깊이)와 cuVSLAM(점 무늬 없는 IR)이 나눠 써야 해서 09-29 에 '번갈이(O1)' 를 골라 두었다. 10-19 에 분리 노드를 만들어 나누기 자체는 맞게 했지만(메타데이터 값이 거꾸로라 `on_mode 0` 으로), 호스트 DDS 로 큰 IR 영상을 나르면 30 Hz 중 21 Hz 만 도착해 드라이버와 한 프로세스로 합쳤고, 그렇게 기록한 f2y1 의 끈 IR 은 너무 어두워 cuVSLAM 이 이동을 못 따라갔다(켠 IR 은 점 무늬에 붙잡혀 이동 ≈ 0). 원인은 '조명에 근적외선이 없다' 가 아니라 **자동 노출이 켠 프레임에 맞춰진 것**(같은 자세에서 번갈이 밝기 17.7 vs 상시 끔 44)이었고, 번갈이 중엔 노출을 고정할 수 없었다. 프로젝터 **상시 끔** 주행 f2z1 에선 cuVSLAM 이 따라갔다(위치 95 % 25.7 cm vs EKF 57.2). 10-21 에 NVIDIA 권장 구성(드라이버 4.51.1 · librealsense 2.55.1 · `realsense_splitter`)을 컨테이너에 세워 다시 쟀지만 같은 두 문제(메타 뒤집힘 · 끈 IR 어두움)가 재현됐고, 기동 파라미터 수동 노출은 들어가지만 켠 깊이를 20 % 잃고 긴 노출에선 점이 끈 프레임에 새어 들었다. 사용자는 **상시 끔 유지**를 정하고 대가인 유령 칸 대응으로 넘어갔다(§20).

## 1. 증상
- **분리가 거꾸로**(10-19 §15.1 첫 시험, 60 fps 번갈이 · 정지) — [`run_split_s1_first.txt`](../debug_log/2026-10-19/outputs/run_split_s1_first.txt):
  ```
    원시 깊이 유효 비율: 켬 중앙 0.318 (n 596, 0.285~0.363) · 끔 중앙 0.768 (n 598, 0.758~0.780) · 메타 없음 0 · 비 2.41
    분리 깊이 유효 비율: n 595, 중앙 0.318, 범위 0.285~0.363, 가운데(0.543) 아래 쪽 프레임 595
    원시 IR1 |라플라시안|: 켬 중앙 0.616 (n 579, 0.601~0.654) · 끔 중앙 5.780 (n 529, 5.768~5.815) · 메타 없음 3 · 비 9.39
  ```
  여기서 '켬' 은 메타데이터 `frame_emitter_mode == 1` — 그 프레임의 깊이 유효 비율이 낮고 IR 점 무늬가 없다 = 실제로는 **꺼진** 프레임.
- **끈 IR 이 어둡다**(10-19 §20, f2y1 230 s) — [`f2y1_ir_pairs.csv`](../debug_log/2026-10-19/outputs/f2y1_ir_pairs.csv) 3414 짝. 11-03 재계산(같은 csv, 중앙 · 5~95 %): 끔 밝기 20.0(17.5~39.6) · |라플라시안| 0.80 · **FAST20 6**(0~428), 켬 31.9 · 11.1 · 2674. 구간별 끔 FAST 중앙: t 0~70 s 18 · **t 70~125 s 291.5**(창가) · **t 130~230 s 0**(최대 17). 그림 [`f2y1_ir_drive_t172.png`](../debug_log/2026-10-19/figures/f2y1_ir_drive_t172.png) · [`_timeline.png`](../debug_log/2026-10-19/figures/f2y1_ir_drive_timeline.png).
- **cuVSLAM 이 이동을 못 따라감**(10-19 §23.1) — 네 변형 모두 SLAM 대비 1.4~11 m(EKF 0.4 m), 그런데 vo_state 는 모두 '성공 100 %'(§3 발췌).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-29 §10.1(앞 이력) | M1 켬/끔 깊이 · M2 60 Hz 번갈이 | 끔 아래 절반 유효 = 켬의 45 % → O2(상시 끔) 기각, M2 메타 0/1 교대 · 카메라 CPU 9.8 % → O1(번갈이) 채택 | O1 채택. ⚠ M2 는 교대만 확인 — **어느 값이 켬인지는 안 잼**(10-19 §15.1 이 지적) | [Isaac 카드](isaac-cuvslam-evaluation.md) §2 · `2026-09-29/outputs/j651_654_emitter.txt` |
| 10-19 §15 | 사용자 "분리 노드부터" → 호스트 C++ `emitter_splitter_node`. S1 정지 판정 선언(S1-a ≥ 27 Hz · S1-b 두 무리 1.5 배 · 전 프레임 가운데 위/아래 · S1-c ≤ 1 % · S1-d ≤ 15 %) | — | Isaac `realsense_splitter` 는 컨테이너 · apt 에 없고(09-29 §10) 카메라가 호스트라 같은 판정을 하는 작은 노드로 | SUMMARY §15 · 커밋 `82eb43eb` |
| 10-19 §15.1 첫 시험 | 60 fps 번갈이, 메타 1 = 켬 가정 | §1 — 깊이 0.318 vs 0.768, IR 0.62 vs 5.78, 두 무리 겹침 0 | **반대로 나뉨**. 값 반전 · 한 프레임 밀림은 교대 중 구분 불가 → 파라미터 `on_mode`(기본 0 = 실측) + 내보낸 깊이 유효 비율을 10 s 통계에 | [`run_split_s1_first.txt`](../debug_log/2026-10-19/outputs/run_split_s1_first.txt) |
| 10-19 §15.1 재시험 | on_mode 0 | 분리 깊이 29.5 Hz · 591/591 가운데 위(0.764~0.785), IR1 539/539 아래, 분리 CPU 12.0 %. **IR 26.9 · 26.6 Hz(✘ 경계)** · IR1 교대깨짐 1.1 %(✘ 경계) · 카메라 CPU **38.2 %**(지금 설정 14.9). IR 은 640×480 그대로(데시메이션은 깊이에만) | 나누기 ✔(오분류 0). 남은 것 = 호스트 → 구독자 DDS 로 큰 영상(≈ 37 MB/s)을 나르는 비용(추정) | [`run_split_s1.txt`](../debug_log/2026-10-19/outputs/run_split_s1.txt) · [`anal_split_s1.py`](../debug_log/2026-10-19/jobs/anal_split_s1.py) |
| 10-19 §16 | 주행 스택에 번갈이: `camera.launch emitter_flash:=true stereo_fps:=30`(켬 15 · 끔 15), 드라이버 영상 → `/camera/raw/...`, 분리 노드가 원래 이름으로. 러너 `BAG_IR=1`. S2 정지 판정 선언(③ CPU ≤ 60 % · EKF 위반 ≤ ① + 2 · 흐름 · IR 기록 ≥ 27 Hz) | 30 fps 를 고른 이유: 켬 깊이 15 Hz = 지금 nvblox 입력과 같음, 부하 절반 | — | SUMMARY §16 · 커밋 `d1edc058` |
| 10-19 §16.1 | S2 ① 지금 ② 번갈이 30 ③ 번갈이 + `ros2 bag record` | ③ CPU **77.2 %** · EKF 위반 **+127** · /odometry 25.0 Hz · nvblox 깊이 12.6 · 기록 IR **7.7~8.7 Hz**. ② 만으로도 분리 노드 IR 입력 210~219/300 · 교대깨짐 16 % | **불합격, 기록 주행 안 함**. 스택 부하 아래 호스트 DDS(UDP) 로 307 kB 영상을 나르는 길에서 잃음(측정: 도착 수) — 사용자 CPU 우려가 맞음 | [`chk_flash_s2_base.txt`](../debug_log/2026-10-19/outputs/chk_flash_s2_base.txt) · [`chk_flash_s2_flash30.txt`](../debug_log/2026-10-19/outputs/chk_flash_s2_flash30.txt) · `_afterbuild.txt`(빌드 직후 오염판) · [`chk_flash_s2.sh`](../debug_log/2026-10-19/jobs/chk_flash_s2.sh) |
| 10-19 §17 · §17.1 | 사용자 "1과 2 같이" — ① 드라이버 + 분리 노드를 한 `component_container_mt`(`realsense2_camera_container`) ② 분리 노드 안 `rosbag2_cpp::Writer` 기록(`record_path`) | ②' 합성: IR 입력 **298/300** · 교대깨짐 0~1 %. ③' 합성 + 기록: CPU 54.3 · 55.5 % · 기록 IR **29.6 · 29.9 Hz** · 메타 100 % · 컨테이너 58.9~59.4 %. EKF 위반 +28 · +7 | 합성 효과 ✔. EKF 위반 '≤ ① + 2' 는 ✘ 였으나 ① 을 반복하니 +0 · +10 · +13 — **기준을 ① 1 회 값에 묶은 선언이 잘못**(정정 읽기: ① 과 구별 안 됨, 표본 작음 — 추정) | [`chk_flash_s3_comp.txt`](../debug_log/2026-10-19/outputs/chk_flash_s3_comp.txt) · [`chk_flash_s3_repeat.txt`](../debug_log/2026-10-19/outputs/chk_flash_s3_repeat.txt) · 커밋 `7355c370` |
| 10-19 §19 · §19.1 | IR 기록 주행 f2y1(b910 1 회, `SENSORS_ADD="emitter_flash:=true"`, `BAG_IR=1`) — 선언: 3/3 · IR ≥ 27 Hz · 메타 ≥ 95 % | 게이트 통과(P 54 %), **3/3**(53.4 · 49.1 · 110.4 s). IR bag 4.0 GiB / 230 s, 좌우 6855 장 = 29.8 Hz, 메타 100 %. 주행 중 IR 입력 298~300/10 s. 로그 누계 EKF 위반 53 · slam 폐기 42 · 제어 놓침 52(f2x1 과 같은 잣대 비교는 미완) | 기록 주행으로 사용 ✔ | [`run_f2y1.txt`](../debug_log/2026-10-19/outputs/run_f2y1.txt) · [`chk_f2y1.sh`](../debug_log/2026-10-19/jobs/chk_f2y1.sh) · Jetson `~/bags/bag_f2y1_ir`(정리 대기, 10-20 §10) |
| 10-19 §20 | 사용자 "영상부터" — IR 짝 영상 | §1 — 끔 FAST 중앙 6, 복귀 길 0~10, 창가만 수백 | '끈 IR 은 특징이 거의 없다'. 원인 후보 = 번갈이에서 켠 프레임 밝기가 자동 노출을 끌어내림(추정, 미확인). **'FAST 6 = 특징 없음' 은 §24.1 에서 과장으로 정정** | [`fig_ir_extract.py`](../debug_log/2026-10-19/jobs/fig_ir_extract.py) → [`f2y1_ir_pairs.csv`](../debug_log/2026-10-19/outputs/f2y1_ir_pairs.csv) · [`fig_ir_drive_video.py`](../debug_log/2026-10-19/jobs/fig_ir_drive_video.py) → 영상 `figures/f2y1_ir_drive.mp4`(git 제외) |
| 10-19 §23 선언 · §23.1 | 오프라인 cuVSLAM: f2y1 IR 을 메타로 `/off` · `/on` 으로 나눠 컨테이너에서 재생, 두 cuVSLAM × IMU 융합 켬/끔. 기준 = SLAM camera_link 자세, 첫 자세만 맞춤. C1 vo_state ≥ 95 % · C2 끝 · 95 % 가 EKF 의 절반 이하 | 네 변형 vo_state 100 %, 위치 오차 끝 137~1097 cm · 95 % 469~1592 cm vs EKF 40 · 36 cm. 켬 = 이동 ≈ 0(±1 cm), 끔 · IMU 끔 = 한 번 (−31, +25 cm, +21°) 튀고 멈춤, 끔 · IMU 켬 = IMU 적분으로 흘러감(z +0.9 m) | **C2 불합격** — 이 조건에선 못 씀. **vo_state '성공' ≠ 정확**. 그때 판정 문장 '이 조명(LED, 근적외선 거의 없음 — 추정)에서 끈 IR 이 장면을 거의 못 본다' 의 원인 부분은 §24.1 · §24.2 측정이 뒤집음(§5 기록 어긋남 2) | [`anal_vslam_cmp_f2y1.txt`](../debug_log/2026-10-19/outputs/anal_vslam_cmp_f2y1.txt) · [`outputs/vslam_f2y1/`](../debug_log/2026-10-19/outputs/vslam_f2y1/) · [`vslam_cmp_f2y1.png`](../debug_log/2026-10-19/figures/vslam_cmp_f2y1.png) |
| 10-19 §24 선언 · §24.1 | 번갈이 중 노출 · 게인 고정(대책 ②). 판정: 끈 IR FAST 중앙 ≥ 100 **그리고** 켠 깊이 ≥ 자동의 90 % | 자동: 실제 노출 **31979 µs(30 fps 최대) · 게인 16(최소)**, 끈 IR 17.7 · FAST 0. 수동 노출 · 게인 **드라이버 거부**(`xioctl(UVCIOC_CTRL_QUERY) failed on control 3` · `VIDIOC_S_CTRL … errno=84`). 자동 노출 끔 → 메타는 교대를 보고하지만 **두 프레임 모두 점 무늬**(밝기 28.4 · 28.5, FAST 2463 · 2486) | **② 기각**(이 드라이버 · 펌웨어 · 커널 조합). 첫 표의 설정별 값은 모두 33000 · 16 — 무효 | [`run_ir_exposure.txt`](../debug_log/2026-10-19/outputs/run_ir_exposure.txt) · [`chk_ir_exposure_diag.txt`](../debug_log/2026-10-19/outputs/chk_ir_exposure_diag.txt) · 그림 [`ir_flash_aeoff_both_dots.png`](../debug_log/2026-10-19/figures/ir_flash_aeoff_both_dots.png) |
| 10-19 §24.2(§24.1 안) | 번갈이 없이 프로젝터 끔 | 수동 게인 **됨**. 자동 밝기 44.0 · FAST 12, 게인 248 · 33 ms 45.5 · 25. 4 배 밝게 보면 의자 · 문 · 상자 · 테이프 또렷 | **정정(§20 읽기)**: FAST 절대 문턱 20 은 밝기 20~45 영상에서 과소 계산. 끈 IR 이 어두운 직접 원인 = **자동 노출이 켠 프레임 기준**(같은 자세 44 vs 17.7) | [`chk_ir_gain_off.txt`](../debug_log/2026-10-19/outputs/chk_ir_gain_off.txt) · 그림 [`ir_emitteroff_auto_vs_gain248_x4.png`](../debug_log/2026-10-19/figures/ir_emitteroff_auto_vs_gain248_x4.png) |
| 10-19 §25 선언 | 사용자 "프로젝터 끔 확인부터" — `camera.launch emitter_off:=true`(새 인자), 깊이 · IR 640×480×15, 원시 IR 만 `/camera/raw` → 분리 노드가 기록. 판정: 3/3 · IR ≥ 13.5 Hz, 오프라인은 **vo_state 가 아니라 SLAM 대비 위치**(95 % ≤ 50 cm 면 '따라감') | 정지 점검: 프로젝터 0 · 원시 IR 14.7 Hz · 깊이 15.0 · 자동 노출 **64.9 ms · 게인 169** | '상자를 치우고 주행' — **틀림, 10-20 §3.2 정정**(실제론 상자 둔 채) | SUMMARY §25 · [`chk_eoff.sh`](../debug_log/2026-10-19/jobs/chk_eoff.sh)(출력 파일 없음 — SUMMARY 서술뿐) · [`prep_eoff.sh`](../debug_log/2026-10-19/jobs/prep_eoff.sh) |
| 10-19 §25.1 | f2z1 주행 | **3/3**(50.3 · 50.5 · 102.3 s), stuck 1, 휠 −157.1° vs EKF −175.3°. IR bag 1.9 GB, 끈 IR 6474 장 | 판정은 다음 날(사용자) | [`run_f2z1.txt`](../debug_log/2026-10-19/outputs/run_f2z1.txt) |
| 10-20 §1 | f2z1 cuVSLAM 판정(§25 기준 그대로) | IMU 끔: 끝 **1.5** · 95 % **25.7** · 최대 31.6 cm, yaw \|95 %\| **0.8°**. IMU 켬: 7.1 · 29.5 · 34.1, 1.9°. EKF 59.8 · 57.2 · 60.9, 5.0° | **'따라감' ✔ 둘 다**, 'EKF 보다 낫다' IMU 끔 ✔ · IMU 켬 ✘(29.5 > 28.6, 경계). f2y1 과의 차이 = 끈 IR 밝기(32 ms · 16 → 65 ms · 169). 오차 성격: cuVSLAM 은 가는 길에 쌓이고 왕복으로 상쇄(끝 오차는 과대평가 — 95 % 가 공정), EKF 는 회전 때 계단(복귀 회전 +18.1 cm). 1 회 · 같은 코스 왕복 · SLAM 오차 섞임 | [`2026-10-20/outputs/anal_vslam_cmp_f2z1.txt`](../debug_log/2026-10-20/outputs/anal_vslam_cmp_f2z1.txt) · [`outputs/vslam_f2z1/`](../debug_log/2026-10-20/outputs/vslam_f2z1/) · [`vslam_cmp_f2z1.png`](../debug_log/2026-10-20/figures/vslam_cmp_f2z1.png) |
| 10-20 §1 함의 | 남은 충돌 정리 | — | 후보 (A) 번갈이 + **850 nm 무늬 없는 IR 조명** (B) 상시 끔 + 수동 스테레오 깊이(낮은 상자 놓침 위험 — 정량 필요) (C) cuVSLAM 을 EKF 에 속도로만 → C 는 [cuVSLAM 속도 융합](cuvslam-velocity-fusion.md) | SUMMARY §1 |
| 10-20 §2 · §2.1 | B 정지 시험(출발 자세, 상자 정면 1.15 m): ① 켬 ② 상시 끔, 각 prep → 20 s → 23 s 기록. 판정: 상자 칸 ② ≥ ① 80 % · 면 차 ≤ 3 cm · 빈 바닥 유령 ② ≤ ① + 2 | 깊이 아래 절반 유효 0.651 → **0.382**(59 %), 상자 부피 점 220 → 227, nvblox 상자 칸 10 → 13, 북 · 서 면 +5.5 · +2.0 → +5.1 · +2.1 cm, 빈 바닥 유령 0 · 0, 미지 21 % · 21 % | **정지 B 통과** — 단 '정지 정면 1.15 m' 는 쉬운 조건(움직일 때 · 비스듬히 · 멀리는 미확인). 상자는 인쇄 무늬가 있어 수동 스테레오로도 잡힘 | [`run_box_depth_ab.txt`](../debug_log/2026-10-20/outputs/run_box_depth_ab.txt) · [`anal_box_static.txt`](../debug_log/2026-10-20/outputs/anal_box_static.txt) · [`box_static_on_off.png`](../debug_log/2026-10-20/figures/box_static_on_off.png) |
| 10-20 §3 · §3.2(포인터) | 상시 끔 · 상자 둔 주행 f2z2 + f2z1 재해석 | 상시 끔 + 상자 2 회(f2z1 · f2z2) 모두 3/3, 출발 길 상자 안 칸 8(켬 · 번갈이와 같음), 복귀 상자 주변 흩어진 칸 21 · 27(켬 8) | 깊이 구멍으로 상자를 놓치는 일은 없었음(인쇄 무늬 상자 한정). 주변 칸 증가 → [상자 과장 출처](box-exaggeration-source.md) | [`anal_slice_box_f2z.txt`](../debug_log/2026-10-20/outputs/anal_slice_box_f2z.txt) |
| 10-21 §13~§15(포인터) | 출발점 둘레 · 문 사이 유령 칸 | 맨바닥 칸: 켬 주행 0~3, **끔 주행 28~99** | 상자 너머 맨바닥 점은 **프로젝터를 끈 뒤에만** — 09-29 M1 이 예고한 대가 → [유령 칸 · 깊이 프리셋](ghost-cells-depth-preset.md) | `2026-10-21/outputs/anal_zone_ghosts.txt` |
| 10-21 §16 | 사용자 "NVIDIA 추천 구성은 어떠한가. 그것으로 가자." — 문서 비교(주행 없음) | 권장: 펌웨어 5.13.0.50 · librealsense 2.55.1 · realsense-ros 4.51.1-isaac('벗어나면 예제가 깨진다'), 예제 `realsense_emitter_flashing.yaml` = 깊이 640×480×**60** 번갈이 · 점군 끔 · 분리 `realsense_splitter`. 지금: 펌웨어 5.15.0.2 · 2.58.3 · 4.58.3(호스트) | 10-19 시험은 구조(번갈이 + 분리)는 같고 버전 · 위치 · fps 가 달랐다. 메타 뒤집힘 · 자동 노출 끄면 번갈이 멈춤이 버전 탓인지 **미확인**. 끈 IR 어두움은 버전을 맞춰도 남을 수 있음(추정). 60 fps 면 노출 상한 ≈ 16 ms 라 더 어두울 쪽(추정) | 웹 출처(저장소에 원문 없음) · SUMMARY §16 표 |
| 10-21 §17 · §17.1 | 사용자 "펌웨어 낮출 필요 없다 · 2번 진행" — 새 이미지 `isaac_ros_dev-aarch64-rs`(지금 이미지 + `Dockerfile.realsense`) · 시험 컨테이너 `isaac_rs_test` · `realsense_splitter` 소스 빌드. 합격 (a)~(d) 선언 | 빌드 `BUILD_EXIT=0`(43.2 GB). (a) 2.55.1.0 · 4.51.1 ✔ (b) 빌드 1 분 30 초 · `nvblox::RealsenseSplitterNode` ✔ (c) nvblox · cuVSLAM 보임 ✔ — 같은 판 apt 설치 뒤 (d) 호스트 카메라 · 옛 컨테이너 그대로 ✔ | 합격. 전제 3 개가 틀려 고침(§5 실수 6): admin 사용자 · `COLCON_IGNORE` · **옛 컨테이너의 nvblox · cuVSLAM 은 이미지가 아니라 쓰기 층 apt 설치** | [`rs_image_build_end.txt`](../debug_log/2026-10-21/outputs/rs_image_build_end.txt) · [`up_rs_splitter_try2.txt`](../debug_log/2026-10-21/outputs/up_rs_splitter_try2.txt) · [`up_rs_apt.txt`](../debug_log/2026-10-21/outputs/up_rs_apt.txt) · [`chk_rs_ws2.txt`](../debug_log/2026-10-21/outputs/chk_rs_ws2.txt) |
| 10-21 §18 선언 · §18.1 | nv1 정지 시험: 시험 컨테이너 한 프로세스에 드라이버(NVIDIA yaml 그대로) + `realsense_splitter` + cuVSLAM. 단계 F 번갈이 60 s · 대조 O 상시 끔 30 s(같은 드라이버 · 장면). 판정 1~6 | 기준 1: 원시 깊이 **모드 0 = 0.681 · 모드 1 = 0.182**, IR \|lap\| 5.38 vs 0.40 → 실제 켬 = 모드 0. 기준 2: 분리 깊이 1619 장 전부 가운데(0.432) 아래. 기준 3: 분리 '끈' IR 1778 장 전부 점 무늬 · 노출 15365 µs · 게인 16, 진짜 끈 프레임 \|lap\| 0.40 = 대조 O(3.90) 의 10 %. 주기 ✔(깊이 27.0 경계). cuVSLAM 이동 0.00 cm(점 무늬 입력 — 뜻 없음) | **불합격(1 · 2 · 3)**. 메타 뒤집힘은 드라이버 판이 아니라 **카메라 쪽**(펌웨어 5.15 또는 장치)으로 좁혀짐 — 5.13 에선 어떤지 미확인. 끈 IR 어두움도 재현 → NVIDIA 구성 그대로 채택은 기각 | [`run_nv_static.txt`](../debug_log/2026-10-21/outputs/run_nv_static.txt) · [`anal_nv_static.py`](../debug_log/2026-10-21/jobs/anal_nv_static.py) · [`nv_static.launch.py`](../debug_log/2026-10-21/jobs/nv_static.launch.py) |
| 10-21 §18.2 | nv1 첫 실행 무효 | 전 토픽 0 Hz · cuVSLAM 적재 실패 | 실수 2 건(§5 실수 7): `-v /dev:/dev` 가 CUDA 메모리 풀을 막음 · 4.51.1 은 토픽에 노드 이름을 안 붙임 | [`run_nv_static_try1.txt`](../debug_log/2026-10-21/outputs/run_nv_static_try1.txt) · [`chk_nv_probe.txt`](../debug_log/2026-10-21/outputs/chk_nv_probe.txt) · [`chk_nv_cmp.txt`](../debug_log/2026-10-21/outputs/chk_nv_cmp.txt) |
| 10-21 §19 선언 · §19.1 | (나) mx1: 2.55.1 은 RSUSB 백엔드라 실행 중 수동 노출이 받아들여질 수 있다(추정). P60 · P30 단계 시험. 판정 1 수락(메타 ± 5 %) · 2 번갈이 유지 · 3 후보(끈 IR ≥ 대조 80 % · 켠 깊이 ≥ 자동 90 %) | P60: 수동 16000 µs **수락** 그러나 자동 노출 끄자마자(33000 > 프레임 16.7 ms) **번갈이 깨짐** · 이후 복구 안 됨. P30: 실행 중 쓰기 **실패**(`set_xu(id=3)` · `RS2_USB_STATUS_PIPE`, ROS 는 'ok'), 남은 16000 × 248 에서 번갈이 유지 · 끈 IR 32.0 / 대조 46.9 = 68 %, 켠 깊이 80 % | 선언상 후보 없음. 단 핵심 지점(30 fps 번갈이 + 긴 노출)을 못 쟀으므로 기각 전에 mx2. 가설 '노출이 프레임 주기에 닿으면 번갈이가 깨진다'(미확인) | [`run_mx1.txt`](../debug_log/2026-10-21/outputs/run_mx1.txt) · [`anal_mx1.py`](../debug_log/2026-10-21/jobs/anal_mx1.py) · [`mx_cam.launch.py`](../debug_log/2026-10-21/jobs/mx_cam.launch.py) |
| 10-21 §19.2 · §19.3 | mx2: P30 번갈이 + **기동 파라미터**로 노출 · 게인 고정 A 24000×248 · B 28000×248 · C 32000×248 · D 32000×128, 대조 상시 끔 | 전부 수락 · 드라이버 오류 0 · 번갈이 유지. 켠 깊이 0.526~0.562(기준 0.678 의 78~83 % ✘). **점이 끈 프레임에 새어 듦**: 아래 1/4 흰 점 A 0 · B 74 · C 209 · D 221 · 대조 0 | 선언상 **(나) 후보 없음**. 판정과 별개 읽기(추정): A 는 '상시 끔 대비' 켠 깊이 2.8 배 · 끈 IR 밝기 87 % · 새어 듦 없음 = 절충점. 실제 효과는 주행으로만 판별(미측정), 쓰려면 분리 노드 모드 반전도 필요 | [`run_mx2.txt`](../debug_log/2026-10-21/outputs/run_mx2.txt) · [`anal_mx2_leak.txt`](../debug_log/2026-10-21/outputs/anal_mx2_leak.txt) · 그림 [`figures/mx2/`](../debug_log/2026-10-21/figures/mx2/) · 정리 페이지 사본 [`mx2_page.html`](../debug_log/2026-10-21/figures/mx2_page.html) |
| 10-21 §20 | **사용자 결정**: "프로젝터를 끈 것을 유지하고, 유령 셀에 대한 대응책을 생각해보자." | 번갈이(NVIDIA 구성 · 절충 A) 채택 안 함. 시험 컨테이너 · 이미지는 남겨 둠. 지금 경로 확인: nvblox 는 드라이버 깊이를 **필터 없이**(`nvblox_up.sh` 28 행, `do_depth_preprocessing: false`), depth_relay 필터는 점군에만, 깊이 프리셋 미지정 | 상시 끔 확정 → 유령 대응(깊이 프리셋 pr1 · §21 부터) | SUMMARY §20 → [유령 칸 · 깊이 프리셋](ghost-cells-depth-preset.md) |

## 3. 가설과 판별
| 가설 · 질문 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 메타 `frame_emitter_mode == 1` 이 프로젝터 켠 프레임(우리 노드 첫 판 · NVIDIA 분리 노드의 가정) | 메타로 나눈 두 무리의 깊이 유효 비율 · IR 점 무늬 세기 | 10-19 드라이버 4.58.3: 1 쪽이 0.318 · 0.62(끔), 10-21 드라이버 4.51.1: 1 쪽이 0.182 · 0.40(끔) — 두 무리 겹침 0 | **기각(측정, 두 드라이버)**. 원인 위치(펌웨어 5.15 · 장치)와 '값 반전 vs 한 프레임 밀림' 은 **미확인**. 덧붙임(11-03, 이 카드): `chk_ir_exposure_diag.txt` 에서 `frame_laser_power 150` 이 늘 `frame_emitter_mode 1` 과 같은 줄에 나온다 — 두 필드가 함께 '켬' 이라고 하는 프레임이 실제론 끔. 한 필드만 뒤집힌 것보다는 메타가 이웃 프레임 것과 짝지어진 쪽과 맞는다(추정, 판별 안 함) |
| IR 손실은 카메라가 아니라 호스트 DDS(UDP) 전달 | 같은 번갈이 30 을 별도 프로세스(②) vs 한 프로세스(②') | IR 입력 210~219 → **298~300**/10 s, 교대깨짐 16 % → 0~1 % | **지지(측정)** — 같은 문제의 일반 해법은 10-20 §7 → [카메라 ↔ 컨테이너 SHM](camera-container-shm.md) |
| `ros2 bag record` 가 CPU · 기록률의 병목 | ③(기록기) vs ③'(프로세스 안 기록) | CPU 77.2 → 54~56 %, 기록 IR 7.7~8.7 → 29.6~29.9 Hz | **지지(측정)** |
| 켠 IR(점 무늬)로도 cuVSLAM 이 된다(09-29 O3 '항상 켬') | §23.1 켬 변형 | 첫 30 s 1 m 넘게 움직이는 동안 이동 ≈ 0(±1 cm) | **기각(측정)** — 카메라와 함께 움직이는 점이 이동 추정을 0 으로 붙잡음(09-29 원리를 이번에 측정) |
| 번갈이 끈 IR 로 cuVSLAM 이 된다 | §23.1 끔 변형 | 위치 95 % 469~483 cm | **기각(이 노출 조건)** |
| 끈 IR 이 어두운 원인 = 실내 조명에 근적외선이 없다(§23.1 판정 문장) | 같은 자세에서 번갈이 vs 상시 끔 밝기(§24.2), 노출 메타(§24.1 · nv1) | 번갈이 17.7(노출 31979 · 게인 16) vs 상시 끔 44.0. nv1: 분리 IR 노출 15365 · 게인 16 vs 대조 O 31979 · 246 | **기각(주원인으로는)** — 지지되는 것은 '자동 노출이 켠 프레임에 맞춰져 게인을 안 올린다'(메타 측정). 창가 구간만 특징이 많았던 것(§20)과 근적외선 가설이 맞는 면은 남음(추정) |
| 번갈이 중 노출 · 게인을 고정할 수 있다 | 10-19 실행 중 쓰기(V4L2) · mx1 실행 중 쓰기(RSUSB) · mx2 기동 파라미터 | 10-19 거부 · 자동 노출 끄면 번갈이 깨짐 / mx1 P60 수락하나 깨짐, P30 쓰기 실패 / **mx2 전부 수락 · 번갈이 유지** | **지지(기동 파라미터만, 2.55.1 · 4.51.1 시험 컨테이너)** — 지금 호스트 드라이버 4.58.3 의 기동 파라미터는 시험 안 함 |
| 노출이 프레임 주기에 닿으면 번갈이가 깨진다 | P60 33000 > 16.7 ms, 10-19 30 fps 33000 ≈ 33.3 ms | 둘 다 깨짐, P30 16000 은 유지 | **미확인(정황)** |
| 긴 노출이면 켠 프레임 점이 끈 프레임에 샌다 | mx2 끈 프레임 한 장씩 흰 점 세기 | 24 ms 0 → 28 ms 74 → 32 ms 209(아래 1/4) | **지지(설정당 한 장 — 참고값)**. 기전(노출 창이 다음 켠 구간과 겹침)은 추정 |
| 버전 차(드라이버 4.58.3 vs 권장 4.51.1)가 10-19 이상의 원인 | nv1 | 뒤집힘 · 끈 IR 어두움 둘 다 재현 | **기각(측정)**. 펌웨어 5.13 은 미시험(사용자가 바꾸지 않기로 함, §17) |
| 상시 끔이면 cuVSLAM 이 이동을 따라간다 | f2z1 오프라인(§25 기준) | 95 % 25.7 cm · yaw 0.8° | **지지(1 회)** — 재현 표본은 10-20 §3.1 f2z2 · 이후 그림자 주행([cuVSLAM 속도 융합](cuvslam-velocity-fusion.md)) |
| 상시 끔이어도 nvblox 가 상자 · 바닥을 지킨다 | B 정지(§2.1) · f2z1 · f2z2 상자 칸 | 정지 상자 칸 13 vs 10 · 유령 0 / 주행 상자 안 칸 8(켬과 같음) / 그러나 맨바닥 유령 28~99(10-21 §15) | **부분** — 상자(인쇄 무늬)는 지킴, 무늬 없는 바닥은 유령 → [유령 칸 · 깊이 프리셋](ghost-cells-depth-preset.md) |

- 메타 뒤집힘(10-19 S1 재시험) — [`anal_split_s1.py`](../debug_log/2026-10-19/jobs/anal_split_s1.py) 19~25 행, 판정은 두 무리 중앙값의 가운데:
  ```python
  def depth_valid(m):   # 0 아닌 깊이 화소 비율
      return float(np.count_nonzero(np.frombuffer(bytes(m.data), np.uint16))) / (m.width * m.height)
  def ir_lap(m):        # 4-이웃 라플라시안 절대값 평균 = 점 무늬 세기
      ...
      return float(np.abs(4 * a[1:-1, 1:-1] - a[:-2, 1:-1] - a[2:, 1:-1] - a[1:-1, :-2] - a[1:-1, 2:]).mean())
  ```
  [`run_split_s1.txt`](../debug_log/2026-10-19/outputs/run_split_s1.txt)(on_mode 0 뒤):
  ```
    분리 깊이 유효 비율: n 591, 중앙 0.774, 범위 0.764~0.785, 가운데(0.544) 아래 쪽 프레임 0
    분리 IR1 |라플라시안|: n 539, 중앙 0.594, 범위 0.584~0.633, 가운데(3.150) 위 쪽 프레임 0
    주기 split infra1   26.9 Hz (539)
  ```
  같은 뒤집힘을 NVIDIA 구성에서 — [`run_nv_static.txt`](../debug_log/2026-10-21/outputs/run_nv_static.txt):
  ```
  Built with LibRealSense v2.55.1
  Device FW version: 5.15.0.2
    원시 깊이 유효 비율: 모드0 중앙 0.681 (n 1698, 0.669~0.690) · 모드1 중앙 0.182 (n 1637, 0.155~0.217) · 메타 없음 33
      → 실제 프로젝터 켬 = 모드 0 (NVIDIA 분리 노드는 모드 1 = 켬 으로 가정)
    분리 IR1 프레임의 메타: 노출 중앙 15365.0 µs · 게인 중앙 16.0 · emitter_mode 값 [0]
  ```
  ⚠ '(NVIDIA 분리 노드는 모드 1 = 켬 으로 가정)' 은 `anal_nv_static.py` 85 행에 박힌 문구다. 그 가정의 원천인 `realsense_splitter` 소스를 읽은 도구 [`chk_splitter_src.sh`](../debug_log/2026-10-21/jobs/chk_splitter_src.sh) 의 출력은 남지 않았다(**원천 소실**, SUMMARY 에도 언급 없음). 다만 분리 깊이 1619 장이 전부 낮은 무리(0.182)였다는 측정이 그 가정과 맞는다.
- 전달 손실 · 합성 효과 — [`chk_flash_s2.sh`](../debug_log/2026-10-19/jobs/chk_flash_s2.sh) 21~32 행(전체 CPU = `/proc/stat` 두 번 차이, 측정 도구를 띄우기 전 30 s 만; EKF 위반 = sensors.log 'Failed to meet update rate' 증가분):
  ```
  == S2 flash30rec (기록 1) 14:39:27
    전체 CPU 사용률 77.2 % (P 게이트 ≤ 60) · load 15.81 9.49 6.22 · EKF 위반 +127 · slam 폐기 +12 (약 80 s)
    /camera/camera/infra1/image_rect_raw   average rate: 7.923
  == S2 comp30rec_b (기록 2) 15:02:15
    전체 CPU 사용률 55.5 % (P 게이트 ≤ 60) · load 7.31 8.76 7.53 · EKF 위반 +7 · slam 폐기 +4 (약 80 s)
                       Topic: /camera/raw/infra1/image_rect_raw | Type: sensor_msgs/msg/Image | Count: 2574 | Serialization Format: cdr
  == S2 base4 (기록 0) 15:07:06
    전체 CPU 사용률 48.6 % (P 게이트 ≤ 60) · load 7.79 7.78 7.39 · EKF 위반 +10 · slam 폐기 +5 (약 80 s)
  ```
  (첫 줄 [`chk_flash_s2_flash30.txt`](../debug_log/2026-10-19/outputs/chk_flash_s2_flash30.txt) 51 · 77 행, 뒤 두 줄 [`chk_flash_s3_repeat.txt`](../debug_log/2026-10-19/outputs/chk_flash_s3_repeat.txt) — base4 의 +10 이 ① 편차의 근거.)
- 오프라인 cuVSLAM — [`anal_vslam_cmp.py`](../debug_log/2026-10-19/jobs/anal_vslam_cmp.py) 3~4 · 65 행: 정렬은 각 추정의 첫 시각에서 SLAM 자세에 맞춤(끼워 맞춤 없음), 오차 = `np.hypot(E[:, 0] - Gi[:, 0], E[:, 1] - Gi[:, 1]) * 100`(cm). 출력 [`anal_vslam_cmp_f2y1.txt`](../debug_log/2026-10-19/outputs/anal_vslam_cmp_f2y1.txt) · [`anal_vslam_cmp_f2z1.txt`](../debug_log/2026-10-20/outputs/anal_vslam_cmp_f2z1.txt):
  ```
  f2y1(번갈이)  false_vs_off   추적 성공 100.0 % · 위치 오차 끝 204.2 · 95 % 483.2 · 최대 507.7 cm · yaw 오차 끝 -106.0°
                false_vs_on    추적 성공 100.0 % · 위치 오차 끝 136.7 · 95 % 588.2 · 최대 652.8 cm · yaw 오차 끝 -169.9°
                EKF            추적 성공   nan % · 위치 오차 끝  40.4 · 95 %  36.3 · 최대  40.4 cm · yaw 오차 끝  +5.0°
  f2z1(상시 끔) false_vs_off   추적 성공 100.0 % · 위치 오차 끝   1.5 · 95 %  25.7 · 최대  31.6 cm · yaw 오차 끝  -0.8°
                               yaw 오차 |95 %| 0.8° · |최대| 1.5° · 구간 변화 t60~80 -0.4° · t160~210 -0.1°
                EKF            추적 성공   nan % · 위치 오차 끝  59.8 · 95 %  57.2 · 최대  60.9 cm · yaw 오차 끝  +4.4°
  ```
  (앞 머리 'f2y1(번갈이)' · 'f2z1(상시 끔)' 은 이 카드가 붙인 것. `false/true` = IMU 융합 끔/켬, `_vs_off/_on` = 입력 끈/켠 IR.)
- 번갈이 중 노출 — [`chk_ir_exposure_diag.txt`](../debug_log/2026-10-19/outputs/chk_ir_exposure_diag.txt)(호스트 4.58.3, V4L2):
  ```
  == 자동 노출 켬 — 메타데이터 연속
  "actual_exposure":31979 "gain_level":16 "frame_laser_power":150 "frame_emitter_mode":1 "actual_exposure":31979 "gain_level":16 "frame_laser_power":0 "frame_emitter_mode":0 ...
  == CLI: 노출 30000
  Setting parameter failed: set_xu(...). xioctl(UVCIOC_CTRL_QUERY) failed on control 3 ...
  == CLI: 게인 128
  Setting parameter failed: xioctl(VIDIOC_S_CTRL) failed on option Gain, value=128, errno=84 ...
  저장: emitter_mode [0, 1] · 밝기 {1: 28.5, 0: 28.4} · 영상 59 메타 60
  ```
  [`chk_ir_gain_off.txt`](../debug_log/2026-10-19/outputs/chk_ir_gain_off.txt)(번갈이 없이 끔): `auto 장 61 · 밝기 44.0 · FAST 중앙 12` · `gain248 장 44 · 밝기 45.5 · FAST 중앙 25`.
- 기동 파라미터 수동 노출 — [`mx_cam.launch.py`](../debug_log/2026-10-21/jobs/mx_cam.launch.py) 16~17 행 `over.update({'depth_module.enable_auto_exposure': False, 'depth_module.exposure': int(os.environ['MX_EXP']), 'depth_module.gain': int(os.environ['MX_GAIN'])})`. [`run_mx2.txt`](../debug_log/2026-10-21/outputs/run_mx2.txt):
  ```
  [Auto]
    모드 0(켬): 깊이 n 88 유효 0.668 아래 0.531 · IR n 90 밝기 27.9 FAST20 2388 FAST5 3116 |lap| 8.96 · 노출 31979 게인 16
    모드 1(끔): 깊이 n 90 유효 0.251 아래 0.184 · IR n 90 밝기 17.9 FAST20 1 FAST5 205 |lap| 0.65 · 노출 31979 게인 16
  [A24k248]
    모드 0(켬): 깊이 n 90 유효 0.533 아래 0.312 · IR n 90 밝기 95.7 FAST20 5509 FAST5 9275 |lap| 23.36 · 노출 24000 게인 248
    모드 1(끔): 깊이 n 88 유효 0.191 아래 0.138 · IR n 90 밝기 39.9 FAST20 27 FAST5 378 |lap| 3.38 · 노출 24000 게인 248
    드라이버 오류: 0건 —
  [Ctl]
    모드 0(켬): 깊이 n 180 유효 0.193 아래 0.141 · IR n 180 밝기 46.0 FAST20 46 FAST5 564 |lap| 3.70 · 노출 31979 게인 246
  ```
  ([Ctl] 은 프로젝터 상시 끔이라 메타가 전부 0 — 분석기 표지 '모드 0(켬)' 은 무리 이름일 뿐.) 새어 듦 — [`anal_mx2_leak.py`](../debug_log/2026-10-21/jobs/anal_mx2_leak.py) 6 행 `th = cv2.morphologyEx(a, cv2.MORPH_TOPHAT, np.ones((5, 5), np.uint8)) > 20`, 연결 성분 수. 출력 [`anal_mx2_leak.txt`](../debug_log/2026-10-21/outputs/anal_mx2_leak.txt): `A24k248_IR_m1 흰 점 전체 38 · 아래 1/4 0` · `C32k248_IR_m1 260 · 209` · `Ctl_IR_m0 50 · 0`.

## 4. 조치와 효과
- **분리 노드 `emitter_splitter`**(10-19 §15) — 판정은 [`emitter_splitter.cpp`](../../ros2_ws/src/rover_bringup/src/emitter_splitter.cpp) 187~193 · 209 행:
  ```cpp
  int64_t mode = jsonInt(m->json_data, "frame_emitter_mode");
  if (mode < 0) {   // 판이 다른 드라이버 대비: 레이저 출력으로 대신 판정
    const int64_t lp = jsonInt(m->json_data, "frame_laser_power");
    mode = lp < 0 ? -1 : (lp > 0 ? 1 : 0); }
  ...
  const bool on = mode == on_mode_;     // on_mode 기본 0(268 행, S1 실측)
  ```
  효과: 오분류 0(S1). ⚠ 대체 판정(레이저 출력 > 0 → 1)은 '1 = 켬' 을 전제하는데 이 카메라에선 메타 1 이 실제 끔 — `frame_emitter_mode` 가 없는 드라이버에서 on_mode 0 과 함께 쓰면 거꾸로 나뉜다(추정, 그런 드라이버로 돌린 적 없음).
- **합성 + 프로세스 안 기록**(10-19 §17): IR 도착 21 → 30 Hz, 기록 IR 29.6~29.9 Hz, CPU 54~56 %. f2y1 에서 230 s 동안 유지(29.8 Hz). 이것으로 '번갈이 IR 을 쓸 수 있나' 를 처음으로 실제 주행 자료로 물을 수 있었다 — 답은 '이 노출로는 못 쓴다'(§23.1).
- **상시 끔 구성 `emitter_off:=true`**(10-19 §25): f2z1 에서 cuVSLAM '따라감'(10-20 §1). 10-21 §20 결정 뒤 운용 기본(10-21 §22 '운용 구성 = 프로젝터 상시 끔 · vslam:=shadow · dds_shm:=true'), 10-23 부터 `prep_patrol.sh` 기본.
- 기각 · 보류한 대안: 번갈이(우리 노드 · NVIDIA 구성), 번갈이 중 실행 중 노출 고정(거부), 번갈이 + 기동 파라미터 노출(선언 기준 미달 · 주행 미시험), 항상 켬(점 무늬에 붙잡힘), 카메라 펌웨어 5.13 으로 내리기(사용자: 필요 없음 §17 — 뒤집힘 판별은 못 함), 850 nm 플러드 조명(시험 안 함), UDP 수신 버퍼(sudo — 사용자 결정, 10-20 §7 로).
- 대가(측정): 상시 끔 깊이 아래 절반 유효 = 켬의 59 %(10-20 §2.1) · 맨바닥 유령 28~99 칸(10-21 §15) → 10-22 깊이 프리셋 3 기본([유령 칸 · 깊이 프리셋](ghost-cells-depth-preset.md)).
- **지금 코드 확인(11-03)**:
  - [`camera.launch.py`](../../ros2_ws/src/rover_bringup/launch/camera.launch.py) 115 · 117 행 `emitter_flash` · `emitter_off` 기본 **false**, 116 행 `stereo_fps` 30. 36~39 행 `if eoff and not flash:` → 깊이 · IR 640×480×15 · `emitter_enabled 0` · IR 만 `/camera/raw` 로. 40~46 행 `if flash:` → `emitter_enabled 1 · emitter_on_off True`, 깊이 · IR · 점군까지 `/camera/raw` 로. 91 행 둘 다 끔이면 호스트 `realsense2_camera_node` 단독(프로젝터 값 지정 없음 = 장치 기본, 10-20 §2 의 '① 켬'). 97~107 행 둘 중 하나면 `realsense2_camera_container` 에 드라이버 + 분리 노드 — **상시 끔에서도 분리 노드가 올라간다**(106 행 `out_ns: /camera/split_unused` · `split_points: False`, 기록 전용). 88~90 행 `depth_preset` 기본 3(10-22 결정 — 유령 카드 몫).
  - 운용 기본: [`prep_patrol.sh`](../tools/prep_patrol.sh) 10~11 행 `ODOM` 기본 vslam → `S="emitter_off:=true vslam:=on dds_shm:=true"` = **프로젝터 상시 끔**. `ODOM=rf2o` 이면 emitter 인자 없음 → 장치 기본(켬). 16 행 `SENSORS_ADD` 로 `emitter_flash:=true` 를 덧붙이면 번갈이로 되돌릴 수 있음(이 뒤로 쓴 기록 없음). 인자는 [`prep_fast.sh`](../tools/prep_fast.sh) 57 행 `ros2 launch rover_bringup sensors.launch.py viz:=map ${EXTRA_SENSORS:-}` 로 들어가고, [`sensors.launch.py`](../../ros2_ws/src/rover_bringup/launch/sensors.launch.py) 30~33 행은 `enable_*` 만 명시해 넘기므로 `emitter_off` 는 launch 설정 상속으로 camera.launch 에 닿는다(코드 읽기 — f2z1 이후 실제로 끈 상태가 측정됨: 10-19 §25 `emitter_enabled 0`).
  - cuVSLAM 입력: [`cuvslam_container.launch.py`](../../ros2_ws/src/rover_bringup/launch/cuvslam_container.launch.py) 24~25 행 `/camera/raw/infra{1,2}/image_rect_raw` — 분리 노드를 거치지 않은 원시 IR(상시 끔이라 나눌 것이 없음).
  - 분리 노드: [`emitter_splitter.cpp`](../../ros2_ws/src/rover_bringup/src/emitter_splitter.cpp) 350 행(268 행 `on_mode` 기본 0 · 269 행 `record_path` · 266 행 `max_wait_s` 0.5), [`CMakeLists.txt`](../../ros2_ws/src/rover_bringup/CMakeLists.txt) 25~29 행 `emitter_splitter_component` + 실행 파일 `emitter_splitter_node`. 상시 끔에선 메타가 늘 0 = on_mode → IR 은 '켬' 으로 분류돼 내보내지 않고(`keep_on` false), 10 s 통계의 '교대깨짐' 이 프레임마다 늘어난다(10-19 §25 '150/10 s — 무시').
  - nvblox 깊이 경로: [`nvblox_up.sh`](../../ros2_ws/src/rover_navigation/scripts/nvblox_up.sh) 28 행 `camera_0/depth/image:=/camera/camera/depth/image_rect_raw`, [`nvblox_local.yaml`](../../ros2_ws/src/rover_navigation/config/nvblox_local.yaml) 48 행 `do_depth_preprocessing: false` — 10-21 §20 확인과 같음.
  - 러너 IR 기록: [`2026-10-27/jobs/job551_f0drive.sh`](../debug_log/2026-10-27/jobs/job551_f0drive.sh) 70 · 95 행 `ros2 param set /emitter_splitter record_path …` 로 시작 · 끝.
  - Jetson(저장소 밖, 11-03 에 확인 안 함): 10-21 §22 기준 시험 컨테이너 `isaac_rs_test` 떠 있음(카메라 안 잡음) · 이미지 `isaac_ros_dev-aarch64-rs:latest` · `:apt`(지울지 사용자 결정), 큰 IR bag `bag_f2y1_ir` 4.0 GB · `bag_f2z1_ir` · `bag_f2z2_ir` · `vslam/*_split` · `s2_comp30rec(_b)` 정리 대기(10-20 §10).

## 5. 내 실수 · 기록 어긋남
1. **어느 메타 값이 켬인지 재지 않고 넘김**(09-29 M2 → 10-19 §15.1) — 하려 한 것: 번갈이 실현성 확인 · 본 것: `frame_emitter_mode` 0/1 교대 · 처음 추론: 1 = 켬(이름 그대로) · 의심한 이유: 10-19 S1 첫 시험에서 분리 깊이가 낮은 무리로만 나옴 · 판별: 두 무리 깊이 유효 · IR 점 무늬(§3) · 결론: 이 카메라에선 1 = 끔 → `on_mode` 파라미터 · 다음에 알아보는 법: 메타 값은 이름이 아니라 영상 지표(깊이 유효 · 점 무늬)로 먼저 확인 · 데이터: [`run_split_s1_first.txt`](../debug_log/2026-10-19/outputs/run_split_s1_first.txt).
2. **판정 기준을 대조군 1 회 값에 묶음**(10-19 §17.1) — 'EKF 위반 ≤ ① + 2' 를 ① 1 회(+0)로 정했으나 ① 반복 +0 · +10 · +13. SUMMARY 가 '정정 읽기' 로 남김. 다음에 알아보는 법: 대조군 편차를 먼저 2~3 회 재고 기준을 정한다. 데이터: [`chk_flash_s3_repeat.txt`](../debug_log/2026-10-19/outputs/chk_flash_s3_repeat.txt).
3. **빌드 직후 측정**(10-19 §16.1 · §17.1 의 * 표시) — load 10~16 에서 잰 값. 첫 값은 `chk_flash_s2_base_afterbuild.txt` 로 보존, 재측정으로 대체.
4. **FAST 절대 문턱 과소 계산**(10-19 §20 → §24.1 정정) — 'FAST 6 = 특징 없음' 은 밝기 20~45 의 낮은 대비 영상에서 과장. 이후 nv1 · mx 는 FAST5 를 함께 셈.
5. **'설정 결과' 를 확인하지 않고 첫 노출 표를 씀**(10-19 §24.1) — `run_ir_exposure.txt` 각 줄 끝 `설정 결과 [True, False, False]` 인데 설정별 값처럼 읽음 → 실제는 모두 33000 · 16. mx1 에서도 같은 교훈: ROS 'ok' 응답 ≠ 수락, 메타의 실제 노출 · 게인으로만 판정(10-21 §19.1).
6. **10-21 §17.1 실수 3 건**(칸 형식 원문은 SUMMARY §17.1 표): admin 사용자 없음(엔트리포인트를 안 옮김) · `COLCON_IGNORE` · 옛 컨테이너 nvblox · cuVSLAM 이 **쓰기 층 apt 설치**(이미지만으로 지금 운용 컨테이너가 재현되지 않음 — 다른 손 설치는 미검토). 데이터 [`up_rs_splitter_try1.txt`](../debug_log/2026-10-21/outputs/up_rs_splitter_try1.txt) · [`chk_rs_ws.txt`](../debug_log/2026-10-21/outputs/chk_rs_ws.txt) · [`chk_rs_ws2.txt`](../debug_log/2026-10-21/outputs/chk_rs_ws2.txt) · [`chk_rs_apt_sim.txt`](../debug_log/2026-10-21/outputs/chk_rs_apt_sim.txt)(10-21 §23 이 대화 기록에서 옮김 — 머리줄에 출처 표시).
7. **10-21 §18.2 실수 2 건**(칸 형식 원문은 SUMMARY §18.2): `-v /dev:/dev` 가 CUDA 메모리 풀을 막아 cuVSLAM 적재 실패(기전 미확인) · 4.51.1 은 토픽에 노드 이름을 안 붙여 분석기가 0 Hz. 데이터 [`run_nv_static_try1.txt`](../debug_log/2026-10-21/outputs/run_nv_static_try1.txt) · [`chk_nv_probe.txt`](../debug_log/2026-10-21/outputs/chk_nv_probe.txt) · [`chk_nv_cmp.txt`](../debug_log/2026-10-21/outputs/chk_nv_cmp.txt).
8. (부수) **재생 nvblox 고아 4 개**(10-19 §15.1) — `run_nvblox_replay.sh` 가 `ros2 run` 래퍼 PID 만 죽임. 오염 없음을 측정으로 확인(재생 출력 8 개 중복 stamp 0). 상자 과장 재생 쪽 일 → [상자 과장 출처](box-exaggeration-source.md).
9. **정지 시험을 실시간 집계만**(10-21 §23) — nv1 · mx1 · mx2 는 bag 없이 분석기가 바로 셈 → 다른 지표로 다시 셀 수 없음. 드라이버 로그 `/tmp/nv_static_*.log` · `/tmp/mx2_*.log` 는 휘발(**원천 소실** 취급), 요약만 `run_*.txt` 에.
- **기록 어긋남**(이 카드에서 찾음):
  1. [10-19 §25](../debug_log/2026-10-19/SUMMARY.md) '상자를 치우고 주행' — 실제론 둔 채(10-20 §3.2 정정, 10-19 SUMMARY 끝에 정정 표시 있음).
  2. [10-19 §23.1](../debug_log/2026-10-19/SUMMARY.md) 판정 문장 '이 조명(LED — 근적외선이 거의 없음, 추정)에서는 끈 IR 이 장면을 거의 못 보고' — §24.1 · §24.2 가 같은 날 '직접 원인 = 자동 노출' 로 바꿨는데 §23.1 에는 정정 표시가 없다(§24.1 은 §20 읽기만 정정한다고 적음). 같은 근거의 대책 ①(850 nm 조명)도 10-20 §1 함의 (A) 로 남아 있다 — 끈 프레임 노출이 켠 프레임에 묶이는 한 조명만으로 풀리는지는 별개 질문.
  3. [10-19 §20](../debug_log/2026-10-19/SUMMARY.md) '복귀 길(t ≈ 130~230 s) 0~10 개' — 같은 csv 재계산은 중앙 0 · **최대 17**(경미, 결론 같음).
  4. [`anal_vslam_cmp_f2z1.txt`](../debug_log/2026-10-20/outputs/anal_vslam_cmp_f2z1.txt) 마지막 줄 그림 경로가 `2026-10-19/figures/vslam_cmp_f2z1.png` 인데 파일은 `2026-10-20/figures/` 에 있다(옮긴 기록 없음, 경미).
  5. 러너 주석 [`job551_f0drive.sh`](../debug_log/2026-10-27/jobs/job551_f0drive.sh) 40 행 'BAG_IR=1 — prep 에 SENSORS_ADD="emitter_flash:=true" 필요' — f2z1 은 `emitter_off:=true` 로 BAG_IR 을 썼다(상시 끔에서도 분리 노드가 기록). 낡은 주석.
  6. [`camera.launch.py`](../../ros2_ws/src/rover_bringup/launch/camera.launch.py) 26~27 행 주석 'emitter_off … cuVSLAM 오프라인 확인용 기록 주행' — 지금은 운용 기본(prep_patrol 11 행). 낡은 주석.
  7. [Isaac 카드 §7](isaac-cuvslam-evaluation.md) 의 '분리 노드는 `camera.launch.py emitter_flash:=` 로만 쓰임' — 상시 끔(`emitter_off:=true`)에서도 기록 전용으로 올라간다(위 지금 코드 확인). Isaac 카드에 정정 표시를 달았다.

## 6. 남은 것 (10-21 시점)
- 메타 뒤집힘의 원인 위치 — 카메라 펌웨어 5.13.0.50 으로 내려 재는 것만 판별 수단(장치 변경 · 사용자 결정, §17 에서 '필요 없음').
- 번갈이 + 기동 파라미터 노출 A(24 ms × 248)의 실제 주행 효과(유령 · cuVSLAM 추적) — 시험 안 함. 지금 호스트 드라이버 4.58.3 에서 기동 파라미터가 들어가는지도 안 잼(mx 는 시험 컨테이너 2.55.1).
- 850 nm 무늬 없는 IR 조명 — 시험 안 함(§5 기록 어긋남 2 의 질문 포함).
- '노출이 프레임 주기에 닿으면 번갈이가 깨진다' · '긴 노출에서 점이 샌다' 의 기전 — 정황 · 한 장 표본.
- 상시 끔의 대가: 무늬 없는 낮은 물체 · 맨바닥 → [유령 칸 · 깊이 프리셋](ghost-cells-depth-preset.md). 인쇄 무늬 없는 상자 감지는 미확인(10-20 §3.2).
- f2z1 IMU 융합 켬이 더 나쁜 이유(`unite_imu_method 1` 의심 — 추정) → [cuVSLAM 속도 융합](cuvslam-velocity-fusion.md).
- 분리 노드의 대체 판정(레이저 출력)이 on_mode 0 과 어긋나는 것(§4) — 코드 그대로.
- Jetson 정리: 시험 컨테이너 · 이미지(43 GB 급) · 큰 IR bag — 사용자 확인 뒤(10-19 §18.1 순서).

## 7. 이후 (10-22 ~)
- 10-22 §6~§10: 상시 끔 위에서 깊이 프리셋 3 기본 · nvblox 통합 거리 2.0 m → [유령 칸 · 깊이 프리셋](ghost-cells-depth-preset.md).
- 10-23 §16: 주 EKF 병진 = cuVSLAM, `prep_patrol.sh` 기본 `ODOM=vslam` = `emitter_off:=true`(위 지금 코드 확인) → [cuVSLAM 속도 융합](cuvslam-velocity-fusion.md).
- 10-24 ~: 다음 시기에서 채움(번갈이로 되돌린 기록은 10-23 까지 없음 — 10-22 · 10-23 SUMMARY 에 '번갈이 · emitter_flash · splitter' 언급 없음, 11-03 grep).

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| S1 | 분리 노드 정지 시험(60 fps 번갈이) — 첫 판 거꾸로 · 재시험 | `2026-10-19/outputs/run_split_s1_first.txt` · `run_split_s1.txt` |
| S2 · S3 | 번갈이 30 정지 부하 ①②③ · 합성 ②'③' | `2026-10-19/outputs/chk_flash_s2_{base,base_afterbuild,flash30}.txt` · `chk_flash_s3_{comp,repeat}.txt` |
| f2y1 | 번갈이 30 IR 기록 주행 3/3 | `2026-10-19/outputs/run_f2y1.txt` · `f2y1_ir_pairs.csv` · 그림 `figures/f2y1_ir_drive_*.png` · Jetson `bag_f2y1_ir` |
| 오프라인 cuVSLAM f2y1 | 켬/끔 × IMU 4 변형 | `2026-10-19/outputs/anal_vslam_cmp_f2y1.txt` · `vslam_f2y1/` · `figures/vslam_cmp_f2y1.png` |
| 노출 시험(10-19) | 번갈이 중 노출 · 게인 · 진단 · 상시 끔 게인 | `2026-10-19/outputs/run_ir_exposure.txt` · `chk_ir_exposure_diag.txt` · `chk_ir_gain_off.txt` |
| f2z1 | 상시 끔 IR 기록 주행 3/3 · 오프라인 판정 | `2026-10-19/outputs/run_f2z1.txt` · `2026-10-20/outputs/anal_vslam_cmp_f2z1.txt` · `vslam_f2z1/` · bag `2026-10-21/bags/bag_f2z1.tgz`(10-21 §23 이 스크래치패드에서 옮김, git 제외) |
| B 정지(bt_on · bt_off) | 켬 vs 상시 끔 nvblox 상자 · 바닥 | `2026-10-20/outputs/run_box_depth_ab.txt` · `anal_box_static.txt` · `figures/box_static_on_off.png` |
| nv1 | NVIDIA 구성 정지(F 번갈이 · O 대조) | `2026-10-21/outputs/run_nv_static.txt` · `run_nv_static_try1.txt`(무효) |
| mx1 · mx2 | 번갈이 중 수동 노출(실행 중 · 기동 파라미터) | `2026-10-21/outputs/run_mx1.txt` · `run_mx2.txt` · `anal_mx2_leak.txt` · `figures/mx2/` |
| 컨테이너 층 | 새 이미지 · 시험 컨테이너 · splitter 빌드 | `2026-10-21/outputs/rs_image_build_end.txt` · `up_rs_splitter_try{1,2}.txt` · `chk_rs_*.txt` · `up_rs_apt.txt` |

## 9. 도구 해설
공통: Jetson 쪽은 전부 PC 의 `run_jn.sh`(실시간 로그 `/tmp/live/current.log`, 메모리 '실행 투명성')로 돌렸다. 스택을 내리는 정지 시험은 같은 프로세스 패턴 목록(`PATS="nvblox_up.sh nvblox_node depth_relay.py navigation.launch …"`)을 TERM → 3~5 s → KILL 하고 `systemctl --user is-active rover-base` 로 base 만 남았는지 찍는다. 끝나면 스택은 `prep_patrol.sh` 로 따로 복귀(PREP_OK 줄이 출력에 남음). 판정 지표 정의는 날마다 같게 유지했다: **깊이 유효 비율**(0 아닌 화소 / 전체, 아래 절반 따로), **|라플라시안|**(점 무늬 세기), **FAST20/FAST5**(OpenCV FAST 문턱 20 · 5 모서리 수 — cuVSLAM 검출기와 다름), **두 무리 가운데**(메타로 나눈 두 무리 중앙값의 평균).

### emitter_splitter (Jetson 호스트, C++ 컴포넌트 · 실행 파일) — `ros2_ws/src/rover_bringup/src/emitter_splitter.cpp`
- 왜(10-19 §15): Isaac `realsense_splitter` 가 컨테이너 · apt 에 없고 카메라는 호스트.
- 하는 일: 스트림마다(`깊이(켬)` · `IR1(끔)` · `IR2(끔)` · 선택 `점군(켬)`) `in_ns/<stream>/image_rect_raw` 와 `meta_ns/<stream>/metadata` 를 stamp(ns) 로 짝지음 — 먼저 온 쪽을 보관, `max_wait_s` 0.5 넘으면 버림('짝없음'). 메타 json `frame_emitter_mode`(없으면 `frame_laser_power > 0`)가 `on_mode`(기본 0)와 같으면 켬. 켬 스트림은 켬만, 끔 스트림은 끔만 `out_ns` 로 내보냄(출력 reliable — nvblox 깊이 구독이 reliable). 같은 모드가 연속되면 '교대깨짐'. 10 s 마다 통계 줄(입력 · 켬 · 끔 · 내보냄 · 짝없음 · 교대깨짐 · 키없음 · 내보낸 깊이 유효). `record_path` 가 비어 있지 않으면 원시 IR(켬 · 끔) · 메타 · IR camera_info · IMU 를 `rosbag2_cpp::Writer`(sqlite3, 캐시 200 MB)로 직접 씀.
- 출력 줄 예([`run_split_s1.txt`](../debug_log/2026-10-19/outputs/run_split_s1.txt)): `깊이(켬) 입력 598 · 켬 299 · 끔 299 · 내보냄 299 · 짝없음 0 · 교대깨짐 1 · 키없음 0 · 내보낸 깊이 유효 0.77 | IR1(끔) 입력 593 …`.
- 계보: §15 단독 노드 → §16 원래 이름 출력(camera.launch remap) → §17 컴포넌트 + 프로세스 안 기록. 지금: 상시 끔 구성에서 기록 전용으로 올라감(§4). 결함: 대체 판정의 '레이저 > 0 → 1'(§4), 짝 맞추기가 stamp 완전 일치라 드라이버가 이미지 · 메타 stamp 를 다르게 주면 전부 '짝없음'.

### up_splitter.sh · run_split_s1.sh · anal_split_s1.py — S1 (Jetson)
- `up_splitter.sh`: `/tmp/spl.tar` 를 `rover_bringup` 소스에 풀고(바뀌는 원본은 `.bak_<시각>`), colcon 빌드. 같이 재생 nvblox 고아 정리.
- `run_split_s1.sh`: 스택 내림 → 카메라를 스택 설정 + 깊이 · IR 640×480×60 + `emitter_on_off true` 로 단독 기동 → 분리 노드 → `top` 5 회(분리 · 카메라 CPU) → `anal_split_s1.py 20`.
- `anal_split_s1.py`: 원시 깊이 · IR1 을 메타로 두 무리 → `depth_valid` · `ir_lap`(§3 발췌) 분포, 분리 출력의 지표가 두 무리 가운데의 맞는 쪽인지 프레임마다 셈. 주기 · 해상도 · 도착 지연(수신 − stamp 중앙 · 95 %).
- 출력 `run_split_s1_first.txt` · `run_split_s1.txt`. 쓰인 곳 §15.1(on_mode 0). 재사용: 번갈이 시험이면 그대로(토픽 이름이 4.58.3 형식 `/camera/camera/...`).

### chk_flash_s2.sh · prep_flash.sh — S2 · S3 정지 부하 (Jetson)
- 부른 형태: `chk_flash_s2.sh <꼬리표> [REC=0|1|2]` — 0 기록 없음, 1 `ros2 bag record`(best effort QoS 덮어쓰기 파일 `/tmp/s2_qos.yaml`), 2 `ros2 param set /emitter_splitter record_path /home/jetson/bags/s2_<꼬리표>`. `prep_flash.sh` = `SENSORS_ADD="emitter_flash:=true stereo_fps:=30" bash /tmp/prep_patrol.sh lite`.
- 하는 일: 시작 전 sensors.log 'Failed to meet update rate' · slam.log 'Message Filter dropping' 개수 → `/proc/stat` 30 s 차이로 전체 CPU(러너 P 게이트와 같은 계산, 측정 도구를 띄우기 전) · loadavg · `top` 프로세스별 → `ros2 topic hz` 7 s 씩(/odometry/filtered · /tf · /scan · 깊이 · 점군 · 조각 · IR) → 분리 노드 10 s 통계 → 기록이면 `ros2 bag info`.
- 출력 `chk_flash_s2_*.txt` · `chk_flash_s3_*.txt`. 결함: ① 1 회를 기준으로 쓴 판정 설계(§5 실수 2), `ros2 topic hz` 자체가 참여자를 늘림(측정 순서로 CPU 와 분리), /tf 값이 40~49 로 흔들림.

### chk_f2y1.sh · 러너 BAG_IR (Jetson)
- 러너 `job551_f0drive.sh`(10-19 판은 날짜 폴더 jobs, 지금 판 `2026-10-27/jobs/`) `BAG_IR=1` → `BAG_DEPTH=1` 포함, 출발 직전 `record_path` 설정 · 끝에 빈 문자열 · `du -sh` · `ros2 bag info`. 출력 줄 `IR 기록 시작: Set parameter successful` · `IR bag 크기 4.0G`.
- `chk_f2y1.sh`: 러너 로그 `/tmp/f0_f2y1.log` 에서 게이트 · 결과 · 'missed' · EKF 줄, IR bag · 깊이 bag 토픽 수, 분리 노드 통계. 출력 [`run_f2y1.txt`](../debug_log/2026-10-19/outputs/run_f2y1.txt).

### fig_ir_extract.py (Jetson) · fig_ir_drive_video.py (PC) — IR 영상
- `fig_ir_extract.py IRbag 출력폴더 [축소]`: IR1 메타 `frame_emitter_mode == 0` = 켬, 끔 프레임마다 직전 켬 프레임과 짝 → 짝 영상(왼쪽 OFF · 오른쪽 ON, FAST 수 글씨) + csv(`t, stamp_ns, off_mean, off_lap, off_fast, on_mean, on_lap, on_fast`). FAST = `cv2.FastFeatureDetector_create(threshold=20)`.
- `fig_ir_drive_video.py 폴더 출력.mp4`: 위 = 짝 영상, 아래 = 지도 위 로버 · 지나온 길 · 카메라 시야 | 시간축(회전 속도 · 특징 수). §21 에서 상자 확대판 추가(상자 과장 카드 몫).
- 출력: csv [`f2y1_ir_pairs.csv`](../debug_log/2026-10-19/outputs/f2y1_ir_pairs.csv), 정지 화면 · 시간축 png, 영상(git 제외). 결함: FAST20 절대 문턱(§5 실수 4). 계보: 10-23 `Docs/tools/fig_drive_video.py` 가 기본 영상 도구.

### mk_vslam_bag.py · run_vso.sh · run_vslam_offline.sh · vslam_offline.launch.py · vslam_run_in.sh · export_vslam.py — 오프라인 cuVSLAM (Jetson 호스트 + 컨테이너)
- 부른 형태: PC `VNAME=f2y1 VMODE= bash run_vso.sh`(준비물 4 개를 `/tmp` 로 올리고 `run_jn.sh run_vslam_offline.sh <이름> [all_off]`). f2z1 은 `VMODE=all_off`.
- `mk_vslam_bag.py IRbag 주행bag 출력bag [all_off]`: 메타 `== 0` 이면 `/on/infra{1,2}`, 아니면 `/off/…`(all_off 면 전부 `/off`), 같은 stamp camera_info 를 붙이고 `/camera/imu` · 주행 bag `/tf_static` 을 더함. 시각은 bag 기록 시각.
- `run_vslam_offline.sh`: 실시간 스택 내림(CPU 경합 배제) → 입력 bag → 컨테이너에서 `vslam_run_in.sh true|false`(IMU 융합) 두 판. `vslam_run_in.sh`: 도메인 42 · 컨테이너 기본 DDS, `set +u`(ROS setup 이 미정의 변수 사용 — 첫 실행 실패 원인), launch → 출력 기록 → `ros2 bag play --clock` 1 배속 → csv. `vslam_offline.launch.py`: cuVSLAM 두 개(끔 · 켬 입력), `rectified_images True` · `enable_imu_fusion` 인자 · `image_jitter_threshold_ms 80` · `base_frame camera_link`, TF 발행 끔. `export_vslam.py`: 출력 bag → 변형별 오도메트리 csv + vo_state(0 미상 · 1 성공 · 2 실패).
- 출력: Jetson `~/workspaces/isaac_ros-dev/vslam/vslam_<이름>_<imu>_vs_<off|on>(_state).csv` → PC 로 받아(`get_vso_f2z1.sh`) `outputs/vslam_f2y1/` · `2026-10-20/outputs/vslam_f2z1/`. 러너가 끝 정리에서 멈춰 시간 초과(결과는 다 나옴, §23.1).
- 재사용: 가능 — 10-20 그림자 · 속도 융합 분석이 이 csv 를 씀([cuVSLAM 속도 융합](cuvslam-velocity-fusion.md)).

### anal_vslam_cmp.py — 오프라인 비교 (PC, Python rosbags)
- 부른 형태: `anal_vslam_cmp.py 주행bag csv폴더 출력.png [정렬 시각]`(10-20 에 yaw 통계 · 정렬 시각 인자 추가).
- 하는 일: 기준 = 주행 bag 의 map→odom ∘ odom→base_link ∘ base_link→camera_link(정적), EKF = 같은 사슬에서 map→odom 을 첫 값으로 고정. 각 추정을 첫 시각에서 기준 자세에 맞춘 뒤(회전 · 이동 끼워 맞춤 없음) 시각마다 위치 오차(cm) · yaw 오차, 끝 · 95 % · 최대, 구간 t 60~80 · 160~210 증가량, vo_state 성공 비율.
- 출력 §3 발췌. 판정 문턱은 선언(§23 · §25)에 있고 도구엔 없음. 결함: 기준 SLAM 자체 오차(수 cm · 점프) 섞임 — 5 cm 이하 차이는 판정에 안 씀(§23 선언). 끝 오차는 왕복 상쇄로 과대평가될 수 있음(10-20 §1).

### run_ir_exposure.sh · chk_ir_exposure.py · chk_ir_exposure_diag.sh · chk_ir_gain_off.sh — 10-19 노출 시험 (Jetson 호스트 4.58.3)
- `chk_ir_exposure.py`: 서비스로 노출 · 게인 설정 → 1.5 s → 4 s 측정. 메타 `== 0` 이면 켬, 실제 노출 · 게인 = 메타 `actual_exposure` · `gain_level`. 줄: `설정 · 실제 노출·게인 · 끈 IR 밝기 · FAST 중앙(5~95 %) · 켠 깊이 유효 · 설정 결과 [...]`. 결함: '설정 결과' False 를 판정에서 안 봄(§5 실수 5).
- `chk_ir_exposure_diag.sh`: 파라미터 범위(`describe` — 노출 1~200000, 게인 16~248), CLI 설정 결과, 메타 연속(노출 · 게인 · 레이저 · 모드), 드라이버 로그 오류, 영상 저장 → 그림 `ir_flash_aeoff_both_dots.png`.
- `chk_ir_gain_off.sh`: 번갈이 없이 IR 만(깊이 · 컬러 끔) 30 fps 로 다시 기동 → 자동 · 게인 64 · 128 · 248 · 노출 33000.
- 출력 `run_ir_exposure.txt` · `chk_ir_exposure_diag.txt` · `chk_ir_gain_off.txt`. 계보 → 10-21 `anal_mx1.py`(RSUSB · 시험 컨테이너, FAST5 추가).

### prep_eoff.sh · chk_eoff.sh · get_f2z1.sh — 상시 끔 주행 준비 (Jetson · PC)
- `prep_eoff.sh` = `SENSORS_ADD="emitter_off:=true" bash /tmp/prep_patrol.sh lite`. `chk_eoff.sh`: `emitter_enabled` 값, 원시 IR · 깊이 · 점군 · 조각 주기, IR1 메타의 레이저 · 노출 · 게인 3 개, 분리 노드 통계 2 줄. 출력은 파일로 안 남음(SUMMARY §25 수치가 전부 — **원문 없음**). `get_f2z1.sh`: 주행 bag 을 PC 스크래치패드 `f2z1_vis/` 로, 러너 결과 줄을 `f2z1_run.txt` 로(→ `outputs/run_f2z1.txt`).

### run_box_depth_ab.sh · anal_box_static.py · fig_box_static.py — B 정지 시험 (Jetson · PC)
- `run_box_depth_ab.sh`: 구성 on(지금) · off(`emitter_off:=true`)마다 prep → 20 s → 20 s 기록(`~/bags/bt_<on|off>`: /tf · /tf_static · 깊이 · camera_info · 조각 · 로컬 코스트맵) → 끝에 지금 구성 복귀.
- `anal_box_static.py 이름=bag …`: 깊이 프레임마다 유효 비율(전체 · 아래 절반), 상자 부피(지도 x 1.10~1.32 · y −0.25~+0.03 · z 0.02~0.17) 안 점 수(그 순간 tf 로 지도에). 조각 마지막 5 s 중앙값: 상자 칸(상자 ± 1 칸) 수, 북 · 서 면(`anal_slice_box` 정의), 빈 바닥(x 0.40~1.05 · |y| < 0.45) 표면 안 칸(유령) · 미지 비율.
- 출력 [`anal_box_static.txt`](../debug_log/2026-10-20/outputs/anal_box_static.txt) 2 줄(§2 표의 원문). 재사용: 10-20 §8 데시메이션 A/B 가 같은 도구를 씀.

### chk_isaac_rs_prereq*.sh · up_rs_image_build.sh · up_rs_splitter.sh · chk_rs_ws*.sh · chk_rs_apt_sim.sh · up_rs_apt.sh — 컨테이너 RealSense 층 (Jetson, docker)
- `chk_isaac_rs_prereq{,2,3,4}.sh`: 이미지 · 컨테이너 목록, `isaac_ros_common` · `isaac_ros_nvblox` 판, `Dockerfile.realsense`, 메모리 · 디스크(읽기만). 출력 파일 없음(SUMMARY §17 서술).
- `up_rs_image_build.sh`: `docker buildx` 로 지금 이미지 + `Dockerfile.realsense`(make -j3) → `isaac_ros_dev-aarch64-rs:latest`, 로그 `~/rs_build/build.log`(Jetson). 끝 줄 `rs_image_build_end.txt`.
- `up_rs_splitter.sh`: 시험 컨테이너 `isaac_rs_test`(옛 옵션 + `/dev` 마운트) 생성 · splitter 빌드 · (a)~(c) 확인. `chk_rs_ws.sh` · `chk_rs_ws2.sh`: `COLCON_IGNORE` · `dpkg` · `docker diff`. `chk_rs_apt_sim.sh`: apt 모의(Inst 46 · Remv 0). `up_rs_apt.sh`: 같은 판 3 개 apt 설치 → `src_rs/` 복사본 빌드 → (a)~(d) 재확인.

### run_nv_static.sh · nv_static.launch.py · anal_nv_static.py · chk_nv_*.sh — nv1 (Jetson 시험 컨테이너)
- `nv_static.launch.py`: 한 component container 에 드라이버(NVIDIA `realsense_emitter_flashing.yaml`, camera_name 'camera') + `nvblox::RealsenseSplitterNode`(입출력 QoS SENSOR_DATA) + cuVSLAM(그림자 설정 · IMU 융합 끔 · 입력 = 분리 노드 끈 IR). `NV_MODE=off` 면 `emitter_enabled 0 · emitter_on_off False · 640x480x30`.
- `anal_nv_static.py [s] [flash|off]`: (1) 원시 깊이 · IR1 을 메타로 두 무리 → 실제 켬 판정(85 행 문구) (2) 분리 깊이 유효 · 아래 절반, 분리 IR1 밝기 · FAST20 · FAST5 · |lap| · 가운데 기준 프레임 수 (3) 끈 IR 메타 노출 · 게인 (4) cuVSLAM odom 수 · 이동 · vo_state (5) 주기. `run_nv_static.sh`: 스택 내림 → F 60 s → O 30 s → 정리, launch · 분석 파일은 PC 가 base64 로 붙여 넣음.
- `chk_nv_log.sh` · `chk_nv_cmp.sh` · `chk_nv_probe.sh`: 첫 실행 무효의 판별(드라이버 · cuVSLAM 로그, 옛 컨테이너 기동 로그 비교, 컨테이너 커밋 `:apt` 뒤 `/dev/input` 만 마운트로 재생성 · 토픽 목록).
- 출력 `run_nv_static.txt` · `_try1.txt` · `chk_nv_*.txt`. 한계: bag 없이 실시간 집계(§5 실수 9).

### run_mx1.sh · run_mx2.sh · mx_cam.launch.py · anal_mx1.py · anal_mx2_leak.py · fig_mx2_page.py — mx1 · mx2 (Jetson 시험 컨테이너 · PC)
- `mx_cam.launch.py`: 시험 컨테이너에 카메라만(NVIDIA yaml), `MX_EXP` · `MX_GAIN` 이 있으면 기동 파라미터로 자동 노출 끔 + 노출 · 게인, `MX_OFF=1` 이면 상시 끔 + 자동.
- `anal_mx1.py 60|30 [이름]`: 이름 없으면 단계별로 파라미터 서비스 설정 → 2 s → 6 s 측정(mx1), 이름 있으면 기동 상태 그대로 한 번(mx2). 메타 두 무리 중 깊이 유효가 높은 쪽 = 실제 켬. 줄: `모드 m(켬|끔): 깊이 n · 유효 · 아래 · IR n · 밝기 · FAST20 · FAST5 · |lap| · 노출 · 게인`, 드라이버 오류 수.
- `run_mx2.sh`: 설정마다 다시 기동 → 측정 → 무리별 IR · 깊이 한 장씩 png(base64 로 PC 에) → `figures/mx2/`. `anal_mx2_leak.py 폴더`: 끈 프레임 한 장에서 top-hat 5×5 > 20 흰 점 연결 성분(전체 · 아래 1/4). `fig_mx2_page.py`: 정리 페이지(수치는 `run_mx2.txt` · `anal_mx2_leak.txt` 에서 옮김) → `figures/mx2_page.html`(게시 주소는 SUMMARY §19.3 끝).
- 결함 · 한계: 새어 듦은 설정당 한 장(참고값). 메타 모드 표지가 무리 이름이라 상시 끔 대조에선 '모드 0(켬)' 으로 찍힘(§3 발췌 주석).

## 10. 용어
- **번갈이(emitter_on_off)**: 프로젝터를 프레임마다 켜고 끄기. 30 fps 면 켬 15 · 끔 15.
- **`frame_emitter_mode` · `frame_laser_power`**: RealSense 프레임 메타데이터의 프로젝터 상태 필드. 이 카메라(펌웨어 5.15.0.2)에선 1 · 150 이 붙은 프레임이 실제로 꺼진 영상이었다(드라이버 4.58.3 · 4.51.1 둘 다).
- **`on_mode`**: 우리 분리 노드가 '켬' 으로 볼 메타 값(기본 0 = 실측).
- **유효 비율**: 깊이 영상에서 0 아닌 화소 비율 — 프로젝터 켬이면 무늬 없는 면에도 깊이가 생겨 높다.
- **|라플라시안|**: 4-이웃 2 차 미분 절대값 평균. 점 무늬가 있으면 크다(켬 5~11, 끔 0.4~0.9, 상시 끔 밝은 장면 3~4).
- **FAST20 · FAST5**: OpenCV FAST 모서리 검출 문턱 20 · 5 의 개수. 추적 특징의 대리값일 뿐(cuVSLAM 검출기와 다름) — 어두운 영상에선 20 이 과소 계산.
- **자동 노출 · 게인**: 카메라가 영상 밝기에 맞춰 노출 시간(µs) · 증폭(16~248)을 정함. 번갈이에선 켬 · 끔 프레임이 같은 값을 쓰고 켠 프레임(밝은 점) 기준으로 잡힌다(메타로 확인).
- **V4L2 백엔드 · RSUSB 백엔드**: librealsense 가 카메라 제어를 커널 UVC(V4L2, 호스트 4.58.3)로 하느냐 libusb 직접(RSUSB, 시험 컨테이너 2.55.1)으로 하느냐. 10-19 거부 오류(`xioctl`)는 앞쪽, mx1 오류(`set_data_usb … RS2_USB_STATUS_PIPE`)는 뒤쪽.
- **component container 합성**: 여러 노드를 한 프로세스에 올려 같은 참여자 안에서 메시지를 넘김(UDP 소켓을 안 탐) — 10-19 §17 에서 IR 손실을 없앤 방법.
- **프로세스 안 기록**: `rosbag2_cpp::Writer` 로 받은 노드가 바로 파일에 씀 — `ros2 bag record` 의 DDS 구독 · 역직렬화를 없앰.
- **짝없음 · 교대깨짐**: 분리 노드 통계 — 이미지와 메타 stamp 가 0.5 s 안에 안 맞음 / 같은 모드가 연속.
- **수동 스테레오**: 프로젝터 없이 장면 자체 질감으로 좌우 영상을 맞춰 깊이를 구함 — 민무늬 바닥 · 흰 벽에 구멍, 틀린 짝은 유령 점.
- **점 새어 듦**: 긴 노출에서 끈 프레임에 다음(또는 앞) 켠 프레임의 점 무늬가 찍히는 것(mx2 관찰, 기전 추정).
- **850 nm 플러드 조명**: 점이 아니라 고르게 비추는 근적외선 조명 — 끈 프레임 장면 밝기를 올리는 후보(시험 안 함).
