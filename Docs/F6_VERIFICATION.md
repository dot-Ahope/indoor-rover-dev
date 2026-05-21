# F6 — 휠 오도메트리 + /wheel_odom 발행

| 항목 | 값 |
|---|---|
| 문서 ID | ROVER-FW-010 |
| 단계 | F6 (펌웨어 개발 9단계) |
| 목적 | 좌·우 휠 속도 적분 → 차체 pose 추정 → `/wheel_odom` (`nav_msgs/Odometry`) 50Hz 발행 |
| 전제 | F5c 완료 (cmd_vel ↔ 모터 정상) |

---

## 1. 추가/변경 사항

### 1.1 새 파일
- [`App/app/odometry.{h,c}`](../firmware/rover_jupiter_fw/App/app/) — 정기구학 + Euler pose 적분

### 1.2 [`Core/Src/freertos.c`](../firmware/rover_jupiter_fw/Core/Src/freertos.c)
- `controlTask` 에 `odometry_init()` + `odometry_update()` 추가 (100Hz)
- 호출 순서: encoder → speed_controller → safety → **odometry**

### 1.3 [`App/microros/microros_task.c`](../firmware/rover_jupiter_fw/App/microros/microros_task.c)
- `nav_msgs/msg/Odometry` publisher `/wheel_odom` 추가
- 정적 msg 1회 초기화: `frame_id="odom"`, `child_frame_id="base_link"`, covariance=0
- Spin loop 20ms 주기 (executor 10ms + osDelay 10ms)
- 매 cycle: `odometry_get()` → quaternion 변환 → `rcl_publish`
- Heartbeat 는 매 50 cycle (= 1Hz)
- **실측 발행률 ~16 Hz** (의도 50Hz). Odometry 메시지 720byte + transport write polling + XRCE-DDS framing 으로 cycle 이 ~63ms 까지 늘어남. Nav2 통상 10~30Hz 충분 → 그대로 사용. 더 빠르게 하려면 transport TX 를 DMA complete IRQ callback 화 또는 baud 2Mbps 검토.

### 1.4 RAM·Flash
| 영역 | F5c | F6 | 증가 |
|---|---|---|---|
| Flash | 93 KB | 103 KB | +10 KB (Odometry msg 타입) |
| RAM   | 94 KB | 97 KB | +3 KB (Odometry msg 글로벌 + frame_id 문자열) |
| 여유 RAM | 34 KB | 31 KB | -3 KB |

---

## 2. 알고리즘

### 2.1 정기구학 (control task, 100Hz)
```
v_l = encoder_read_velocity_mps(ENC_LEFT)
v_r = encoder_read_velocity_mps(ENC_RIGHT)
v   = (v_l + v_r) / 2
ω   = (v_r − v_l) / B          (B = 0.190 m)
```

### 2.2 Pose 적분 (Euler 1차)
```
x   += v · cos(yaw) · dt
y   += v · sin(yaw) · dt
yaw += ω · dt
yaw  = wrap(yaw, [-π, π])
```
dt = 10 ms (100 Hz).

### 2.3 ROS 메시지 변환 (microros task, 50Hz)
- `pose.pose.position.{x,y}` ← `(x, y)` (m)
- `pose.pose.orientation` ← yaw → quaternion (Z 축만): `qz = sin(yaw/2), qw = cos(yaw/2)`
- `twist.twist.linear.x` ← `v`
- `twist.twist.angular.z` ← `ω`
- `header.stamp` ← `HAL_GetTick() ms` 기반 (boot time, Agent sync 안 함)
- 6×6 covariance: 모두 0 (Nav2 가 "unknown" 처리)

---

## 3. 검증 절차

### 3.1 사전
- 새 펌웨어 플래시
- Jetson agent 동작 중
- 휠 받침대 상태 (cmd_vel 보내며 모터 회전 시킬 거)

### 3.2 토픽 발견
```bash
ros2 topic list
# 기대: /wheel_odom, /cmd_vel, /rover/f5b_heartbeat 모두 보임

ros2 topic info /wheel_odom
# 기대: Type: nav_msgs/msg/Odometry, Publisher count: 1

ros2 topic hz /wheel_odom
# 기대: ~50 Hz
```

### 3.3 메시지 구조 확인
```bash
ros2 topic echo --once /wheel_odom
```
기대 (정지 상태):
```yaml
header:
  stamp: {sec: 23, nanosec: 456000000}
  frame_id: odom
child_frame_id: base_link
pose:
  pose:
    position: {x: 0.0, y: 0.0, z: 0.0}
    orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
  covariance: [0.0, 0.0, ...]
twist:
  twist:
    linear:  {x: 0.0, y: 0.0, z: 0.0}
    angular: {x: 0.0, y: 0.0, z: 0.0}
  covariance: [0.0, 0.0, ...]
```

### 3.4 동작 검증 (cmd_vel + odom 비교)

**Test A — 직진**: `ros2 topic pub --once /cmd_vel ... "{linear: {x: 0.2}}"` 후 ~3초 회전, 정지 명령
- `pose.position.x` 가 ~0.6 m (0.2 × 3) 근처로 증가 (실제는 가속 시간 빼고 0.5 m 정도)
- `pose.position.y` ≈ 0 (직진)
- `yaw` ≈ 0

**Test B — 제자리 좌회전**: `... "{angular: {z: 1.0}}"` ~3초
- `position` 거의 변화 없음
- `yaw` 가 ~3 rad (= 1.0 × 3) 증가 (실제 약간 미달)

**Test C — 원 그리기**: `... "{linear: {x: 0.15}, angular: {z: 0.5}}"`
- `x, y` 곡선 그리며 변화
- `yaw` 가 증가

### 3.5 RViz 시각화 (선택)
```bash
ros2 run rviz2 rviz2
# Fixed Frame: odom
# Add → Odometry → Topic: /wheel_odom
# 차체가 odom 좌표계에서 cmd_vel 명령대로 움직이는 화살표가 나타남
```

### 3.6 체크 항목

| # | 항목 | 통과 조건 |
|---|---|---|
| 1 | 토픽 발견 | `/wheel_odom` 보임 |
| 2 | 발행률 | `ros2 topic hz` ≈ 15~20 Hz (Nav2 충분) |
| 3 | 정지 시 변화 없음 | cmd_vel=0 일 때 x, y, yaw 일정 |
| 4 | 직진 누적 | x 증가, y·yaw 거의 변화 없음 |
| 5 | 회전 누적 | yaw 증가/감소 (z 부호 매칭) |
| 6 | quaternion 정합 | yaw=0 → q={0,0,0,1}, yaw=π → q≈{0,0,1,0} |
| 7 | F5c 그대로 | `/cmd_vel` 명령 → 모터 회전, `/rover/f5b_heartbeat` 1Hz |
| 8 | freeHeap 안정 | F1 콘솔 freeHeap 변동 없음 |

---

## 4. 알려진 한계 / 다음 단계

- **시간 동기 안 됨**: header.stamp 가 boot time 기준. ROS2 `wall_clock` 과 차이. F8 에서 `rmw_uros_sync_session()` 으로 agent 시간 사용.
- **Euler 1차 적분**: 빠른 회전·고속에서 곡선 추적 오차 누적. 미세 개선은 mid-point yaw 또는 RK2.
- **Covariance 0**: Nav2 가 가중치 부여 못 함. F8 에서 휠 slip / IMU fusion 기반 추정.
- **휠 slip 무시**: dev 단계 평지 가정. 농지에선 IMU + GPS fusion 필요 (양산기).
- **TF broadcasting 없음**: `tf2_ros::TransformBroadcaster` 를 펌웨어가 보내려면 추가 작업. 일반적으로 Jetson 측에서 `odom → base_link` TF 변환을 별도 노드가 발행 (`/wheel_odom` subscribe → tf broadcast).

---

## 5. F6 완료 기준 (DoD)

- [ ] `ros2 topic list` 에 `/wheel_odom`
- [ ] `ros2 topic hz` ≈ 50 Hz
- [ ] 정지 시 x, y, yaw 일정 (드리프트 < ±5 mm/10s)
- [ ] cmd_vel 직진 → x 증가, y·yaw 거의 0
- [ ] cmd_vel 회전 → yaw 변화 (부호 정합)
- [ ] F5b/c 기능 그대로 (heartbeat, cmd_vel)

→ 통과하면 **F6 완료**, F7 (ICM-20948 IMU 본 init + `/imu/data_raw` 발행) 진행.

---

*문서 끝.*
