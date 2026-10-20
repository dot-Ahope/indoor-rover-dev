# 2026-10-20 TOOLS

| 시각 · § | 상황 | 도구 | 값 | 추론 ✔/✘/？ |
|---|---|---|---|---|
| 09:xx · §0 | 하루 시작 | `jobs/chk_day_start_1020.sh` | 재부팅 직후, /tmp prep 없음, f2z1 csv 있음 | ✔ |
| 09:xx · §1 | f2z1 cuVSLAM 판정 | `jobs/get_vso_f2z1.sh` · 10-19 `anal_vslam_cmp.py`(yaw 통계 추가) | IMU 끔: 95 % 25.7 cm · yaw 0.8° vs EKF 57.2 cm · 5.0° | 밝으면 따라감 ✔ · IMU 켬이 나쁜 이유 ？ |
| 10:xx · §2 | B 정지 시험(켬/끔) | `run_box_depth_ab.sh` · `anal_box_static.py` · `fig_box_static.py` | 깊이 아래 절반 65 → 38 %, nvblox 상자 칸 10 → 13 · 면 차 ≤ 0.4 cm · 유령 0 | 정지에선 B 통과 ✔ · 움직일 때 ？ |
