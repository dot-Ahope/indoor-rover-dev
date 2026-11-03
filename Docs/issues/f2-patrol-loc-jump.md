# F2 순회와 위치 추정 점프 — 지도 구멍이 만든 1.33 m (5 기: 10-01 §8 · 10-02 §1~§9 · 6 기: 10-07 · 10-08 순회)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **점프: 해결**(원인 = 저장 지도의 빈 곳 — 재생으로 재현 · 보완 지도에서 소멸 **측정**, 실주행 f2b3 에서 같은 자리 점프 0 **1 회 확인**). **순회: 10-02 시점 진짜 성공 6 · 실패 1 · 접촉 2**(의자 다리 · 상자). 남서 구석 방향 맞춤 정체는 10-07 에 3/3 재현 → 러너 '위치만(f)' 으로 **우회** → [남서 구석 방향 맞춤 정체](southwest-orient-stall.md). **6 기(10-07 · 10-08)**: 순회 f2c 9/10 · f2d 8/10 · f2e 3/3 × 2, 점프 보고 없음(측정은 f2c 두 주행만, §7) | 10-01 ~ 10-02 (이 카드는 10-01 §8 의 코스 · 점프 부분과 10-02 §1~§9 를 채움) · 6 기 10-06 ~ 10-08 은 §7 | [10-01 §8.41](../debug_log/2026-10-01/SUMMARY.md) — 영상 36 s 에서 사용자가 '로버가 x 0.6 → −1.0 으로 뛰었다' 고 봄 | 지도 **office_v3**(Jetson `~/maps/office/office_v3.*`, 저장소 [`office_v3.pgm`](../04_navigation/maps/office_v3.pgm) · [`.yaml`](../04_navigation/maps/office_v3.yaml)) — prep 기본 지도(지금도 `Docs/tools/prep_fast.sh` `MAP=office_v3`). 러너 `job551_f0drive.sh` 에 `G2_SKIP` · 래퍼 `run_f2b2.sh`(목표 문자열을 파일 안에). 위치 추정 탐색 창은 **바꾸지 않음**(3.0 유지, 지금 [`slam.yaml`](../../ros2_ws/src/rover_bringup/config/slam.yaml) 45 · 57 행) | [회전 중 장애물 번짐](rotation-obstacle-smear.md)(§7.2 에서 갈라짐) · [rf2o 도입](rf2o-introduction.md) · [제자리 회전 옆 밀림 F0-a](f0-rotation-side-slip.md) · [SLAM map→odom 시각 정체](slam-stamp-freeze.md)(위치 추정 모드의 다른 결함) · [라이다 근접 사각](near-wall-blindspot.md)(낮은 물체 · 옆 사각) · [첫 SLAM 지도](first-slam-map.md)(office_v1 · v2 계보) · [낮은 상자 기억](low-box-global-memory.md) · [전선 밟기](cable-step-over.md) · [회전 방식 · 트랙 비율](rotation-method-track-ratio.md) (6 기) · [F2 기준선 no5](f2-baseline-no5.md) (7 기) · [PathBlockedAhead only_new](pathblocked-only-new.md) (8 기) |

**한 줄**: F2(저장 지도 위 웨이포인트 순회)를 처음 돌린 10-01, 열두 번째 주행 f2a12 의 목표 6 시작에서 위치 추정 노드가 map→odom x 를 **한 번에 −1.33 m** 옮겨, Nav2 는 가짜 '도착' 을 하고 다음 목표에서 엉뚱한 자리의 의자 앞에서 떨었다. 사용자는 '지도의 빈 곳' 을 원인으로 짚었고, 다음 날 같은 bag 을 위치 추정 노드에 다시 먹이니 점프가 **같은 시각 · 같은 크기로 재현**됐다(라이브와 x 차 ≤ 0.03 m). 구멍을 메운 지도(②)와 탐색 창을 1.0 으로 줄인 설정(③)은 **각각 단독으로** 점프를 없앴다. 사용자는 탐색 창은 3.0 그대로 두고(넓은 창 = 실제 큰 오차 회복력) 구멍 메운 지도를 **office_v3** 로 채택했고, 이어진 f2b 순회에서 같은 자리 점프는 없었다(최대 한 번 0.184 m). 순회 자체는 6 성공 · 1 실패(D → 남서 구석 방향 맞추기 정체) · 접촉 2(전진 중 의자 다리, 복귀 때 출발 방 상자 — 둘 다 라이다 아래 · 카메라 화각 밖)로 끝났고, 남서 구석 정체를 파다가 '회전 중 벽이 odom 좌표에서 12 cm 두꺼워진다' 는 별도 줄기([회전 중 장애물 번짐](rotation-obstacle-smear.md))가 나왔다.

## 1. 증상
- f2a12(10-01 16:59:08 출발, 목표 10 개, `GOAL_FRAME=map`): 목표 1~6 SUCCEEDED, 목표 7 CANCELED 45.2 s(nav_guard 무진행) — [`f0_f2a12_runner.log`](../debug_log/2026-10-01/outputs/f0_f2a12_runner.log) · [10-01 §8.37](../debug_log/2026-10-01/SUMMARY.md).
- 사용자 관찰(영상 36 s, 10-01 §8.41): 그림 속 로버가 x ≈ 0.6 → −1.0 으로 뛰었는데 실제로는 0.6 에 있었다.
- 측정(10-01 §8.41, `f2a12_full.npz` — 스크래치패드 · **원천 소실**, bag 은 [`2026-10-01/bags/bag_f2a12.tgz`](../debug_log/2026-10-01/bags/) PC 사본, git 제외): map→odom x **−0.062 → −1.393(−1.33 m, 한 갱신)**, y +0.006 m · yaw +0.1°. 그때 로버는 목표 6(남쪽 통로 → 서쪽) 시작 직후 **제자리 회전 중**(159° → 169°). 점프 뒤 스캔-지도 잔차 0.088 → 0.139 → 0.18 m 로 **커짐**(틀린 자리에 맞춤). slam 로그에 1.5 s 전 'Message Filter … queue is full' 1 건([`j793_slamlog.txt`](../debug_log/2026-10-01/outputs/j793_slamlog.txt)).
- 결과: Nav2 는 이미 1.4 m 서쪽에 왔다고 믿고 0.46 m 만 더 가 목표 6 **가짜 SUCCEEDED**, 목표 7 은 틀린 지도 좌표에서 시작해 로컬(odom, 실제 센서)이 본 실제 앞의 의자 앞에서 떨다가 취소. 10-01 §8.37~§8.40 의 목표 6 · 7 위치 해석은 전부 무효가 됐다(§8.41 정정).
- 그림: [`2026-10-01_f2a12_jump_pair.png`](../04_navigation/figures/2026-10-01_f2a12_jump_pair.png)(점프 직전 · 직후 3 × 3 m — 남쪽 벽은 양쪽 다 맞고 x 만 바뀜) · [`_jump_hole.png`](../04_navigation/figures/2026-10-01_f2a12_jump_hole.png) · [`_traj_jump.png`](../04_navigation/figures/2026-10-01_f2a12_traj_jump.png).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-01 §8 · §8.1 | F2 코스 안 · 확정(주행 전 선언). 지도 office_v2 · 위치 추정 = slam_toolbox localization(10-01 §7.3 사용자 결정) · 속도 0.07 · 정지 3 s · 목표 yaw `p`(경로 끝 방향) | 목표 B 문 밖 (2.25, −1.60) 여유 1.03 m · C (−1.60, −2.00) 0.88 · D 남쪽 통로 (1.60, −5.55) 0.67 · W3 (5.50, −2.20) 0.67 · 출발 (0, 0) 0.46. 직선 합 ≈ 23 m. 사용자: 사람 있어도 주행, 케이블 가드 턱 그대로 넘기 | 판정 F2-a 5 목표 성공 · F2-b 접촉 0(라이다 ↔ 차체 ≥ 0.05) · F2-c 10 s 넘는 정체 0 · F2-d 복귀 줄자 ≤ 5 cm · **F2-e 위치 튐 0.30 m 넘는 것 0** · L-d 시작 ≤ 5 cm. '사람 있음 · 턱 미통제' 라 기준선 태그로 쓸지는 결과 보고 | `2026-10-01/jobs/f2_candidates.py` · 그림 [`2026-10-01_f2_candidates.png`](../04_navigation/figures/2026-10-01_f2_candidates.png) · prep [`j731_f2_prep.txt`](../debug_log/2026-10-01/outputs/j731_f2_prep.txt) |
| 10-01 §8.2 ~ §8.36 | f2a1 ~ f2a11 — 이 카드 밖의 문제들(위치 추정 노드 부하 · transform_timeout · CPU 포화 · stuck_monitor 오판 · nav_guard 결함 · 재계획 정책 · 전역 정적 층이 '다시 그린 /map' 이던 것 · 전역 카메라 층) | — | 각 § 참조. 이 카드에 이어지는 것: §8.32~§8.33 전역 정적 층 = 저장 지도(`/map_nav`), §8.35 전역 카메라 점군 층, §8.39 BT `PathBlockedAhead` | [10-01 SUMMARY](../debug_log/2026-10-01/SUMMARY.md) |
| 10-01 §8.37 | f2a12 | 목표 1~6 SUCCEEDED(도착 오차 0.140~0.149 m), 목표 7 (−1.65, −3.70) CANCELED 45.2 s. '통로 앞 새 물체(의자) · 남은 틈 0.39 m · 재계획 1 회 · MPPI 지령 ±0.015 m/s 떨림' 분석 | 10 목표 중 6 — 불합격. 목표 7 해석은 **나중에 무효**(§8.41) | [`f0_f2a12_runner.log`](../debug_log/2026-10-01/outputs/f0_f2a12_runner.log) · [`j786_f2a12.txt`](../debug_log/2026-10-01/outputs/j786_f2a12.txt) · [`j788_g7_cmd.txt`](../debug_log/2026-10-01/outputs/j788_g7_cmd.txt) |
| 10-01 §8.40 | 사용자 '그림 속 위치가 실제와 좀 다르다' → 전체 영상 · 스캔-지도 잔차 | 출발 방 · 북쪽 0.03~0.06 m → 남쪽 통로 · 목표 7 자리 **0.09~0.18 m**. 국소 탐색(±0.3 m)으로 0.11~0.16 아래로 안 내려감. `fit_scan.py` 의 **dx +1.35 m** 해 | '남쪽은 지도가 덜 깨끗 + 지도에 없는 물체' 로 해석, dx +1.35 는 '책상 반복 구조 오탐' 으로 버림 — **틀림**(§5 실수 1) | `2026-10-01/jobs/job792_full.py` · `render_f2a12.py` · `fit_scan.py` · `fit_scan2.py` · 그림 [`2026-10-01_f2a12_south_scanfit.png`](../04_navigation/figures/2026-10-01_f2a12_south_scanfit.png) · 영상 `videos/f2a12_full.mp4`(git 제외) |
| 10-01 §8.41 | 사용자 영상 관찰 → map→odom 기록 확인 | §1 수치. 사용자 눈대중 실제 x ≈ 0.6 vs 추정 −1.29(차 ≈ 1.9 m, 0.5 m 미설명) | **위치 추정 점프 확인**. 추정 원인(미검증): 탐색 창 `loop_search_space_dimension 3.0`(±1.5 m)이 남쪽 책상 줄의 반복 구조(~1.4 m 간격)를 잘못 맞춤 + 제자리 회전 중 · 처리 밀림 | `j793_slamlog.txt` · 그림 3 장(§1) |
| 10-01 §8.42 | 사용자 가설 '점프 원인 = 지도 구멍' | office_v2 점프 지점 (0.54, −5.62) ±1 m: 자유 70 % · 벽 12 % · **미지 18 %**. 통로 북쪽에 x 방향을 잡아 줄 벽이 거의 없고 남쪽 벽은 곧음 | '곧은 벽 하나는 벽 방향(x) 위치를 못 정함 + 구멍 → x 로만 1.33 m' — 가설 **지지(추정)**. 다음 날 ① 구멍 보완 ② 재생으로 소멸 확인 ③ 탐색 창 1.0 대조 | `2026-10-01/jobs/render_jumphole.py` |
| 10-02 §1 선언 | 구멍 보완: office_v2 포즈 그래프에서 **이어 그리기**(루프 클로저 끔 — 10-01 §2~4 교훈: 켜면 옛 지도를 옮김), f2a12 bag 을 **+276 s 까지만**(점프 전) 재생 | 이 구간에 목표 4→5(남쪽 통로 동행) · 6 앞부분이 들어 있어 구멍 자리를 두 번 지남 | 판정 H-1 구멍 ≤ 5 % · H-2 재생 중 점프(> 5 cm · > 2°) 0 건 · H-3 영역별 office_v2 대비 최적 이동 ≤ 0.05 · H-4 남쪽 벽 v1 ± 0.05 | `job800_chk.sh` · `job801_bagup.sh`(재부팅으로 `/tmp` bag 소실 → PC 사본을 `~/bags` 로) |
| 10-02 §1.1 | 재생 · 비교 | 스캔 2,757 · do_loop_closing False. H-1 **9.6 %**(통로 안만 0.3 %, 구멍 상자 0.0 % — 남은 미지는 벽 뒤). H-2 **29 건**(+182~254 s, 0.05~0.11 m · 0.4~1.0°). H-3 다섯 영역 모두 최적 이동 **(0, 0)**, 겹침 98/99/83/91/96 %. H-4 후보 −6.24/−6.20/−6.25(원문 2 자리) vs v1 −6.21/−6.15/−6.20, 기울기 −0.07° | H-1 은 **기준 정의 잘못**(벽 뒤 포함, §5 실수 2) — 의도 기준으로 통과. H-2 **불합격**(루프 끔이라 스캔 정합이 트랙 미끄러짐 5~11 cm 를 바로잡은 것으로 추정). H-4 경계 통과(남쪽 벽 안쪽 면이 x −0.3~2.7 에서 한 칸 남쪽 — 어느 쪽이 실제인지 줄자 없이 모름) | [`job802_extend.sh`](../debug_log/2026-10-02/jobs/job802_extend.sh) · [`j802_extend.txt`](../debug_log/2026-10-02/outputs/j802_extend.txt) · [`cmp_maps.py`](../debug_log/2026-10-02/jobs/cmp_maps.py) · [`cmp_maps_c276.txt`](../debug_log/2026-10-02/outputs/cmp_maps_c276.txt) · 그림 [`2026-10-02_hole_fill.png`](../04_navigation/figures/2026-10-02_hole_fill.png) · 후보 [`cand_1002_f2a12_c276_nolc.pgm`](../debug_log/2026-10-02/outputs/cand_1002_f2a12_c276_nolc.pgm) |
| 10-02 §2 선언 | f2a12 bag 전체(344 s)를 1 배속 · sim time 으로 localization 노드에 — 운용과 같은 0.30 m · 0.15 rad · 갱신 10 s · tt 0.5, 시작 (0,0,0). 조합 ① v2 · 3.0 ② 후보 · 3.0 ③ v2 · 1.0 | — | P-0 ① 에서 ≥ 1.0 m 점프 재현돼야 비교 성립 · P-1 ② 0.30 m 넘는 변화 0 + 점프 뒤 x 가 −0.06 ± 0.15 · P-2 ③ 같은 기준 | [`job803_locjump.sh`](../debug_log/2026-10-02/jobs/job803_locjump.sh) · [`job803_locjump.py`](../debug_log/2026-10-02/jobs/job803_locjump.py) |
| 10-02 §2.1 | 재생 3 조합 | ① 0.10 m · 3° 넘는 변화 4 건, **+281.9 s 1.28 m**, +285/300/340 s 재생 x −1.394/−1.409/−1.279(라이브와 x 차 ≤ 0.03). ② 3 건 ≤ 0.15 m, x −0.116/−0.145/+0.046. ③ 3 건 ≤ 0.17 m, x −0.120/−0.121/−0.008. 212 · 218 · 229 s 의 0.11~0.17 m 3 건은 세 조합 공통 | **P-0 재현 · P-1 · P-2 통과** → 점프는 CPU · 타이밍 우연이 아니라 **지도 + 설정으로 결정**. 사용자 판단(빈 곳) 지지. 라이브 점프 시각은 bag 기준 **+283.0 s**(10-01 의 +278.4 는 환산 실수 — §5 실수 3) | [`j803_locjump.txt`](../debug_log/2026-10-02/outputs/j803_locjump.txt) · [`render_locjump.py`](../debug_log/2026-10-02/jobs/render_locjump.py) · 그림 [`2026-10-02_locjump_replay.png`](../04_navigation/figures/2026-10-02_locjump_replay.png) |
| 10-02 §2.1 남은 의문 | 점프가 없을 때 끝 x ≈ 0.0~0.05 vs 사용자 '실제 x ≈ 0.6' | 0.5 m 차 | 사용자: 0.6 은 **눈대중** → 의문 닫음. 끝 정확도는 다음 주행에서 줄자로 | 대화(사용자 답) |
| 10-02 §3 | 사용자 결정 | ⓐ 후보 채택 · ⓑ 탐색 창 3.0 → 1.0 · ⓒ 둘 다(내 권장) 중 **ⓑ 기각 · 3.0 유지** | 근거(사용자): 점프는 지도에 없는 빈 곳을 지난 특수 상황. 그보다 움직이는 물체(의자)가 저장 지도에 남아 통로를 좁히는 게 더 중요. 내 설명: 탐색 창은 정밀도가 아니라 **찾는 범위** — ①·③ 의 점프 전 보정값이 소수 셋째 자리까지 같음(+200 s −0.110, +250 s +0.097) | `j803_locjump.txt` |
| 10-02 §4 | office_v3 채택(사용자 승인) | Jetson 복사 · sha256 앞 16 자 일치(posegraph 38f464056ce970c4 · data 823c81a397eabe9d · pgm 5be798b8d4a7a993), v1 · v2 보존. prep 기본 지도 v3 | 지우기 계획: 위치 추정 포즈 그래프는 그대로, **경로 계획용 격자(`/map_nav`)만** 고친다 | [`job804_save_v3.sh`](../debug_log/2026-10-02/jobs/job804_save_v3.sh) · [`j804_save_v3.txt`](../debug_log/2026-10-02/outputs/j804_save_v3.txt) · `job726_prep_map.sh` · `job731_f2_prep.sh` · `job760_nav2_restart.sh` |
| 10-02 §5 | 지울 후보 추출(10-01 F2 bag 12 개, 자동으로 지우지 않음) | 자세 검증 통과율 f2a1 · f2a4 100 % · f2a12 77 % · f2a6 58 % · f2a8 25 % · f2a10 9 %. 1 차(반사 없는 빔을 6 m 까지 '통과') 1,652 칸 → **폐기**. 2 차 **296 칸(A 19 · B 275 · C 2), 3 칸 이상 묶음 22**. 병목 세 곳 덩어리는 후보 아님(칸당 맞음 중앙 서 117 · 가운데 705 · 동 564) | 사용자: 병목 덩어리 = **책상 다리**(고정) · **자동으로 지우지 않음** — 사용자가 GIMP 로 `office_v3_nav.pgm` 을 손으로(방법 안내). ⚠ **지금 저장소에 `office_v3_nav` 없음**(손 수정 미적용으로 보임, Jetson 쪽은 미확인) | [`job805_evid.py`](../debug_log/2026-10-02/jobs/job805_evid.py) · [`clear_cand.py`](../debug_log/2026-10-02/jobs/clear_cand.py) · [`clear_cand.txt`](../debug_log/2026-10-02/outputs/clear_cand.txt) · 그림 [`2026-10-02_clear_candidates.png`](../04_navigation/figures/2026-10-02_clear_candidates.png) |
| 10-02 §6 선언 | f2b1: office_v3 + BT PathBlockedAhead 첫 검증. 코스 f2a12 와 같은 10 목표 | prep: 시작 원점에서 1.23 cm · 흔들림 0 · Nav2 6 노드 active · BT 플러그인 49 개(rover 1) · `/map_nav` 발행자 1 | 판정 F2-a 10 목표 · 사람 도움 없음 · 접촉 0 · 복귀 ≤ 5 cm, **F2-b 한 번에 > 0.30 m 0 건**, F2-c PathBlockedAhead 적재 · 작동 | [`j811_prep.txt`](../debug_log/2026-10-02/outputs/j811_prep.txt) · [`j812_navchk.txt`](../debug_log/2026-10-02/outputs/j812_navchk.txt) |
| 10-02 §6.2 | f2b1 | 게이트 A · B · J(15.1 Hz) · C · G2 0.377 · P 42 % 통과. **목표 1 만 실행** — B SUCCEEDED 52.5 s | **내 실수**: wsl 이 인자를 한 줄로 이어 `;` 뒤 9 목표가 별도 명령("-1.6,-2.0,p: command not found") → 래퍼 파일 안에 목표 문자열(§5 실수 4) | [`f0_f2b1_runner.log`](../debug_log/2026-10-02/outputs/f0_f2b1_runner.log) |
| 10-02 §6.3 | f2b2(B 에서 이어 가기) | G2 불합격 0.067 m — 라이다 최소 0.646 m 인데 로컬 치명 칸 1 개가 로버 기준 (+0.32, +0.06)(범퍼 6.7 cm 앞) · (+0.67, +0.01) — 라이다에 없음 = 카메라(nvblox) 표시 | 사용자 '없다, 출발 가능' → `G2_SKIP=1`(값은 기록) | [`f0_f2b2_runner.log`](../debug_log/2026-10-02/outputs/f0_f2b2_runner.log) · [`job814_nearcells.py`](../debug_log/2026-10-02/jobs/job814_nearcells.py) · [`j814_nearcells_100.txt`](../debug_log/2026-10-02/outputs/j814_nearcells_100.txt) · [`_99.txt`](../debug_log/2026-10-02/outputs/j814_nearcells_99.txt) · [`run_f2b2.sh`](../debug_log/2026-10-02/jobs/run_f2b2.sh) |
| 10-02 §6.4 | f2b3(B → 9 목표) | W3 53.7 · 서쪽 통로 29.4 · 남서 50.4 · D 45.4 s SUCCEEDED(오차 0.146~0.157 m). D → 남서 **CANCELED 97.3 s** — 도착 (−1.519, −5.619, 67.4°): 위치 0.144 m 안 · 방향 −81.6° 차. map→odom 한 번에 최대 **0.184 m**(+253 s), 0.08 m 넘는 변화 6 건. PathBlockedAhead 13:25:36 · 40 '비용 99 — 2 s 지속되면 재계획' 2 회, 2 s 안에 풀림 | **F2-b 통과** — 10-01 점프 자리(목표 6 시작 남쪽 통로 회전, 13:25:08~)에서 점프 없음 = office_v3 실주행 효과. F2-c 적재 · 작동(실제 막힘 재계획은 미시험) | [`f0_f2b3_runner.log`](../debug_log/2026-10-02/outputs/f0_f2b3_runner.log) · [`job816_g5log.sh`](../debug_log/2026-10-02/jobs/job816_g5log.sh) · [`j816_g5log.txt`](../debug_log/2026-10-02/outputs/j816_g5log.txt) |
| 10-02 §6.4 경과 | 목표 6 nav2 로그 | D 에서 후진 16 s(vx −0.06) → 제자리 180° → 전진 → +251 s 0.14 m 안 도착(방향 157°) → 방향 맞추기 중 **시계 방향 113° → 54°**(목표 149° 반대쪽) → 13:26:11 'Optimizer fail to compute path' 2 회 → 13:26:37 진행 검사 실패 → 13:26:45 nav_guard '45 s 동안 최대 0.25 m' 취소 | 추정: 차체가 내접 · 치명 칸에 걸쳐 MPPI 가 회전 방향을 잃음. ⚠ SUMMARY 는 스무더 충돌 2 건을 모두 '출발 자세가 충돌 칸' 이라 썼으나 13:25:08 건 (−1.526, −5.555)은 로버가 D(x 1.45)에 있을 때라 **경로 끝(목표 쪽)**이다(§5 모순 1) | `j816_g5log.txt` |
| 10-02 §7 | f2b3 목표 6 정체 원인 — 사용자: '로버가 의자 다리를 밀고 가길래 치워 줌' | 차체 외곽 ↔ 라이다 최근접 +33 s 0.087 m(앞왼) · +42 s **0.044 m**(뒤왼), 로컬 치명 0.072 · 0.037 · 정지 중 0.048 | '목표 서남쪽에 지도에 없는 의자 → 반시계 회전 막혀 시계로 크게 돎 → 뒤왼 모서리가 의자에 닿음' — **틀림**(§7.1). F2-a '접촉 0' 불합격 | [`job817_lviz.py`](../debug_log/2026-10-02/jobs/job817_lviz.py) · [`render_corner.py`](../debug_log/2026-10-02/jobs/render_corner.py) · 그림 [`2026-10-02_f2b3_corner.png`](../04_navigation/figures/2026-10-02_f2b3_corner.png) · `f2b3_lviz.npz`(스크래치패드, **원천 소실**) |
| 10-02 §7.1 | 사용자 정정 '회전 중엔 아무것도 안 닿았다 — 의자는 그 전 전진 중에 걸렸다' → 재확인 | 회전 구간 가까운 라이다 점은 모두 **저장 지도의 벽 · 구조물**(지도 벽까지 0.00~0.05 m): +33 s (−1.85, −5.40) 0.087 m · +42 s (−1.82, −5.89) 0.044 m | §7 '의자에 붙어 회전' 은 **내 오판**(§5 실수 5). 다시 쓴 기전: 남서 경유점 (−1.6, −5.5)이 서쪽 구조물(x ≈ −1.85)에서 0.25 m, 모서리 반경 0.31 m 라 정렬 회전 자체가 구조물 몇 cm 앞을 쓺. 의자 접촉 = 라이다 아래 높이 다리 · 바퀴, 카메라 화각 밖 옆(추정, 시각 · 위치 모름) | 같은 npz · 그림 |
| 10-02 §7.2 | 사용자 '+36 s 에 x −1.8 이던 왼쪽 장애물이 회전하며 −1.73 까지 커진다' → 측정 | 라이다 벽 안쪽 면 map −1.81~−1.86 그대로인데 **odom −1.40 → −1.53(12 cm)**, 로컬 치명 −1.84 → **−1.72**(남음). 같은 구간 odom 이동 0.246 vs map 0.153 · map→odom 보정 0.263 m | **확인** — 회전 중 EKF 가 미끄러짐을 잘못 적분 → odom 좌표 로컬 코스트맵에 옛 표시가 남아 벽이 ≈ 12 cm 두꺼워짐 → 외곽 4.8 cm 안 치명 → MPPI 실패. 어느 층인지는 bag 에 nvblox 슬라이스가 없어 분리 못 함 → **[회전 중 장애물 번짐](rotation-obstacle-smear.md) 으로 갈라짐** | `f2b3.csv`(+247~265 s, **원천 소실** — 러너 csv 는 outputs 에 없음) · 출력 원문 없음(SUMMARY 표만) |
| 10-02 §7.1 대책 후보 | (A) 중간 목표 방향 무시 (B) 남서 경유점을 (−1.35, −5.55)로(회전 여유 10 cm 이상: 중심 x ≥ −1.85 + 0.31 + 0.10 = −1.44) (C) 옆 낮은 물체 사각은 별도 과제 | — | 결정 대기 → 이후 10-07 (A) 를 '위치만(f)' 로 구현 | — |
| 10-02 §8 · §8.1 | 사용자 결정: 남은 순회 대신 **출발로만 복귀**(f2b4, `BAG_PROFILE=nvblox` 처음 포함) | 남서 구석 (−1.52, −5.62, 67°) → (0, 0) 경로 5.82 m **SUCCEEDED 157.4 s**, 도착 (0.123, 0.054, −177°) 목표 대비 0.135 m · 19.5°. map→odom 누적 (0.125, −0.003) m · −2.55°, 누적 회전 휠 131.6° vs EKF 118.6° | 오늘 누적: **진짜 성공 6(B · W3 · 서쪽 통로 · 남서 · D · 출발), 실패 1(D → 남서)**, 접촉 1(의자 다리) — §9 상자를 더해 **2**. PC 러너는 `&` 로 끊김(내 실수, 주행 영향 없음) → `wait819.sh` 로 회수 | [`f0_f2b4_runner.log`](../debug_log/2026-10-02/outputs/f0_f2b4_runner.log) · [`wait819.sh`](../debug_log/2026-10-02/jobs/wait819.sh) |
| 10-02 §9 | 사용자 '복귀 때 출발 방에서 상자를 치며 들어옴' → 인지했나 | 상자 자리(10-01 §8.36: x 1.15~1.25, y 0~−0.17)의 ≥ 99 칸이 접근 내내 전역 0(문 쪽 1 칸 잠깐) · 로컬 0 · nvblox 0. +63~66 s 차체가 상자 자리를 덮음 = 접촉. 같은 시각 nvblox 장애 칸 720~940(카메라는 동작) | **전혀 인지 못 함**(측정). 원인 후보 ① 짧은 노출 ② 근거리 제거 0.45 m ③ 면 깊이 결측 — 깊이 원본이 없어 판별 불가 | [`job820_lviz.py`](../debug_log/2026-10-02/jobs/job820_lviz.py) · [`job820_gviz.py`](../debug_log/2026-10-02/jobs/job820_gviz.py) · [`render_box.py`](../debug_log/2026-10-02/jobs/render_box.py) · 그림 [`2026-10-02_f2b4_box.png`](../04_navigation/figures/2026-10-02_f2b4_box.png) |
| 10-02 §9.1 | 사용자: 화각 안이었는지만 | 카메라 (0.234, 0.044) · yaw −2.68° · 수평 ±43.5° 로 상자 모서리 12 점 기하: +50 s 까지 화각 밖(최소 각 44~78°), +51~58 s 만 모서리 1~3 점이 가장자리(37~44°), 그중 점군 구간(0.45~1.2 m) 안은 +51 · 53~55 s 1~3 점, 접촉 +63~66 s 는 117~146° | **사실상 화각에 안 들어옴**(측면 접근) → 카메라 처리 문제가 아니라 화각 문제. 사용자: '낮은 물체를 카메라로 피하기' 기능 시험과 별개로 둠 | [`box_fov.py`](../debug_log/2026-10-02/jobs/box_fov.py) · [`box_fov.txt`](../debug_log/2026-10-02/outputs/box_fov.txt) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 점프 = CPU · 타이밍 우연(라이브 부하) | 같은 bag 을 재생(로봇 정지 · 부하 낮음 load 0.41)으로 같은 노드 설정에 | 같은 시각(+281.9 vs 라이브 +283.0) · 같은 크기(1.28 vs 1.33 m), 모든 비교 시각 x 차 ≤ 0.03 | **기각** — 재생이 결정적 |
| 점프 = 지도 빈 곳(사용자) | 구멍만 메운 지도(②, 탐색 창 같음) | 0.30 m 넘는 변화 0 | **지지** |
| 점프 = 넓은 탐색 창 ± 1.5 m(10-01 §8.41 내 추정) | 지도 그대로, `loop_search_space_dimension` 1.0(③) | 0.30 m 넘는 변화 0 | **지지** — 두 조건 모두 '필요조건 중 하나' 로 보임. 단 ③ 은 `loop_search_maximum_distance`(3.0)는 그대로 둔 시험(`job803_locjump.sh` 가 넘긴 것은 dimension 하나) |
| 점프 기전 = 곧은 벽 하나 + 구멍 → 벽 방향(x) 으로만 미끄러짐 | 점프 성분 · 지도 미지 비율 | x −1.33 · y +0.006 · yaw +0.1°, ±1 m 미지 18 % | **지지(정황)** — 정합 점수 내부는 안 봄(미확인) |
| office_v3 가 실주행에서도 점프를 막는다 | f2b3 같은 자리 통과 | 한 번에 최대 0.184 m, 같은 자리 점프 없음 | **지지(1 회)** |
| f2b3 남서 정체 = 의자에 붙어 회전 | 회전 구간 라이다 최근접 점의 지도 벽 거리 | 0.00~0.05 m — 지도 구조물 | **기각**(§7.1) |
| f2b3 남서 정체 = 회전 중 odom 벽 두꺼워짐(사용자 관찰) | 같은 벽을 map · odom 으로 | map 그대로 · odom 12 cm · 로컬 치명 남음 | **지지** → [회전 중 장애물 번짐](rotation-obstacle-smear.md) |
| f2b4 상자 접촉 = 카메라 처리 실패 | 화각 기하 | 접근 내내 거의 화각 밖 | **기각** — 화각(측면 접근) 문제 |
| 상자 면 깊이 결측 · 근거리 제거 0.45 m | 깊이 원본 | bag 에 없음 | **미확인** |

## 4. 조치와 효과
- **office_v3 채택**(§4): 구멍 상자 미지 0.0 %, 옛 지도 이동 0. 재생에서 점프 소멸(②), f2b3 실주행에서 같은 자리 점프 없음. 대가: 남쪽 벽 안쪽 면이 x −0.3~2.7 에서 한 칸(5 cm) 남쪽으로 새로 그려짐(실제 위치 미확인). 지금도 prep 기본 지도(`Docs/tools/prep_fast.sh` 9 행 `MAP=${MAP:-office_v3}`, `places.yaml` 8 행 `map: office_v3`).
- **탐색 창 3.0 유지**(§3, 사용자): 지금 [`slam.yaml`](../../ros2_ws/src/rover_bringup/config/slam.yaml) `loop_search_maximum_distance: 3.0`(45 행) · `loop_search_space_dimension: 3.0`(57 행), 위치 추정 모드는 [`slam.launch.py`](../../ros2_ws/src/rover_bringup/launch/slam.launch.py) 75~77 행이 0.30 · 0.15 · 갱신 10 · **transform_timeout 1.5**(10-27 에 0.5 → 1.5 — 10-02 재생은 0.5 조건)만 덮어씀. 점프 감시(map→odom 한 번에 0.3 m · 10° 넘으면 취소, 10-01 §8.41 ②)는 **구현되지 않음**(이 시기 기록 기준).
- **지우기**: 후보만 뽑고 자동 적용 안 함. 손 수정본 `office_v3_nav.pgm` 은 저장소에 없다.
- **러너**: `G2_SKIP=1`(사용자가 현장 확인한 경우만, 값은 기록) · 목표 문자열은 래퍼 파일 안에(`run_f2b2.sh` — `rest` · `full` · `home`) · `BAG_PROFILE=nvblox`(f2b4 부터).
- 남서 구석 정체: 10-02 에는 대책 결정 없음(§7.1 A · B · C 후보).

## 5. 내 실수
**실수 1 — 점프 신호를 '오탐' 으로 버림(10-01 §8.40 → §8.41)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 사용자 '그림 속 위치가 다르다' 를 스캔-지도 맞춤으로 확인 — `fit_scan.py` · `fit_scan2.py`(10-01 jobs) |
| 본 것 | 남쪽 잔차 0.09~0.18 m, 넓은 탐색에서 필요 보정 **dx +1.35 m** |
| 처음 추론 | 남쪽 책상 줄은 비슷한 모양이 반복되므로 1.35 m 해는 반복 구조에 걸린 오탐 — 국소 탐색(±0.3 m) 결과만 채택 |
| 의심한 이유 | 사용자가 영상 36 s 에서 '위치가 뛰었다' 고 짚음 → map→odom 기록에 실제 −1.33 m 한 번 이동 |
| 판별 | `f2a12_full.npz` 의 map→odom 시계열(+283.0 s 한 갱신 −1.33 m), 점프 뒤 잔차가 커짐 |
| 결론 | dx +1.35 는 **실제 점프를 되돌리는 보정**이었다. §8.37~§8.40 의 목표 6 · 7 해석 무효 |
| 다음에 알아보는 법 | 맞춤 도구가 큰 보정을 내면 버리기 전에 **같은 시각 map→odom 의 계단**을 먼저 본다. 잔차가 '커지는 쪽' 으로 바뀌었다면 틀린 자리에 맞춘 것 |
| 데이터 | `2026-10-01/jobs/fit_scan.py` · `fit_scan2.py` · `job792_full.py`, npz 는 스크래치패드(**원천 소실**), 원천 bag [`2026-10-01/bags/bag_f2a12.tgz`](../debug_log/2026-10-01/bags/)(git 제외) |

**실수 2 — 구멍 판정 H-1 의 영역을 벽 뒤까지 잡음(10-02 §1.1)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 보완 지도의 구멍이 메워졌는지 — `cmp_maps.py` H-1(점프 지점 ±1 m 미지 비율 ≤ 5 %) |
| 본 것 | 후보 9.6 %(v2 18.3 %) — 불합격 수치 |
| 처음 추론 | (선언 그대로면) 보완 실패 |
| 의심한 이유 | 그림(`hole_fill.png`)에선 통로 안 구멍이 다 메워져 있음. 남은 미지가 어디 있는지 나눠 봄 |
| 판별 | 통로 안(y −6.15~−4.62)만 9.3 % → 0.3 %, 구멍 상자 0.0 %, 벽 뒤 띠는 미지 41 % |
| 결론 | 기준 정의가 잘못(벽 뒤는 원래 관측 불가). 기준을 바꿔 통과시킨 것이 아니라 두 값 모두 기록 |
| 다음에 알아보는 법 | 지도 '미지' 비율 판정은 **로봇이 볼 수 있는 영역(벽 안쪽)** 으로 범위를 정하고 선언한다 |
| 데이터 | [`cmp_maps_c276.txt`](../debug_log/2026-10-02/outputs/cmp_maps_c276.txt)(원문엔 ±1 m 값만 — 통로 안 9.3 → 0.3 % 는 SUMMARY 수치로 **출력 원문 없음**) |

**실수 3 — 점프 시각 +278.4 s(10-01 §8.41 · 10-02 §1 → §2.1 정정)**: 추출 시각 기준(러너 출발 −5 s)을 bag 기준으로 잘못 환산. 기록 map→odom 에서 직접 보면 **+283.0 s**(1.332 m). 영향: §1 의 자르기 +276 s 는 점프 7 s 전이라 결과 무관. ⚠ [`job803_locjump.py`](../debug_log/2026-10-02/jobs/job803_locjump.py) 머리 주석에는 아직 '+278.4 s' 가 남아 있다. 알아보는 법: 시각은 **bag 첫 메시지 기준**인지 **추출 창 기준**인지 항상 같이 적는다.

**실수 4 — wsl 인자 분리로 목표 1 만 실행(§6.2)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | f2b1 10 목표 — `wsl … bash run_f0.sh NAME "목표들"` 을 대화 쪽에서 바로 |
| 본 것 | 목표 1 SUCCEEDED 뒤 끝, 화면에 '-1.6,-2.0,p: command not found' |
| 처음 추론 | (없음 — 바로 원인 확인) |
| 결론 | wsl 이 인자를 셸 한 줄로 이어 붙여 `;` 뒤가 별도 명령. 10-01 에는 래퍼 파일(run_x7xx.sh)에 적어 불러 안 겪음 |
| 다음에 알아보는 법 | `;` 가 들어간 인자는 **파일 안**에 적는다(`run_f2b2.sh` 의 `FULL` · `REST` · `GHOME`) |
| 데이터 | [`f0_f2b1_runner.log`](../debug_log/2026-10-02/outputs/f0_f2b1_runner.log) |

**실수 5 — 지도 구조물을 의자로 읽음(§7 → §7.1)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | f2b3 남서 정체 원인 — `job817_lviz.py` 로 13:25:30~13:26:50 추출, `render_corner.py` 4 장면 |
| 본 것 | 회전 중 라이다 최근접 0.087 · 0.044 m(앞왼 · 뒤왼), 사용자 '의자 다리를 밀고 가길래 치워 줌' |
| 처음 추론 | 목표 서남쪽의 지도에 없는 의자가 반시계 회전을 막아 시계로 크게 돌았고 뒤왼 모서리가 닿았다 — 접촉 = 회전 중 |
| 의심한 이유 | 사용자 정정 '회전 중엔 아무것도 안 닿았다, 의자는 그 전 전진 중' |
| 판별 | 그 최근접 점들을 저장 지도 벽까지 거리로: 0.00~0.05 m |
| 결론 | 가까웠던 것은 **지도 구조물**. 의자는 라이다(18.5 cm) 아래 다리 · 바퀴로 이 bag 에 점이 없음(시각 · 위치 모름) |
| 다음에 알아보는 법 | '지도에 없는 물체' 라고 쓰기 전에 그 점의 **저장 지도 점유 칸까지 거리**를 먼저 잰다(≤ 1 칸이면 지도에 있는 것) |
| 데이터 | `f2b3_lviz.npz`(스크래치패드, **원천 소실**), 그림 [`2026-10-02_f2b3_corner.png`](../04_navigation/figures/2026-10-02_f2b3_corner.png), 원천 bag `bag_f2b3`(Jetson `/tmp` — PC 사본 없음, 10-06 §2 재생엔 쓰였음) |

작은 실수(한 줄): §7.2 층 분리 불가 = 러너가 `BAG_PROFILE` 을 안 넘겨 nvblox 슬라이스 미기록(→ `run_f2b2.sh` 에 추가) · §8.1 PC 러너를 `&` 로 띄워 대화 쪽 연결이 끊김(주행 영향 없음, `wait819.sh` 로 회수).

**모순 · 원문 대조(이 카드를 쓰며 찾은 것)**
1. §6.4 '스무더 충돌 (−1.53/−1.56, −5.56/−5.61) = 출발 자세가 충돌 칸': [`j816_g5log.txt`](../debug_log/2026-10-02/outputs/j816_g5log.txt) 13:25:08 건(−1.526, −5.555)은 목표 6 을 받은 순간(로버는 D, x ≈ 1.45)이라 **경로 끝(남서 목표 자리)**의 충돌이고, '출발 자세' 는 13:26:12 건(−1.555, −5.606)에만 맞다. 즉 목표 자리 자체가 처음부터 스무더 충돌 판정을 받은 곳이었다.
2. [`j802_extend.txt`](../debug_log/2026-10-02/outputs/j802_extend.txt) 끝에 '**Ceres(루프 클로저) 흔적: 1 건**' — do_loop_closing False 확인과 함께 찍혔는데 SUMMARY §1.1 은 언급 없음. 흔적이 기동 때 한 번인지 실제 최적화인지 **미확인**(H-3 이동 0 이라 결과엔 영향 없어 보임).
3. [`f0_f2b3_runner.log`](../debug_log/2026-10-02/outputs/f0_f2b3_runner.log) 목표 3(남서) 'SUCCEEDED … 목표 대비 0.146 m, **89.4°**' — yaw 허용(0.35 rad ≈ 20°)보다 큰 차로 성공 표시. 러너의 비교 yaw 가 출발 때 계산한 `p` 초기값이고 실제 보낸 목표 yaw 와 다를 수 있음 — **미확인**. 같은 줄의 'stuck 진단 1 회' 도 SUMMARY 에 없음.
4. §1.1 H-4 의 v1 값 −6.205/−6.154/−6.200(3 자리)은 원문(2 자리 −6.21/−6.15/−6.20)에 없음 — 별도 계산의 출력 원문 없음(차 −0.036/−0.044/−0.048 도 같음).
5. (6 기 작성 중, 11-02) 위 3 번 판별: 10-01 판 러너([`2026-10-01/jobs/job550_f0run.py`](../debug_log/2026-10-01/jobs/job550_f0run.py))도 루프 안에서 `gyaw = path_end_yaw(...)` 로 **바꾼 뒤** 결과 줄을 찍으므로 89.4° 는 보낸 방향(−107°) 기준이다 → '`p` 초기값' 가설 기각. Nav2 `yaw_goal_tolerance` 0.35 rad 인데 SUCCEEDED 라면 **컨트롤러가 비교한 목표 방향이 보낸 방향과 달랐다**(도착 −18.0° 는 0° 기준 20° 안 — BT `TruncatePath` 의 끝 방향 0° 와 맞음, 정황). 목표 6 에서 '시계 방향 113° → 54°' 로 돈 것도 0° 쪽이다. 10-07 에도 같은 서명 2 건 → [남서 구석 방향 맞춤 정체 §3](southwest-orient-stall.md).
6. (6 기 작성 중) '한 번에 최대 0.184 m'(§6.4) · 10-07 '한 번에 5 cm 넘는 보정' 은 **map→odom 변환의 병진 변화**다. 로버 위치의 변화와 같지 않다 — 원점에서 r 만큼 떨어진 곳에서 yaw 보정 Δθ 는 변환 병진을 ≈ r·Δθ 만큼 바꾼다(남서 구석 r ≈ 5.6 m 면 1° 에 ≈ 10 cm, 정의상 계산). 10-01 점프(x −1.33 · yaw +0.1°)처럼 병진이 지배적이면 같지만, 수 cm~십수 cm 의 '한 번 보정' 은 yaw 몫을 빼고 봐야 한다. 지금까지 그렇게 나눠 본 기록 없음.
7. (6 기 작성 중) 목표 이름 'W3' 이중 사용 — 10-02 §6 코스 줄 'W3 (−1.6, −2.0) … W3 (5.5, −2.2)'. 앞의 것은 10-01 §8.1 · `places.yaml` 의 **C**. 이 카드 §2 의 'f2b3 W3 53.7 s' 는 C(−1.6, −2.0) 이다. 10-07 §2 · §2.2 표도 같은 이름을 이어 씀.

## 6. 남은 것 (10-02 시점)
- 점프 감시(map→odom 계단 감지 → 취소)는 없다. 다른 빈 곳 · 반복 구조에서 같은 일이 생기면 막을 장치가 지도 품질뿐.
- 탐색 창 3.0 의 대가(반복 구조 오정합)는 재생 ③ 으로만 확인 — 다른 자리에서의 위험은 미측정.
- office_v3 남쪽 벽 한 칸 이동 — 줄자 미확인.
- `/map_nav` 움직이는 물체 지우기 — 사용자 손 수정 대기(저장소엔 아직 없음).
- 남서 구석 방향 맞춤 정체 — 대책 미결정(§7.1 A · B), 기전 중 '시계 방향으로 크게 돈 이유' 미확인. → 6 기 [남서 구석 방향 맞춤 정체](southwest-orient-stall.md)(시계 방향 = 0° 쪽, 아래 모순 5).
- 옆 · 뒤 낮은 물체(의자 다리 · 상자) 사각 — 센서 범위 문제로 별도 과제.
- 위치 정확도 F2-d(복귀 줄자 ≤ 5 cm) — 10-02 에는 재지 않음.

## 7. 6 기 (10-06 ~ 10-08) — rf2o 켠 순회 f2c · f2d, 전역 nvblox 순회 f2e
이 시기의 순회는 목적이 '위치 점프' 가 아니라 rf2o(10-07)와 전역 nvblox(10-08)의 비교였다. 이 카드에는 **순회 결과 · map→odom 보정 · 점프 여부**만 남기고, 남서 정체는 [남서 구석 방향 맞춤 정체](southwest-orient-stall.md), rf2o 판정(③-b · ③-c · G4)은 [rf2o 도입](rf2o-introduction.md), 상자 ② · 전역 nvblox 층 프레임 결함은 상자 줄기(카드 미작성 — 10-07 §2.6 · §7.1~§8, 10-08 §1~§3)로 간다.

### 7.1 흐름
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-06 §2 | 순회 주행 없음. f2b3 · f2b4 bag 을 rf2o 정식 launch 로 재생(도메인 42) | f2b3 남서 구석 벽 안쪽 면 범위 A 0.196 / B 0.096 / SLAM 0.084 m, 기동 뒤 남은 차 A−SLAM −15.1 / B−SLAM −4.7 cm(정식 launch 열) | rf2o 가 10-02 남서 구석의 odom 번짐을 재생에서 줄임 → [rf2o 도입](rf2o-introduction.md) | [10-06 SUMMARY §2](../debug_log/2026-10-06/SUMMARY.md) · [`j850_r3_replay.txt`](../debug_log/2026-10-06/outputs/j850_r3_replay.txt) |
| 10-07 §2 선언 | 같은 office_v3 · 같은 10 목표 · rf2o + G4 + 그림자 EKF A. 비교 기준 = 10-02 f2b(시도 7 · 성공 6 · 실패 1 · 접촉 2 · 점프 최대 0.184 m) | — | ③-a 10 목표 · 접촉 0 · 복귀 줄자, ③-b 번짐, ③-c G4 비용, ③-d 부하 | [10-07 SUMMARY §2](../debug_log/2026-10-07/SUMMARY.md) |
| 10-07 §2.2 · §2.5 | f2c1(목표 1~4) · f2c2(5~10) | f2c1 3/4(남서 CANCELED 71.2 s), f2c2 **6/6** → **9/10**. 도착 오차 0.122~0.165 m(f2c2 목표 6 남서만 0.242 m). map→odom 누적 f2c1 Δ(0.032, 0.094) m · −3.66° · f2c2 Δ(0.422, 0.265) m · −9.65° | 실패 1 = 남서 방향 맞춤(→ 남서 카드). 사용자: 복귀 때 상자를 밀며 옴 → 접촉 1 | [`f0_f2c1_runner.log`](../debug_log/2026-10-07/outputs/f0_f2c1_runner.log) · [`f0_f2c2_runner.log`](../debug_log/2026-10-07/outputs/f0_f2c2_runner.log) |
| 10-07 §3.4 | map→odom 0.42 m · −9.7° 가 이상치인가(f2b3 와 비교) + 어디서 쌓였나 | f2b3(rf2o 끔, 293 s) Δ(0.393, 0.137) · −5.70° vs f2c2(430 s) Δ(0.422, 0.265) · −9.65°. 변화 합: f2c1 위치 회전 중 0.493 · 밖 0.379 m / yaw 4.98 · 6.57°, f2c2 1.163 · 1.505 m / 8.56 · 17.49°. **한 번에 5 cm 넘는 변화** f2c1 2 회(181 s 8.1 · 191 s 14.4 cm — 둘 다 남서 접근 중), f2c2 15 회(출력된 12 개 중 최대 103 s 11.9 cm) | **이상치 아님** · rf2o 는 직진 드리프트를 줄이지 못함(직진 몫 2~4 %, 예상대로). 0.30 m 넘는 한 번 변화 없음 = **점프 없음**(f2c 두 주행, 측정 — 단 아래 §5 6 번 · 7.2 의 한계) | [`f2c_anal.txt`](../debug_log/2026-10-07/outputs/f2c_anal.txt) · [`f2c_anal.py`](../debug_log/2026-10-07/jobs/f2c_anal.py) 27~31 행 · [`job913_extract.py`](../debug_log/2026-10-07/jobs/job913_extract.py) · 입력 `x913_f2c{1,2}.npz` **원천 소실**(bag `2026-10-07/bags/bag_f2c{1,2}.tgz` 로 재생성 가능) |
| 10-07 §6.2 · §7.1 | f2d1(같은 10 목표, G4 휠 잔차 · MPPI tol 0.5) · f2d2(5~10, 남서 `f`) | f2d1 3/4(남서 CANCELED 69.4 s), f2d2 5/6(남서 SUCCEEDED_XY 59.6 s · 목표 10 상자 ② 앞 정지 → nav_guard 123.2 s) → **8/10**. map→odom 누적 f2d1 Δ(0.051, 0.170) · −3.66° · f2d2 Δ(0.380, 0.230) · −8.82° | 남서 3/3 재현 → 러너 '위치만(f)'. 상자 ② 는 실제 낮은 상자(사용자). 한 번 보정 크기는 **미측정**(f2c_anal 을 f2d 엔 안 돌림) | [`f0_f2d1_runner.log`](../debug_log/2026-10-07/outputs/f0_f2d1_runner.log) · [`f0_f2d2_runner.log`](../debug_log/2026-10-07/outputs/f0_f2d2_runner.log) · [`j921_f2d2_g10.txt`](../debug_log/2026-10-07/outputs/j921_f2d2_g10.txt) |
| 10-08 §2 | '전역에 nvblox 를 넣었다면' — f2c2 · f2d2 bag 재계산 | 카메라만 본 장애물 묶음 f2c2 35 · f2d2 41, 대부분 10 s 넘게 지속, 거의 모두 통로 안. 사용자: "대부분 실제 물체 · (0.1, −5.8) 근처는 바닥 에어캡" | 상자 ② 첫 표시는 두 주행 모두 그 목표의 첫 경로 **뒤** → 전역 nvblox + 주기 재계획 A/B 로 | [`whatif_f2c2_f2d2.txt`](../debug_log/2026-10-08/outputs/whatif_f2c2_f2d2.txt) · [`nv_global_whatif.py`](../debug_log/2026-10-08/jobs/nv_global_whatif.py) · 그림 [`2026-10-08_nvblox_global_whatif.png`](../04_navigation/figures/2026-10-08_nvblox_global_whatif.png) |
| 10-08 §3 · §3.1 | 전역 nvblox(`global_camera:=nvblox`) + `replan_hz:=0.5` + `mppi_viz:=true` 선언 — 10 목표(남서 `f`)였으나 사용자가 **B → W3 (5.5, −2.2) → 출발** 3 목표로 줄임 | — | ③-a 3 목표 · 접촉 0 · nav_guard 0, ③-b 상자 ② 첫 표시 ≤ 3 s 안 회피 경로 | [10-08 SUMMARY §3](../debug_log/2026-10-08/SUMMARY.md) · 그림 [`2026-10-08_patrol_goals.png`](../04_navigation/figures/2026-10-08_patrol_goals.png) |
| 10-08 §3.3 · §3.5 | f2e1 | 3/3 SUCCEEDED 53.8 · 48.3 · 122.7 s, map→odom 누적 Δ(0.062, 0.312) · −7.34°. 사용자: 복귀 때 상자에 닿음 | 전역 nvblox 층 `nav2_costmap_global_frame = odom`(기본값) → map→odom 보정(끝 Δy 0.31 m)만큼 상자가 ≈ 0.3 m 밀려 찍힘 = **위치 추정 보정이 전역 지도 좌표로 새어 든 결함**(측정) → map 으로 고침 | [`f0_f2e1_runner.log`](../debug_log/2026-10-08/outputs/f0_f2e1_runner.log) · [`f2e1_box_replan.txt`](../debug_log/2026-10-08/outputs/f2e1_box_replan.txt) · [`f2e1_costmaps.txt`](../debug_log/2026-10-08/outputs/f2e1_costmaps.txt) · [`f2e1_contact.txt`](../debug_log/2026-10-08/outputs/f2e1_contact.txt) · [`job937_src.sh`](../debug_log/2026-10-08/jobs/job937_src.sh) |
| 10-08 §3.7 · §3.8 | f2e2(프레임만 고친 같은 구성) | 3/3 SUCCEEDED 52.1 · 49.1 · 108.5 s, map→odom 누적 Δ(−0.056, 0.375) · −5.28°. 전역 · 로컬 상자 칸 중심 차 ≤ 0.04 m. 사용자: 상자에 **닿지 않음** | 프레임 수정 확인. 점프 검사는 **미측정** | [`f0_f2e2_runner.log`](../debug_log/2026-10-08/outputs/f0_f2e2_runner.log) · [`f2e2_box_align.txt`](../debug_log/2026-10-08/outputs/f2e2_box_align.txt) · [`box_align.py`](../debug_log/2026-10-08/jobs/box_align.py) |

### 7.2 6 기 누적 · 판정
| 주행 | 코스 | 성공 / 시도 | 실패 · 정지 | 접촉(사용자) | map→odom 끝 − 처음 |
|---|---|---|---|---|---|
| f2c1 + f2c2 | 10 목표(rf2o) | 9 / 10 | 남서 방향 맞춤 1 | 1(복귀 상자 ②) | (0.032, 0.094) · −3.66° / (0.422, 0.265) · −9.65° |
| f2d1 + f2d2 | 10 목표(G4 잔차 · tol 0.5, f2d2 남서 `f`) | 8 / 10 | 남서 1 · 상자 ② 앞 정지 1 | 0(멈춤) | (0.051, 0.170) · −3.66° / (0.380, 0.230) · −8.82° |
| f2e1 | B → W3 → 출발(전역 nvblox, 프레임 결함) | 3 / 3 | — | 1(상자 ②) | (0.062, 0.312) · −7.34° |
| f2e2 | 같은 코스(프레임 고침) | 3 / 3 | — | 0 | (−0.056, 0.375) · −5.28° |

(전부 러너 로그 원문 — 위 표 데이터 칸.)
- **위치 점프**: 6 기에 10-01 식의 점프(한 번에 ≥ 0.30 m)를 보고한 기록은 없다. 측정한 것은 f2c1 · f2c2 뿐(최대 14.4 cm, f2c2 는 출력된 12 개 중 11.9 cm — `f2c_anal.py` 31 행이 앞 12 개만 찍음). f2d · f2e 는 계산하지 않음. 남서 접근 중 f2c1 의 8.1 · 14.4 cm 가 남서 정체와 관계있는지는 미확인(→ 남서 카드 §3).
- **map→odom 누적**: 10 목표 순회 끝에서 0.4~0.5 m · −9° 수준(f2b3 · f2c2 · f2d2), 3 목표(약 15 m)에서 0.31~0.38 m(f2e). rf2o 로도 줄지 않음(10-07 §3.4). 이 보정이 odom 좌표로 그린 층에 새면 장애물이 그만큼 밀린다는 것이 10-08 f2e1 에서 실제로 드러났다(전역 nvblox 층).
- 판정(10-08 시점): office_v3 위에서 점프 재발 0 은 '측정한 두 주행에서' 만 확인. 점프 감시 장치는 여전히 없다(§6 그대로).

### 7.3 이후 (10-12 ~): 다음 시기에서 채움
- 포인터만: 위치 추정 모드의 다른 결함 — 10-27 정합 중 map→odom stamp 정체 → transform_timeout 1.5([SLAM map→odom 시각 정체](slam-stamp-freeze.md)), 10-28 오래 세워 둔 스택의 odom yaw 드리프트([세워 둔 로버의 방향 드리프트](stationary-yaw-drift.md)). 회전 중 벽 두꺼워짐 → [회전 중 장애물 번짐](rotation-obstacle-smear.md) · [rf2o 도입](rf2o-introduction.md). 남서 정체의 재해석(10-14 §16) → [남서 구석 방향 맞춤 정체](southwest-orient-stall.md).

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2a12 | 10-01 F2 열두 번째 — 목표 6 시작 점프 | `2026-10-01/outputs/f0_f2a12_runner.log` · `j786` · `j793` · bag `2026-10-01/bags/bag_f2a12.tgz` |
| cand_1002_f2a12_c276_nolc → office_v3 | 이어 그리기 +276 s · 루프 끔 | `2026-10-02/outputs/cand_*.pgm/.yaml` · `j802` · `cmp_maps_c276.txt` · `Docs/04_navigation/maps/office_v3.*` |
| 재생 ① ② ③ | 위치 추정 재생(v2·3.0 / 후보·3.0 / v2·1.0) | `j803_locjump.txt` · 그림 `2026-10-02_locjump_replay.png` |
| 지울 후보 | 10-01 F2 bag 12 개 증거 | `clear_cand.txt` · 그림 `2026-10-02_clear_candidates.png` |
| f2b1 · f2b2 · f2b3 · f2b4 | F2 순회 재시도(office_v3) | `f0_f2b{1,2,3,4}_runner.log` · `j811` · `j812` · `j814_*` · `j816` (bag · csv 는 PC 사본 없음) |
| `job802` · `job719_cutreplay.py`(10-01) · `cmp_maps.py` · `render_hole_fill.py` | 지도 보완 · 판정 | `2026-10-02/jobs/` · `2026-10-01/jobs/` |
| `job803_locjump.sh` · `.py` · `render_locjump.py` | 위치 추정 재생 | `2026-10-02/jobs/` |
| `job805_evid.*` · `clear_cand.py` · `render_cand_clear.py` · `render_cand_label.py` | 지울 후보 | `2026-10-02/jobs/` |
| `run_f0.sh` · `job551_f0drive.sh` · `job550_f0run.py` · `run_f2b2.sh` · `wait819.sh` | 러너 | `2026-10-02/jobs/`(job550 은 Jetson `/tmp` 판) |
| `job814_nearcells.py` · `job816_g5log.sh` · `job817_lviz.py` · `render_corner.py` · `job820_lviz/gviz.py` · `render_box.py` · `box_fov.py` | f2b 분석 | `2026-10-02/jobs/` |
| f2c1 · f2c2 · f2d1 · f2d2(6 기) | 10-07 rf2o 켠 순회 · 남서 `f` | `2026-10-07/outputs/f0_f2{c1,c2,d1,d2}_runner.log` · `f2c_anal.txt` · bag `2026-10-07/bags/bag_f2*.tgz` → 남서 카드 |
| f2e1 · f2e2(6 기) | 10-08 전역 nvblox 순회 3 목표 | `2026-10-08/outputs/f0_f2e{1,2}_runner.log` · `f2e1_*.txt` · `f2e2_box_align.txt` · bag `2026-10-08/bags/bag_f2e*.tgz` |
| `job913_extract.py` · `f2c_anal.py`(6 기) | map→odom 보정 합 · 한 번 보정 | `2026-10-07/jobs/` — 해설은 [남서 카드 §9](southwest-orient-stall.md) |

## 9. 도구 해설
공통: Jetson 쪽 도구는 PC(WSL) 에서 `sshpass -p <PW> ssh jetson@192.168.0.101`(10-02 당시 주소, 지금은 192.168.0.110)로 스크래치패드 → `/tmp` 에 올려 돌렸다. 재생 도구는 **도메인 42 · sim time · `fastdds_udp_only.xml`** 로 라이브 스택과 분리. 분석 결과 npz 는 대부분 PC 스크래치패드(`…\scratchpad\f2a6\…`)에 있었고 **지금은 소실**(자동 삭제) — 출력 txt 만 `outputs/` 에 남았다.
도구 계보: (지도 재생) 09-30 `job580` 재생기 → 10-01 `job719_cutreplay.py`(CUT 초까지 · 기록 map→odom 뺌) → 10-02 `job802_extend.sh`(인자화) / `job803_locjump.py`(위치 추정 노드 · 1 배속 · 라이브 비교) → 10-27 `Docs/tools/run_slam_replay.sh`(상시 도구). (bag 장면 추출) 10-01 `job787_lviz.py` → 10-02 `job817/820/821/828/831_lviz.py`(같은 본문, 출력 이름 · 간격만 다름) → 10-23 `Docs/tools/fig_drive_video.py`.

### job802_extend.sh — 지도 이어 그리기 재생 (Jetson, bash)
- 부른 형태: `bash /tmp/job802_extend.sh 276`(환경 `BAG=/home/jetson/bags/bag_f2a12` · `BASE=office_v2` · `N=cand_1002_f2a12_c276_nolc`).
- 왜: 점프 지점의 지도 구멍을 같은 bag 의 그 구간 스캔으로 메우되, 옛 지도는 움직이지 않게(10-01 §2~§4: 루프 클로저를 켜면 옛 지도가 10 cm 옮겨짐).
- 하는 일: ① 같은 이름 출력이 있으면 중단 ② 도메인 42 에서 `async_slam_toolbox_node` 를 `slam.yaml` + `use_sim_time true` + `map_file_name=office_v2` + `map_start_pose [0,0,0]` + **`do_loop_closing false`** 로 띄움(이 slam_toolbox 는 `~/slam_ws` 포크) ③ 파라미터가 보일 때까지 최대 30 s, 실제 do_loop_closing 값 출력 ④ `/tmp/job719_cutreplay.py BAG CUT OUT` 실행(아래) ⑤ slam 로그에서 `preprocessor.cc`(Ceres 루프 최적화 흔적) 건수 ⑥ SIGINT 로 종료 ⑦ pgm 이 안 생겼으면 그래프만 불러 `map_saver_cli` 로 격자 저장(10-01 `job722` 방식).
- 출력: [`j802_extend.txt`](../debug_log/2026-10-02/outputs/j802_extend.txt) — 재생 스캔 수 · 점프(> 5 cm · > 2°) 목록(20 줄까지) · CUT 시점 map→odom · 서비스 결과 · 파일 목록. 후보 파일 `outputs/cand_*.pgm/.yaml`(posegraph · data 는 Jetson 만).
- 쓰인 곳: 10-02 §1.1 H-2(29 건), §4 office_v3.
- 결함: 점프 목록이 20 줄에서 잘림(29 건 중). Ceres 흔적 1 건의 의미를 확인하지 않음(§5 모순 2).
- 지금 다시: 지도 보완이 다시 필요하면 쓸 수 있으나 경로 · 버전은 하드코딩. 상시 판은 없다.

### job719_cutreplay.py(10-01) — CUT 초까지 재생 · 저장 (Jetson, Python rclpy · rosbag2_py)
- 부른 형태: `python3 -u /tmp/job719_cutreplay.py BAG CUT_S OUT_PATH`(job802 가 부름). 원본 [`2026-10-01/jobs/job719_cutreplay.py`](../debug_log/2026-10-01/jobs/job719_cutreplay.py).
- 하는 일: bag 을 읽어 `/scan` · `/tf` · `/tf_static` 만, **CUT 초 이후 버림**, `/tf` 에서 기록된 `map→odom` 제거(새 SLAM 이 직접 내게) → `/clock` 과 함께 재생 → 재생 SLAM 의 map→odom 을 모아 > 5 cm · > 2° 변화 목록 → 시계를 계속 흘리며 `serialize_map` · `save_map` 서비스 호출.
- 계보: 09-30 §17 '점프 전까지만 지도 되살리기' 용으로 만든 것을 그대로 재사용.

### cmp_maps.py — 후보 지도 판정 (PC, Python)
- 부른 형태: `python cmp_maps.py <후보.pgm>`(PC — 경로 `F:\…\Docs\04_navigation\maps` 하드코딩, 원점 (−5.29, −6.96) 고정, v1 원점은 yaml 에서).
- 하는 일: H-1 점프 지점 (0.54, −5.62) ±1 m 상자에서 칸 값 254 = 자유, 0 = 벽, 그 밖 = 미지 비율 + 구멍 상자(x −0.5~0.4, y −5.9~−4.9) 미지 비율. H-3 영역 5 곳(출발 방 · 동쪽 방 · 남쪽 · 남동 · 서쪽 띠)마다 v2 점유 ∧ 후보 점유를 ±3 칸(±15 cm) 평행이동으로 겹쳐 최대 겹침 이동 · 그대로 겹침 %. H-4 x −2~6 열마다 y −6.6~−5.9 점유 칸 중 가장 북쪽(안쪽 면) → 2 m 구간 평균 · 직선 기울기.
- 출력: [`cmp_maps_c276.txt`](../debug_log/2026-10-02/outputs/cmp_maps_c276.txt). 쓰인 곳 §1.1.
- 결함: H-1 상자가 벽 뒤 포함(§5 실수 2). 평행이동 탐색이 칸 단위(5 cm) — 5 cm 보다 작은 이동은 못 봄. 회전은 안 봄.
- 지금 다시: 원점이 같은 지도끼리는 그대로 쓸 수 있음.

### render_hole_fill.py — 구멍 보완 그림 (PC)
- office_v2 vs 후보를 겹쳐 남쪽 통로 확대(벽 안쪽 면 줄 포함) → [`2026-10-02_hole_fill.png`](../04_navigation/figures/2026-10-02_hole_fill.png). 출력 원문 없음(그림만).

### job803_locjump.sh · job803_locjump.py — 위치 추정 재생 (Jetson, bash + Python)
- 부른 형태: `bash /tmp/job803_locjump.sh office_v2:3.0 cand_1002_f2a12_c276_nolc:3.0 office_v2:1.0`(인자 = '지도:탐색 창' 목록, 약 20 분, 로버 안 움직임).
- 왜: 사용자 가설(지도 빈 곳)과 내 가설(탐색 창)을 주행 없이 가르려고. 재생이 라이브 점프를 재현해야 비교가 성립(P-0).
- 하는 일(sh): 조합마다 이전 sim-time slam 노드를 죽이고 `localization_slam_toolbox_node` 를 `slam.yaml` + `mode localization` + `map_file_name` + `minimum_travel_distance 0.30 · heading 0.15 · map_update_interval 10 · transform_timeout 0.5` + **`loop_search_space_dimension=$WIN`** 으로 띄움 → 실제 값 · 부하 출력 → py 실행 → 종료.
- 하는 일(py): ① bag 전체에서 `/scan` · `/tf` · `/tf_static` 만 메모리에 읽음, `/tf` 의 `map→odom` 은 '라이브' 목록으로 따로 빼고 재생에선 제거 ② `/tf_static` 을 transient-local 로 먼저 발행 ③ 메시지마다 벽시계로 **1 배속** 맞춰 발행, 5 ms 마다 `/clock` ④ 재생 노드가 내는 `map→odom` 을 bag 기준 시각(stamp − bag 시작)으로 모음 ⑤ 연속 두 값의 차가 > 0.10 m 또는 > 3° 인 것 목록 · 최대 ⑥ +100~340 s 10 시각에서 재생 vs 라이브 (x, y, yaw) · x 차 ⑦ npz 저장.
- 출력: [`j803_locjump.txt`](../debug_log/2026-10-02/outputs/j803_locjump.txt)(마지막 줄 `rc=1` — 마지막 pkill 의 종료 코드로 보임, 결과엔 영향 없음). npz `/tmp/locjump_*.npz` → PC 로 옮겨 `render_locjump.py` 가 그림([`2026-10-02_locjump_replay.png`](../04_navigation/figures/2026-10-02_locjump_replay.png)), npz 는 **원천 소실**.
- 쓰인 곳: §2.1 판정 · §3 결정의 근거.
- 결함: ① 머리 주석의 점프 시각 '+278.4 s' 는 틀린 값(실수 3) ② 탐색 창 조합에서 `loop_search_maximum_distance`(3.0)는 그대로 — '창 1.0' 은 dimension 만 바꾼 것 ③ 재생 시작 자세 (0,0,0) 고정 · tt 0.5(지금 운용은 1.5).
- 계보 · 지금: 10-27 `Docs/tools/run_slam_replay.sh`(도메인 42 재생 A/B 상시 도구)가 같은 역할. 이 판은 bag · 설정이 하드코딩이라 그대로는 안 씀.

### job804_save_v3.sh — 후보 → office_v3 (Jetson, bash)
- `office_v3.posegraph` 가 이미 있으면 중단 → posegraph · data · pgm 복사, yaml 은 `image:` 줄만 바꿔 저장 → 원본 · 사본 sha256 앞 16 자 나란히 출력. 출력 [`j804_save_v3.txt`](../debug_log/2026-10-02/outputs/j804_save_v3.txt). 1 회용.

### job805_evid.sh · job805_evid.py — 지우기 증거 추출 (Jetson, Python rosbag2_py)
- 부른 형태: sh 가 10-01 F2 bag 12 개를 `~/bags/f2` 에 풀고 `python3 job805_evid.py BAG OUT.npz` 를 bag 마다.
- 하는 일: `/tf` 의 map→odom · odom→base_link 시계열, `/scan` 은 0.19 s 이상 간격(≈ 5 Hz)으로 거리 배열(float16), `/nvblox_node/static_map_slice` 는 0.99 s 간격으로 격자 · 원점 · 해상도 · unknown 값. 스캔마다 그 시각 map 자세 = map→odom ∘ odom→base(직전 값). 슬라이스마다 그 시각 map→odom.
- 출력: `/tmp/evid/*.npz` → PC 로(**원천 소실**), 화면 한 줄(스캔 · 빔 · 슬라이스 · 길이) 원문 없음.

### clear_cand.py — 지울 후보 계산 (PC, Python)
- 부른 형태: `python clear_cand.py`(스크래치패드 `evid\*.npz` 를 읽음, office_v3.pgm).
- 왜: 사용자 우선순위(§3) — 저장 지도에 박힌 의자 등 움직이는 물체를 경로 계획용 격자에서 지울 근거.
- 하는 일: ① 스캔마다 빔 1/2, 끝점을 기록 자세로 map 에 놓아 **스캔-지도 잔차**(끝점 → 가장 가까운 점유 칸 거리, 0.3 m 상한의 RMS) > 0.06 m 면 그 스캔 버림(자세 틀린 구간 제거) ② 통과 스캔에서 끝점 칸 = 맞음(hit), 라이다에서 0.25 m ~ (끝점 − 0.15 m) 를 2.5 cm 간격으로 밟은 칸 = 통과(pass, 스캔당 칸마다 1 회). **반사 없는 빔(inf · 최대 거리)은 통과에서 제외**(1 차 시도 결함 수정) ③ 통과 스캔 0.5 s 안의 nvblox 슬라이스만, 관측 칸 중 거리 > 0.10 = 빈칸, ≤ 0.05 = 장애물(odom → map 은 기록 map→odom) ④ 판정: 지도 점유 ∧ pass ≥ 5 ∧ hit ≤ 10 % → L, 지도 점유 ∧ nv 빈칸 ≥ 3 ∧ nv 장애물 0 → N. A = L ∧ N, B = L 만, C = N 만(pass < 5). hit ≥ 3 칸 주변 1 칸은 제외(벽 가장자리 깎기 방지) ⑤ 8 연결 묶음 · 크기순.
- 출력: [`clear_cand.txt`](../debug_log/2026-10-02/outputs/clear_cand.txt) · `clear_cand.npz`(소실) → `render_cand_clear.py`(회색 증거 부족 · 검정 확인된 벽 · 주황 B · 초록 A) · `render_cand_label.py`(묶음 번호 · 병목 점선 원) → [`2026-10-02_clear_candidates.png`](../04_navigation/figures/2026-10-02_clear_candidates.png).
- 결함 · 한계: 2D 라이다 단면(18.5 cm) · nvblox 슬라이스(6~30 cm)뿐이라 높이가 다른 물체는 판단 못 함. 잔차 0.06 문턱은 근거 수치 없음.
- 지금 다시: 지도 원점 · 경로 하드코딩. 지우기 작업을 재개하면 출발점으로 쓸 수 있음(결과는 사용자 확인 필요).

### job731_f2_prep.sh · job726_prep_map.sh · job760_nav2_restart.sh · job812_navchk.sh — prep · 확인 (Jetson)
- 10-01 판에 `MAP` 기본(또는 인자)만 office_v3 로 바꾼 사본. `job812_navchk.sh` 는 Nav2 6 노드 lifecycle · `plugin_lib_names` 의 `_bt_node` 개수와 `rover_path_blocked` 수 · `/map_nav/info` 크기 · nav2.log 적재 오류 · load 출력 → [`j812_navchk.txt`](../debug_log/2026-10-02/outputs/j812_navchk.txt). 계보: 10-12 이후 `Docs/tools/prep_patrol.sh` → `prep_fast.sh` 로 대체.

### run_f0.sh · job551_f0drive.sh · job550_f0run.py — F0/F2 러너 (PC → Jetson)
- 해설은 [제자리 회전 옆 밀림 F0-a §9](f0-rotation-side-slip.md). 10-02 판의 차이(이 날 사본 [`job551_f0drive.sh`](../debug_log/2026-10-02/jobs/job551_f0drive.sh) vs 09-23 판 diff): ① 게이트 A 의 프로세스 이름 `lifecycle_manager` → `lifecycle_manager_navigation` ② **`G2_SKIP=1`** 이면 G2 값만 출력하고 진행(§6.3) ③ 10-01 §8.9 **부하 게이트 P** — 정지 10 s `/proc/stat` 코어 평균 사용률 > `LOAD_MAX`(기본 60 %)면 주행 안 함 ④ 2 s 마다 전체 프로세스 CPU 틱 기록 `/tmp/proc_<NAME>.log`. 러너 Python(`job550`)은 10-01 판(`GOAL_FRAME=map` · 목표 yaw `p`) — 이 날 바뀐 것 없음.

### run_f2b2.sh — 목표 문자열 래퍼 (PC/WSL, bash)
- 부른 형태: `bash run_f2b2.sh NAME rest|full|home "NOTE" GIT_HEAD`. 목표 문자열 `FULL`(10 목표) · `REST`(B 다음 9) · `GHOME`(출발)을 파일 안에 두고 `BAG_PROFILE=nvblox` · `G2_SKIP` · `GOAL_FRAME=map` · `STAGE=F2b` 를 export 해 `run_f0.sh NAME "$G" 0.07`.
- 왜: f2b1 의 wsl 인자 분리(실수 4). `BAG_PROFILE=nvblox` 는 §7.2 뒤 추가(f2b4 부터 슬라이스 기록).

### wait819.sh — 끊긴 러너 결과 회수 (PC/WSL)
- Jetson `/tmp/f0_f2b4.log` 에 '=== 끝' 또는 '주행하지 않음' 이 나올 때까지 10 s × 120 → `f0_f2b4.log` · `f2b4.csv` · `bag_f2b4.tgz` 를 스크래치패드로 scp(비밀번호 `<PW>` 가림). 회수본 중 log 만 `outputs/` 에 남음.

### job814_nearcells.py — G2 불합격 원인 칸 (Jetson, rclpy)
- `/local_costmap/costmap`(transient-local) 한 장과 `odom→base_link` TF 를 최대 8 s 기다려, 값 ≥ 100 인 칸을 차체 좌표로 옮기고 외곽(앞 0.25 · 옆 0.165 — 뒤도 0.25 로 계산) 까지 거리 오름차순 15 개. 출력 `j814_nearcells_100.txt`(문턱 100) · `_99.txt`(문턱 99 로 바꿔 한 번 더). 결함: 뒤 외곽을 0.25 로 씀(실제 0.248, 영향 2 mm).

### job816_g5log.sh — nav2 로그 발췌 (Jetson, Python 인라인)
- `/tmp/nav2.log` 의 `[epoch.ns]` 를 읽어 13:24:55 이후 · 'Message Filter' 아닌 줄 중 PathBlocked · nav_guard · Fail · Abort · Cancel · Received · Recovery · clear · BackUp · Wait · Goal · collision · Optimizer · Stuck 를 포함한 줄을 'HH:MM:SS 내용' 으로. 출력 [`j816_g5log.txt`](../debug_log/2026-10-02/outputs/j816_g5log.txt). 시각 하드코딩 1 회용.

### job817_lviz.py(· job820_lviz.py · job821/828/831) — bag 장면 추출 (Jetson, rosbag2_py)
- 부른 형태: `python3 job817_lviz.py BAG T_START T_END`(epoch). 다섯 파일은 **본문이 같고** 출력 이름(`/tmp/f2b3_lviz.npz` · `f2b4_lviz` · `f2b4s_lviz` · `rot2_lviz` · `rot3_lviz`)과 간격(1 s, rot 판은 0.5 s)만 다르다. 머리 주석은 10-01 §8.22 'f2a8 D 구간' 그대로(복사 흔적).
- 하는 일: `/tf` 의 map→odom · odom→base 를 모두 모으고, 창 안에서 `/scan` · `/plan` · 코스트맵 · `/nvblox*` 의 최신 메시지를 보관 → 간격마다 표본 1 개: map 자세(map→odom ∘ odom→base), 그 시각 map→odom(`mo`, 로컬 → map 변환용), 스캔 점(라이다 x 0.152 · yaw π − 0.04677 로 map 좌표), 경로, **로컬 코스트맵**(키 이름은 `gcm` 이지만 내용은 `/local_costmap/costmap` — 주석의 '전역 코스트맵' 과 다름), nvblox 슬라이스(있으면).
- `job820_gviz.py` 는 같은 본문에서 코스트맵만 `/global_costmap/costmap` 으로(그리고 `mo` 저장 없음).
- 출력: npz(**원천 소실**) → `render_corner.py`(§7, 6 장면 — 2 × 3 판) · `render_box.py`(§9) · `box_fov.py` · `smear_layers.py`(§10) · `smear_rot.py`(§11).
- 결함: 키 이름 `gcm` 오해 소지 · 주석 낡음 · 시각 창을 epoch 로 직접 받아 주행마다 손 계산.
- 계보: 10-23 `Docs/tools/fig_drive_video.py` 가 상시 영상 도구로 대신.

### render_corner.py — f2b3 남서 구석 4~6 장면 (PC, matplotlib)
- `f2b3_lviz.npz` 에서 +27 · 30 · 33 · 36 · 42 · 48 s 장면: office_v3 배경 · 로컬 치명 칸(odom → map 변환) · 라이다 점 · 차체 사각형(앞 0.262 · 뒤 0.248 · 옆 0.165) · 경로. 그림 [`2026-10-02_f2b3_corner.png`](../04_navigation/figures/2026-10-02_f2b3_corner.png). §7 표의 거리 수치는 같은 npz 로 계산 — **출력 원문 없음**.

### render_box.py · box_fov.py — f2b4 상자 (PC)
- `render_box.py`: `f2b4_lviz` · `f2b4_gviz` 로 6 장면(로컬 · nvblox · 라이다 · 전역) → [`2026-10-02_f2b4_box.png`](../04_navigation/figures/2026-10-02_f2b4_box.png). §9 의 '≥ 99 칸 0' 수치는 출력 원문 없음.
- `box_fov.py`: 매 표본(1 s) 카메라 위치 = 로버 자세 + (0.234, 0.044), 방향 = 로버 yaw − 0.04677. 상자 모서리 3 × 4 = 12 점(x 1.15~1.25, y −0.17~0)까지 거리 · 시선각, |각| ≤ 43.5° 면 화각 안. 열: 화각 안 점 수 · 최소 거리 · 최소 각 · 화각 안 ∧ 0.45~1.2 m · 화각 안 ∧ ≤ 1.4 m. 출력 [`box_fov.txt`](../debug_log/2026-10-02/outputs/box_fov.txt)(+40 s 부터).
- 한계: 상자 위치는 10-01 §8.36 값(10-02 에 다시 재지 않음). 수직 화각 · 가림은 안 봄.

## 10. 용어
- **위치 추정 점프**: slam_toolbox 위치 추정 모드가 스캔을 저장 지도의 다른 자리에 맞춰 map→odom 을 한 번에 크게 바꾸는 것. Nav2 의 map 좌표(경로 · 목표 판정)가 통째로 옮겨지고, odom 좌표(로컬 코스트맵 · MPPI)는 그대로라 둘이 어긋난다.
- **탐색 창(`loop_search_space_dimension`)**: 스캔 정합(루프 · 재정합)에서 후보 위치를 찾는 정사각 범위의 한 변(m). 3.0 = ±1.5 m. 넓으면 큰 실제 오차를 회복할 수 있지만 반복 구조 · 빈 곳에서 틀린 자리에 맞출 여지가 커진다. 정밀도와는 무관.
- **이어 그리기(continue mapping)**: 저장된 포즈 그래프를 불러 그 위에 새 스캔을 더하는 매핑. 루프 클로저를 켜면 옛 노드까지 다시 최적화돼 옛 지도가 움직일 수 있다.
- **스캔-지도 잔차**: 기록된 자세로 라이다 끝점을 저장 지도에 놓았을 때 가장 가까운 점유 칸까지 거리의 RMS. 자세가 맞으면 작다(0.03~0.06 m). 지도에 없는 물체가 많아도 커지므로 자세 오차와 섞인다.
- **`/map_nav`(경로 계획용 격자)**: 10-01 §8.33 부터 전역 정적 층이 읽는 저장 지도 사본(map_server). 위치 추정이 쓰는 포즈 그래프와 분리돼 있어, 여기만 손으로 지워도 위치 추정에는 영향이 없다.
- **G2 · P 게이트**: 러너 출발 전 검사. G2 = 출발 자세에서 차체 외곽 ↔ 로컬 치명 칸 · 라이다 점 여유 ≥ 0.10 m, P = 정지 10 s CPU 평균 ≤ 60 %.
- **SUCCEEDED_XY(`f` 모드, 10-07)**: 러너가 map 위치만 0.15 m 안이면 목표를 끝내고 방향 맞춤 회전을 요구하지 않는 모드.
