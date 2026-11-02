# 2026-11-02 SUMMARY

## §0 문제 대장 4 기 마무리 · 5 기 착수 (사용자: "A·C 이어서 마무리하자. 그리고 다음 기수 진행하자.")
- 10-30 중단된 두 묶음은 이어 붙일 수 없어(중지된 작업 재개 불가) 남은 일만 맡긴 새 묶음 둘로 마무리 → 4 기 카드 전부 완료: 새 `pre-drive-dds-participants.md` · `phase-s-baseline.md`, `obstacles-to-costcritic.md` 도구 해설, `depth-obstacle-costmap.md` 09-21 §5~§6, `f0-rotation-side-slip.md` · `sensor-conditioner.md` 완료 확인, `jetson-wifi-link.md` 09-23 보강. `Docs/issues/ISSUES.md` 4 기 표 갱신(‘이어서 할 일’ 절 제거).
- 원본 대조(내가 확인): `ros2_ws/src/rover_bringup/launch/ekf.launch.py` 39~40 행 — vslam ≠ off(기본 prep) 또는 rf2o 면 **B3(회전 구간 vx·vy σ 0.3) 자동 켜짐**(10-06 R3 · 10-20 근거 주석) → 의도된 동작. CLAUDE.md §6 'B2·B3 는 코드만 있고 기본 끔' 은 B3 에 대해 낡음(문서만, 결정 대기).
- 묶음 보고(대조 안 함): cc1 원인(메타 스냅숏) 근거가 기록보다 약함 — 스냅숏 전에 이미 map→odom 이 절반 속도 · '30 s' 는 측정 근거 없음 · relay min_range 0.45 는 기본 global_camera:=obstacle 에만 걸리고 순회 구성(nvblox)은 우회.
