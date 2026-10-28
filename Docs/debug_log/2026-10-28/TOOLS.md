# 2026-10-28 도구 (상황 → 도구 → 나온 값 → 그때의 추론, 나중에 ✔/✘/？)
⚠ 이 파일은 §8 시점에 늦게 만들었다(작업하면서 채우는 규칙을 앞 § 에서 놓침). §0~§7 은 SUMMARY 에서 옮겨 적음.

| § | 상황 | 도구 | 나온 값 | 그때의 추론 | 판정 |
|---|---|---|---|---|---|
| 0 | 하루 시작 상태 | `jobs/chk_day_start_1028.sh` | `outputs/chk_day_start_1028.txt` | 스택 · 지도 정상 | ✔ |
| 1~2 | 확인 주행 준비 | `jobs/up_prep_1028.sh` → `jobs/prep_smac_1028.sh` | `outputs/prep_smac_1028_1.txt` PREP_OK | 출발 가능 | ✔ |
| 3~4 | f2tt2 회수 | `jobs/get_f2tt2.sh` | `outputs/drives/f2tt2/*` | 처음엔 '러너 미실행' 으로 봄 | ✘(§3.1 정정) |
| 5 | 통로 반복 막힘 칸 출처 | `jobs/anal_corridor_cell.py` | `outputs/corridor_cell/*` | 회전 중 가장자리 한 칸 더 찍힘 | ✔ |
| 7 | place_server dry_run | `jobs/up_place_dry_1028.sh` → `jobs/chk_place_dry_1028.sh` | `outputs/chk_place_dry_1028{,b}.txt` 5 checked | 등록부 전부 통과 | ✘(통로 북쪽 빠짐, §8.1) |
| 7.1 · 8 | S1 실주행 f2pl1 | `jobs/up_place_s1_1028.sh` → `jobs/run_place_s1_1028.sh` | `outputs/drives/f2pl1/place_s1.log` 2 arrived · 통로 북쪽 rejected | 검사가 명목 자세를 봄 | ✔(§8.2) |
| 8 | 거절 순간 방향별 여유 | `jobs/anal_place_clear.py` | `outputs/place_clear_f2pl1.txt` −90° 0.110 · 비스듬 0.000 | 동쪽 물체 칸 x −1.365 | ✔ |
| 8 | 같은 자리 재현 · 수정 확인 | `jobs/up_place_dry_1028c.sh` → `jobs/chk_place_dry_1028c.sh` | `outputs/chk_place_dry_1028c1.txt`(−51° 거절 3/3) · `c2.txt`(−86° 수락, 여유 0.10) | 방향 고침으로 통과, 경계값 | ？(f2pl2 에서) |
