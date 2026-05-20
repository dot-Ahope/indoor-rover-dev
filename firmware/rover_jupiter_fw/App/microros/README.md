# micro-ROS 통합 (Comm Layer)

micro-ROS client 통합. F405가 직접 ROS2 노드로 동작한다.

## 구성 (예정)
- micro-ROS executor / publisher · subscriber
- serial transport (USART1 → CH340N → Jetson)
- 토픽:
  - 구독: `/cmd_vel`
  - 발행: `/wheel_odom`, `/imu/data_raw`, `/imu/mag`, `/rover/status`, `/battery`

## 통합 도구
`micro_ros_stm32cubemx_utils` (CubeMX 프로젝트용 공식 유틸).
micro-ROS 본 통합은 **F5 단계**에서 진행.

참조: `docs/FIRMWARE_DEV_PLAN.md §3.3, §4, §5`
