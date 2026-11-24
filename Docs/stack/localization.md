# 위치 추정 — slam_toolbox 저장 지도 위 위치 추정

[← 첫 페이지](../../README.md)

<p align="center"><img src="../media/2026-11-19_localization.gif" width="90%"/><br/><sub>같은 라이다 스캔(빨강)을 저장 지도에 얹음: 왼쪽 EKF 만 — 점점 벽에서 틀어짐, 오른쪽 slam_toolbox 보정 — 벽에 겹침. 30 배속</sub></p>

## 하는 일
- 사무실을 한 번 매핑해 저장한 지도(`office_v3`) 위에서, 라이다 스캔을 지도에 맞춰 `map → odom` 보정을 낸다. EKF 에 남은 오차(순회 중 최대 0.36 m)를 이 보정이 지운다.
- 포크 수정 한 줄: 원본은 새 스캔을 쓸지를 이동 거리로만 정해 제자리 회전 중 스캔을 버린다. '거리 또는 회전각이 문턱을 넘으면 처리' 로 바꿨다.
- 라이다 빔마다 취득 시각 차만큼 EKF 각속도로 각도를 되돌린다(회전 중 스캔 지연 101 → 9 ms).
- 출발 테이프 = 지도 원점. prep 이 출발 자세를 검사한다(±0.10 m · ±2° 밖이면 주행하지 않음).

## 알려진 한계
- 위치 추정 중 보정 시각이 멈추는 경우가 있어 Nav2 쪽 변환 대기 시간으로 막아 뒀다(원인 일부만 확인). → [SLAM stamp 정체](../issues/slam-stamp-freeze.md)
- 로버가 서 있으면 스캔을 처리하지 않아 정지 중 방향 드리프트를 고치지 못한다. → [정지 중 방향 드리프트](../issues/stationary-yaw-drift.md)
- 빔 시각 보정은 빔 순서 가정(번호가 클수록 나중)을 따로 확인하지 않았다. → [스캔 시각 보정](../issues/scan-drag-deskew.md)

## 관련 기록
- [slam_toolbox 포크](../issues/slam-fork-rotation.md) · [위치 점프 → office_v3](../issues/f2-patrol-loc-jump.md) · [사무실 매핑](../issues/f1-office-mapping.md)
- 지금 값(지도 · 처리 문턱 · 변환 대기): [CURRENT_STACK §2.1](../04_navigation/CURRENT_STACK.md)
