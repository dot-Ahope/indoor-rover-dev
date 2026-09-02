# 2026-08-28 — Step 4 완료: LiDAR yaw 확정 + SLAM 첫 맵(360° 회전, 자세 0.2cm 복귀)

> 출력: `outputs/`, 스크립트: `jobs/`. 전날(08-27) 이어서.

## 한 일
- 아침 Jetson 재부팅(08:51) 후 스택 재시작. **커널 HID 모듈 재부팅 후 자동 로드 확인**(iio:device0/1 생존) — 어제 빌드 영구 적용 입증.
- LiDAR yaw 정렬 실측·확정: 종이 흔들기(job6d/f/g) → 신뢰 낮음(좁은 스캔면·클러터) → **코너 벽 정지 테스트(job6h)로 확정**.

## 결과 (수치)
| 항목 | 값 |
|---|---|
| 재부팅 후 스택 | `/wheel_odom` 50Hz, `/scan` 10Hz, `/camera/camera/imu` 200Hz, `/odometry/filtered` 30Hz, battery 12.09V. HID 모듈 자동 로드 |
| LiDAR yaw | **π 확정.** 코너(정면+좌측 벽) 배치에서 스캔 근거리 아크가 base_link 0°(전방벽)~+90°(좌측벽)에 일치, 우측·후방 트임 일치. job6d(정면종이→raw lidar ±180°)·이전 C8과 정합. 좌우 반전 없음 |

## 판단·결정
1. **yaw 정렬은 코너 정지 테스트가 최선**: 종이 흔들기는 S2L 스캔면(지면+18.5cm)이 좁아 종이가 비껴가기 쉽고 사방 클러터로 신호가 묻힘. 코너 벽은 전 높이를 덮어 확실 + ground truth(정면/좌측) 명확.
2. **`Docs/rover.urdf` lidar_joint rpy = (0,0,π) 확정** (전날 적용분 유지). camera_link y부호(±0.0475)는 여전히 미확정 — 포인트클라우드 정합으로 판정 예정.


## LiDAR yaw 최종 확정 (오후, 여러 차례 오락가락 후)
- **결론: yaw=π, /scan은 ROS 오른손계 일치, inverted 불필요.**
- 과정: 종이 흔들기(job6d/f/g)는 S2L 스캔면 협소로 비신뢰. 코너 벽·단일물체도 클러터로 흐림. **좌측325mm·정면800mm 명확 배치(job6n)로 확정**.
- 판정 데이터: angle_increment=+0.1996°(오른손 표기), 좌측벽 raw−86°·정면벽 raw−168° → θ_L−θ_F=+82°≈+90°(방향 보존=회전, 거울 아님). base_link 프레임(yaw=π): 정면벽 +11°(정면)·좌측벽 +94°(좌측) 검증(job6o).
- **Foxglove 반전 착시 = stale tf_static**: yaw π→0→π 변경 중 클라이언트가 예전 yaw=0 캐시(정면벽 raw−168 → base −168=−x, 관찰과 일치). 브라우저 새로고침으로 해소. base_link 축 미표시로 world 프레임 기준 판단했던 것도 혼선 요인.
- 교훈: 라이다 정렬은 **거리로 구분되는 2벽 명확 배치 + base_link 프레임 수치**가 최선. Foxglove 육안은 시점·캐시·프레임표시에 취약. 최종 증명은 SLAM 주행.
- **★ ROOT CAUSE 확정(사용자 발견)**: Foxglove **fixed frame이 `map`으로 설정**돼 있었음. slam_toolbox 미가동으로 `map` 프레임 부재 → Fox글로브가 렌더 기준 못 잡아 스캔이 엉뚱하게 표시됨. **fixed frame을 `base_link`로 변경하니 정상**(정면·좌측 벽 포인트 올바름). yaw=π는 처음부터 맞았고(base_link 수치 항상 정합), 모든 혼선의 원인은 이 fixed frame 오설정. → SLAM 가동 후엔 map 프레임 생겨 map 기준도 정상.

## 코드 위치 이전 (사용자 요청)
- ros2 패키지 소스를 scratchpad → **`F:_Indoor_Rover\Rover
os2_ws\src\`** 로 이전(정본). `.gitignore`가 이미 ros2_ws/build·install·log 제외. `ros2_ws/README.md`에 동기화·실행법. 이후 여기서 편집→Jetson 동기화.

## ★ SLAM 첫 맵 완성 (Step 4 마무리)
- **360° 제자리 회전 맵핑 완주** (detach 실행 → WiFi 무관, 59s, 최소 여유 16.4cm 가드 미발동).
- **결정적 성공 지표: 360° 후 복귀 자세 x=+0.2cm, y=+0.1cm, yaw=+1°** → yaw(π)·EKF·자이로융합·슬립보정 전 체인 정합 최종 증명.
- 맵 215×225 @5cm(10.8×11.3m), 벽 492셀. 저장 `ros2_ws/maps/rover_map.{pgm,png,yaml}`. 제자리 회전 = 단일시점 별모양 → 전체 방 맵은 병진 주행 필요.
- WiFi 드롭 무관(제어경로 Jetson→USB→보드 로컬). 배터리 11.71V — 충전 필요.

## 스캔 포인트 끌림 진단·수정 (사용자 관찰)
- 증상: 회전 시 lidar 포인트가 회전방향으로 밀리다 특징점에 스냅. → **루프클로저 아님, 스캔매칭 보정 + 스캔 시간지연**.
- 진단(정적): `/scan` now-stamp **+112ms**, scan_time 95ms(10Hz 스윕), 스탬프=스윕시작, scan-odom 스탬프차 −160ms. → 10Hz 스윕을 slam이 한 순간 처리(deskew 없음) + 스탬프가 스윕시작이라 ~47ms 추가 과거앵커. 회전 0.28rad/s에서 ~1.8° 오차.
- 수정: **(1) `scan_restamp` 노드** — 스탬프 +scan_time/2(스윕중앙), `/scan_raw`→`/scan`. 지연 **100.6→52.8ms(−47.8)**. **(2) slam** minimum_travel_heading 0.08→0.03, minimum_time_interval 0.3→0.1 (보정 3배 잦게).
- 효과: 밀림 ~1.8°→~0.85° + 스냅간격 축소. 잔여 53ms=10Hz 라이다 근본한계(deskew/고속라이다 = 양산검토). **실시각 확인은 충전 후 회전 주행에서**.
- 파일: `ros2_ws/src/rover_bringup/scripts/scan_restamp.py`, `launch/lidar.launch.py`(rplidar→/scan_raw remap), `config/slam.yaml`.

## 미해결·다음
- **camera_link y 부호**: depth 포인트클라우드 vs scan 정합(RViz/Foxglove)으로 ±0.0475 판정.
- **SLAM 맵핑**(Step 4 마무리): yaw 확정됐으니 진행 가능. 저속 주행(≤0.08 m/s, ≤0.4 rad/s), 접지·안전 확인 후 `!`. 맵 일관성이 yaw 최종 증명 + 직진/자이로 스케일 재캘리브레이션 기준.
- **Step 5**: `full.launch.py` + systemd(사용자 확인 후).
