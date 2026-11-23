# 센서 융합 — robot_localization EKF

[← 첫 페이지](../../README.md)

<p align="center"><img src="../media/2026-11-19_fusion.gif" width="80%"/><br/><sub>같은 주행을 휠 엔코더만 · EKF · 지도 위 위치(slam_toolbox)로 그림. 휠과 EKF는 출발 자세만 맞추고 그 뒤 보정 없음. 오른쪽 위 수치 = 그 순간 지도 위치와의 거리, 40배속</sub></p>

## 하는 일
- 휠 속도 + 카메라(RealSense D455f) IMU 자이로 + Isaac ROS cuVSLAM 의 병진 속도를 EKF 하나로 합쳐 `odom` 자세를 낸다.
- 결과(8 목표 순회 f2rr1, 444 s): 지도 위 위치와의 최대 차이 **휠만 4.81 m, EKF 0.36 m**.

## 왜 이렇게 했나
- **궤도 차량은 제자리 회전 때 트랙이 미끄러진다.** 180° 돌 때마다 중심이 10~27 cm 옆으로 밀렸고(스캔 정합으로 잼), 휠 · 자이로만 쓰는 EKF 는 이 이동을 보지 못했다 → [제자리 회전 옆 밀림](../issues/f0-rotation-side-slip.md)
- 처음엔 라이다 스캔 정합(rf2o)을 넣었다. 회전 중 미끄러짐은 잡았지만 사람이 라이다를 가리면 틀린 값을 냈다 — 가림 · 오염을 거르는 게이트를 만들었고, 지금은 대조 구성으로 남김 → [rf2o 게이트 · 사람 시험](../issues/rf2o-gates-people.md)
- 지금은 카메라 영상 오도메트리(cuVSLAM)의 **병진 속도만** 넣는다. 회전 속도까지 넣는 것은 200 Hz 자이로에 가려 효과가 없었고, 병진 속도는 회전 미끄러짐을 12~29 % 줄였다(오프라인 재실행) → [cuVSLAM 병진 속도 융합](../issues/cuvslam-velocity-fusion.md)
- 보드 IMU 는 자이로 무반응이라 쓰지 않는다 → [자이로 소스](../issues/gyro-source-d455f.md)

## 남은 것
- 오래 세워 두면 `odom` 방향이 천천히 돈다(분당 0.04~0.39°) — 출발 전 다시 기동해서 피함 → [정지 중 방향 드리프트](../issues/stationary-yaw-drift.md)

## 더 보기
- 지금 값(EKF 입력 · 카메라 설정): [CURRENT_STACK §1](../04_navigation/CURRENT_STACK.md)
