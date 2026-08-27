# 2026-08-26 — Jetson Phase 2: Step 0 ~ Step 3 (사후 작성 2026-08-27)

> 출력 캡처는 이 날 규약 채택 전이라 없음. 스크립트 원본은 `jobs/` (job0*~job3*), 핵심 수치는 아래에 옮김.

## 한 일
- **Step 0 환경 점검**: Ubuntu 22.04.5 / L4T R36.5.0(JetPack 6.2계) / Humble 설치됨 / dialout·docker 그룹 OK. WSL `Ubuntu-22.04` + sshpass 패턴 확립.
- **Step 1 micro_ros_agent**: apt 패키지 없음 → Docker(`microros/micro-ros-agent:humble`, `--net host`, `--device <실장치>:/dev/rover`, `-b 2000000`). 세션 수립 → 토픽 7종 확인.
- **Step 2 ros2_ws**: `rover_description`(URDF+RSP) + `rover_bringup`(`base.launch.py` = Docker agent + description). 접지 상태 저속 주행 테스트(사용자 승인).
- **Step 3 EKF**: robot_localization + `sensor_conditioner`(covariance 주입·자이로 바이어스 캘리브레이션·회전 슬립 보정). 정적/주행 검증.
- 문서 정합화: `JETSON_SETUP_BRIEF.md`(장치명 정책, hz 플래그, 휠 반경 Ø51, 모터 속도, IMU 경고, 슬립 계수), `rover.urdf`(wheel_radius 0.02567, imu_link).

## 결과 (수치)
| 항목 | 값 |
|---|---|
| CH340 장치 | `/dev/ttyCH341USB0` (WCH 벤더 드라이버 ch341 V1.9) → udev `/dev/rover` 심볼릭 링크 |
| 토픽 주기 | `/wheel_odom` 49.998Hz, `/imu/data_raw` 49.999Hz (σ≤0.2ms), `/battery` 12.12V |
| 주행 테스트 (접지) | 전진 0.05m/s 3s → 140mm, 후진 복귀 오차 3mm; 회전 0.3rad/s → 휠 36°/실 15° |
| F1 펌웨어 로그 대조 | 50mm/s 유지에 duty 92~93% (여유 거의 없음); 회전 시 휠 속도 목표의 52% |
| EKF | `/odometry/filtered` 30.000Hz; 휠 단독 구성 정적 드리프트 0 (45s) |
| 보드 자이로 | 손 회전 녹화 2회(88.6s·114.7s) 모두 \|z\|≤0.041 rad/s — **무반응** |
| 자기계 `/imu/mag` | 무발행 (`mag.valid` 항상 false) |
| 회전 슬립 계수 | 0.42 @ 0.20 rad/s, 0.28 @ 0.57 rad/s (육안 기준 2점) |

## 판단·결정 (근거)
1. **장치명 하드코딩 금지** → `lsusb`로 CH340 탐지 후 udev 심볼릭 링크(사용자 지시).
2. **agent 재시작 시 보드 RESET 필요** — 펌웨어는 부팅 시 1회만 세션 수립(`microros_task.c:183`), 60s resync는 엔티티 재생성 안 함. 펌웨어 과제로 기록.
3. **보드 IMU 융합 제외** — 정지 시 중력·노이즈는 실물처럼 보였으나(정적 값으로는 판별 불가) 동적 테스트에서 자이로가 회전을 전혀 감지 못함. 사용자 판단("프로토콜에 없음") 확인. D455f IMU로 대체 예정.
   - 기각된 가설: "저속이라 노이즈에 묻힘" — 실회전 0.087 rad/s는 노이즈 σ의 14배; 손 회전(1~3 rad/s)에도 무반응.
   - 기각된 가설: "트랙 슬립으로 차체가 안 돌았다" — 실제로는 15° 돌았고, 그마저 자이로에 없음.
4. **펌웨어 covariance=0 → Jetson 측 컨디셔너로 보완** (펌웨어 수정 금지 규칙). robot_localization은 0을 ε로 치환해 "완벽 측정"으로 취급하므로 필수.
5. **회전 슬립은 속도 의존** → 2점 선형보간 보정, 각속도 ≤0.4 rad/s 권장. LiDAR 확보 후 스캔매칭 기준 재캘리브레이션.
6. PID 정확도 질의: 휠 속도 루프는 슬립 영향 밖(정확), 시스템 전체(지령→차체) 정확도는 플랜트 모델 오차로 깨짐 → 정직한 오도메트리 + Nav2 외곽 루프로 보상, 근본은 실동작 자이로.
7. 모터 구동 스크립트는 Claude Code 분류기가 차단 → 사용자가 `!` 접두어로 직접 실행하는 운영 패턴 확립.

## 펌웨어 과제 목록 (보고만, 수정 안 함)
- agent 재연결(ping 실패 → 엔티티 재생성) 로직 부재
- covariance 전부 0 발행
- `imu_processor`가 비실측 자이로 값을 `valid=true`로 발행, 자기계 `valid=false`
- 접지 부하에서 duty 여유 부족(50mm/s에 92%) — 지속 주행 최고속 재실측 필요

## 미해결·다음
- Step 4: LiDAR(S2L) + D455f + SLAM — 센서 데크 3D 프린트 후. 사전 조사·준비는 2026-08-27로.
