# 카메라(깊이)로 낮은 장애물 보기 · 기억하기 — 수평 띠 → VoxelLayer → STVL

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **우회**(이 카드 시기 기준) — 근접 때 깊이점이 끊기는 것(원인)은 남고, STVL 의 시간 감쇠로 '끊겨도 기억' 을 얻었다. 단 그 확인(job170)은 TF 정지가 겹친 주행이라 근거가 약하다(§3 · §5.14). 이후 09-10 에 감쇠 재설계 · 계측 결함 발견, Phase N 에서 nvblox 로 교체 | 09-08 ~ 09-09 (이 카드), 이후 09-10 ~ | [09-08 'N1.5 — D455f depth → 코스트맵 (`job59`)'](../debug_log/2026-09-08/SUMMARY.md) | `ros2_ws/src/rover_bringup/launch/camera.launch.py`(09-08 오전 `depthimage_to_laserscan` 노드 추가 → 같은 날 철회, 포인트클라우드 ON · `decimation_filter` ×4 · depth 15 fps) · `ros2_ws/src/rover_navigation/config/nav2_params.yaml`(obstacle_layer + `depth_scan` → `voxel_layer` → `voxel_layer`(카메라) + `obstacle_layer`(라이다) 분리 → `stvl_layer`). 커밋 `9782f851` · `f3fcae94` · `06e25103` · `569afa39` · `105cf07d` · `36121c6a` · `0d15ba08`(09-08), `f58df246` · `35e0c12f` · `dd519f62` · `134b157f` · `d1b4f940` · `f4dfaad9`(09-09) | [inflation · padding · 충돌검사 지평](inflation-padding-roles.md)(같은 주행들의 다른 줄기) · [라이다 근접 사각](near-wall-blindspot.md) · [Nav2 첫 구축](nav2-first-setup.md) · micro-ROS 보드율 회귀 · DDS 공유메모리(09-09 §8.9 · §8.15, 카드 예정) · nvblox 이전(Phase N, 카드 예정) |

**한 줄**: 라이다(z 0.185 m) 평면 아래의 낮은 상자를 카메라 깊이로 코스트맵에 넣으려 했다. 09-08 오전의 '깊이 이미지 수평 띠 → 가상 LaserScan' 은 가까운 낮은 상자를 띠가 넘어가서 철회했고, 포인트클라우드 + `VoxelLayer` 로 바꿨다. 그 뒤 이틀 동안 '피하다가 상자 쪽으로 돌진' 이 되풀이됐는데, 그 원인으로 소거(근접 · 라이다 · 카메라 자신)를 차례로 의심해 고쳤다가 모두 기각했다. 09-09 `clearing: false` 시험(job155)으로 **지워지는 게 아니라 마킹이 끊긴다**(가까워지면 카메라가 상자 점을 못 만듦)로 좁혔고, 스톡 VoxelLayer 에는 '관측이 끊겨도 유지' 기능이 없어 STVL(시간 감쇠 + 절두체)을 들였다. 근평면 `min_z` 를 실제 끊김 거리(0.45~0.51 m)보다 가깝게(0.25) 주면 STVL 이 '보여야 하는데 없다' 로 판단해 5 초 만에 지운다는 것까지 확인했다. 그사이 내 오진이 많았다(§5, 14 건). 그리고 이 카드에서 원문 출력을 다시 읽으니 SUMMARY 와 어긋나는 곳이 몇 군데 있다(§5.5 · §5.15 · §6).

## 1. 증상
- 09-08 job59 이전: 라이다만으로는 높이 0.11 m 상자를 못 본다(라이다 z 0.185, 회피 없이 직진할 상황). → 깊이 카메라로 보완하려는 N1.5 단계.
- 09-08 job66 · job70 · job81 사용자 관찰: "박스를 피해 왼쪽으로 꺾어 이동하다가, 어느정도 전진하니 박스가 인식이 안되었는지 박스쪽으로 돌진. 박스를 밀면서 목적지에 도착."(job66), "상자가 인식될 때는 피해가는 경로를 따라가다가, 상자가 사라지니 바로 상자가 있는 곳으로 경로를 수정"(job81, Foxglove).
- 09-09 job124 · job128 · job134: 접촉(실제 최근접 0.0 cm, 계산) — 코스트맵의 상자 칸이 0 으로 떨어진 직후 계획 여유가 음수가 됨.
- 그림: 09-08 SUMMARY '시각화 제공' 의 분석 페이지 링크(코스트맵 수정 전후 격자, 계획 대 실제 궤적) — 이 카드 작성 때 열어 보지 않았다. 원문 ASCII 격자는 `outputs/job64e_map.txt` · `job65_strictdepth.txt` · `job72_globalmark.txt` · `job79_accum.txt` · `costmap_ascii.json`.

## 2. 흐름 (시간순)
09-08 SUMMARY 에는 § 번호가 없어 절 제목으로 적는다. 09-09 결과는 `outputs/` 가 **비어 있어**(원문 출력 · CSV 미보관) SUMMARY 본문의 인용 블록이 유일한 데이터다 → 09-09 행의 데이터 칸은 '원천 소실(SUMMARY 인용만)'.

| 날짜 · 곳 | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-08 'N1.5 — 설계 선택' | 깊이 이미지 수평 띠 → `/camera/scan`(depthimage_to_laserscan, `scan_height` 50, range 0.30~1.50, 31 Hz 목표), local · global `obstacle_layer` 에 `depth_scan` 소스(marking + clearing) | 설계 계산: 광선 피치 ±3.7°, 1.0 m 에서 높이 0.08~0.21 m, 최하 광선 바닥 접점 2.2 m | 포인트클라우드(≈5.5 M pt/s) 대신 CPU 절감 | 커밋 `9782f851`, camera.launch 주석 |
| 09-08 'N1.5 — 결과 (정적)' | `job59_sensors_restart` · `job59b` · `job59c` · `job59f` · `job59g` | `/camera/scan` 31 Hz, 640 빔 ±39°, 유효 36 %. 정면 ±16° 에서 깊이가 (라이다 − 0.08) 보다 **5~10 cm 짧음**. −20° 에서 깊이 1.46 m vs 라이다 5.79 m → 로컬 −20° 광선 0.75~1.05 m 점유 | '깊이 전용 감지 확인'. −8 cm 편향은 원인 미확정(평평한 벽 재확인 예정 → **이후 기록 없음, 미확인**) | [job59f_depthcmp.txt](../debug_log/2026-09-08/outputs/job59f_depthcmp.txt) · [job59g_costchk.txt](../debug_log/2026-09-08/outputs/job59g_costchk.txt) |
| 09-08 'N1.5 재설계 — 왜 철회했나' | 사용자가 상자를 놓음 → `job59f`(= job60a) · `job60b` | `/camera/scan` 정면 1.40 m 그대로(배치 전과 같음). 행별 최소거리: 상자 = **행 277~316(피치 +7~+10°), 0.38 / 0.30 m, 높이 0.094 / 0.090 m**. 띠는 행 212~262 | 띠가 가까운 낮은 상자 위를 지나감 → **수평 띠 철회**(§5.1). '깊이를 라이다와 같은 레이어에 넣은 것도 오류'(→ 09-09 §8.7 에서 원인 아님으로 정정, §5.8) | [job60a_box_depthcmp.txt](../debug_log/2026-09-08/outputs/job60a_box_depthcmp.txt) · [job60b_depthrows.txt](../debug_log/2026-09-08/outputs/job60b_depthrows.txt) |
| 09-08 'N1.5 재설계 — 새 구성' | realsense 포인트클라우드 ON(`pointcloud__neon_.enable` — ARM 빌드 이름), decimation ×4, depth 15 fps. local · global `voxel_layer`(z 0~0.40, 5 cm × 8 층), 소스 `scan` + `depth`(min_h 0.06, max 0.40, range 0.30~1.8). `job60c` · `job60d` · `job60e` | 13.1 k pt/frame @15 Hz. CPU realsense 14.7 → 15.6 %, planner 8 → 11 % | 허용 | 커밋 `f3fcae94` (출력 원문 없음 — 60c/d/e) |
| 09-08 '결과 (정적)' | `job60f_pcbox`(base_link 집계), 코스트맵 광선 | x 0.5~0.7 m 에 z 0.06~0.40 점 **450 개**(307 + 143, z 중앙 0.079 / 0.085) = 상자. 광선 4 방향 모두 **0.6 m 부터 #** | 라이다 사각 보완 동작 확인. 상자가 범퍼 앞 7 cm 라 회피 불가 → 재배치 | [job60f_pcbox.txt](../debug_log/2026-09-08/outputs/job60f_pcbox.txt) · 재배치 뒤 [job60g_box2.txt](../debug_log/2026-09-08/outputs/job60g_box2.txt)(x 0.8~1.0 에 222 점) |
| 09-08 '회피 주행 `job61`' | 상자 정면 0.85 · y +0.13, 목표 (1.2, 0) | CANCELED 8.6 s · 16 cm, 제자리 좌우 회전 반복, stuck_monitor 1 회 | 'depth→코스트맵 정상 작동', 미완주 원인은 통로 기하(→ [inflation 카드](inflation-padding-roles.md) 에서 세 번 고쳐 씀) | [job61_avoid.txt](../debug_log/2026-09-08/outputs/job61_avoid.txt) · `.csv` |
| 09-08 '전역 플래너가 경로를 못 내던 문제 `job64`' | `job63_planquery` → 경로 없음(status 6). `job64c` · `job64d` · `job64e` | 전역 전방 0.8 m 부터 99~100, SLAM `/map` 은 0. 전역 셀 분포 미지 9858 · 자유 2434 · 치명(≥99) 3781. **초기화해도, 전역에서 depth 를 빼도(min_h 5.0) 그대로 99** | 원인 ① 깊이 단일 복셀 잡음(`mark_threshold 0`) + 전역 누적 ② 진단 오판(latched 스냅샷, §5.3). 조치: `always_send_full_costmap: true` · min_h 0.06 → **0.08** · range 1.8 → **1.2** · `mark_threshold` 0 → **1** | [job64b_planquery.txt](../debug_log/2026-09-08/outputs/job64b_planquery.txt) · [job64c_globaldiag.txt](../debug_log/2026-09-08/outputs/job64c_globaldiag.txt) · [job64d_cleartest.txt](../debug_log/2026-09-08/outputs/job64d_cleartest.txt) · [job64e_map.txt](../debug_log/2026-09-08/outputs/job64e_map.txt), 커밋 `06e25103` |
| 09-08 같은 절 '결과' | 조치 뒤 질의 | 경로 84 점 · 2.19 m(직선 1.60), 좌 +0.36 m 우회, 경로점 최대 비용 99. 전역 ASCII 는 전방 0.8~1.7 m 에 여전히 X 가 많음 | '전역이 깨끗해지고 경로 발견'(ASCII 를 보면 '깨끗' 은 과장 — 통로 가운데 띠만 열림) | [job65_strictdepth.txt](../debug_log/2026-09-08/outputs/job65_strictdepth.txt) |
| 09-08 '회피 주행 `job66`' | job56_osc 로 회피 | SUCCEEDED 21.6 s, 그러나 상자 구간(x 0.6~1.2) 실제 y **+0.086~+0.104**(CSV 재계산 일치) → 상자와 겹침 | 해석 후보 ① RPP 코너컷 ② 근접 깊이 소거 ③ 측정 오차 | [job66_avoid.txt](../debug_log/2026-09-08/outputs/job66_avoid.txt) · `.csv` |
| 09-08 '원인 확정 (사용자 관찰)' | 사용자: 왼쪽으로 꺾다 상자로 돌진 · 밀고 도착 | — | **'근접 시 깊이 소거로 상자가 지워짐'**(가설 ② 확정이라 씀) — 기제: 0.3 m 안 무효 + 상자 너머 광선이 레이트레이싱으로 지움. **오진**(§5.4) | SUMMARY 문장 |
| 09-08 '소프트웨어 기억 1차 시도 `job70`' | depth `raytrace_min_range` 0.30 → **0.90**(local · global) | 질의: 1.76 m · 좌 +0.38 · 최대 비용 **0**. 주행 SUCCEEDED 20.0 s, 최대 좌 +0.022 m, 상자 구간 y −0.005~+0.013 → 또 밀고 지나감. t 1.1 s ω +0.130 → t 3.3 s ω −0.202 | '원인이 소거가 아닐 가능성' | [job69a_planquery.txt](../debug_log/2026-09-08/outputs/job69a_planquery.txt) · [job70_memory_avoid.txt](../debug_log/2026-09-08/outputs/job70_memory_avoid.txt), 커밋 `569afa39` |
| 09-08 '★ 원인 확정 `job71`' | Nav2 없이 0.04 m/s 직진 0.42 m, 고정 상자 칸의 로컬 · 전역 비용 + 깊이점 | SUMMARY 표: 0.45~0.21 m 내내 로컬 100 · **전역 0**, 깊이점 319 → 8 | '기억은 성공, 전역에 깊이가 마킹되지 않는 것이 진짜 원인' — **오진**(§5.5). ⚠ 원문 출력은 **전역이 t 0~4.3 s(카메라~상자 0.625~0.472 m) 동안 100, t 4.5 s(0.462 m)부터 0** — SUMMARY 표는 0.45 m 부터만 옮겨 '처음부터 0' 이라 썼다 | [job71_watchbox.txt](../debug_log/2026-09-08/outputs/job71_watchbox.txt) |
| 09-08 같은 절 '검증 한계' | `job72`(전역 파라미터 · ASCII) · `job73_run`(전역 min_h · range 바꿔 재확인) | 전역 voxel 파라미터 = 로컬과 같음. job73: 'TF 실패' 1 회 뒤 '상자 후보 부족 9~17' 만 9 줄 | 상자가 이미 카메라 최소거리 안이라 재검출 불가 | [job72_globalmark.txt](../debug_log/2026-09-08/outputs/job72_globalmark.txt) · [job73_globalfilter.txt](../debug_log/2026-09-08/outputs/job73_globalfilter.txt) |
| 09-08 '⚠⚠ 정정 2건' A | 상자 재배치(앞범퍼 0.6 m) 뒤 `job74`(static ON/OFF, min_h · range 완화, 원복) | 네 조건 모두 로컬 99 · 전역 99, 상자 base (0.88, −0.02) = map (1.30, −0.07) | '전역 미마킹' 은 내 좌표 처리 오류(로컬 odom 을 map 좌표로 조회 · 고정 좌표 어긋남) | [job74_layers.txt](../debug_log/2026-09-08/outputs/job74_layers.txt) |
| 09-08 같은 절 B | `job75_forward`(프레임 정정, 전방 축 최근접 ≥99 거리) | 전역 최근접 0.64 → 0.32 m 로 줄어듦. 로컬 최근접은 **처음부터 끝까지 0.3** | '기억이 양쪽에서 유효', 남은 용의자는 RPP. ⚠ 로컬 열은 측정 하한(0.30)에 붙어 상자를 추적하지 못함(§5.15) | [job75_forward.txt](../debug_log/2026-09-08/outputs/job75_forward.txt) |
| 09-08 '★ 진짜 원인 확정 `job76`' | 충돌검사 지평 1.5 → 5.0 s | 우회 시작 → 정지 · BackUp → stuck 취소, 밀지 않음 | '코스트맵 소거설 · 전역 미마킹설은 모두 내 오진' — 이 줄기는 [inflation 카드](inflation-padding-roles.md) | [job76_avoid2.txt](../debug_log/2026-09-08/outputs/job76_avoid2.txt) |
| 09-08 '⚠ 소프트웨어 기억의 부작용' | 상자를 한쪽으로 재배치, `job77` → 사용자 중단 · `job79` 전역 ASCII | 질의: 직선 1.40 m 에 경로 5.79 m(비 4.14), 우 −1.11 m. 주행 ABORTED 82.3 s · 1.31 m · 최종 오차 133.6 cm. 전역 ASCII 가 X/# 로 가득 | 원인 = `raytrace_min_range 0.90` 을 **비롤링 전역**에 건 것 → 전역 0.30 · 로컬 0.90 | [job77_avoid3.txt](../debug_log/2026-09-08/outputs/job77_avoid3.txt) · [job79_accum.txt](../debug_log/2026-09-08/outputs/job79_accum.txt) · `job80_apply.sh`, 커밋 `105cf07d` |
| 09-08 '검토: 동적 장애물 vs 근접 기억의 충돌' | 사용자 질문(치운 물체가 유령으로 남지 않나) | job71 깊이점: 0.25 m 288 → 0.21 m 8 → '최소 측정거리 ≈ 0.22~0.25 m' | '지우지 않을 반경 = 물리 사각' → 로컬 0.90 → **0.35**(0.25 + 0.10). 결론 "충돌하지 않는다" — 전제가 09-09 §8.7 에서 틀림(§5.7) | 커밋 `36121c6a` |
| 09-08 '★★ 상자 소실의 진짜 기전' | 사용자 Foxglove 관측(job81) + 기하 | job81 SUCCEEDED 30.6 s, 좌 최대 +0.147 → 상자 밀림(사용자 확인). 표: 1.0 · 0.7 m 앞면(3 칸), 0.5 m 이하 윗면(z ≈ 0.11, 1 칸) | 가까우면 윗면만 보여 복셀 1 칸 → `mark_threshold 1` 이 거름. 조치 `mark_threshold` 1 → **0**, min_h 0.08 → **0.06**(`job82_apply`). ⚠ '보이는 면 · 복셀 칸 수' 표는 **기하 계산이지 측정이 아님**(원문 없음) | [job81_avoid.txt](../debug_log/2026-09-08/outputs/job81_avoid.txt) · 커밋 `0d15ba08` |
| 09-08 '마킹 지속 검증 성공' | `job83`(= job75 재실행) | 로컬 최근접 0.62 → 0.30, 전역 0.48 → 0.30, 깊이점 233 → 933 → 189~248 | '끝까지 사라지지 않는다' ✅. ⚠ 전역 최근접이 t 3.9 s 0.34 → t 4.2 s **0.54** 로 20 cm 뛰었다가 다시 줄어듦(SUMMARY 미언급, §6) | [job83_approach.txt](../debug_log/2026-09-08/outputs/job83_approach.txt) |
| 09-08 '회피 재시도' · '★ 마지막 발견' | job84 · 86 · 87 · 89 | 밀고 가는 현상 소멸, job89 만 완주 — 그러나 사용자 '치고 지나갔다' | 이 줄기는 [inflation 카드](inflation-padding-roles.md) | 같은 폴더 |
| 09-09 §1~§7 | micro-ROS 2 Mbps 에서 `/wheel_odom` 소실 → 460,800 bps | — | 이 카드 밖. 09-09 §10 '소급 영향': 09-08 이상 거동 일부가 odom 간헐 소실의 약한 증상일 가능성 인정 | 09-09 SUMMARY |
| 09-09 §8 | job119 · job124(lookahead) | job124 '최소 여유 28.0 cm' 보고 | → §8.6 에서 틀림(§5.10) | 원천 소실(SUMMARY 인용만) |
| 09-09 §8.6 | 계측 고침 `job125_avoid3.py` — 출발 때 map 에 고정한 상자 사각형 ↔ 차체 사각형 기하 거리, 계획 여유, lc_box · gc_box | job124 재계산 실제 최근접 **0.0 cm**(차체 좌측 끝 +0.132, 상자 좌측 끝 +0.134). '코너 컷' 진단 철회(횡오차 RMS 2.0 cm) | 계측 결함 인정 | 원천 소실 |
| 09-09 §8.6 원인 B | job128 | t 14 lc 99 · gc **0**, t 15 둘 다 0 → 계획 여유 −10.2 cm → t 17 접촉. 카메라~상자 0.147 m(최소 깊이 안), 라이다~상자 0.227 m(scan `raytrace_min_range` 0.2 밖) | '라이다가 못 보는 상자 칸을 관통해 지운다' → **레이어 분리**(voxel_layer = depth, obstacle_layer = scan, `combination_method 1`), `job129_layers.sh` | 커밋 `f58df246`, 원천 소실 |
| 09-09 §8.6 '남은 위험과 STVL 검토' | `job130_stvl.sh` | STVL 미설치, apt 2.3.4-1jammy | **도입 보류**(유령 문제 미측정 · 하루 세 원인 변경 직후) | 출력 원문 없음 |
| 09-09 §8.7 | 레이어 분리 배포 뒤 job134(상자 우측으로, 좌 여유) · `job135_live.sh` | 질의 좌 +0.29, 비용 최대 72(최근접 0.319 m → 여유 15.4 cm). 주행: t 5 gc 100 → **0**(카메라~상자 0.48 m), t 9 lc 100 → 0(0.29 m), t 12 접촉. live 파라미터로 분리 적용 확인 | **원인 B 기각**(§5.8). 새 기전 '카메라 자기 소거'(상자 옆 · 너머 바닥점 광선이 5 cm 격자로 상자 칸을 스침) → `raytrace_min_range` 로컬 0.35 · 전역 0.30 → **0.60** | 커밋 `35e0c12f`, 원천 소실 |
| 09-09 §8.8 job152 | 0.60 적용, 좌 여유 배치 | SUCCEEDED 1.56 m, 실제 최근접 **4.1 cm**, 접촉 경로 샘플 0/234, 좌우 전환 0. 그러나 gc t 5 · lc t 7 에 0. 그 시점 카메라~상자 0.518 m(< 0.60, 소거가 막혔어야 함). `job153_rt.sh` live 0.6 확인 | 패딩 0.05 로 양안정성 해결 · 여유 있으면 지워져도 완주. 소거 기전과 모순 | 원천 소실 |
| 09-09 §8.8 job155 | `job154_reinit.sh` 로 depth `clearing: false` 배포 → 주행 → `job156_stop.sh` 로 되돌림 | **소거 불가 상태에서** lc_box t 3 · 0 → t 6 · 100 → t 11 · 0 → t 12 · 99 → t 13 · 0 → t 15 이후 0. CANCELED, 실제 최근접 0.0, 계획 최소 여유 −16.1 cm | **기전 = 마킹 중단**(매 주기 마스터 리셋 뒤 각 레이어가 다시 그림 — 레이어 격자에 그 순간 마킹이 없으면 0). 소거 계열 가설 3 개 기각 | 커밋 `dd519f62`, 원천 소실 |
| 09-09 §8.10 | 대안 조사 `job158_alt.sh` | 스톡 심볼 `observation_persistence` · `expected_update_rate` · `combination_method` 존재, realsense `json_file_path` 존재, STVL 미설치 | 대안 4: persistence · 계획 확정성(BT RateController 1.0 → 0.33) · RealSense 최소거리 축소 · STVL. **미해결 모순**: 끊김 0.518 m vs job71 최소거리 0.22~0.25 m → 지표 ⑤(상자 사각형 안 깊이점 수) 추가 | 출력 원문 없음 |
| 09-09 §8.11 | STVL 설치(`job160` — 사용자 사전 고지, sudo) · 파라미터 이름 확인(`job161` · `job162` 심볼, `job163` 공식 예제) · 배포(`job164` · 실패 → `job165` 로그 → 복구 `job166`) | 첫 배포 planner_server exit 255: `Can not get 'plugin' param value for static_layer` — 교체 스크립트가 static_layer 블록까지 지움(§5.12). 복구 뒤 양쪽 `stvl_layer ... Initialized`, 코스트맵 1.667 / 0.667 Hz | 구성: voxel_decay 15 · decay_model 0 · `depth_mark`(marking, range 1.2, min_h 0.06) + `depth_clear`(clearing, 절두체 min_z **0.25** · max_z 1.5 · 87°×58° · decay_acceleration 3.0). '공식 실내 예제의 마킹/소거 소스 분리' 패턴 | 커밋 `134b157f`, 원천 소실 |
| 09-09 §8.13 job167 | voxel_decay 15, min_z 0.25 | t 3 깊이점 142 · lc 99 → t 4 깊이점 0 · lc 99 유지 → t 19 만료. 지표 ⑤: 로컬이 잃은 81 샘플 중 깊이점 있던 것 **0 %**. 끊김 거리 0.51 → 0.45 m | 'STVL 은 정확히 voxel_decay 만큼 버팀', **'카메라가 점을 못 만든다'**(코스트맵이 버리는 게 아님). decimation 4 가 사각을 넓혔다(S2, 추정). 설정 주석: 15 s 만료 때 최근접 0.4 cm 까지 붙음 → 30 s | 커밋 `d1b4f940` 주석, 원천 소실 |
| 09-09 §8.13 job169 | voxel_decay 30, min_z 0.25 | t 5 점 소실 → t 10 마킹 소실(카메라~상자 0.43 m, 절두체 **안**) | 근평면이 실제 끊김보다 가까워 '볼 수 있는데 없다' → decay_acceleration 가속 소거. **min_z 를 잘못 준 내 실수**(§5.13) | 원천 소실 |
| 09-09 §8.13 job170 | voxel_decay 30, min_z **0.55** | 깊이점 t 2 · 3 → t 3 이후 0, 상자 자리 로컬 최소 99 · 전역 최소 99, 접촉 경로 0/140, 좌우 전환 0 | **'S1 의 기전 확정'**. ⚠ 같은 주행이 §8.14 에서 **t ≈ 4.0 s 부터 map→base_link 갱신 정지**로 밝혀짐 → '전 구간 유지' 는 대부분 TF 가 멈춘 구간의 값(§5.14) | 커밋 `f4dfaad9`, 원천 소실 |
| 이후 09-10 ~ | (다른 카드에서 채움) | 09-10 §2 decay_acceleration 3.0 → 0.0(절두체 안 0.580 m 에서 2~3 s 소실), §8 로컬 `decay_model -1`(영속) · 전역 voxel_decay 90, §9 **job125 `detect_box` 가 벽을 상자로 잡는 결함**(median, 52 cm 어긋남) → ①②③⑤ 무효 · job167 결론도 무효 판정, §11.1 고친 계측으로 **끊김 ≈ 0.40 m 실재**(무효 판정 정정), §11.2 영속인데도 로컬이 깊이 소실 1.3 s 뒤 상자 버림. 09-11 · 09-21 Phase S 기준선 → Phase N nvblox | — | [09-10 SUMMARY](../debug_log/2026-09-10/SUMMARY.md) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 깊이 이미지 수평 띠면 낮은 장애물을 본다 | job60a(상자 놓은 뒤 `/camera/scan` 정면) · job60b(행별 최소거리) | 정면 1.40 m 그대로, 상자는 띠 아래 행(+7~+10°) | **기각**(가까운 낮은 물체) |
| 포인트클라우드 + VoxelLayer 로 9 cm 상자가 마킹된다 | job60f(점 집계) · 코스트맵 광선 | 0.6 m 부터 # | **지지**(정지 상태) |
| 전역 오마킹 = 단일 복셀 잡음 + 누적 | job64c/d/e → mark_threshold 1 · min_h 0.08 · range 1.2 뒤 job65 | 경로 생김. 단 job64d 의 '깊이를 빼도 99' 는 latched 스냅샷 때문에 해석 불가 | **부분 지지**(조치 뒤 경로가 생겼다는 것만 측정. 어느 조치가 효과인지 분리 안 됨) |
| 근접 때 깊이 광선이 상자 칸을 지운다(raytrace) | job70(0.90 으로 근접 소거 금지) | 또 밀고 지나감 | **기각**(09-08 job75 · 09-09 job155 로 재확인) |
| 전역 코스트맵에 깊이가 안 찍힌다 | job74 · job75 | 양쪽 99 | **기각**(내 조회 오류). 단 job71 원문의 '전역이 0.46 m 에서 100 → 0' 은 설명되지 않은 채 남음(§5.5) |
| 전역에 근접 기억을 걸면 유령이 쌓인다 | job77 · job79 | 5.79 m 경로, ASCII X/# 가득 | **지지** |
| 기억 반경 = 물리 사각(0.22~0.25 m)이면 기억 · 망각이 양립 | 09-08 논리, 09-09 job134 | 전역 0.30 · 로컬 0.35 인데 0.48 · 0.29 m 에서 소실 | **기각**(전제 '못 봐서 지워짐' 이 틀림) |
| 근접 때 윗면만 보여 복셀 1 칸 → mark_threshold 1 이 거름 | 사용자 관측 + 기하 계산, job83 | 1 → 0 뒤 job83 끝까지 유지 | **부분 지지**(job83 은 정지 · 직진 접근이고, 09-09 주행에서는 다시 소실) |
| 라이다가 못 보는 상자 칸을 관통 소거(원인 B) | 레이어 분리 뒤 job134 · job135 | 같은 방식으로 소실 | **기각**(분리는 원칙상 유지) |
| 카메라가 자기 마킹을 광선으로 지운다 | raytrace_min_range 0.60(job152) | 0.518 m(< 0.60)에서도 소실 | **기각** |
| 소거 자체가 기전이다 | **clearing: false**(job155) | 셀이 100 ↔ 0 을 오감 | **기각 → 마킹 중단** |
| 마킹 중단 = 카메라가 점을 못 만든다(코스트맵이 점을 버리는 게 아님) | 지표 ⑤(job167) | 잃은 81 샘플 중 깊이점 있음 0 % | 당시 **지지** → 09-10 §9 에서 계측 결함(벽을 상자로)으로 **무효 판정** → 09-10 §11.1 에서 끊김 ≈ 0.40 m 실재로 **부분 복원** |
| STVL 시간 감쇠로 '끊겨도 기억' 이 된다 | job167 · 169 · 170 | 15 s 유지 / 5 s(근평면 오류) / 전 구간 | **지지(약함)** — job170 은 t ≈ 4 s 부터 TF 정지(§8.14). 깨끗한 확인은 09-10 job192 'S1 완주'(이후) |
| STVL 근평면 min_z 는 실제 끊김 거리여야 한다 | job169(0.25) vs job170(0.55) | 5 s vs 유지 | **지지**(단 job169 · 141 도 TF 정지 서명일 가능성 — §8.14 "job141 · 169 도 같은 서명일 가능성이 높다", 미확인) |

## 4. 조치와 효과 — 깊이 소스 파라미터 이력
| 시점(커밋) | 레이어 · 소스 | mark_threshold | depth min_h | depth range(max) | depth raytrace_min_range (로컬 / 전역) | 근거 | 효과 |
|---|---|---|---|---|---|---|---|
| 09-08 오전(`9782f851`) | obstacle_layer: scan + depth_scan(LaserScan) | — | — | 1.5(min 0.3) | 0.3 / 0.3 | CPU | 가까운 낮은 상자 놓침 → 철회 |
| 09-08(`f3fcae94`) | voxel_layer: scan + depth(PointCloud2), z 0~0.40 · 8 층 | 0 | 0.06 | 1.8(min 0.30) | 0.30 / 0.30 | 3D 소거 · 높이 | 정적 마킹 OK |
| 09-08(`06e25103`) | 같음 + `always_send_full_costmap: true` | **1** | **0.08** | **1.2** | 0.30 / 0.30 | 전역 잡음 | 경로 생김(job65) |
| 09-08(`569afa39`) | 같음 | 1 | 0.08 | 1.2 | **0.90 / 0.90** | 근접 소거 금지 | job70 실패, 전역 유령(job79) |
| 09-08(`105cf07d`) | 같음 | 1 | 0.08 | 1.2 | 0.90 / **0.30** | 전역 누적 | — |
| 09-08(`36121c6a`) | 같음 | 1 | 0.08 | 1.2 | **0.35** / 0.30 | 물리 사각 0.25 + 0.10 | — |
| 09-08(`0d15ba08`) | 같음 | **0** | **0.06** | 1.2 | 0.35 / 0.30 | 윗면 1 칸 | job83 유지 |
| 09-09(`f58df246`) | voxel_layer: depth 만 / obstacle_layer: scan 만(combination 1) | 0 | 0.06 | 1.2 | 0.35 / 0.30 | 원인 B | job134 소실 |
| 09-09(`35e0c12f`) | 같음 | 0 | 0.06 | 1.2 | **0.60 / 0.60** | 카메라 자기 소거 | job152 완주(소실은 남음) |
| 09-09 job155(런타임 배포, 되돌림) | 같음 + depth `clearing: false` | 0 | 0.06 | 1.2 | 0.60 / 0.60 | 판별 시험 | 소실 그대로 → 마킹 중단 |
| 09-09(`134b157f`) | **stvl_layer**: depth_mark + depth_clear / obstacle_layer: scan | 0 | 0.06 | 1.2(obstacle_range) | (STVL: 절두체 min_z 0.25 · max_z 1.5) | 끊겨도 기억 | job167 15 s 유지 |
| 09-09(`d1b4f940`) | 같음, voxel_decay 15 → **30** | 0 | 0.06 | 1.2 | min_z 0.25 | job167 만료 때 0.4 cm | job169 5 s 소실 |
| 09-09(`f4dfaad9`) | 같음 | 0 | 0.06 | 1.2 | min_z **0.55** | 실측 끊김 0.45~0.51 + 여유 | job170 유지(TF 정지 겹침) |

- 카메라 쪽(camera.launch, `f3fcae94`): depth 640×480 **15 fps**(30 → 15), 포인트클라우드 ON(`pointcloud.enable` · `pointcloud__neon_.enable` 둘 다), `decimation_filter` ×4(160×120, 주석 '19.2 k pt/frame', 실측 유효점 13.1~14.7 k).
- 한계: (1) 근접 깊이 끊김 거리 자체는 그대로(0.40~0.51 m — 09-09 job167 · 09-10 §11.1). decimation 이 원인이라는 것은 **추정**(S2 미실행). (2) STVL 절두체 소거는 '하단 화각 밖 · 가림' 을 구분 못 함(09-10 §10). (3) 09-08 '확정된 인과' 표의 #2(mark_threshold)는 09-09 에 그 조치 상태에서도 소실이 되풀이돼 충분 조건이 아니었다.

## 5. 내 실수 (칸 형식)
### 5.1 수평 띠(depthimage_to_laserscan) 설계
| 칸 | 내용 |
|---|---|
| 하려 한 것 | CPU 를 아끼려 깊이 이미지 가운데 50 행만 가상 LaserScan 으로 만들어 라이다와 같은 ObstacleLayer 에 넣음(`9782f851`) |
| 본 것 | job60a: 상자를 놓았는데 `/camera/scan` 정면 1.40 m(배치 전 1.40). job60b: 상자는 행 277~316(피치 +7~+10°), 0.30~0.38 m, 높이 ≈ 0.09 m |
| 처음 추론 | 설계 계산 '1.0 m 에서 높이 0.08~0.21 m 를 본다' 로 낮은 장애물이 잡힐 것 |
| 의심한 이유 | 상자를 놓아도 가상 스캔 값이 바뀌지 않음 |
| 판별 | 행 띠별 최소거리(job60b) |
| 결론 | 띠의 높이 창은 거리에 비례해 좁아져, 10 cm 물체는 0.66 m 안쪽에서 띠 **아래**로 빠진다(SUMMARY 계산). 낮은 물체는 가까울수록 위험한데 가까울수록 안 보이는 설계였다 → 철회 |
| 다음에 알아보는 법 | 센서 창(높이 · 거리)은 '먼 곳에서 보이는가' 가 아니라 '**회피가 필요한 거리**(범퍼 앞 0.3~0.6 m)에서 보이는가' 로 검사한다. 설계 직후 실제 물체를 놓고 원 이미지 행별로 확인 |
| 데이터 | `2026-09-08/outputs/job60a_box_depthcmp.txt` · `job60b_depthrows.txt`, 도구 `jobs/job59f_depthcmp.py` · `job60b_depthrows.py` |

### 5.2 결론을 '정리된' 격자로 과장 — job65 '전역이 깨끗해졌다'
- job65 출력 ASCII 는 전방 0.8~1.7 m 좌우에 X 가 여전히 많고 가운데 한 줄(폭 0.5~0.7 m)만 열렸다. '깨끗해지고 경로 발견' 중 측정된 것은 '경로 발견' 뿐이다. 어느 조치(mark_threshold · min_h · range · full 발행)가 효과였는지는 한 번에 넷을 바꿔 분리되지 않았다. 데이터: `outputs/job65_strictdepth.txt`.

### 5.3 latched 스냅샷 진단 오판
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 초기화 · 깊이 제외 뒤 전역 코스트맵이 바뀌는지 보고 원인을 가름(job64d) |
| 본 것 | 초기화 직후에도, 전역 depth min_h 를 5.0 으로 올려도 전방 0.8~1.8 m 가 99~100 그대로 |
| 처음 추론 | (기록상) 그 관찰을 근거로 '누적성 오마킹' 을 의심 |
| 의심한 이유 | 초기화 서비스가 성공했는데 값이 그대로 |
| 판별 | Nav2 발행 방식 확인: 기본은 증분(`*_updates`)이라 TRANSIENT_LOCAL 로 `/…/costmap` 을 읽으면 마지막 **전체** 발행(옛 스냅샷)을 받는다 |
| 결론 | job64d 의 두 결과는 해석 불가. `always_send_full_costmap: true`(양쪽) |
| 다음에 알아보는 법 | 코스트맵을 토픽으로 읽는 도구는 먼저 '읽은 메시지의 stamp 가 지금에 가까운가' 를 출력한다. `always_send_full_costmap` 이 꺼진 시기의 모든 정지 상태 진단(아래 §8 의 job59g · 60h · 60j · 62b · 64c · 64d · 64e)은 같은 위험이 있다 — 로버가 움직이지 않으면 롤링 로컬도 전체 재발행이 없다(**추정**, Nav2 발행 조건을 이 저장소에서 확인하지 않음) |
| 데이터 | `outputs/job64d_cleartest.txt`, 도구 `jobs/job64d_cleartest.sh` · `job64c_globaldiag.py` |

### 5.4 '근접 소거로 상자가 지워진다'
| 칸 | 내용 |
|---|---|
| 하려 한 것 | job66 의 '피하다 직진 · 밀고 도착'(사용자 관찰) 원인 |
| 본 것 | job66 실제 y +0.086~+0.104(상자와 겹침), 사용자 관찰 |
| 처음 추론 | 카메라~상자 < 0.30 m 에서 픽셀 무효 + 상자 너머 바닥 · 벽을 맞힌 광선이 상자 칸을 레이트레이싱으로 지움 → '원인 확정' 이라고 씀 |
| 의심한 이유 | `raytrace_min_range` 0.90(job70)으로 근접 소거를 막았는데 또 밀고 지나감. 궤적상 경로가 직진으로 바뀐 시점 카메라~상자 ≈ 0.40 m(실명 전) |
| 판별 | job71(코스트맵만 관찰), job74 · job75 |
| 결론 | 당시: '소거 아님, 충돌검사 지평'(job76). 뒤에 09-09 job155 로 '소거 아님, 마킹 중단' 으로 다시 확인 |
| 다음에 알아보는 법 | '사용자 관찰과 맞는 기제' 하나를 찾았다고 '확정' 이라고 쓰지 않는다. 기제를 끄는 시험(여기서는 clearing false)을 먼저 하고 확정. 이번에는 그 시험을 하루 뒤에야 했다 |
| 데이터 | `outputs/job66_avoid.csv` · `job70_memory_avoid.txt`, 09-09 §8.8(원천 소실) |

### 5.5 '전역에 깊이가 마킹되지 않는다' (job71) — 그리고 SUMMARY 표가 원문과 다르다
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 접근 중 상자 칸이 언제 · 왜 사라지는지 판정표(깊이점 × 비용)로 가름 |
| 본 것(SUMMARY) | 카메라~상자 0.45~0.21 m 에서 로컬 100 · 전역 0 |
| 본 것(원문 재독) | `job71_watchbox.txt`: t 0.0~4.3 s(0.625~0.472 m) **전역 100**, t 4.5 s(0.462 m)부터 전역 0, 그 순간 깊이점 316(많음). 로컬은 끝까지 100 |
| 처음 추론 | '전역은 처음부터 끝까지 0, 한 번도 마킹 안 됨 → depth 가 전역에 반영 안 됨', 'job61 · 66 · 70 의 원인' |
| 의심한 이유 | job74 정적 4 조건에서 전역 99 |
| 판별 | job74 · job75(프레임 정정판) |
| 결론(당시) | 내 조회 오류 — ① 시작 자세로 고정한 map 좌표가 map→odom 보정으로 어긋남 ② 로컬(odom)을 map 좌표로 조회 |
| 결론(이 카드) | ② 는 **로컬** 열의 문제이고, map 프레임인 전역 열의 0 을 직접 설명하지 않는다. ① 은 가능하나(5 cm 칸 하나만 봄) 어긋남을 잰 값이 없다. 원문 패턴(깊이점이 충분한데 전역이 0.46 m 에서 꺼짐)은 09-09 job134 '전역이 0.48 m 에서 먼저 소실' 과 같은 꼴이다. 즉 job71 은 이미 '깊이점이 있는데 전역 칸이 꺼지는' 현상을 담고 있었고, 그 원인은 **미확인**이다(그때 전역 `raytrace_min_range` 는 0.90 이라 '근접 소거' 로도 설명이 안 됨). 또 SUMMARY 의 '카메라 최소 측정거리 0.22~0.25 m' 도 이 출력의 '상자근방 깊이점' 에서 나왔는데, 그 수는 고정 map 좌표 ±0.12 m 상자 안 점이라 좌표가 어긋났다면 함께 틀린다 |
| 다음에 알아보는 법 | 표를 SUMMARY 로 옮길 때 **전 구간**을 옮기거나, 자른 구간을 밝힌다. 칸 하나를 조회하는 도구는 그 칸 둘레(±2 칸) 최댓값도 함께 낸다. 코스트맵 조회는 그 코스트맵의 `global_frame` 으로(09-08 마무리 '공통 교훈') |
| 데이터 | `outputs/job71_watchbox.txt` · `job74_layers.txt` · `job75_forward.txt`, 도구 `jobs/job71_watchbox.py` · `job75_forward.py` |

### 5.6 근접 기억(raytrace_min_range 0.90)을 비롤링 전역에 검
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 근접 실명 구간에서 상자를 지우지 않게(job70, local · global 모두 0.90) |
| 본 것 | job77: 직선 1.40 m 에 경로 5.79 m, ABORTED 82.3 s. job79 전역 ASCII X/# 가득. 사용자 "멈춰라 이상하게 움직인다" |
| 처음 추론 | (적용 때) 양쪽에 같은 값이 안전 |
| 의심한 이유 | 경로 비 4.14 |
| 판별 | 전역 ASCII(job79) |
| 결론 | 전역은 누적이라 '지우지 않는 반경' 안의 모든 마킹이 영구히 남는다 → 전역 0.30 · 로컬 0.90(`105cf07d`) |
| 다음에 알아보는 법 | 같은 파라미터라도 롤링(자가 소멸) vs 누적 레이어에 주는 효과가 반대일 수 있다. 전역 변경 뒤에는 ASCII 덤프로 '로버가 지나간 자리' 를 본다 |
| 데이터 | `outputs/job77_avoid3.txt` · `job79_accum.txt`, 도구 `jobs/job64e_map.py` · `job80_apply.sh` |

### 5.7 '지우지 않을 반경 = 물리 사각(0.25 m)' 의 전제
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 근접 기억과 동적 장애물 망각의 양립(사용자 질문) |
| 본 것 | job71 깊이점 0.25 m 288 → 0.21 m 8 |
| 처음 추론 | 소거가 '못 봐서' 일어나므로 반경을 최소측정거리 + 0.10 = 0.35 로 두면 충돌 없음 → 로컬 0.35 |
| 의심한 이유 | 09-09 job134: 전역 0.30 · 로컬 0.35 인데 0.48 m · 0.29 m 에서 순서대로 소실 |
| 판별 | 09-09 §8.7 기하, §8.8 job155 |
| 결론 | 전제 둘 다 틀림 — '못 봐서 지운다' 도 아니고(마킹 중단), 실제 끊김 거리도 0.22~0.25 m 가 아니라 0.40~0.51 m |
| 다음에 알아보는 법 | 이 카드 §5.5 처럼 '최소 측정거리' 를 다른 조건(정지 · 저속 · 다른 좌표 고정)에서 잰 값을 그대로 옮기지 않는다. 같은 조건에서 거리별 점 수를 다시 센다 |
| 데이터 | `2026-09-08/outputs/job71_watchbox.txt`, 09-09 §8.7(원천 소실) |

### 5.8 원인 B '라이다가 못 보는 것을 지운다' → 레이어 분리
| 칸 | 내용 |
|---|---|
| 하려 한 것 | job128 의 t 14 소실 설명 |
| 본 것 | 카메라~상자 0.147 m(못 봄), 라이다~상자 0.227 m(scan raytrace_min_range 0.2 밖), 소실 직후 계획 여유 −10.2 cm |
| 처음 추론 | 같은 voxel_layer 를 쓰는 라이다 광선이 상자 칸을 관통해 지움(09-08 오전 '같은 레이어에 넣은 것도 오류' 와 같은 생각) |
| 의심한 이유 | 분리 뒤 job134 에서 같은 시점 · 같은 방식으로 소실 |
| 판별 | job135 live 파라미터(분리 적용 확인) |
| 결론 | 원인 아님. 분리는 '센서는 자기가 감지할 수 있는 것만 지운다' 원칙상 유지 |
| 다음에 알아보는 법 | 기하로 '가능하다' 를 보인 것은 원인의 증거가 아니다. 가능한 기전을 하나 끄고 증상이 사라지는지로 판정 |
| 데이터 | 09-09 §8.6 · §8.7(원천 소실), 도구 `2026-09-09/jobs/job129_layers.sh` · `job135_live.sh` |

### 5.9 '카메라가 자기 마킹을 지운다' → raytrace_min_range 0.60
| 칸 | 내용 |
|---|---|
| 하려 한 것 | job134 에서 전역(0.30)이 먼저(0.48 m), 로컬(0.35)이 나중(0.29 m) 무너진 순서 설명 |
| 본 것 | '값의 크기 순서와 정확히 일치' |
| 처음 추론 | 상자 옆 · 너머 바닥점 광선이 5 cm 격자에서 상자 칸을 스침 → 0.60 |
| 의심한 이유 | job152: 0.518 m(< 0.60)에서도 소실, live 값 0.6 확인(job153) |
| 판별 | job155 clearing:false |
| 결론 | 기각. '순서가 맞는다' 는 우연(0.48 m 는 0.30 보다 멀어 0.30 이 막을 수 있는 거리도 아니었다 — 이 카드 재독) |
| 다음에 알아보는 법 | 반경 파라미터의 효과를 주장하려면 소실 거리가 그 반경 '안' 인지 '밖' 인지 먼저 본다(0.48 > 0.30 은 그 시점 이미 반증) |
| 데이터 | 09-09 §8.7 · §8.8(원천 소실), 도구 `job153_rt.sh` |

### 5.10 '최소 여유' 를 실시간 깊이 점으로 잼(job92 · job124)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 실제 접촉 여부를 수치로(job92_avoid.py '최소 여유') |
| 본 것 | job124 '최소 여유 28.0 cm (접촉 0)' |
| 처음 추론 | 접촉 없음 |
| 의심한 이유 | 사용자 "상자에 너무 가까이 붙어서 움직였다" |
| 판별 | CSV 로 상자 사각형(주행 직전 서베이 x 1.033~1.143, y −0.046~+0.134) ↔ 차체 사각형 기하 |
| 결론 | 실제 0.0 cm. 상자가 화각을 벗어나면 '최근접 점' 이 다른 물체로 바뀜(t 16 nan · t 17 1.211) → job125 의 출발 고정 상자 기하로 교체 |
| 다음에 알아보는 법 | 옆을 지나는 간격은 전방 센서로 재지 않는다. 지표가 '무엇까지의 거리' 인지(대상 고정 여부)를 이름에 넣는다 |
| 데이터 | 09-09 §8.6(원천 소실), 도구 `2026-09-09/jobs/job92_avoid.py` → `job125_avoid3.py`. ⚠ 고친 job125 도 상자 검출이 median 이라 09-10 §9 에서 벽을 상자로 잡는 결함이 드러남 |

### 5.11 '코너 컷' 진단(09-09 §8)
- job119 에서 '같은 x 에서 계획 +0.315 인데 로버 +0.230 → 8.5 cm 코너 컷' 이라 했으나, 비교한 경로가 **주행 전 질의 경로**였다(Nav2 는 계속 재계획). 주행 중 횡오차 RMS 2.0 cm 로 컨트롤러는 그때의 경로를 잘 따랐다 → 철회(09-09 §8.6). 칸 형식 기록은 [inflation 카드 §5](inflation-padding-roles.md).

### 5.12 STVL 첫 배포에서 static_layer 블록 삭제
| 칸 | 내용 |
|---|---|
| 하려 한 것 | nav2_params.yaml 의 voxel_layer 블록을 stvl_layer 로 스크립트 교체 |
| 본 것 | planner_server exit 255, `FATAL: Can not get 'plugin' param value for static_layer` |
| 처음 추론 | — |
| 판별 | `job165_err.sh`(nav2.log 의 planner_server · global_costmap 줄) |
| 결론 | 교체 스크립트가 `plugins:` 줄부터 다음 마커까지 잘라내며 인접한 static_layer 블록까지 지움 |
| 다음에 알아보는 법 | 'plugins 에 나열된 모든 레이어에 plugin 키가 있는가' 를 YAML 파싱으로 검증(09-09 §8.11 에서 추가한 절차). 문자열 범위 치환으로 YAML 을 고치지 않는다([Nav2 첫 구축 카드 실수 ②](nav2-first-setup.md) 와 같은 계열) |
| 데이터 | 09-09 §8.11(원천 소실), 도구 `job164_stvlup.sh` · `job165_err.sh` · `job166_nav2only.sh` |

### 5.13 STVL 근평면 min_z 를 옛 실측값(0.25)으로 줌
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 근평면 = '못 보기 시작하는 거리' 로 두어 실명 구간 마킹을 보존 |
| 본 것 | job169: voxel_decay 를 15 → 30 으로 늘렸는데 5 초 만에 소실 |
| 처음 추론 | (설정 때) job71 실측 0.22~0.25 m 가 사각 |
| 의심한 이유 | 수명을 2 배로 늘렸는데 더 빨리 사라짐 → 수명이 아닌 다른 것이 지움 |
| 판별 | 소실 시점 상자 거리 0.43 m = 근평면 0.25 보다 멀어 절두체 **안** → '보여야 하는데 없다' → decay_acceleration 가속 감쇠. min_z 0.55 로 job170 유지 |
| 결론 | 내 설정 실수. 같은 날 같은 구성에서 잰 끊김 거리(job167 0.51 → 0.45 m)를 써야 했다 |
| 다음에 알아보는 법 | 센서 사각을 파라미터로 줄 때는 **현재 구성**(decimation · fps)에서 잰 값만 쓴다. `min_z` 와 디시메이션은 짝(설정 주석에 명시) |
| 데이터 | 09-09 §8.13(원천 소실), 설정 주석 `nav2_params.yaml`(커밋 `f4dfaad9`) |

### 5.14 job170 '전 구간 유지 · S1 기전 확정' 과 '배터리 탓 무이동'
| 칸 | 내용 |
|---|---|
| 하려 한 것 | min_z 0.55 의 효과 확인 |
| 본 것 | 상자 자리 로컬 · 전역 최소 99, 접촉 경로 0 %. 로버는 t 5 부터 전진 0.240 에 고정, 후진 지령 −0.050 을 8 초 받고도 무이동 |
| 처음 추론 | '전 구간 유지 ✅ S1 기전 확정', 무이동은 '배터리가 공통 인자로 가장 유력'(11.94 V) |
| 의심한 이유 | 사용자 질의 "왜 후진하고 멈췄나" → CSV 전체 정밀도 재독: t 4.01 이후 99 샘플이 소수점 17 자리까지 같음, 9.90 s 뒤 조회 실패 = tf2 버퍼 10 s |
| 판별 | 09-09 §8.14 시간표 |
| 결론 | 로버가 아니라 **map→base_link 갱신이 멈춤**(§8.16: CPU 부족 → EKF 주기 실패 → slam 스캔 폐기). 배터리설 철회. 그렇다면 job170 의 '유지' 는 t ≈ 4 s 이후 코스트맵 · 조회 둘 다 낡은 변환 위에서 나온 값이라 STVL 효과의 증거로 약하다(이 카드 판단 — SUMMARY 는 §8.13 결론을 고치지 않음) |
| 다음에 알아보는 법 | 결과 표에 '로버 위치가 마지막으로 바뀐 시각' 을 함께 낸다. 같은 값이 N 샘플 이상 연속이면 TF 정지 경고. '배터리' 같은 공통 인자는 상관만 보고 원인으로 쓰지 않는다 |
| 데이터 | 09-09 §8.13 · §8.14 · §8.16(원천 소실 — CSV 미보관) |

### 5.15 job75 · job83 의 '로컬 최근접' 열
- job75 원문: 로컬 최근접이 34 샘플 내내 **0.3**(조회 시작점 d = 0.30 m 에서 이미 ≥99). 전역은 0.64 → 0.32 m 로 줄었다. 즉 이 주행의 로컬 열은 상자 거리를 따라가지 않았고, '소프트웨어 기억이 **양쪽**에서 유효'(09-08 '정정 B') 중 로컬 쪽은 이 데이터로 보이지 않는다. 0.30 m 에 무엇이 있었는지(근접 기억 0.90 반경 안의 다른 마킹, 차체 근처 잡음 등)는 **미확인**. job83(mark_threshold 0 뒤)에서는 로컬 열이 0.62 → 0.30 으로 움직여 정상적으로 읽힌다. 데이터: `outputs/job75_forward.txt` · `job83_approach.txt`, 도구 `jobs/job75_forward.py`.

### 5.16 포인트클라우드 해석 정정의 범위
- job62c 머리 주석 "이전 job60f/60i 는 x, y, z 를 연속 배열로 잘못 읽었을 수 있음". 코드를 보면 **job60f** 는 `point_step == 12` 일 때만 연속 읽기(틀림)이고 그 밖에는 점마다 `struct.unpack_from(i*step + offset)`(맞음)인데, 실제 `point_step` 은 16 이었다(job62c 출력) → job60f 의 450 점 결과는 **올바른 해석**이다. **job60i** 는 늘 `np.frombuffer(count=N, offset=…)` 연속 읽기라 point_step 16 에서 틀린다(그 출력은 보관 안 됨 · SUMMARY 미인용 — 영향 없음). '폭 0.30 m' 오독은 해석 오류가 아니라 min/max 통계 오류다([inflation 카드 §5](inflation-padding-roles.md)).

## 6. 남은 것
- **근접 깊이 끊김의 원인 · 거리**: 09-09 0.45~0.51 m(job167), 09-10 §11.1 ≈ 0.40 m. D455 사양 최소 거리보다 훨씬 멀다. decimation ×4 가 넓혔다는 것은 추정(S2 '디시메이션 재검토' 는 이 시기 미실행).
- job71 에서 깊이점이 충분한데 **전역 칸만** 0.46 m 에서 꺼진 이유(§5.5) — 미확인. job83 의 전역 최근접 0.34 → 0.54 m 점프도 미설명.
- 09-08 의 −8 cm 깊이 편향(라이다 대비) — '평평한 벽 재확인 예정' 뒤 기록 없음.
- 상자 치수 기록: 09-08 사용자 실측 폭 0.18 · 높이 0.11 · 세로 0.11 m, 09-21 BASELINE 은 '18×14×11 cm'. 같은 상자인지 · 어느 쪽이 맞는지 미확인.
- 09-09 의 모든 주행 수치는 원문 출력 · CSV 가 저장소에 없다(`2026-09-09/outputs/` 비어 있음). 그리고 09-10 §9 의 `detect_box` median 결함은 09-09 job125 판(같은 median 코드)에도 그대로 있어, 09-09 의 ①(실제 최근접) · ②(계획 여유) · ③(lc_box/gc_box) · ⑤(깊이점)가 벽을 상자로 잡은 채 계산됐는지 **확인할 수 없다**(원천 소실). 09-09 §8.6 job124 '상자 x 1.033~1.143, y −0.046~+0.134' 는 상자 폭 0.18 과 맞아 그 주행은 상자를 잡은 것으로 보인다(추정).
- 동적 장애물 망각('상자 치우기 시험')은 09-08 · 09-09 내내 미실행.
- 이후(09-10 ~): 다른 카드에서 채움 — decay_acceleration 0 · 로컬 영속 · 전역 90 s(09-10 §2 · §8), 계측 결함과 정정(09-10 §9 · §11), STVL 절두체 한계와 nvblox 이전 판단(09-10 §10), Phase S 기준선(09-21) · Phase N.

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| job59 · 59b · 59c · 59d · 59e | 센서 재시작 · 가상 스캔 확인 · Nav2 소스 확인 · stuck_monitor 중복 정리 · CPU | `2026-09-08/jobs/` (출력 원문 없음) |
| job59f · job60a | 깊이 가상스캔 vs 라이다 각도별 비교(상자 전 · 후) | `outputs/job59f_depthcmp.txt` · `job60a_box_depthcmp.txt` |
| job59g · job60a | 로컬 코스트맵 광선 | `outputs/job59g_costchk.txt` · `job60a_box_costchk.txt` |
| job60b | 깊이 이미지 행별 최소거리 | `outputs/job60b_depthrows.txt` |
| job60c · 60d · 60e | VoxelLayer 기동 · 포인트클라우드 파라미터 진단 · NEON 이름으로 켜기 | `jobs/` (출력 원문 없음) |
| job60f · job60g | 포인트클라우드 x 구간 집계 + 광선 | `outputs/job60f_pcbox.txt` · `job60g_box2.txt` |
| job60h · 60i · 60j | 코스트맵 초기화 · 높이 점검 · min_h 단계 시험 | `jobs/` (출력 원문 없음) |
| job61 · 66 · 70 · 76 · 77 · 81 · 84 · 86 · 87 · 89 | `job56_osc.py` 주행(목표 · 20 Hz CSV) | `outputs/<이름>.txt` · `.csv` |
| job62c · job64a · job69b | 상자 경계 · y 히스토그램 · 바닥 z | `outputs/job62c_boxdim.txt` · `job64a_boxpos.txt` · `job69b_boxnow.txt` |
| job63 · 64b · 65 · 69a | 무주행 경로 질의 | `outputs/job64b_planquery.txt` · `job65_strictdepth.txt` · `job69a_planquery.txt` |
| job64c · 64d · 64e · 72 · 79 | 전역 진단 · 초기화 시험 · ASCII | `outputs/job64c_globaldiag.txt` · `job64d_cleartest.txt` · `job64e_map.txt` · `job72_globalmark.txt` · `job79_accum.txt` · `costmap_ascii.json` · `drive_path.json` |
| job67 · 68 · 78 · 80 · 82 | foxglove 화이트리스트 · 기억 설정 확인 · Nav2 정지 · 전역 raytrace 0.30 · mark_threshold 0 | `jobs/` (출력 원문 없음) |
| job71 · 73 · 74 · 75 · 83 | 상자 칸 추적 · 프로브 · 레이어 배제 · 전방 축 추적 | `outputs/job71_watchbox.txt` · `job73_globalfilter.txt` · `job74_layers.txt` · `job75_forward.txt` · `job83_approach.txt` |
| job125 계열(09-09) | `job125_avoid3.py` 주행: job126 · 128 · 134 · 141 · 152 · 155 · 167 · 169 · 170 | `2026-09-09/jobs/job125_avoid3.py`, **출력 · CSV 원천 소실** |
| job127 · 129 · 135 · 153 · 154 · 156 | 배포 · live 파라미터 · 재기동 · 정지 | `2026-09-09/jobs/` |
| job130 · 158 · 160~166 · 168 · 171 | STVL 조사 · 설치 · 파라미터 · 배포 · 확인 | `2026-09-09/jobs/` |
| run_j.sh · run_osc.sh · run_param.sh | PC(WSL) → Jetson 전송 · 실행 | `2026-09-08/jobs/` · `2026-09-09/jobs/` |

## 8. 도구 해설
공통:
- **실행 위치**: 전부 Jetson(당시 192.168.0.101). PC 의 WSL 에서 `run_j.sh <파일> [인자]`(09-09 폴더) 또는 `run_osc.sh` · `run_param.sh`(09-08 폴더)가 `sshpass -p <PW> scp` 로 스크래치패드(세션 `82ce61d4…`, 09-28 자동 소실 — 저장소 사본이 유일) 파일을 `/tmp/` 로 보내고 `ssh` 로 `python3 /tmp/…` 또는 `bash /tmp/…` 를 실행해 마지막 60 줄을 돌려받는다. 셸 스크립트 속 `/tmp/job59g_costchk.py` 처럼 다른 도구를 부르는 것은 그 파일이 먼저 `/tmp` 에 올라가 있어야 한다.
- **코스트맵 읽기**: `/local_costmap/costmap` · `/global_costmap/costmap`(OccupancyGrid)을 QoS depth 1 · TRANSIENT_LOCAL · RELIABLE 로 구독해 마지막 한 장을 쓴다. 값 0~100(Nav2 가 0~255 를 줄임: 253 내접 → 99, 254 치명 → 100, 255 미지 → −1). 칸 = `int((x − origin)/resolution)`. 09-08 14:24(`06e25103`) 전에는 `always_send_full_costmap` 이 꺼져 있어 정지 상태에서 옛 스냅샷일 수 있다(§5.3).
- **yaw**: 쿼터니언에서 `atan2(2·w·z, 1 − 2·z²)`(roll · pitch 0 가정).
- **포인트클라우드**: `/camera/camera/depth/color/points`(frame `camera_depth_optical_frame`, point_step 16), TF 로 base_link 또는 map 으로 회전 · 이동.

**도구 계보**
- 깊이 → 코스트맵 확인: job59f(가상 스캔 vs 라이다, 각도) → job60b(원 이미지 행) → job60f(포인트클라우드 x 집계, 점마다 unpack) → job62c(point_step 스트라이드 정확 해석 · y 히스토그램 · 바닥 z) → 09-09 job137(job125 검출 필터 단계별 점 수) → 09-10 클러스터링 판(`_clusters_y`) → 09-21 `job478_boxphys.py`.
- 코스트맵 칸 조회: job59g(로컬 광선 4 개, 기호) → job62b(로컬 부채꼴 격자) → job64c(전역 · `/map` 대조) → job64e(전역 · `/map` ASCII 로버 기준) → 09-09 job131(전역 · 로컬 · SLAM 부채꼴, 프레임 변환 포함).
- 상자 칸 추적: job71(고정 map 좌표 1 칸, 로컬도 map 좌표로 — 결함) → job73_probe(정지 1 회) → job75(전방 축 최근접 ≥99, 각 코스트맵 자기 프레임) → 09-09 job125(출발 고정 상자 사각형, 로컬은 map→odom 변환, 주행 중) → 09-10 재고정 · 클러스터링 → 09-18 · 09-23 재고정 조건(TEST_COURSE_AND_GATES §15).
- 주행 러너: job56_osc(목표 + 20 Hz 진동 지표) → 09-09 job92_avoid(실시간 깊이점 '최소 여유' — 결함) → job125_avoid3(상자 기하 · 계획 여유 · 칸 비용 · ⑤ 깊이점) → 이후 계속 수정되며 Phase S · N 러너로 쓰임.
- 정지 · 재기동: job59_sensors_restart · job78_killnav(`pkill -9`) → 09-09 job154_reinit · job156_stop(SIGTERM 우선, `/dev/shm/fastrtps*` 삭제 — DDS 사고 뒤).

### job56_osc.py — 목표 주행 + 20 Hz 트레이스 (09-08 회피 주행 전부)
- 부른 형태: PC `run_osc.sh <csv이름> <x> <y> <yaw_deg> <timeout>` → Jetson `python3 /tmp/job56_osc.py x y yaw timeout 이름`. 예: job61 은 (1.2, 0, 0), job66 은 (1.6, 0, 0), job89 는 (1.7, 0, 0).
- 왜: 09-08 오전 RPP 조향 진동 측정(§5.y)용으로 만들었고, 그 뒤 회피 주행에 그대로 썼다.
- 하는 일: `/cmd_vel`(지령) · `/odometry/filtered`(odom yaw) · `/plan`(전역 경로) 구독, TF map→base_link. `NavigateToPose` 목표(map) → 50 ms 마다 (t, v, ω, x, y, yaw_map, yaw_odom, lat_err) 기록. lat_err = 현재 `/plan` 선분까지 최근접 거리. 지표: 직진 구간(|v| > 0.03) ω 부호반전 / 주행거리 · 횡오차 RMS · map yaw 점프(|Δyaw_map − Δyaw_odom| > 1°) · ω 스파이크(|Δω| > 0.05 / 50 ms) · 제자리 회전(|v| < 0.01, |ω| > 0.2) 종료 뒤 3 s 부호반전 · 최종 오차.
- 출력: 화면 7 줄 + `/tmp/<이름>.csv` → PC 회수 → `outputs/job61_avoid.*` 등 10 회분.
- 쓰인 곳: 09-08 회피 표 전부. 상자와의 겹침(job66 y +0.086~+0.104, job70 최대 +0.022, job89 +0.219~+0.255)은 이 CSV 를 따로 계산한 값(이 카드 작성 때 재계산 일치).
- 결함: 상자 위치 · 여유를 재지 않는다(그래서 '접촉' 판정은 사용자 확인 · 손 계산). lat_err 는 '그 순간의 경로' 기준이라 재계획이 잦으면 작게 나온다(09-09 §8.6 코너 컷 철회와 같은 이유). 지금 다시 쓰기: 안 씀(job125 계열로 대체).

### job59 계열 — 가상 스캔 단계의 기동 · 확인 (간단 표)
| 도구 | 하는 일 | 출력 |
|---|---|---|
| `job59_sensors_restart.sh` | Nav2 · sensors · slam 관련 프로세스를 `pkill -9` → 잔존 수 → sensors.launch(26 s) → slam.launch(10 s) → `/camera/scan` · `/scan` · `/odometry/filtered` · `/wheel_odom` hz, depth_scan 로그 오류 수, load. agent 는 유지(보드 세션 보존). 머리 주석: ssh 인라인으로 돌리면 `pkill -f` 가 자기 셸을 죽임 | 원문 없음(SUMMARY '부수 수정') |
| `job59b_depthchk.sh` | depth_scan 프로세스 수 · `/camera/scan` hz → 두 스캔 1 장씩: 카메라 frame · 빔 수 · 유효 % · 정면 ±5 빔 최소, 라이다 정면(스캔각 ±π ± 3°, LYAW π) 최소 → top CPU · python3 정체 | 원문 없음 → SUMMARY '31 Hz · 640 빔 · 유효 36 %' |
| `job59c_navchk.sh` | 로컬 · 전역 `obstacle_layer.observation_sources`, `/camera/scan` 구독자 수, nav2.log 의 depth_scan 줄 · 경고, stuck_monitor 모드, CPU · load · 배터리 | 원문 없음 |
| `job59d_smfix.sh` | stuck_monitor 인스턴스가 2 개 이상이면 최신 1 개만 남기고 `kill -9`, CPU 평균 | 원문 없음 (stuck_monitor 줄기) |
| `job59e_cpu.sh` | job25e 로 Nav2 재기동 → stuck_monitor 인스턴스 · CPU(top 4 s) · 모드 | 원문 없음 (stuck_monitor 줄기) |
- 계보 · 다시 쓰기: 가상 스캔이 철회돼 59b · 59c 는 쓸 일 없음. job59 의 '파일로 실행' 원칙은 `jetson-access` 메모리 · 이후 prep 도구로 이어짐.

### job59f_depthcmp.py — 가상 스캔 vs 라이다 각도별 비교
- 부른 형태: 인자 없음, 정지.
- 왜: 깊이 가상 스캔이 라이다와 맞는지, 라이다가 못 보는 방위가 있는지.
- 하는 일: 4 s 동안 `/camera/scan`(yaw 0, maxr 1.5) · `/scan`(yaw π, maxr 12) 을 모아 1° 칸 360 개에 각 칸 최솟값. −36°~+36° 4° 간격으로 '깊이' 와 '라이다 − 0.08'(카메라가 라이다보다 0.080 m 앞이라는 주석 가정) 차를 출력, **차 < −0.15 m** 면 '◀ 낮은 장애물 후보'. 깊이 유효 방위 수.
- 출력: [job59f_depthcmp.txt](../debug_log/2026-09-08/outputs/job59f_depthcmp.txt)(상자 전), [job60a_box_depthcmp.txt](../debug_log/2026-09-08/outputs/job60a_box_depthcmp.txt)(상자 뒤 — 같은 도구, 이름만 바꿈).
- 쓰인 곳: '정면 5~10 cm 짧음(−8 cm 편향)', '−20° 깊이 1.46 vs 라이다 5.79', '상자 뒤에도 정면 1.40 그대로 → 철회'.
- 결함: 0.080 m 는 카메라 x 0.232 − 라이다 x 0.152 를 각도 무관 상수로 뺀 근사(정면만 맞음). 가상 스캔은 띠의 행별 **최솟값**이라 걸레받이 · 바닥 돌출이 섞일 수 있음(SUMMARY 후보). 지금 다시 쓰기: 안 씀.

### job59g_costchk.py — 로컬 코스트맵 광선 4 개
- 하는 일: 로컬 코스트맵 1 장 + TF(코스트맵 frame ← base_link, 최대 10 s 대기). −20° · 0° · −12° · +8° 방향으로 0.60~1.50 m 를 5 cm 간격(19 칸) 조회 → `.`(0) · `+`(1~98) · `#`(≥99) · 공백(범위 밖).
- 출력: [job59g_costchk.txt](../debug_log/2026-09-08/outputs/job59g_costchk.txt) — 파일 앞쪽 6 줄은 **이전 판**(점 5 개 이름 붙여 조회, 마지막에 'TF 실패 base_link does not exist')의 출력이 섞여 있다. 뒤쪽 광선 4 줄이 현재 코드의 출력. 같은 도구가 job60a · 60f · 60g · 60h · 60j · 62 에 재사용됨.
- 쓰인 곳: '−20° 광선 0.75~1.05 m 점유', '0.6 m 부터 #'.
- 결함: 시작이 0.60 m 라 더 가까운 마킹은 안 보임. latched 스냅샷 위험(§5.3). 지금 다시 쓰기: 안 씀.

### job60b_depthrows.py — 깊이 이미지 행 띠별 최소거리
- 하는 일: `/camera/camera/depth/image_rect_raw`(16UC1, mm) + camera_info(fx · fy · cx · cy). 정면 열 cx ± 40 px 에서 행 cy−100 ~ cy+160 을 20 행씩, 0.25~4.0 m 유효값의 최솟값, 피치 = atan((행 중앙 − cy)/fy)(+ 아래), '그 거리의 높이' = 0.143 − d·tan(피치)(d 는 깊이 Z 값을 거리처럼 씀 — 근사), 유효 %, 좌 · 우 30° 열 최솟값.
- 출력: [job60b_depthrows.txt](../debug_log/2026-09-08/outputs/job60b_depthrows.txt): fx = fy = 393.2(설계 주석 'fy ≈ 385' 와 다름), 상자 = 행 277~316, 0.38 · 0.30 m, 높이 0.094 · 0.090.
- 결함: 행 297 아래가 전부 '0.30' 으로 같다 — 상자 · 바닥이 실제로 0.30 m 에 있었는지, 측정 하한 근처 값인지 이 출력으로는 구분 안 됨(유효 % 가 0~57 로 낮음). 지금 다시 쓰기: 원 깊이 행 확인용으로는 유효.

### job60c · 60d · 60e — VoxelLayer 기동 · 포인트클라우드 켜기 (간단 표)
| 도구 | 하는 일 | 출력 |
|---|---|---|
| `job60c_voxchk.sh` | 포인트클라우드 hz · width → job25e 로 Nav2 재기동(active 수) → 로컬 plugins · voxel 소스 → nav2.log voxel/depth/pointcloud 오류 → CPU · load · 배터리 | 원문 없음 |
| `job60d_pcdiag.sh` | points 토픽 목록, depth hz, realsense 파라미터 6 개(`pointcloud.enable` · decimation · depth_profile 등) 실제값, sensors.log 의 파라미터 경고 | 원문 없음 → 'pointcloud.enable 은 Parameter not set' 발견 |
| `job60e_pcon.sh` | `ros2 param set /camera/camera pointcloud__neon_.allow_no_texture_points true` · `pointcloud__neon_.enable true` → 토픽 · hz · width/height · frame · CPU | 원문 없음 → '13.1 k pt @15 Hz, camera_depth_optical_frame' |
- 의미: ARM 빌드 realsense-ros 4.58.3 은 처리 블록 이름이 'pointcloud (neon)' → 파라미터가 `pointcloud__neon_.*`. 모르는 이름은 조용히 무시되므로 launch 에 둘 다 적음(`f3fcae94`). 지금도 유효한 함정 기록.

### job60f_pcbox.py — 포인트클라우드 x 구간 집계
- 하는 일: 포인트클라우드 1 장 → base_link 로 변환(point_step 12 면 연속 읽기, 아니면 점마다 unpack — §5.16), x 0.2~2.0 · |y| < 0.6 을 x 10 cm 구간별로 전체 · 바닥(z < 0.06) · 장애물층(0.06~0.40) 점 수, 장애물층 z · y 중앙값. 뒤에 job59g 광선을 이어 붙여 실행.
- 출력: [job60f_pcbox.txt](../debug_log/2026-09-08/outputs/job60f_pcbox.txt)(범퍼 앞 7 cm 상자: x 0.5~0.7 에 307 + 143), [job60g_box2.txt](../debug_log/2026-09-08/outputs/job60g_box2.txt)(재배치 뒤 x 0.8~1.0 에 197 + 25, y 중앙 +0.13 / +0.07).
- 결함: z 범위 −2.71~4.10 같은 이상점을 거르지 않음(구간 집계라 영향 작음). 지금 다시 쓰기: job62c 로 대체.

### job60h · 60i · 60j — 초기화 · 높이 점검 · min_h 단계 시험 (간단 표, 출력 원문 없음, SUMMARY 미인용)
| 도구 | 하는 일 |
|---|---|
| `job60h_clear.sh` | 로컬 · 전역 `clear_entirely_*` 서비스 → 4 s → job59g 광선 → map→base_link 위치 |
| `job60i_zchk.py` | EKF pose z · 쿼터니언(roll/pitch 유무), 포인트클라우드를 base_link · odom 으로 변환해 0.5~1.4 m · |y| < 0.3 의 바닥 · 장애물층 점 수와 z 중앙값, odom 반경 1.6 m z 백분위. ⚠ point_step 16 인데 연속 배열로 읽어 **틀린 해석**(§5.16) |
| `job60j_minh.sh` | 로컬 depth `min_obstacle_height` 0.15 → 0.10 → 0.06 으로 런타임 변경 · 초기화 · job59g 광선, 마지막에 depth `max_obstacle_height` 0.0(사실상 깊이 끔)으로 라이다만의 광선 → 0.40 복귀 |
- 지금 다시 쓰기: 안 씀. 런타임 파라미터 변경을 되돌리는 방식은 10-14 '실행 중 패딩 변경 = 멈칫' 교훈 전의 습관이라 이후엔 재기동으로 대신.

### job62c_boxdim.py — 상자 경계 · y 히스토그램 · 바닥 z
- 하는 일: 포인트클라우드를 `reshape(-1, point_step)` 뒤 x · y · z 오프셋 4 바이트씩 정확히 읽음 → base_link. ① 전체 z 범위 · 바닥 수 ② 장애물층(z 0.06~0.40, x 0.3~1.45, |y| < 0.9)의 x · y · z **min~max** ③ y 히스토그램(라벨은 '5cm' 지만 실제 칸은 **10 cm**) 칸별 점 수 · x · z 중앙 ④ 바닥 후보(z < 0.20, x > 0.3)의 x 20 cm 구간별 z 5 · 50 · 95 백분위(피치 오차 점검).
- 부른 형태: 인자 없음(job68 이 안에서 부르기도 함).
- 출력: [job62c_boxdim.txt](../debug_log/2026-09-08/outputs/job62c_boxdim.txt)(y −0.1~+0.1 에 357 점, +0.1~+0.2 에 19 점, 바닥 중앙 −0.02~+0.03), 같은 도구 재실행 [job64a_boxpos.txt](../debug_log/2026-09-08/outputs/job64a_boxpos.txt) · [job69b_boxnow.txt](../debug_log/2026-09-08/outputs/job69b_boxnow.txt).
- 쓰인 곳: '폭 0.30 m'(min/max 오독) → 사용자 실측 뒤 '코어 0.20 = 실측 0.18'. '카메라 피치 오차 없음'.
- 결함: 경계를 min/max 로 냄(오독의 직접 원인). 한 장만 씀. 지금 다시 쓰기: 바닥 z 점검 부분은 유효, 상자 경계는 백분위 · 클러스터링 판(09-10 이후)으로.

### job64c_globaldiag.py · job64d_cleartest.sh · job64e_map.py — 전역 진단
- `job64c`: 전역 코스트맵 · `/map` 1 장씩 + map→base_link. 크기 · 원점 · frame, 셀 분포(미지 −1 · 자유 0 · ≥99 · 기타), 로버 헤딩 방향 0~1.8 m 를 0.2 m 간격으로 전역 · map 값, 고정 목표 (1.60, 0) 둘레 ±0.3 m 의 전역 값. 출력 [job64c_globaldiag.txt](../debug_log/2026-09-08/outputs/job64c_globaldiag.txt)(앞 3 줄 allow_unknown · inflation 은 다른 명령의 출력, 뒤에 planner 로그 4 줄 붙음 — 'failed to create plan with tolerance 0.25'). 결함: '치명(≥99)' 계산식이 `sum(...) and sum(...)` 꼴로 꼬여 있으나 결과는 개수로 나옴. 목표 (1.60, 0) 하드코딩.
- `job64d`: ① 양쪽 초기화 → 2 s → job64c(4~16 줄) · job63(1.6, 0, 0) ② 전역 depth `min_obstacle_height` 5.0(깊이 마킹 배제) → 전역 초기화 → 3 s → 같은 두 도구. 출력 [job64d_cleartest.txt](../debug_log/2026-09-08/outputs/job64d_cleartest.txt): 두 경우 모두 99 · 경로 없음 → latched 스냅샷 때문에 해석 불가(§5.3). 이 시험 뒤 min_h 를 5.0 에서 되돌린 기록은 스크립트에 없다(이후 Nav2 재기동으로 파일값 복귀로 보임 — 추정).
- `job64e`: 로버 기준 전방 2.4 m ~ 후방 0.6 m, 좌우 ±1.2 m 를 0.1 m 격자로 전역 · `/map` ASCII(`.` 0 · `+` 1~98 · `X` 99 · `#` 100 · `?` 미지 · `R` 로버). 출력 [job64e_map.txt](../debug_log/2026-09-08/outputs/job64e_map.txt), 같은 도구가 job65 · job72 · job79 · job80 안에서 쓰임, `costmap_ascii.json`(before/after 격자)은 분석 페이지용 사본. 결함: 0.1 m 격자라 5 cm 칸의 절반만 봄. 지금 다시 쓰기: 이후 bag 기반 그림 도구로 대체.

### job67_foxglove.sh · job68_memory.sh · job78_killnav.sh · job80_apply.sh · job82_apply.sh (간단 표, 출력 원문 없음)
| 도구 | 하는 일 · 쓰인 곳 |
|---|---|
| `job67_foxglove.sh` | foxglove_bridge `pkill -9` → foxglove.launch(화이트리스트에 코스트맵 · `/plan` · `/local_plan` · `/rover/stuck` 추가판) → 프로세스 · 포트 8765 · 서빙 토픽 · IP. '시각화 제공' 절 |
| `job68_memory.sh` | job25e 로 Nav2 재기동 → 로컬 · 전역 depth `raytrace_min_range` 실제값 · stuck_monitor 모드 → 양쪽 초기화 → job62c(4~12 줄) · job21c_where. job70 직전 '기억 0.90' 적용 확인 |
| `job78_killnav.sh` | Nav2 프로세스만 `pkill -9`(센서 · slam · agent 유지) → 잔존 · 남은 노드 · 보드 상태 · `/cmd_vel` 발행자 수. job77 사용자 중단 때로 보임(추정, SUMMARY 미언급) |
| `job80_apply.sh` | 전역 depth `raytrace_min_range` 0.30 런타임 설정 · 양쪽 초기화 · 두 값 확인 · job64e 전역 ASCII. '최종 설정(기억은 로컬 전용)' |
| `job82_apply.sh` | 양쪽 `voxel_layer.mark_threshold` 0 · depth min_h 0.06 런타임 설정 · 확인 · 초기화 · job73_probe. '★★ 조치' |
- 결함 공통: `pkill -9` 는 09-09 §8.9 DDS 공유메모리 사고의 원인이 된 습관. 런타임 설정과 파일 반영이 따로라, 파일 반영 여부는 커밋으로만 확인된다.

### job71_watchbox.py — 상자 칸 추적(Nav2 없이 직진)
- 부른 형태: `python3 job71_watchbox.py [거리 0.45] [속도 0.04]`(실행은 0.42 m).
- 왜: job70 이 왜 또 밀고 지나갔는지 — '깊이점 × 비용' 판정표로 소거 · 마킹 실패 · 기억 정상을 가름(09-08 '다음: 원인 확정 실험').
- 하는 일: ① base_link 포인트클라우드에서 z 0.06~0.35 · x 0.4~1.3 · |y| < 0.4 점의 중앙값 = 상자(30 점 미만이면 중단) ② 시작 map 자세로 그 점을 map 좌표 (BX, BY) 에 **한 번 고정** ③ `/cmd_vel` 0.04 m/s 를 50 ms 마다 발행, 0.25 s 마다 카메라~상자 거리(카메라 = base + 0.232 m 전방), 로컬 · 전역 코스트맵의 (BX, BY) 칸 값(**둘 다 map 좌표로** 조회), map 프레임 점군 중 상자 ±0.12 m · z 0.06~0.35 점 수 ④ 끝나면 0 Twist 20 회.
- 출력: [job71_watchbox.txt](../debug_log/2026-09-08/outputs/job71_watchbox.txt)(43 줄).
- 쓰인 곳: '★ 원인 확정 — 전역 미마킹'(오진, §5.5), '최소 측정거리 0.22~0.25 m'(→ 로컬 raytrace 0.35, STVL min_z 0.25 의 근거가 됨 — 둘 다 뒤에 틀림).
- 결함: 로컬(odom) 을 map 좌표로 조회, 고정 좌표 드리프트, 칸 하나만 봄. SUMMARY 표가 원문의 앞 18 줄(전역 100 구간)을 뺌.
- 계보: → job75(프레임 정정) → job125. 지금 다시 쓰기: 안 씀.

### job72_globalmark.sh · job73_probe.py · job73_run.sh · job74_layers.sh — 전역 미마킹 원인 배제
- `job72`: job64e 전역 ASCII 3~16 줄, nav2.log 의 transform · tolerance · observation · sensor origin · out of bounds 경고, 전역 voxel_layer 파라미터 10 개 + 로컬 3 개 대조. 출력 [job72_globalmark.txt](../debug_log/2026-09-08/outputs/job72_globalmark.txt): 경고 0, 파라미터 같음(`combination_method` 전역 칸은 빈 값 — 조회 실패, 로컬 1).
- `job73_probe`: 정지 1 회. 포인트클라우드 · 로컬 · 전역 모두 받고 **TF 준비(base_link · map ← 카메라)까지 15 s 대기**(초기판이 메시지만 기다려 'TF 실패' — 09-08 '부수 버그'), 상자 = z 0.04~0.35 · x 0.4~1.3 · |y| < 0.4 중앙값, base_link · map 좌표 · z 백분위, 로컬 · 전역 그 칸 값(로컬도 map 좌표로 — job71 과 같은 결함이 남음. 정적 · 원점 근처라 영향 작음, 추정).
- `job73_run`: 현재 → 전역 depth min_h −1.0 → 전역 range 3.0, 각각 초기화 · 6 s 뒤 probe. 출력 [job73_globalfilter.txt](../debug_log/2026-09-08/outputs/job73_globalfilter.txt): 'TF 실패' · '상자 후보 부족 9~17' 만(세 번 실행분). 상자가 이미 너무 가까움.
- `job74`: 전역 초기화(5 s) 뒤 probe 를 A 기준 · B static_layer 끔 · C static 켬 + 전역 min_h −1.0 · range 3.0 · D 원복(0.08 · 1.2) 네 번. 출력 [job74_layers.txt](../debug_log/2026-09-08/outputs/job74_layers.txt): 전부 99 / 99 → '정정 A'.
- 다시 쓰기: 안 씀. 'TF 준비까지 기다린다' 는 이후 러너 · 게이트 도구의 기본이 됨(job125 의 카메라 TF 대기).

### job75_forward.py — 전방 축 최근접 추적(프레임 정정판)
- 부른 형태: `[거리 0.40] [속도 0.04]`, job83 은 같은 도구 재실행.
- 하는 일: 0.3 s 마다 로컬은 **odom** 프레임 자세, 전역은 **map** 프레임 자세로 각자 전방 축을 0.30~1.30 m 를 2 cm 간격(51 점) 조회 → 처음 ≥99 인 거리와 그때까지 최댓값. 깊이점 = base_link 전방 0.3~1.3 · |y| < 0.25 · z 0.05~0.35 점 수. 좌표 고정이 없어 드리프트 무관.
- 출력: [job75_forward.txt](../debug_log/2026-09-08/outputs/job75_forward.txt) · [job83_approach.txt](../debug_log/2026-09-08/outputs/job83_approach.txt).
- 쓰인 곳: '정정 B — 기억이 양쪽에서 유효', '마킹 지속 검증 성공'.
- 결함: 전방 축 한 줄이라 상자가 축에서 벗어나면 다른 물체를 잡음. 시작 0.30 m 하한 — job75 로컬 열은 내내 0.3(§5.15). 지금 다시 쓰기: 안 씀.

### job125_avoid3.py — 회피 주행 계측판 (09-09, 이후 Phase S · N 러너의 뿌리)
- 부른 형태: `run_j.sh job125_avoid3.py <D=1.80> <timeout=90> <csv이름>` — 09-09 의 job126 · 128 · 134 · 141 · 152 · 155 · 167 · 169 · 170 은 이 도구의 실행 이름으로 보인다(추정 — 실행 명령 기록 없음).
- 왜: job92 의 '최소 여유'(실시간 깊이점)가 접촉을 28 cm 로 보고한 결함(§5.10).
- 하는 일:
  1. TF · 포인트클라우드 · 로컬 대기(20 s), **카메라 정적 TF(base_link ← camera_depth_optical_frame) 따로 대기**(job136 에서 foxglove 고 CPU 로 `/tf_static` 이 늦어 검출 실패).
  2. 상자 검출(최대 60 회): base_link 점 중 z 0.05~0.30 · x 0.5~1.5 · |y| < 0.5 가 40 점 이상이면, 중심 y = **중앙값**, 전면 x = 5 백분위. 사용자 실측 폭 0.18 × 깊이 0.11 사각형을 출발 자세로 map 에 고정, 둘레를 변마다 21 점(84 점)으로 샘플.
  3. 0.1 s 마다: ① `clear_geo` = 상자 둘레 점들을 차체 좌표로 옮겨 차체 사각형(반길이 0.25 · 반폭 0.165, 패딩 제외)까지 최소 거리(0 = 접촉) ② `plan_clear` = 현재 `/plan` 점 ↔ 상자 둘레 최소 거리 − 0.165(음수면 계획이 접촉 경로)와 상자 x 에서의 계획 횡좌표 ③ lc_box = 로컬(odom 프레임으로 map→odom 변환) · gc_box = 전역(map)의 **상자 중심 칸** 값 ⑤ 상자 사각형(수평 투영) 안 · z 0.03~0.40 의 map 프레임 깊이점 수. 1 s 마다 화면 줄.
  4. 요약: ① 최솟값과 그때 위치 ② 계획 최소 여유 ③ 로컬 · 전역 최소 / 최근접 때 ④ 경로 좌우 전환(계획 횡좌표 부호, |y| < 0.05 무시) · 접촉 경로 샘플 비율 ⑤ 로컬이 0 인 샘플 중 깊이점 > 0 비율 · 조향 부호반전 / m.
- 출력: 화면 + `/tmp/<이름>.csv`(t, fwd, lat, clear_geo, plan_clear, plan_lat_at_box, lc_box, gc_box, v, w, box_pts). **09-09 분 출력 · CSV 는 저장소에 없음**(원천 소실, SUMMARY 인용만).
- 쓰인 곳: 09-09 §8.6~§8.13 의 모든 수치.
- 결함 · 이후: (a) 상자 y 를 클러스터링 없이 중앙값으로 → 범위 안의 벽이 끌어감(09-10 §9, 52 cm 어긋남, ①②③⑤ 무효 판정) (b) 상자를 출발 때 한 번 고정 → SLAM 보정 · 드리프트(09-10 §7 '보일 때마다 재고정') (c) lc_box · gc_box 는 칸 하나(경계 칸이면 0 이 나올 수 있음) (d) 깊이점 ⑤ 는 상자 사각형 안 점만 세므로 사각형이 어긋나면 0. 09-10 이후 재고정 · 클러스터링, 09-18 재고정 yaw 조건, 09-23 위치 조건(±0.06)이 붙어 Phase S · N 러너로 계속 쓰임(TEST_COURSE_AND_GATES §15). 지금 다시 쓰기: 이 09-09 판은 안 씀 — 최신판은 위 경로를 따른다.

### job92_avoid.py (09-09, job125 의 앞판)
- 하는 일: job56 과 같은 목표 주행 + 실시간 '최소 여유' = base_link 깊이점(z 0.03~0.35, x −0.1~1.5, |y| < 0.9) 중 차체 외곽(반길이 0.25, 반폭 **0.185** = 패딩 포함)까지 최소 거리 · 시작 때 검출한 상자 map 좌표 거리 · 횡오차 · 부호반전.
- 결함: 상자를 지나 옆에 오면 상자가 화각 밖이라 '최소 여유' 가 다른 물체 거리로 바뀜(§5.10). → job125.

### 09-09 배포 · 확인 도구 (간단 표, 출력 원문 없음)
| 도구 | 하는 일 | 쓰인 곳 |
|---|---|---|
| `job127_pad.sh` | `/tmp/nav2_params.yaml` CR 제거 → src · install 두 곳 복사(설치본은 링크가 아닌 사본으로 덮음) → `footprint_padding: 0.05` 개수 → Nav2 `pkill -9` · 재기동(28 s) → lifecycle · 오류 | §8.6 원인 A |
| `job129_layers.sh` | 같은 배포 → obstacle_layer · `observation_sources: depth` 개수 → Nav2 재기동 → 로컬 · 전역 plugins · 코스트맵 hz · 오류 | §8.6 원인 B 레이어 분리 |
| `job130_stvl.sh` | 설치본 YAML 의 레이어 plugin 줄, STVL dpkg · lib · pkg 유무, `apt-cache policy`, nav2_costmap_2d 등록 레이어, clear 서비스 목록 | §8.6 'STVL 미설치, apt 2.3.4-1jammy' |
| `job131_probe.py` | 전역 · 로컬(frame 이 map 이 아니면 변환) · `/map` 을 로버 전방 ±30° 10° 간격, 0.4~2.4 m 0.1 m 부채꼴로 기호 출력(X 범위 밖 · u 미탐사 · # · + ≥50 · − >0 · .), 전방 1.20 · 1.60 m 목표 칸 값 | SUMMARY 미언급(경로 실패 진단용) |
| `job132_stop.sh` · `job133_verify.sh` | 배터리 → 0 Twist 12 회 → 전부 `pkill -9` → agent 제거 → 남은 노드 · 프로세스 · docker / ros2 daemon 재시작 뒤 노드 목록 · CPU 상위 | 세션 정리(SIGKILL — §8.9 사고 목록에 포함) |
| `job135_live.sh` | 실행 중 로컬 plugins · 두 레이어 sources · combination_method · padding, depth clearing · marking · raytrace min/max · obstacle_max_range · min_h, scan clearing · raytrace_min, 전역 같은 항목 | §8.7 '분리 실제 적용 확인' |
| `job137_det.py` | job125 상자 검출 필터(z > 0.05 · z < 0.30 · x > 0.5 · x < 1.5 · |y| < 0.5)를 누적 · 단독으로 풀어 점 수, job62c 조건 점 수 | job136 검출 실패 원인(→ 카메라 TF 대기 추가) |
| `job153_rt.sh` | 로컬 · 전역 depth raytrace min/max · obstacle_max_range · clearing · scan raytrace_min · padding 실제값, 설치본 `raytrace_min_range` 줄 | §8.8 'live 0.6 확인' |
| `job154_reinit.sh` | depth `clearing: false` 판 YAML 배포 → sensors · slam · nav2 를 **SIGTERM** 으로 끄고 최대 12 s 대기 · `/dev/shm` fastrtps 잔재 수 · 보드 유지 확인 → sensors(26 s, 자이로 바이어스) · slam(14 s) · nav2(28 s) → lifecycle · EKF hz · odom→base · clearing 적용값 | §8.8 job155 준비 |
| `job156_stop.sh` | clearing true 판 YAML 배포(되돌림) → 0 Twist 12 회 → SIGTERM 최대 15 s → agent 제거 · daemon stop · `/dev/shm/fastrtps*` 삭제 | job155 뒤 되돌림 · 충전 전 정지 |
| `job158_alt.sh` | `strings` 로 nav2_costmap_2d 라이브러리 심볼(`observation_persistence` 등), foxglove capabilities, realsense `json_file_path` · disparity 관련, librealsense 버전, 등록 레이어 클래스 | §8.10 '확인된 가용 수단' |
| `job160_stvlinst.sh` | 설치 전 policy · 디스크 → `sudo -S apt-get install -y ros-humble-spatio-temporal-voxel-layer`(비밀번호 `<PW>` 를 echo 로 넣음 — 저장소 사본은 가려짐) → pkg · lib · 플러그인 클래스 | §8.11 설치 |
| `job161_stvlparam.sh` · `job162_p2.sh` · `job163_ex.sh` | STVL 코어 라이브러리 `strings` 로 레이어 · 소스 파라미터 이름 후보의 존재, 예제 파일 목록, 공식 예제 `constrained_indoor_environment_config.yaml` · `global_costmap_params.yaml` 전문 출력 | §8.11 '파라미터 이름은 추측하지 않고 설치본에서 확인' |
| `job164_stvlup.sh` | STVL 판 YAML 배포 → 전부 SIGTERM · agent 제거 · SHM 삭제 → base(12 s) · sensors(26 s) · slam(12 s) · nav2(30 s) → lifecycle · plugins · 코스트맵 hz · STVL · nav2 오류 · foxglove CPU · 보드 유무 | §8.11 첫 배포(→ static_layer 삭제 오류) |
| `job165_err.sh` | nav2.log 의 planner_server · global_costmap · stvl 줄 30 개 + 마지막 40 줄 | §8.11 오류 원인 |
| `job166_nav2only.sh` | 고친 YAML 배포 → Nav2 만 SIGTERM 재기동(32 s) → lifecycle · plugins · hz · STVL 초기화 로그 · 오류 · CPU | §8.11 '결과 — Initialized' |
| `job168_pre.sh` | 로컬 plugins · `stvl_layer.voxel_decay` · `decay_model` · `depth_clear.min_z` · `decay_acceleration` 실제값, 보드 · 배터리 · `/wheel_odom` hz | §8.13 주행 전 확인 |
| `job171_chk.sh` | `/rover/status`(스톨 · 래치), 배터리 5 회, `/tf` · `/odometry/filtered` · `/wheel_odom` · `/map` hz, EKF 발행자 수, fastrtps 잔재 수, nav2.log cancel · abort · collision 등 6 줄 | §8.13 '남은 문제 — 무이동' 표 |
- 공통 결함: 설치본 YAML 을 `cp` 로 덮는 방식은 `--symlink-install` 링크를 끊는다(이후 '[prep 이 설치본 링크 끊음]' 메모리와 같은 계열). 09-09 오후부터 `pkill -TERM` 우선으로 바뀜.

## 9. 용어
- **ObstacleLayer vs VoxelLayer**: Nav2 코스트맵 장애물 레이어. ObstacleLayer 는 2D 격자(높이 무시), VoxelLayer 는 칸마다 z 방향 복셀(여기서는 5 cm × 8 층 = 0~0.40 m)을 두어 점의 높이를 보고 3D 광선으로 소거한다. 마스터 코스트맵에는 '그 칸 위 복셀 중 점유가 mark_threshold 를 넘는가' 로 투영.
- **mark_threshold**: 칸 하나의 z 기둥에서 점유 복셀이 이 수를 **초과**해야 그 칸을 점유로 표시. 0 이면 복셀 1 개로 충분, 1 이면 2 개 이상(09-08 SUMMARY 해석).
- **marking / clearing**: 관측 소스의 두 역할. marking = 점이 떨어진 칸을 점유로, clearing = 센서 원점에서 점까지 광선이 지나간 칸을 자유로(raytrace). 소스마다 켜고 끈다(STVL 예제처럼 같은 토픽을 '마킹 전용' · '소거 전용' 두 소스로 나눌 수도 있다).
- **raytrace · raytrace_min_range / max_range · obstacle_min/max_range**: 소거 광선을 원점에서 min~max 거리 구간에서만 적용 / 마킹을 그 거리 구간의 점만으로. Nav2 `raytraceLine` 은 원점 쪽 min 길이만큼 칸을 건너뛴다(09-08 job70 근거 문장). '지우지 않을 반경' 으로 쓰면 그 안의 마킹은 영구히 남는다(누적 레이어에서 유령).
- **min / max_obstacle_height**: 이 높이 구간의 점만 마킹(바닥 반사 · 천장 배제). 09-08 바닥 실측 z ≈ −0.02 m.
- **combination_method**: 레이어를 마스터에 합치는 법. 1 = Maximum(다른 레이어 값을 낮추지 못함) — 레이어 분리의 근거.
- **롤링 창 vs 누적(전역)**: 로컬은 로버를 따라 움직이는 3×3 m 창이라 지나간 자리는 창 밖으로 사라진다. 전역은 지도 전체를 유지 → 지워지지 않는 마킹이 쌓인다.
- **always_send_full_costmap · latched 스냅샷**: 끄면 Nav2 는 변경분(`*_updates`)만 보내고 `/…/costmap` 전체는 드물게 보낸다. TRANSIENT_LOCAL 로 읽는 도구는 마지막 전체본(옛 것)을 받는다.
- **STVL(spatio_temporal_voxel_layer)**: 복셀마다 마지막 관측 시각을 두고 시간이 지나면 지우는 레이어(OpenVDB). `voxel_decay`(초) · `decay_model`(0 선형 · 1 지수 · −1 영속). 소거는 광선 대신 **절두체**로: 소거 소스의 시야 원뿔 안에 있는데 이번 프레임에 점이 없는 복셀은 `decay_acceleration` 으로 더 빨리 감쇠.
- **frustum(절두체) · min_z / max_z · FOV**: 깊이 카메라 시야를 근평면(min_z) · 원평면(max_z) · 수평 · 수직 화각으로 자른 뿔대. 근평면보다 가까운 복셀은 '못 보는 곳' 이라 가속 감쇠를 안 받는다 — 그래서 min_z 는 실제로 깊이가 끊기는 거리여야 한다(job169).
- **마킹 중단 vs 소거**: 소거 = 광선 · 절두체가 칸을 적극적으로 자유로 되돌림. 마킹 중단 = 그 칸을 다시 찍을 점이 이번 주기에 없음. 스톡 VoxelLayer 는 매 주기 관측 버퍼로 다시 그리므로, 관측이 끊기면(observation_persistence 0) 소거가 없어도 칸이 0 이 될 수 있다(09-09 job155 의 해석).
- **observation_persistence**: 관측 버퍼에 지난 N 초 관측을 남겨 재마킹(09-09 §8.10 대안 1, 이 시기 미시험 — STVL 에서는 0).
- **decimation_filter**: RealSense 깊이 영상을 n×n 블록으로 줄이는 필터. ×4 면 640×480 → 160×120. 근거리 해상도를 잃어 근접 끊김을 넓혔을 가능성(추정).
- **depthimage_to_laserscan · scan_height**: 깊이 영상의 가운데 scan_height 행에서 열마다 최솟값을 골라 가상 LaserScan 을 만드는 노드. 높이 창이 거리에 비례해 좁아진다.
- **카메라~상자 거리 기준**: 이 카드의 '카메라~상자' 는 base_link + 0.232 m(카메라 x) 에서 상자(중심 또는 전면 — 도구마다 다름)까지. 09-08 에 사용자 '상자 정면 0.47 m'(앞범퍼 기준) vs 내 0.74 m(base_link 기준) 혼선이 있었다(0.47 + 0.25 ≈ 0.72).
