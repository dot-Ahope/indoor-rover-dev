# 2026-10-28 SUMMARY

## §0 하루 시작 (사용자: "오늘 할 일 뭔가" → 제안: 시작 점검 → 확인 주행 1~2 회 → (SLAM A/B 한 회 더는 결과 보고) → F2.5 설계 착수; 사용자: "진행하라")
- 점검 `jobs/chk_day_start_1028.sh` → `outputs/chk_day_start_1028.txt`: Jetson 10:05 기준 가동 1 h 11 min(**밤사이 재부팅**) · Wi-Fi WEB_DEV_5G · `/tmp` prep 스크립트 전부 없음 · 스택 꺼짐(에이전트 컨테이너 1) · 10-27 수정 유지(`slam.launch.py` transform_timeout 1.5 · nvblox 층 return 수정 1 줄) · 디스크 45 %.
- 스크래치패드 러너 파일 수정 시각 갱신(7 일 자동 삭제 대비, 10-27 §9).

## §1 확인 주행 선언 — 결과 보기 전
- 목적: 10-27 의 두 변경(SLAM 위치 추정 transform_timeout 1.5 · 게이트 정리판 러너)은 f2tt1 1 회만 확인 → 같은 구성 반복.
- 구성: f2tt1 과 같음(no5 · `prep_patrol` + `planner:=smac` + 재계획 0.01 · Smac tol 0.35 · MPPI 28 · 5 · 수정 nvblox 층 · timeout 1.5). 주행 이름 f2tt2(· f2tt3). 상자는 테이프 자리.
- 판정(회마다): ① 8/8 · ABORT 0 · nav_guard 취소 0 ② nav2 odom→map 외삽 실패 0(SLAM 정체가 1.5 s 를 넘은 창 안의 실패는 따로 셈) · 'TF 외삽 → 중단' 0 ③ 1 s 넘는 정지 ≤ 1 ④ 통로 최소 정확 여유 ≥ 2.9 cm ⑤ 게이트 → 출발 ≤ 50 s. 기록: SLAM 정체 > 0.5 s 수 · 최대, 미래 여유 최소, 상자 복귀 최소, 통로 Smac 사용, Control loop missed.

## §2 prep 재전송 · prep
- `jobs/up_prep_1028.sh`(재전송 + `jobs/prep_smac_1028.sh`, 원문은 Jetson `/tmp/prep_full_1.txt`) → `outputs/prep_smac_1028_1.txt`: prep_fast aeb6e6cf3b · prep_patrol 4fe16954f6 · chk_prep 64b8beeadd · chk_drive_gate 5e92ec4a0a — **모두 PC HEAD blob 과 같음** · CR 0. 보드 세션 그대로(에이전트 세션 1 · /wheel_odom 25 Hz, 리셋 불필요).
- **PREP_OK** +86 s · 위치 추정 0.008 m · −0.3° · 배터리 12.37 V · tolerance 0.35 · REEDS_SHEPP · cp 3.0 · PathAlign 28 · PathFollow 5 · 프리셋 3 · odom1 /vslam/odom · SLAM localization · transform_timeout 1.5. chk_prep 이름표 수정(10-27 §24) 반영 확인(PathAlign · PathFollow 로 찍힘).
