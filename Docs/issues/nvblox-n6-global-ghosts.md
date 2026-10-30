# Phase N 후반 — nvblox 를 기본 구성으로(N6-0) · 전역 코스트맵까지(N6-1) · 유령 셀 · N6 최종 판정(N6-2)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **완료(N6 판정 통과, 09-23) · 유령 셀은 우회 → 이후 다시 열림** — 기능 기준(중단 0 · 여유 · 기억)은 통과, CPU 는 STVL 과 동등(절감 기대 미달). 전역 층이 낸 '유령 셀' 은 통합 거리 1.4 m · 슬라이스 최소 높이 0.06 으로 막고, 원인 물체(반사성 바닥 테이프)는 테이프를 덮어서 확정. 기전(IR 반사)은 추정 | 09-22 §4 ~ §5.5, 09-23 §0 ~ §4 · §6 ~ §10 · §12 ~ §14 (이 카드), 이후 10-13 · 10-14 · 10-22 | [09-22 §5.1](../debug_log/2026-09-22/SUMMARY.md)(n61a 게이트 '목표 풋프린트 ↔ LETHAL 0.000 m') | `ros2_ws/src/rover_navigation/launch/navigation.launch.py`(`camera_layer` · `camera_pointcloud` 인자, 커밋 `55ebe7e3` · `384c1eb6` · `45ab8d89`) · `launch/nvblox.launch.py` · `scripts/nvblox_up.sh`(래퍼, `55ebe7e3` → `74b3ca37`) · `config/nav2_params.yaml`(전역 `nvblox_layer` 블록, `384c1eb6`) · `config/nvblox_local.yaml`(통합 1.4 · 슬라이스 0.06, `f325e8f7`) · `rover_bringup/scripts/depth_relay.py`(lazy, `384c1eb6`) · 게이트 `job505_modeN_gate.sh`(M · N, 09-23) · 러너 `job125_avoid3.py`(`REFIX_MAX` 0.06) · `Docs/04_navigation/TEST_COURSE_AND_GATES.md` v2.1 → v2.2 | [Phase N 전반 N0~N4](nvblox-migration-n0-n4.md)(앞 단계 — 컨테이너 · 로컬 층 · 절단 · 감쇠 · N4 A/B) · [nvblox 층 round→floor](nvblox-layer-round-floor.md) · [깊이 점군 아티팩트 · depth_relay](depth-relay-artifacts.md)(lazy 로 경로 밖) · [회피 주행 계측](avoid-run-metrics.md)(재고정 · 조향 지표 · 계측 부하) · [Jetson Wi-Fi](jetson-wifi-link.md)(n62b CPU 오염) · [F0 회전 옆 미끄러짐](f0-rotation-side-slip.md)(09-23 §12.1) |

**한 줄**: 09-22 오후, 로컬 층으로 채택한 nvblox 를 (1) launch 인자 하나로 기본 구성에 넣고(N6-0, 검증 V1~V5), (2) 전역 코스트맵의 카메라 층까지 nvblox 로 바꿔 STVL · `depth_relay` 를 경로에서 뺐다(N6-1). 그러자 **전역 층이 카메라 지평선 안의 바닥 깊이 잡음을 치명 셀로 올려 목표 자리를 막았고**('유령 셀'), 통합 거리 2.0 → 1.6(실패: 유령이 옮겨옴) → 슬라이스 최소 높이 0.08(11 → 1 셀) → 0.12(상자까지 잘림, 계산 착오) → **통합 1.4 m · 최소 높이 0.06** 으로 정리해 주행 3/3 성공. 09-23 N6-2 에서 게이트 M(목표 부근 근거 없는 치명 셀)이 같은 유령을 다시 잡았고, **초록 바닥 테이프를 덮자 0 셀** → 원인 물체 확정. CPU 는 릴레이 −15 %p 와 nvblox +18 %p 가 상쇄되어 STVL 과 같다(320~325 %) — 'CPU 절감' 은 채택 근거가 못 되고, 채택은 회피 여유 · 기억 · 3D/GPU 경로라는 기능 근거로 남았다.

---

## 1. 증상
- **N6-0 V2 불합격(09-22 §4.1)**: `navigation.launch.py` 를 끝내도 컨테이너 안 `nvblox_node` 가 남았다 — 1 차 12 s 뒤 1 개, 2 차 28 s 뒤 1 개 · 래퍼는 정리 로그 없이 사라짐([`j513_verify_run1.txt`](../debug_log/2026-09-22/outputs/j513_verify_run1.txt) · [`run2`](../debug_log/2026-09-22/outputs/j513_verify_run2.txt)).
- **N6-1 G3 첫 회차 출발 거부(09-22 §5.1)**: 러너 게이트 "목표 map (2.00, 0.01) | 풋프린트↔LETHAL 최소 **0.000 m** (셀 map 1.85, 0.12) | 목표 셀 비용 99"([`j507_n61a_gatefail.txt`](../debug_log/2026-09-22/outputs/j507_n61a_gatefail.txt)). 목표 부근엔 사람 · 물체가 없었다. 모드 S(STVL) 전역 코스트맵에는 그 셀이 없었다.
- **같은 자리 재발(09-23 §9)**: n62b 준비에서 목표 여유 0.191 m(< 0.20), 게이트 M "전역 LETHAL 1 셀, 라이다 근거 점 0 → 불합격", 클리어 + 20 s 뒤에도 같은 자리(1.57, −0.26)([`j510_prep_n62b.txt`](../debug_log/2026-09-23/outputs/j510_prep_n62b.txt)).
- **CPU 기준 미달**: N6-1 G3 주행 3 회 CPU 합 324 · 325 · 320 %(기준 < 320), N6-2 n62a 324 · n62c 321(09-22 §5.3, 09-23 §8 · §13).
- **점군을 끄자 계측이 멈춤(09-23 §6 · §7)**: prep 의 상자 게이트 줄이 "상자 x= y= … IndexError … 창 nan"([`j510_prep_0923b.txt`](../debug_log/2026-09-23/outputs/j510_prep_0923b.txt)), 러너 게이트 "창 −0.221 m"([`j507_n62a_gatefail.txt`](../debug_log/2026-09-23/outputs/j507_n62a_gatefail.txt)).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-22 §4 | N6-0 설계 · 기준 V1~V5 선언(실행 전) | — | `camera_layer:=nvblox\|stvl`(기본 nvblox) → `/tmp/nav2_params_active.yaml` 생성 + 래퍼 `nvblox_up.sh` | 커밋 `55ebe7e3` |
| 09-22 §4.1 1 차 | `run_j513_deploy.sh` → `job513_verify.sh` | V1 · V4 통과, **V2 12 s 뒤 노드 1 개 · V3 잔존(V2 의 고아)** | 래퍼가 신호를 못 받는다 | [`j513_verify_run1.txt`](../debug_log/2026-09-22/outputs/j513_verify_run1.txt) |
| 09-22 §4.1 진단 | `job514_trapdiag.sh` | launch 아래 래퍼 `SigIgn 0x7`(HUP · INT · QUIT 무시 상속), 수동 실행 `0x6`. TERM 직접 → launch 아래 4 s · 수동 3 s 에 노드 0 | ① `setsid nohup … &` 로 뜬 launch 의 자식은 INT 무시를 물려받아 1 차 INT 가 래퍼에 안 닿음(5 s 뒤 TERM 만) ② 검증 스크립트가 래퍼를 `-9` 로 죽임 | [`j514_trapdiag.txt`](../debug_log/2026-09-22/outputs/j514_trapdiag.txt) |
| 09-22 §4.1 2 차 | 래퍼에 부모 소멸 감시 · 검증에서 −9 제거 | V2 **28 s 뒤 노드 1, 래퍼 생존 no**(정리 로그 없음) | ③ launch 가 먼저 죽으면 래퍼 stdout 파이프가 끊겨 다음 `echo` 에서 SIGPIPE 로 래퍼가 죽음 | [`j513_verify_run2.txt`](../debug_log/2026-09-22/outputs/j513_verify_run2.txt) |
| 09-22 §4.1 3 차 | 기동 뒤 `exec >> …_up.log` · `trap '' PIPE` · 정리 함수는 kill 먼저 | **V1~V4 통과** — V1 J 15.1/9.5 Hz · 0.104 s, L 11 셀 · V2 **2 s** · V3 노드 0 · V4 `docker stop` 뒤 복구, 30 s 뒤 깊이 15.1 Hz | N6-0 기능 확인 | [`j513_verify_run3.txt`](../debug_log/2026-09-22/outputs/j513_verify_run3.txt) |
| 09-22 §4.2 | V5: prep(`run_mp9prep.sh`) 재기동 | 게이트 A~D(상자 1.145/−0.068, 창 0.330, 목표 여유 0.332, 12.20 V), nvblox PID 457141 → **465625**, J 15.1/9.6 Hz · L 12 셀 | V5 통과 — 절차 v2.0 §4-9 'prep 뒤 nvblox 재시작' 자동화 → v2.1 | [`j515_v5_prep.txt`](../debug_log/2026-09-22/outputs/j515_v5_prep.txt) · [`j516_v5chk.txt`](../debug_log/2026-09-22/outputs/j516_v5chk.txt) |
| 09-22 §4.2 | 래퍼 둘(`465497 484152`)로 보임 → `job517_wrapchk.sh` | 매 루프 `$(nv_pids)` 의 수명 0 s 서브셸 | 결함 아님. 그래도 **자기 PID 만** 감시 · 정리하도록 강화 → 4 차 V1~V4 재통과(V2 3 s). V5 는 재실행 안 함(정직 기록) | `j517` 출력 원문 없음 · [`j513_verify4.txt`](../debug_log/2026-09-22/outputs/j513_verify4.txt), 커밋 `74b3ca37` |
| 09-22 §5 | N6-1 설계 · 기준 G1~G4 선언(실행 전) | 목표 = STVL · 릴레이를 경로에서 빼 **CPU 합 < 320**, G2 '정지 합 S 대비 ≥ 25 %p 감소' | 전역 plugins 도 `camera_layer` 로 전환, `depth_relay` lazy | 커밋 `384c1eb6` |
| 09-22 §5.1 | 배포(`run_j519_deploy2.sh`) → G1 · G2(`run_j518.sh`) | 정지 CPU **N 212 % = S 212 %**. S 의 python3 19.7 % 가 N 에서 빠지고 nvblox 17.7 % 가 들어옴. 릴레이 구독자 N 0 / S 4. 전역 상자 N x 1.10~1.35 · y −0.35~+0.05(13 셀) vs S x 1.10~1.25 · y −0.15~+0.05(8), 통과 폭 N 0.35 / S 0.40(@1.20), 전역 LETHAL 근거 N 98 %(3 셀 없음) / S 100 % | G2 의 '≥ 25 %p 감소' 는 **정지에서 이미 0** — 판정은 G3 로 미룸. G1 앞면 동일 · 뒤 · 오른쪽은 절단 띠 | [`j520_n61_static.txt`](../debug_log/2026-09-22/outputs/j520_n61_static.txt) · [`j521_g1.txt`](../debug_log/2026-09-22/outputs/j521_g1.txt) · `grid_n61{N,S}{g,l}_costmap.json` |
| 09-22 §5.1 | **n61a 게이트 거부** → 탐침 `job522_goalprobe.py` | 목표 풋프린트 ↔ LETHAL 0.000 m. 목표 부근(base x 1.5~2.3, \|y\|<0.45) 라이다 점 0, 카메라 점 14(y −0.42~−0.05), 슬라이스 ≤0 셀 7 개(예: (1.88,+0.12) (1.93,+0.12)) → 전역 LETHAL 6 | **추정**: 통합 거리 2.0 m 끝자락(1.9~2.2 m)의 희소 깊이 잡음 → 통합 거리 2.0 → 1.6 | [`j507_n61a_gatefail.txt`](../debug_log/2026-09-22/outputs/j507_n61a_gatefail.txt) · 탐침 1 차 원문 없음(SUMMARY 수치만) |
| 09-22 §5.2 | 통합 1.6 재배포 · 재탐침(`run_j523.sh`) | 실효값 1.6 확인. 유령 **11 셀로 1.5~1.8 m 로 옮겨옴**, 전역 LETHAL 10 · 로컬 2. 그 구역 카메라 점 5 개 전부 **z 0.03~0.11**, 라이다 0. 게이트 L 상자 셀 18(평소 10~12) | **거리 한계 가설 기각**(❌ 정정) → '바닥 잡음' 가설: 최소 높이 0.03 은 바닥(−0.026) 바로 위 | [`j523_intdist.txt`](../debug_log/2026-09-22/outputs/j523_intdist.txt) |
| 09-22 §5.2 | 최소 높이 0.03 → **0.08** | 실효 0.08. 유령 11 → **1**((1.72, −0.28)), 전역 LETHAL 10 → 1, 로컬 0, L 18 → 11. 남은 1 셀에 카메라 점 6 개 **z 0.09~0.11** | 바닥 잡음 가설 채택. 남은 1 셀은 '높이 ≈10 cm 의 실제 무언가' | [`j523b_minheight.txt`](../debug_log/2026-09-22/outputs/j523b_minheight.txt)(탐침은 TF 예외로 실패) · [`j524_probe.txt`](../debug_log/2026-09-22/outputs/j524_probe.txt)(실제 0.08 탐침 값) |
| 09-22 §5.2 | 1 분 뒤 재탐침 | 유령 0, 목표 여유 **0.316**(최근접 = 우측 벽 (1.80, −0.48)) | '광선 소거로 지워진 잔상' → G3 진입 | [`j524b_probe.txt`](../debug_log/2026-09-22/outputs/j524b_probe.txt) |
| 09-22 §5.2 | **n61a 2 차 시도도 거부** | 목표 여유 다시 0.122(셀 (1.70, −0.28)) | 간헐적으로 관측되는 실제 낮은 물체(높이 < 라이다 0.185) | [`j507_n61a_gatefail2.txt`](../debug_log/2026-09-22/outputs/j507_n61a_gatefail2.txt) |
| 09-22 §5.2 | 컬러 스냅샷(`job322_snap.py`) | 의심 지점 = 통로 우측 바닥 **초록 테이프 띠**, 그 너머 유리 벽. 사람 · 물체 없음 | **추정**: 테이프의 IR 반사율 차(또는 유리 반사) → 스테레오 깊이가 간헐적으로 z 0.09~0.11 의 가짜 점 | [`snap_n61a_goalarea.jpg`](../debug_log/2026-09-22/outputs/snap_n61a_goalarea.jpg) |
| 09-22 §5.2 | 최소 높이 0.08 → **0.12**(첫 시도는 `run_j523.sh` 편집 실수로 실행 안 됨) | 0.12 에서 유령 0 · 목표 여유 0.316 이지만 **게이트 L 상자 셀 0/프레임 → 불합격** | ❌ 계산 착오: 상자 윗면은 base_link 기준 **z 0.088**(높이 0.114 − 원점 0.026) — 0.12 는 상자를 통째로 잘랐다(실수 ②) | [`j525_minh12.txt`](../debug_log/2026-09-22/outputs/j525_minh12.txt)(구문 오류 + 0.08 상태 재탐침) · [`j525b_minh12.txt`](../debug_log/2026-09-22/outputs/j525b_minh12.txt) |
| 09-22 §5.2 | **통합 1.4 · 최소 높이 0.06**(STVL `min_obstacle_height` 와 같음), 대표 높이 0.10 | 30 s 간격 2 회: 유령 0, L 10 셀, J · K 통과, 목표 여유 0.316 / 0.319 | 높이로는 상자(윗면 0.088)와 테이프(0.09~0.11)를 못 가르니 **거리로 가른다**. 채택 yaml 최종 | [`j527_int14.txt`](../debug_log/2026-09-22/outputs/j527_int14.txt), 커밋 `f325e8f7` |
| 09-22 §5.3 | G3 주행 n61a(15:55) · n61b(16:10) · n61c(16:26) | 3/3 성공, 중단 0 · 미달 0. 코스트맵 상자 여유 15.8 · 19.2 · 13.9 cm, ③ 로컬 · 전역 99~100. **CPU 324 · 325 · 320**, 릴레이 19 → 4.5 %, nvblox 17.8~18.1, bag 기록기 27.0~27.4 %. GPU 2.5~3.5 %, 6.69~6.79 W | 기능 통과. CPU 는 '문자상 1~5 %p 미달, 계측 보정 시 S 와 동등'. n61b 준비에서 상자 왼쪽 가장자리가 ≈4~5 cm 안쪽(슬라이스 0.06 이 상자 위 3.8 cm 만 봄) | `j507_n61{a,b,c}_drive.txt` · `j509_n61{a,b,c}_analysis.txt` · `n61{a,b,c}.csv` · `top_` · `tegra_` · [`j510_prep_n61b.txt`](../debug_log/2026-09-22/outputs/j510_prep_n61b.txt) · bag `2026-09-22/bags/bag_n61{a,b,c}.tgz`(로컬) |
| 09-22 §5.4 | G3 판정 | 기능 통과 · CPU '경계' · n61c 조향 반전 6.29 /m 은 범위 밖(원인 미조사) | 점군 끄기 · 릴레이 정지로 <320 '여유 있게 만족할 것으로 **예상**'(❌ 09-23 에 −6 %p 만, 그나마 적용 불가) | 09-22 §5.4 |
| 09-22 §5.5 | 조향 부호반전 지표 재검토 | 문턱 0.01 의 반전은 대부분 0.01~0.03 rad/s 영교차 | 지표 결함 → [회피 주행 계측 카드 §7.2](avoid-run-metrics.md) | `n4*.csv` · `n61*.csv` |
| 09-23 §0 · §2 | **실제 재부팅 뒤 복구 B1** | 스크립트 재전송 → `docker start` → prep 한 번으로 A~D(상자 1.147/−0.051, 창 0.235, 목표 여유 0.324, 12.35 V) · **J · K · L · M 통과**(15.1/9.5 Hz, L 10, M 0). N 은 파서 결함으로 판정 불가 | B1 통과 — 재부팅 뒤 손작업은 보드 리셋뿐 | [`j510_prep_a.txt`](../debug_log/2026-09-23/outputs/j510_prep_a.txt) · [`j531_b1_c1.txt`](../debug_log/2026-09-23/outputs/j531_b1_c1.txt) |
| 09-23 §1 | N6-2 기준 선언(R1 · C1 · C2 · M · N · H1 · B1) | — | — | 09-23 §1 |
| 09-23 §3 | C1 점군 끄기 정지 A/B(`job531_pcl_toggle.sh`) | 1 · 2 차는 파라미터 이름 오류(`pointcloud.enable` 미선언). 3 차 `pointcloud__neon_.enable false`: 점군 · 릴레이 출력 0 Hz, 깊이 15 Hz · nvblox 콜백 15.1 Hz 유지. realsense **15.3 → 13.9 %**, depth_relay **3.7 → 0**, 합 **201 → 195 %**(−6) | 기대 −10 %p 보다 작음. C1 선언 기준(realsense ≤ 10 %)은 **불합격**인데 SUMMARY 는 '기대보다 작다' 로만 씀 | [`j531c_pcl.txt`](../debug_log/2026-09-23/outputs/j531c_pcl.txt) · [`j531b_pcl.txt`](../debug_log/2026-09-23/outputs/j531b_pcl.txt) · [`j531_b1_c1.txt`](../debug_log/2026-09-23/outputs/j531_b1_c1.txt) |
| 09-23 §4 | H1 슬라이스 최소 높이 0.03 vs 0.06(`job532_slice_h.sh`, 통합 1.4 고정) | 0.06: L 10 · 11 · 11, 유령 0/0 × 3. 0.03: L 11 · 10 · 10, 슬라이스 ≤0 / 전역 LETHAL 0/2 · 1/3 · 1/3 | **0.06 유지**(H1 불합격). 09-22 의 '0.03 복귀 가능' 추정 기각. 가장자리 차는 job315 호출 오류로 못 잼 | [`j532_slice_h.txt`](../debug_log/2026-09-23/outputs/j532_slice_h.txt) |
| 09-23 §6 | IP 복귀 뒤 prep · 게이트(점군 끔 상태) | J · K · L · M · N 통과, 점군 0 Hz. prep 상자 줄 "x= y=" 빔 | 'job248 파싱 실패, **일시적으로 추정**'(❌ §7 에서 정정) | [`j510_prep_0923b.txt`](../debug_log/2026-09-23/outputs/j510_prep_0923b.txt) · [`j510_prep_0923c.txt`](../debug_log/2026-09-23/outputs/j510_prep_0923c.txt) |
| 09-23 §7 | n62a 출발 거부 | 감사 불완전 → 창 −0.221 | **원인 = 점군 끄기**: 게이트 D · E · F 와 러너 상자 모델이 점군을 입력으로 씀 → `camera_pointcloud:=keep\|off`(기본 keep), 점군 · 릴레이 · 기록기는 '계측 부하' 로 분류 | [`j507_n62a_gatefail.txt`](../debug_log/2026-09-23/outputs/j507_n62a_gatefail.txt) · [`j537_pclkeep.txt`](../debug_log/2026-09-23/outputs/j537_pclkeep.txt), 커밋 `45ab8d89` |
| 09-23 §8 | n62a(10:35) | 성공 31.7 s · 2.18 m, 여유 16.8, 러너 ① 14.0(유효 — R1), CPU **324**, '계측 제외' ≈ 258(S 같은 방식 ≈ 254) | 스택 CPU 는 S 와 +4 %p 안 | `j507_n62a_drive.txt` · `j509_n62a_analysis.txt` · `n62a.csv` · `n62a_refix.csv` · [`meta_n62a.txt`](../debug_log/2026-09-23/outputs/meta_n62a.txt) |
| 09-23 §9 | n62b 준비 — **게이트 M 이 유령 셀을 잡음** | 목표 여유 0.191, M: 전역 LETHAL 1 (1.57, −0.26), 라이다 0. 클리어 + 20 s 뒤 같은 자리 | 자리 = 우측 초록 테이프 점선. 1.57 m(카메라 기준 1.34 m)라 통합 한계 1.4 **안** — 09-22 의 '거리로 가른다' 가 이 배치에선 안 통함 | [`j510_prep_n62b.txt`](../debug_log/2026-09-23/outputs/j510_prep_n62b.txt) · [`snap_n62b.jpg`](../debug_log/2026-09-23/outputs/snap_n62b.jpg) |
| 09-23 §10 | 테이프 제거 검증(사용자 결정: 통제 벤치마크는 테이프를 치우고, 테이프 사례는 강건성 시험 R1 로 등록) | 1 차(왼쪽 곡선 테이프만): (1.53, −0.27) 3 표본 지속. 2 차(오른쪽 점선도 가림): 슬라이스 ≤0 **0** · 전역 LETHAL **0**(2 표본), J~N 통과 | **테이프가 원인 물체로 확정**(덮기 전 지속 1 셀 → 덮은 뒤 0). IR 반사 기전은 여전히 추정 | [`j538_tape_off.txt`](../debug_log/2026-09-23/outputs/j538_tape_off.txt) · [`snap_n62b2.jpg`](../debug_log/2026-09-23/outputs/snap_n62b2.jpg) · [`snap_n62b3.jpg`](../debug_log/2026-09-23/outputs/snap_n62b3.jpg) |
| 09-23 §12 | n62b(12:24, Wi-Fi 끊김 2 회 뒤) | 성공 33.2 s, 미달 1, 여유 19.0, ① 16.9. **CPU 422**(ekf 37.6 · slam 34.8 · bt 25.0 · planner 19.7 — n62a 의 2~3 배) | CPU 무효(Wi-Fi 재연결 뒤 DDS 부하 **추정**) — 안전 지표는 유효. 운영 규칙 13 후보 | `j507_n62b_drive.txt` · `top_n62b.log` · [Wi-Fi 카드](jetson-wifi-link.md) |
| 09-23 §12.1 | n62b 끝의 좌회전 미끄러짐 | 끝 −2~−1 s: 휠 +22.8° · EKF +8.7° · 라이다 +8.5° | → [F0 회전 옆 미끄러짐](f0-rotation-side-slip.md) | `j545_slipyaw.txt` · `j546_scanrot.txt` |
| 09-23 §13 | n62c(12:44, 스택 재기동 직후) + **N6 최종 판정** | 성공 32.3 s, 미달 1, 여유 15.1, ① 13.8, CPU **321**(ekf 11.6 · slam 11.6 — n62a 와 같음) | 재기동으로 부하 해소 → n62b 추정 뒷받침. N6: 기능 통과 · **CPU 는 STVL 과 동등(절감 기대 미달)** | `j507_n62c_drive.txt` · `j509_n62c_analysis.txt` · [`j510_prep_n62c.txt`](../debug_log/2026-09-23/outputs/j510_prep_n62c.txt) · [`j510_prep_n62c2.txt`](../debug_log/2026-09-23/outputs/j510_prep_n62c2.txt) |
| 09-23 §14 | 마감 | 절차 v2.2(게이트 M · N, 규칙 13~15), 마감 보고 `Docs/05_nvblox/figures/2026-09-23_phase_n_close.html` | Phase N 종료 → F0 | — |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| (N6-0) 래퍼가 launch 종료 신호를 못 받는다 | `job514`: launch 아래 래퍼의 `/proc/<pid>/status` SigIgn · TERM/INT 직접 송신 · 수동 실행 대조 | launch 아래 SigIgn 0x7, 수동 0x6. TERM 은 둘 다 3~4 s 안에 정리 | **지지**(원인 ①) — 무시된 채 시작된 신호는 비대화 bash 가 trap 할 수 없다 |
| (N6-0) 래퍼가 정리 전에 스스로 죽는다 | 2 차 V2 의 '래퍼 생존 no · 정리 로그 없음' | 3 차에 stdout 을 파일로 돌리고 PIPE 무시 → V2 2 s | **지지**(원인 ③, SIGPIPE). 직접 관찰(strace 등)은 없음 — 수정 뒤 증상 소멸로 판정 |
| (G3) 유령 = 통합 거리 2.0 m 끝자락의 원거리 희소 잡음 | 2.0 → 1.6 재탐침 | 유령이 1.5~1.8 m 로 옮겨오고 11 셀로 늘어남 | **기각** |
| 유령 = 바닥(첫 복셀 층 z 0~0.05) 깊이 잡음 | 최소 높이 0.03 → 0.08 | 11 → 1 셀, 상자 가짜 표면(L 18 → 11)도 사라짐 | **지지**(09-22 의 대부분). 09-23 H1(0.03 에서 통합 1.4 안에서도 2~3 셀 재발)도 같은 방향 |
| 남은 1 셀 = 높이 ≈10 cm 의 실제 물체(관찰자 발?) | 1 분 뒤 재탐침 · 컬러 스냅샷 | 사라졌다 다시 나타남(0.122 → 0.316 → 0.122), 스냅샷엔 테이프만 | '사람 · 물체' **기각**, 테이프 **의심** |
| 그 자리 유령의 원인 물체 = 초록 바닥 테이프 | 09-23 §10: 테이프를 덮기 전/후 같은 배치 · 같은 게이트 | 지속 1 셀 → 0 셀(2 표본). 왼쪽 테이프만 치웠을 땐 오른쪽 점선 자리에 지속 | **지지**(원인 물체 확정) |
| 기전 = 테이프 표면의 IR 반사율 차이로 스테레오 깊이가 튐 | (판별 안 함) — IR 영상 · 깊이 신뢰도 · 다른 재질 비교 없음 | — | **미확인**(추정) |
| 슬라이스 최소 높이 0.12 로 테이프(0.09~0.11)를 버릴 수 있다 | 0.12 적용 · 게이트 L | 상자 셀 0 — 상자 윗면 0.088 이 같이 잘림 | **기각**(높이로는 못 가름) |
| 통합 거리 1.4 m 가 테이프 유령을 막는다 | 09-22 2 회 탐침 · G3 3 회 | 09-22 배치에선 유령 0. **09-23 n62b 에선 1.57 m(카메라 1.34 m) 자리에 다시 나옴** | **부분 기각** — 거리 필터는 그날 유령이 1.5 m 밖에 떨어졌기 때문에 통했던 것(테이프가 1.4 m 안까지 이어짐은 사진 근거, 범위 실측 없음) |
| (N6-1) 전역까지 nvblox 로 바꾸면 CPU 합 < 320 | G2 정지 · G3 · C2 주행 | 정지 212 = 212, 주행 320~325 | **기각** — 릴레이 −15, nvblox +18 |
| 점군 생성을 끄면 <320 여유 있게 | C1 정지 A/B | −6 %p(201 → 195), realsense 15.3 → 13.9 | **기각**(크기), 그리고 계측이 점군을 써서 **적용 불가** |
| 모드 N 은 점군 소비자가 없다(09-22 §5.3 · §5.4) | 09-23 §7 n62a 거부 | 게이트 D · E · F(job248 · job315 · job440) · 러너 job125 가 `/camera/camera/depth/color/points` 사용 | **기각**(스택 입력이 아니라 계측 입력) |
| 슬라이스 0.03 으로 되돌려도 통합 1.4 안에서는 유령이 없다(09-22 §5.4 추정) | H1 정지 3 표본씩 | 0.03 에서 목표 부근 전역 LETHAL 2~3 | **기각** |
| n62b CPU 422 = Wi-Fi 재연결 뒤 DDS 재발견 부하 | n62c 를 스택 재기동 직후에 | ekf · slam 11.6(n62a 와 같음), 합 321 | **지지(간접)** — 재기동으로 해소. 재연결 → DDS 부하의 직접 계측(패킷 · 재전송) 없음 |

## 4. 조치와 효과
### 4.1 N6-0 — bringup 통합(지금 저장소 코드 기준)
- `navigation.launch.py` 의 OpaqueFunction 이 원본 `nav2_params.yaml` 을 읽어 로컬(그리고 N6-1 뒤 전역) `plugins` 줄만 바꾼 `/tmp/nav2_params_active.yaml` 을 쓴다(머리줄 `# 자동 생성(navigation.launch.py, camera_layer=…)`). 원본은 그대로 — 예전의 '설치 YAML 을 sed 로 고치는 방식'(job488 의 N3 판)은 폐기.
- `nvblox` 면 `nvblox.launch.py` → `scripts/nvblox_up.sh <yaml> [로그]`: (1) 컨테이너가 Exited 면 `docker start`(없으면 exit 3 — 재생성은 `2026-09-21/jobs/job472_container.sh`) (2) DDS 프로파일 · yaml 을 `/tmp` 로 복사(`/tmp/nvblox_active.yaml`) (3) 남은 `nvblox_node` 정리 (4) `docker exec -d` 로 기동 → **자기가 띄운 PID 만** 2 s 마다 감시 (5) TERM · INT · HUP 또는 부모 PPID = 1(launch 소멸)이면 컨테이너 안 노드를 INT → 3 s → KILL. `docker exec` 는 신호를 넘기지 않으므로 직접 죽인다. 기동 뒤 출력은 `/tmp/nvblox_node_up.log`, `trap '' PIPE`.
- 게이트 J 를 러너 `job254_s4run.sh` 에도 넣음(활성 yaml 이 nvblox 층일 때만). 메타 `job453_runmeta.sh` 에 활성 yaml · `nvblox_active.yaml` · `nvblox_local.yaml` sha256. prep 정리 목록(`job240_clean.sh` PATS)에 `nvblox_up.sh`.
- 효과: prep 한 번으로 모드 N(V5), 재부팅 뒤에도 보드 리셋 외 손작업 없음(09-23 B1). 한계: 래퍼는 컨테이너가 **없으면** 복구 못 함(이미지 재생성은 사람).

### 4.2 N6-1 — 전역 코스트맵 이전 · 유령 셀 대응
- 전역 plugins: nvblox 모드 `["static_layer", "nvblox_layer", "obstacle_layer", "inflation_layer"]` / stvl 모드는 원래 줄. 슬라이스는 odom 프레임이고 전역은 map → 층 플러그인이 TF 로 변환(09-21 §10.4 코드 확인). nvblox 는 `map_clearing_radius_m 3.0` 안만 채우고 나머지는 static(SLAM 지도) + 라이다가 맡는다.
- `depth_relay.py` lazy(구독자 0 이면 콜백 첫 줄에서 return) → [깊이 점군 카드](depth-relay-artifacts.md) '이후'.
- nvblox yaml 의 변경 경로와 각 단계 측정(09-22 §5.2, 같은 배치 상자 1.145/−0.068):

| 판 | 통합 거리 | 슬라이스 최소 / 대표 / 최대 | 목표 부근 슬라이스 ≤0 · 전역 LETHAL | 게이트 L 상자 셀 | 목표 여유 | 판정 | 데이터 |
|---|---|---|---|---|---|---|---|
| N0 · N4 판 | 2.0 | 0.03 / 0.10 / 0.30 | 7 · 6 | 10~12 | 0.000 | 유령 | `j507_n61a_gatefail.txt` |
| 1 | 1.6 | 0.03 | 11 · 10(로컬 2) | **18** | (job377 오류) | 유령이 앞으로 옴 | `j523_intdist.txt` |
| 2 | 1.6 | 0.08 | 1 · 1 → 1 분 뒤 0 · 0 → 다시 0.122 | 11 → 10 | 0.122 → 0.316 → 0.122 | 테이프 1 셀 간헐 | `j524_probe.txt` · `j524b_probe.txt` · `j507_n61a_gatefail2.txt` · `j525_minh12.txt` |
| 3 | 1.6 | 0.12 / 0.15 / 0.30 | 0 · 0 | **0** | 0.316 | 상자까지 잘림 | `j525b_minh12.txt` |
| **4(채택)** | **1.4** | **0.06 / 0.10 / 0.30** | 0 · 0(2 회) | 10 | 0.316 / 0.319 | G3 진입 | `j527_int14.txt` |

  (j525b · j527 의 '실효값' 줄은 sed 따옴표 오류로 비었다 — 실효값은 `job526_parmchk.sh` 로 따로 봤다고 SUMMARY 에 있으나 그 출력은 남지 않음. 다만 n61a 메타의 `nvblox_active.yaml` sha256 앞 12 자리 `f98fc6bf11d1` 이 커밋 `f325e8f7`(1.4 · 0.06) 판과 일치 — 주행에 쓴 값은 확인됨, 이번 정리에서 계산.)
- 효과(G3, 09-22 §5.3): 3/3 성공, 여유 13.9~19.2(평균 16.3, N4 12.3~14.6 · S 9.3~11.7 보다 큼 — 전역 코스트맵에 상자 + 절단 띠가 들어가 NavFn 원경로 자체가 넓어짐, 경로 2.18~2.26 m), 기억 3/3.
- 대가: (1) 슬라이스 0.06 은 상자(윗면 0.088)의 위 3.8 cm 만 보아 코스트맵 상자 왼쪽(통과 측)이 ≈4~5 cm 안쪽(게이트 F 최대 y −0.027 vs N4 · S +0.020~+0.025). (2) 10 cm 이하 바닥 물체 · 1.4 m 밖 물체는 카메라 층이 못 봄(라이다 0.185 도 못 보는 높이). (3) STVL 슬라이스 상한 0.40 보다 낮은 0.30(가구 윗부분) — 0.30 → 0.40 A/B 는 미실행.

### 4.3 N6-2 — 판정 전 정리
- 러너 재고정 `REFIX_MAX` 0.30 → 0.06(R1 통과) → [회피 주행 계측 카드 §7.2](avoid-run-metrics.md).
- 게이트 M · N 추가(`job505_modeN_gate.sh` 09-23 판, 절차 v2.2). M 이 n62b 에서 실제로 유령을 잡음(09-22 에는 러너의 목표 여유 게이트가 우연히 잡던 것).
- 점군: C1 은 −6 %p 였고, 계측이 점군을 쓰므로 `camera_pointcloud:=keep`(기본) — `off` 는 계측 없는 운용에서만. 지금 코드: `layer == 'stvl' or pcl == 'off'` 일 때만 15 s 뒤 `ros2 param set /camera/camera pointcloud__neon_.enable …`(nvblox + off → false, 그 밖 → true), nvblox + keep 은 아무것도 안 함.
- 슬라이스 최소 높이: H1 → 0.06 유지.
- 운영 규칙(절차 v2.2): 13 Wi-Fi 재연결 뒤 스택 재기동, 14 점군 유지, 15 러너 재고정 0.06.

### 4.4 N6 최종 판정과 CPU 회계 (09-23 §13, 유효 회차 n61a~c · n62a · n62c 5 회)
| 기준(BASELINE §4 + §5 선언) | 결과 | 판정 |
|---|---|---|
| 중단 0 · 미달 ≤ 1 | 5/5 성공, 미달 0 · 0 · 0 · 0 · 1 | 통과 |
| 코스트맵 상자 여유 ≥ 8(평균 ≥ 11) | 13.9~19.2(기준선 8.4~12.9) | 통과 |
| ①·④ 동등 이상 | ① 13.8 · 14.0(러너 수정 뒤 유효), ④ 0 | 통과 |
| ③ 로컬 · 전역 기억 | 5/5 | 통과 |
| GPU · 전력 · 온도 | GPU 2.5~3.5 %, 6.7~6.8 W, tj 50 °C | 통과 |
| **CPU 합 < 320** | 320 · 321 · 324 · 324 · 325 | **문자상 1~5 %p 미달** |
| 기대 '릴레이 + STVL 분 ≥ 30 %p 감소'(G2 는 ≥ 25) | 릴레이 −15 · nvblox +18 → 스택 순증 ≈ +3~6 %p | **미달성** |

- CPU 를 나눠 보면(같은 표의 top 값): S 315~318 → N4(로컬만 nvblox) 330~337 → N6-1 · N6-2 320~325. '계측 제외'(bag 기록기 · 러너 · 릴레이): n62a ≈ 258 vs S ≈ 254. 모드 N bag 은 슬라이스 · 점유 · 깊이를 더 담아 기록기가 27 %(S 21~24).
- **정직한 결론(09-23 §13 그대로)**: nvblox 이전은 CPU 를 줄이지 못했다(동등). 얻은 것 = ① 회피 여유 증가 ② 표면 뒤 기억 · 물리에 가까운 상자 모양 ③ 3D 지도 · GPU 경로 ④ 근거리 사각(0.45 m) 제거(정지 게이트 기준). 잃은 것 = ⑤ 반사 바닥 표시에 대한 유령 셀 민감도(강건성 시험 R1) ⑥ 컨테이너 · 포크 유지 비용. 이 결론이 [`PHASE_N_RESULTS.md`](../05_nvblox/PHASE_N_RESULTS.md) N6-2 행 · CLAUDE.md §6 '상태' 의 '채택 근거는 회피 여유 · 기억 · 3D/GPU 경로' 다.

## 5. 내 실수
### 실수 ① 유령 셀을 '통합 거리 끝자락의 원거리 잡음' 으로 읽고, 정지 검증 출력에 이미 있던 신호를 놓침 (09-22 §5.1 → §5.2)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | N6-1 정지 검증(G1 · G2, `run_j518.sh` → `job518_g1g2.sh`) 뒤 G3 첫 주행 n61a |
| 본 것 | 정지 검증 출력 머리(prep 부분)에 이미 "목표 map (2.00, 0.00) … 풋프린트↔LETHAL 최소 **0.000 m** (셀 map 1.90, 0.12) · 목표 셀 비용 99"([`j520_n61_static.txt`](../debug_log/2026-09-22/outputs/j520_n61_static.txt) §3). 그러나 G1 · G2 기준엔 목표 여유가 없어 지나쳤고, 러너 게이트가 n61a 에서 거부한 뒤에야 봄. 탐침: 라이다 0 · 카메라 14 점 · 슬라이스 ≤0 7 셀이 1.58~2.17 m 에 흩어짐 |
| 처음 추론 | 통합 거리 2.0 m 의 끝(1.9~2.2 m)에서 희소한 원거리 깊이 잡음이 한 복셀 표면으로 적분됐다 → 통합 거리 1.6 |
| 의심한 이유 | 1.6 에서 유령이 사라지지 않고 **1.5~1.8 m 로 따라왔다**(11 셀). '거리 끝자락' 이면 한계를 당기면 같이 물러나야 한다. 같은 구역 카메라 점 5 개가 전부 z 0.03~0.11(바닥 높이), 게이트 L 상자 셀이 10~12 → 18 로 늘어 상자 둘레에도 가짜 표면이 붙음 |
| 판별 시험 | 최소 높이 0.03 → 0.08(거리 1.6 고정) |
| 결론 | 11 → 1 셀, L 18 → 11 — **바닥 잡음**(첫 복셀 층 z 0~0.05). N0 의 0.03 은 정지 근거리(≤ 1.3 m) 측정만 통과한 값이었다(09-21 §9) |
| 다음에 알아보는 법 | ① 유령 위치가 필터 경계를 따라 움직이면 그 필터 축(거리)은 원인이 아니다 — 다른 축(높이)으로 같은 구역 점의 분포를 먼저 본다. ② prep 출력의 **목표 여유 줄**은 정지 검증 기준에 없어도 읽는다(0.000 은 그 자체로 이상) → 09-23 게이트 M 으로 명시화 |
| 데이터 | [`j520_n61_static.txt`](../debug_log/2026-09-22/outputs/j520_n61_static.txt) · [`j507_n61a_gatefail.txt`](../debug_log/2026-09-22/outputs/j507_n61a_gatefail.txt) · [`j523_intdist.txt`](../debug_log/2026-09-22/outputs/j523_intdist.txt) · [`j524_probe.txt`](../debug_log/2026-09-22/outputs/j524_probe.txt) · 도구 [`job522_goalprobe.py`](../debug_log/2026-09-22/jobs/job522_goalprobe.py). 첫 탐침(2.0 m) 원문은 없음(SUMMARY 수치만) |

### 실수 ② 슬라이스 최소 높이 0.12 — 상자 윗면 높이를 base_link 기준으로 바꾸지 않음 (09-22 §5.2)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 남은 테이프 유령(카메라 점 z 0.09~0.11)을 높이로 버리려 `esdf_slice_min_height` 0.08 → 0.12(대표 0.15) |
| 본 것 | 유령 0 · 목표 여유 0.316 인데 **게이트 L 상자 띠 셀 0/프레임 → 불합격**(2 회 모두) |
| 처음 추론 | (계획 단계) '상자 0.14 의 앞면 · 의자 다리는 유지' — 상자 높이를 0.14 로 기억하고, 바닥 기준 높이를 그대로 슬라이스 높이로 씀 |
| 의심한 이유 | 상자가 0.12 위로 나와 있다면 L 이 0 일 수 없다 |
| 판별 시험 | 상자 실측 높이 0.114 · base_link 원점 바닥 위 0.026 으로 다시 계산 |
| 결론 | 상자 윗면 = base_link z **0.088** → 0.12 는 상자를 통째로 잘랐다. 0.08(복셀 행 [0.05, 0.10))에서는 상자 윗부분과 테이프 유령(0.09~0.11)이 같은 행 — **높이로는 못 가른다** → 거리(1.4)로, 높이는 STVL 과 같은 0.06 |
| 다음에 알아보는 법 | 높이 문턱을 바꿀 땐 대상 물체 윗면을 **슬라이스 좌표(odom z = base_link 원점 기준)** 로 먼저 적고, 복셀 행 경계(0.05 단위)에 대입해 본다. 게이트 L 처럼 '보여야 할 것' 의 수를 같이 본다 |
| 데이터 | [`j525b_minh12.txt`](../debug_log/2026-09-22/outputs/j525b_minh12.txt) · 지금 `nvblox_local.yaml` 68 줄 주석 |

### 실수 ③ 배포 스크립트가 실행되지 않은 것을 모르고 0.08 상태를 다시 잼 (09-22 §5.2)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | `run_j523.sh` 로 0.12 yaml 배포 · 재기동 · 탐침, 30 s 뒤 2 차 탐침(`run_j524.sh`) |
| 본 것 | 출력 첫 줄 "`/tmp/run_j523.sh: line 8: unexpected EOF while looking for matching '"'`" 뒤에 2 차 탐침만 돌아 목표 여유 **0.122**, 슬라이스 ≤0 (1.72, −0.28) — 0.08 때와 같은 값 |
| 처음 추론 | (기록상) 0.12 로도 남는 것으로 보일 수 있었음 — SUMMARY 는 바로 '편집 실수로 실행되지 않아 0.08 로 재탐침한 것' 으로 정정 |
| 의심한 이유 | 출력 머리의 bash 구문 오류 · '설치 yaml 확인' 줄이 없음 |
| 판별 시험 | 고쳐서 다시 실행(`j525b`) — '설치 yaml 확인: 1' 이 찍히고 결과가 달라짐(L 0) |
| 결론 | 첫 시도는 무효. 저장된 `run_j523.sh` 는 고친 판(기본 확인 문자열이 `esdf_slice_min_height: 0.12`) |
| 다음에 알아보는 법 | 배포 러너는 '설치 yaml 확인' · '실효값' 줄이 찍혔는지부터 본다. 실효값 줄이 비면(`j525b` · `j527` 의 sed 따옴표 오류) 값이 바뀌었다고 쓰지 말고 메타 sha256 로 확인 |
| 데이터 | [`j525_minh12.txt`](../debug_log/2026-09-22/outputs/j525_minh12.txt) · [`run_j523.sh`](../debug_log/2026-09-22/jobs/run_j523.sh) |

### 실수 ④ '모드 N 에는 점군 소비자가 없다' — 계측 도구를 소비자로 세지 않음 (09-22 §5.3 · §5.4 → 09-23 §6 → §7)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | CPU 회수: 모드 N 에서 realsense 점군 생성을 끄고(`pointcloud__neon_.enable false`) launch 에 연동 |
| 본 것 | 09-23 §6 prep: "상자 x= y= | … IndexError … → | 창 nan"(두 번). §7 n62a 러너 게이트: "감사 출력 불완전 — 재시도 … 창 −0.221 m" |
| 처음 추론 | §6: 'job248 파싱 실패, **일시적으로 추정** — 러너가 출발 전 게이트 D 로 다시 검사' |
| 의심한 이유 | 같은 증상이 prep 두 번 · 러너에서 반복 — 일시적이면 반복되지 않는다. 점군을 끈 시점부터 시작 |
| 판별 시험 | 게이트 D · E · F(job248 · job315 · job440)와 러너 job125 의 구독 토픽 확인 → 모두 `/camera/camera/depth/color/points`. 점군을 다시 켜고(`j537_pclkeep.txt`) 게이트 J~N 통과 |
| 결론 | 점군은 스택 입력이 아니라 **계측 도구의 입력** — 시험 중엔 끌 수 없다. `camera_pointcloud:=keep\|off`(기본 keep). CPU 판정에 '계측 제외' 값을 함께 적는 규칙 |
| 다음에 알아보는 법 | 토픽을 끄기 전에 `ros2 topic info -v` 로 구독자를 세고, 지금 떠 있지 않은 **게이트 · 러너 스크립트의 구독 목록**(`grep -l <토픽> jobs/`)도 센다. 같은 '일시적' 실패가 두 번이면 일시적이 아니다 |
| 데이터 | [`j510_prep_0923b.txt`](../debug_log/2026-09-23/outputs/j510_prep_0923b.txt) · [`j510_prep_0923c.txt`](../debug_log/2026-09-23/outputs/j510_prep_0923c.txt) · [`j507_n62a_gatefail.txt`](../debug_log/2026-09-23/outputs/j507_n62a_gatefail.txt) · [`j537_pclkeep.txt`](../debug_log/2026-09-23/outputs/j537_pclkeep.txt) |

### 실수 ⑤ CPU 절감 기대를 nvblox 자신의 비용 없이 세움 (09-22 §5 → §5.1 → 09-23 §13)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | N6-1 목표 '릴레이 · STVL 을 빼 CPU 합 < 320 회수', G2 '정지 합 S 대비 ≥ 25 %p 감소', 판정표의 기대 '≥ 30 %p' |
| 본 것 | 정지 합 N 212 = S 212(§5.1). 주행 320~325 |
| 처음 추론 | 릴레이(≈19 %) + STVL 갱신분이 빠지면 25~30 %p 가 줄어든다 |
| 의심한 이유 | N4 에서 이미 nvblox 노드가 18~20 % 를 쓴다고 쟀다(09-22 §3.1) — 빠지는 것과 들어오는 것이 비슷한 크기. 또 lazy 릴레이도 수신 · 역직렬화로 3.7~4.7 % 가 남았다 |
| 판별 시험 | G2 정지 측정 · G3/C2 주행 top |
| 결론 | 릴레이 −15, nvblox +18 → 순증 +3~6 %p. 'CPU 절감' 은 채택 근거가 아니다(09-23 §13). 09-22 §5.4 의 '점군 끄기 · 릴레이 정지로 <320 여유 있게' 도 예상이었고 −6 %p 에 그침 |
| 다음에 알아보는 법 | 절감 기대는 '빠지는 것 − 들어오는 것' 을 이미 잰 수치로 먼저 셈한다. '구독자 0 이면 0' 같은 코드 주석의 기대값은 top 로 확인 전엔 쓰지 않는다 |
| 데이터 | [`j520_n61_static.txt`](../debug_log/2026-09-22/outputs/j520_n61_static.txt)(CPU 줄) · `top_n61*.log` · `top_n62*.log` · [`j531c_pcl.txt`](../debug_log/2026-09-23/outputs/j531c_pcl.txt) |

(n61c 조향 반전 6.29 /m 를 '기준선 밖' 으로 표시한 것은 지표 결함이었다 → [회피 주행 계측 카드](avoid-run-metrics.md) 실수 ⑩.)

## 6. SUMMARY · PHASE_N_RESULTS ↔ 원문 · 코드 모순 (이번 확인)
1. **09-22 §5.2 '결과(`j523b_minheight.txt` · `j524_probe.txt`)'**: `j523b` 의 탐침은 `tf2.LookupException: "base_link" … does not exist` 로 실패했고 목표 여유 줄도 `Bad file descriptor`. 0.08 의 탐침 수치(11 → 1)는 **`j524_probe.txt` 에만** 있다.
2. **j525b · j527 의 '실효값' 줄이 비어 있다**(sed 따옴표 오류): SUMMARY 의 '최소 높이 0.12 적용 뒤' · '통합 1.4 · 0.06 배포 뒤' 는 '설치 yaml 확인: 1'(grep 개수)과 결과 변화로 뒷받침될 뿐, 노드 실효값 원문은 없다(`job526_parmchk.sh` 출력은 저장 안 됨). 주행 값은 메타 sha256 으로 확인(§4.2).
3. **09-22 §5.1 'S 의 python3 19.7 %(depth_relay) 가 N 에서 사라짐'**: top 은 프로세스 이름이 전부 `python3` 라 어느 것이 릴레이인지 출력에 없다(추정 귀속). N 쪽에도 4.5 · 3.8 % 의 python3 가 있고, 09-23 측정으로 lazy 릴레이는 3.7~4.7 % 를 쓴다 — '사라짐' 이 아니라 '19.7 → ≈4'. 같은 과장이 `depth_relay.py` 62 줄 주석 '릴레이 CPU(≈19 %)를 0 으로' 에 남아 있다(지금 코드).
4. **09-22 §5.1 의 목표 여유 0.000 은 n61a 전에 이미 출력돼 있었다**(`j520_n61_static.txt` 머리) — SUMMARY 는 n61a 게이트에서 처음 본 것으로 씀(실수 ①).
5. **09-23 §1 게이트 M 선언 vs 구현**: 선언은 'LETHAL 중 **라이다 · 카메라** 근거 없는 셀 0'. 구현(`job505` 09-23 판)은 구역 전체의 라이다 점 수가 0 이고 전역 LETHAL 이 ≥ 1 일 때만 불합격 — 셀별 근거 대조가 아니고 카메라 근거는 안 본다. 구역에 라이다 점이 하나라도 있으면(예: 벽 끝) 유령이 있어도 통과한다(코드 확인, 실사례는 없음). `TEST_COURSE_AND_GATES.md` M 행은 '라이다 점 근거 없는 셀' 로 구현과 가깝게 적혀 있다.
6. **게이트 N 은 값이 비면 통과 쪽으로 계산된다**(fail-open): `awk a-b` 에서 빈 값은 0 → `j533_deploy_pcl.txt` "N 코스트맵 상자 최대 y ? − 카메라 왼쪽 가장자리 ? = 0.000 m → 통과", `j510_prep_0923c.txt` "0.025 − ? = 0.025 → 통과". SUMMARY §6 은 '판정은 통과 방향' 으로 적었지만, `TEST_COURSE_AND_GATES.md` 의 '게이트 출력 파서 취약점 — 불완전하면 안전하게 거부된다' 는 N 에는 맞지 않는다.
7. **09-23 §2 · §4 가 가리키는 '§2.1' 은 없다**(게이트 N 파서 수정 결과는 §6 에 있음).
8. **C1 은 선언 기준으로 불합격이다**: §1 'realsense 14.6 → ≤ 10 %, 릴레이 ≤ 1 %' vs 측정 13.9 · 0. SUMMARY §3 은 '기대보다 작다' 로만 쓰고 합격 여부를 적지 않음. 같은 날 1 · 2 차 시도(`j531_b1_c1` · `j531b`)는 끄기가 실패한 상태라 사실상 '같은 조건 반복' — 합 199~202 % 가 측정 잡음 폭(±2 %p)이다(이번 정리에서 읽음).
9. **H1 의 '가장자리 차' 는 재지 못했다**: `j532` 머리 "job315 … IndexError"(인자 없이 호출) — 표의 '카메라 상자 y 구간' 은 점군(job248) 값이라 슬라이스 설정과 무관. 판정은 유령 셀 수만으로 났다.
10. **j538 의 마지막 '통과' 블록에서 게이트 L 의 상자 띠 최소 x 가 0.875**(물리 전면 1.149 → −0.274 m)인데 L 은 셀 수(≥ 8)와 근거리 자취만 판정해 통과. 테이프를 덮으러 들어온 사람 · 덮개의 흔적인지 **미확인** — SUMMARY §10 에 없음.
11. **n62c 첫 prep(`j510_prep_n62c.txt`)은 L 7 · M 1 · N −0.028 로 불합격**, 목표 map (3.91, 0.07) — 로버가 출발 테이프로 돌아오기 전 자세로 prep 이 돈 것으로 보임(추정). 두 번째(`j510_prep_n62c2.txt`) 통과. SUMMARY §13 에 첫 시도 기록 없음.
12. **j514 SigIgn**: SUMMARY 는 'SIGINT · SIGQUIT 무시 상속(SigIgn 0x7)' 이라 썼는데 0x7 은 HUP · INT · QUIT(신호 1 · 2 · 3)이다. 그래서 래퍼의 `trap cleanup TERM INT HUP` 중 **HUP · INT 는 launch 아래에서 효과가 없다**(TERM 과 부모 소멸 감시만 작동) — 지금 코드 주석은 INT 만 언급.
13. **`PHASE_N_RESULTS.md` 가 N6 뒤 값으로 갱신되지 않은 곳**: §2 '(3) 범위: nvblox 통합 2.0 m', '(4) 높이: 슬라이스 0.03~0.30', §4 '통합 2.0 m · 슬라이스 z 0.03~0.30'(N6-1 뒤 1.4 · 0.06), §5 항목 2 '0.03 복귀를 정지 측정으로 결정'(09-23 H1 로 0.06 유지 결정됨), 항목 4 '러너 재고정 위치 조건'(09-23 REFIX_MAX 0.06 으로 처리됨) — 표 §1 의 N6-1 · N6-2 행은 맞다.
14. **`nvblox_local.yaml` 머리 주석(지금 저장소)**: 6 줄 '⚠ 아직 bringup 에 통합되지 않음 … 모드 N 은 job488/job508 로'(N6-0 뒤 틀림), 12 줄 '최소 0.03'(지금 0.06). 68 줄 슬라이스 주석 '높이로는 … 못 가르므로 거리(1.4 m)로 가른다' 는 통합 거리가 10-22 에 **2.0** 으로 바뀐 지금은 성립하지 않는다(테이프 대책은 '테이프 제거 + 깊이 프리셋 3' 쪽으로 옮겨감 — 이후 참조).
15. **09-23 §13 'R1: 3 회 모두 t≈1.1 s 의 튄 검출이 점프로 거부'** — `_refix.csv` 로는 n62a 만 'jump', n62b · n62c 는 그 시각 yaw 7.5° · 5.5° 로 'yaw' 건너뜀([회피 주행 계측 카드 §6 ⑯](avoid-run-metrics.md)).
16. `run_j523.sh` 저장판에는 `job377_goalclear.py 2.0 0.0` 인자가 있지만 `j523_intdist.txt` 에는 job377 의 `IndexError`(인자 없음)가 찍혀 있다 — 실행한 판과 저장판이 다르다(첫 실행 뒤 고침).

## 7. 남은 것 (09-23 시점) · 이후
- 테이프 유령의 **기전**(IR 반사 · 유리 반사 · 깊이 신뢰도) 미확인. 해법 후보 3 개(nvblox 최소 가중치 상향 · `do_depth_preprocessing` · 라이다 근거 교차검증) 미시험 — 강건성 시험 R1 로 등록.
- 통합 거리 1.4 는 그날 유령이 1.5 m 밖에 떨어져서 통했던 것 — n62b 처럼 1.4 m 안에 오면 못 막는다(테이프 제거로만 해결).
- 슬라이스 0.06 의 통과 측 ≈4~5 cm 과소 마킹 — 게이트 N 이 지키지만 N 은 fail-open(§6-6).
- 슬라이스 최대 0.30 → 0.40 A/B 미실행.
- 컨테이너가 사라졌을 때(이미지 삭제)의 자동 복구 없음.
- lazy 릴레이의 수신 · 역직렬화 비용 3.7~4.7 % — 구독 자체를 끊으면 0 이 될 것(미시험).
- **이후**:
  - 10-13 §14 — 통합 거리 1.4 → 2.0 복구(사용자: 복귀 길 상자가 1.5 m 까지 와야 보임), 10-14 §6 — 다시 1.4(멀리서 처음 찍힌 면이 한 줄 두꺼움 · 방향 오차가 거리에 비례), 10-15 §30 — 1.0 근거 약함. 이 카드의 '1.4 = 유령 차단' 근거와 다른 이유들로 오갔다([10-13 SUMMARY](../debug_log/2026-10-13/SUMMARY.md) · [10-14](../debug_log/2026-10-14/SUMMARY.md) · [10-15](../debug_log/2026-10-15/SUMMARY.md)).
  - 10-22 §6~§10 — 프로젝터 상시 끔 구성에서 **맨바닥 유령**이 경로를 막아 주행 중단(f2dr1) → 깊이 프리셋 3(High Accuracy) 기본, min_weight · 프리셋 5 기각. §13~§15 — 프리셋 3 + 1.4 는 복귀 때 낮은 상자를 놓쳐 접촉(f2lp1) → 통합 거리 **2.0**(지금 값). 같은 '근거 없는 셀' 이 카메라 쪽 원인으로 다시 열린 것([10-22 SUMMARY](../debug_log/2026-10-22/SUMMARY.md), 카드는 그 시기에).
  - 게이트 M 은 W1 시험 코스용(`job505`)이었고 지금 주행 전 검사 `Docs/tools/chk_drive_gate.py`(B · C · G2)에는 목표 부근 근거 없는 칸 검사가 없다(코드 확인). 장소 이동(F2.5)의 `place_server` 는 목표 여유 검사를 한다(CLAUDE.md §6).

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| V1~V5 · 4 차 | N6-0 검증 | 09-22 §4.1 · §4.2, `j513_verify_run{1,2,3}.txt` · `j513_verify4.txt` · `j514_trapdiag.txt` · `j515_v5_prep.txt` · `j516_v5chk.txt` |
| G1 · G2 정지 | 모드 N/S 전역 · 로컬 격자 · CPU | 09-22 §5.1, `j520_n61_static.txt` · `j521_g1.txt` · `grid_n61{N,S}{g,l}_costmap.json` |
| 유령 셀 탐침 6 회 | 통합 2.0/1.6/1.4 · 최소 높이 0.03/0.08/0.12/0.06 | 09-22 §5.2, `j523_intdist` · `j523b_minheight` · `j524_probe` · `j524b_probe` · `j525_minh12` · `j525b_minh12` · `j527_int14` · `snap_n61a_goalarea.jpg` |
| n61a · n61b · n61c | G3 주행 | 09-22 §5.3, `outputs/*n61*`, bag `2026-09-22/bags/bag_n61{a,b,c}.tgz`(로컬) |
| B1 · C1 · H1 | 재부팅 복구 · 점군 끄기 · 슬라이스 0.03 | 09-23 §2~§4, `j510_prep_a` · `j531_b1_c1` · `j531b_pcl` · `j531c_pcl` · `j532_slice_h` |
| 게이트 · 점군 재배포 | 점군 끔 → keep | 09-23 §6 · §7, `j510_prep_0923b/c` · `j533_deploy_pcl` · `j537_pclkeep` · `j507_n62a_gatefail` |
| 테이프 | 게이트 M 검출 · 제거 검증 | 09-23 §9 · §10, `j510_prep_n62b` · `j538_tape_off` · `snap_n62b{,2,3}.jpg` |
| n62a · n62b · n62c | C2 주행 · N6 판정 | 09-23 §8 · §12 · §13, `outputs/*n62*`, bag `2026-09-23/bags/bag_n62{a,b,c}.tgz`(로컬) |
| 도구(09-22) | `run_j513_deploy.sh` · `job513_verify.sh` · `job514_trapdiag.sh` · `job516_v5chk.sh` · `job517_wrapchk.sh` · `run_j519_deploy2.sh` · `run_j518.sh` · `job518_g1g2.sh` · `job489_gridcmp.py`(토픽 인자) · `job522_goalprobe.py` · `run_j523.sh` · `run_j524.sh` · `job526_parmchk.sh` · `job528_dynchk.sh` · `run_jx.sh` · `job505_modeN_gate.sh` | §9.1 ~ §9.8 |
| 도구(09-23) | `job505_modeN_gate.sh`(M · N) · `job531_pcl_toggle.sh` · `job532_slice_h.sh` · `run_xfer_all_h.sh` · `run_jx.sh`(두 IP) | §9.6 · §9.9 ~ §9.11 |
| 코드(저장소) | `navigation.launch.py` · `nvblox.launch.py` · `scripts/nvblox_up.sh` · `depth_relay.py` | §4.1 · §9.12 |

## 9. 도구 해설
공통: 실행은 Jetson `/tmp`. PC 쪽 `run_*.sh` 는 WSL 에서 스크래치패드 사본의 CR 을 `tr -d '\r'` 로 지우고 `sshpass -p <PW>` 로 scp · ssh 한다(호스트 `JETSON_HOST`, 기본 192.168.0.101; 09-23 아침엔 172.30.1.8). ROS 는 `FASTRTPS_DEFAULT_PROFILES_FILE=…/fastdds_udp_only.xml` 로 UDP 전용. 컨테이너 안 명령은 `docker exec -u admin isaac_ros_dev-aarch64-container bash -lc …`(컨테이너용 DDS 프로파일은 래퍼가 `/tmp/fastdds_udp_only.xml` 로 복사). 스크래치패드 경로 `…/21d4aa9f-…/scratchpad` 가 박혀 있어 **지금 그대로는 다른 세션에서 못 돈다** — 저장소 사본을 쓰려면 경로를 바꿔야 한다.

### 9.1 `run_j513_deploy.sh` → `job513_verify.sh` — N6-0 배포 · 검증 V1~V4 (09-22 §4.1)
- **실행 위치 · 형태**: PC `bash run_j513_deploy.sh [all]` → Jetson `bash /tmp/job513_verify.sh`(timeout 560 s).
- **왜**: N6-0 의 '기본값 전환 확정' 조건(V1~V5)을 한 번에 자동으로 확인하려고.
- **하는 일**: 배포 — 저장소 `rover_navigation` 의 `launch/navigation.launch.py` · `launch/nvblox.launch.py` · `scripts/nvblox_up.sh` · `config/nvblox_local.yaml` · `CMakeLists.txt` 를 CR 제거해 Jetson 소스에 넣고 `job488` · `job505` · `job513` 을 `/tmp` 로. 검증 — ⓪ `colcon build --symlink-install --packages-select rover_navigation`, 설치 폴더 목록 · `pyyaml` 확인 ① V1 `QUICK=1 job488 nvblox` → nav2.log 의 `nvblox_up` 줄 → 8 s 뒤 `job505 node`(게이트 J · K · L) → 활성 yaml 머리 · `local_costmap.plugins` 를 yaml 로 읽어 출력 ② V2 노드 PID · 래퍼 PID 기록 → `pkill -TERM -f navigation.launch` → 1 s 마다 컨테이너 안 `pgrep -fc '^/opt/ros/humble/lib/nvblox_ros/nvblox_node'` 가 0 이 될 때까지 최대 25 s → 경과 s · 래퍼 생존 · 래퍼 로그 꼬리 → 나머지 Nav2 프로세스 −9 정리(래퍼는 −9 하지 않음 — 2 차부터), 노드가 남았으면 직접 정리 ③ V3 `job488 stvl` → 노드 수(0 이어야) ④ V4 `docker stop` → `job488 nvblox` → 컨테이너 상태 · 노드 수 · 래퍼 로그 → 30 s 뒤 `/tmp/nvblox_node.log` 의 `NVBlox Rates` 블록 `ros/depth_image_callback` Hz · plugins 실효값.
- **출력**: 화면 → `outputs/j513_verify_run{1,2,3}.txt` · `j513_verify4.txt`(4 차).
- **쓰인 곳**: 09-22 §4.1 · §4.2 판정(1 차 V2 · V3 불합격 → 3 차 통과 → 4 차 재통과).
- **계보**: 이 날 처음. V5 는 PC 의 `run_mp9prep.sh`(prep) + `job516_v5chk.sh`. 후속 상시 도구 없음(이후 prep 이 같은 경로를 매번 지나감).
- **알려진 결함**: 1 차 판은 V2 뒤 래퍼를 −9 로 죽여 V3 잔존을 V2 의 고아로 만들었다(원인 ②). V2 의 '래퍼 생존 yes' 는 2 s 시점 값이라 래퍼가 그 뒤 끝났는지는 출력에 없다.
- **지금 다시 쓸 수 있나**: 스크래치패드 경로를 고치면 가능. launch 를 끄고 컨테이너를 멈추므로 주행 스택이 떠 있을 땐 쓰지 않는다.

### 9.2 `job514_trapdiag.sh` — 래퍼 신호 진단 (09-22 §4.1) ★ 원인 ①을 가른 도구
- **형태**: Jetson `bash /tmp/job514_trapdiag.sh`(인자 없음, `run_jx.sh` 로).
- **왜**: V2 에서 launch 를 끄면 노드가 남는데, 래퍼가 신호를 못 받는 건지 받고도 못 하는 건지 가르려고.
- **하는 일**: ① 지금 래퍼 PID(`pgrep -f "bash .*nvblox_up.sh"`) 의 cmdline 과 `/proc/<pid>/status` 의 `SigIgn · SigCgt · SigBlk · PPid`, 자식 목록 → TERM 을 직접 보내 1 s 마다 노드 수(최대 8 s) → 남으면 INT 를 보내 5 s 뒤 다시 → nav2.log 의 래퍼 줄 ② 대조: 노드를 −9 로 지우고 래퍼를 launch 없이 백그라운드로 직접 띄워 6 s 뒤 같은 SigIgn/SigCgt → TERM → 노드 수 ③ `launch.actions.execute_process` 소스에서 `start_new_session · preexec_fn · send_signal · killpg · SIGINT · sigterm_timeout` 문자열 개수.
- **출력**: [`j514_trapdiag.txt`](../debug_log/2026-09-22/outputs/j514_trapdiag.txt) — launch 아래 SigIgn `0x7`, TERM → 4 s 뒤 노드 0; 수동 SigIgn `0x6`, TERM → 3 s 뒤 0; launch 소스는 `sigterm_timeout` 2 회만.
- **쓰인 곳**: §4.1 원인 ①(무시 신호 상속) · ②(−9) 판정. ③ SIGPIPE 는 이 도구로는 못 봄(2 차 검증에서 드러남).
- **알려진 결함**: SigIgn 비트 해석을 출력에 안 함 → SUMMARY 가 0x7 을 'INT · QUIT' 로 적음(실제 HUP · INT · QUIT, §6-12). ③ 은 문자열 개수라 동작 증명은 아님.
- **지금 다시 쓸 수 있나**: 예(읽기 + 래퍼 · 노드를 죽임 — 스택이 떠 있을 땐 주의).

### 9.3 `job516_v5chk.sh` · `job517_wrapchk.sh` — V5 · 래퍼 중복 확인 (09-22 §4.2)
| 도구 | 하는 일 | 출력 | 쓰인 곳 · 결함 |
|---|---|---|---|
| `job516_v5chk.sh` | prep 뒤 컨테이너 안 노드 PID · 래퍼 PID 들 · `/tmp/nvblox_node_up.log` 꼬리 4 줄 · nav2.log 의 래퍼 줄 · 활성 yaml 머리 · loadavg · job240 '정리 전/후' 줄 | [`j516_v5chk.txt`](../debug_log/2026-09-22/outputs/j516_v5chk.txt) — 노드 465625, 래퍼 `465497 484152` | V5 판정(PID 교체). job240 정리 줄은 비어 나옴(nav2.log 가 새로 써져서, 추정) |
| `job517_wrapchk.sh` | 래퍼마다 pid · ppid · 경과 s · cmdline, launch 프로세스, 컨테이너 안 노드 pid · ppid · 경과 | **출력 원문 없음**(SUMMARY §4.2 'j517' 결론만) | '두 번째 래퍼 = 수명 0 s 서브셸' 판정 → 그래도 자기 PID 만 감시하도록 강화(`74b3ca37`) |

### 9.4 `run_j519_deploy2.sh` — N6-1 배포 (09-22 §5.1)
- **형태**: PC `bash run_j519_deploy2.sh`(인자 없음). 스크래치패드 `n61_src/` 의 `nav2_params.yaml` · `navigation.launch.py` · `depth_relay.py` 를 CR 제거 → PC 에서 `yaml.safe_load` 로 파싱 확인 → Jetson 소스 경로에 scp → `job489_gridcmp.py` 도 `/tmp` 로 → `colcon build --packages-select rover_navigation rover_bringup` → 설치본 md5 앞 12 자리 · `nvblox_layer` 등장 횟수.
- **출력**: [`j519_deploy2.txt`](../debug_log/2026-09-22/outputs/j519_deploy2.txt). 재기동은 하지 않음(prep 으로 따로).
- **계보 · 지금**: 같은 꼴이 09-23 `j533`(점군 연동) · `j537`(keep) 배포에도 쓰였다(그 러너 원본은 저장 안 됨). 지금은 `Docs/tools/up_tools.sh` · prep 이 배포를 맡는다.

### 9.5 `run_j518.sh` → `job518_g1g2.sh` — N6-1 정지 G1 · G2 (09-22 §5.1)
- **형태**: PC `bash run_j518.sh [BX=1.145] [BY=-0.068]` → Jetson `bash /tmp/job518_g1g2.sh <NAME> <BX> <BY>` 를 모드 N(n61N) → `job488 stvl` → 모드 S(n61S) → `job488 nvblox` 복귀 순으로. 끝에 격자 JSON 4 개를 PC 로 회수.
- **왜**: 전역 층을 바꾼 뒤 '상자 셀이 물리 상자와 맞나(G1)' · '정지 CPU 가 얼마나 줄었나(G2)' 를 같은 자세에서 N/S 로 비교.
- **하는 일(`job518`)**: ① 활성 yaml 에서 로컬 plugins[0] · 전역 plugins[1] 출력 ② `ros2 topic info /camera/depth/points_filtered` 의 구독자 수 · `ros2 topic hz`(릴레이 lazy 확인) ③ 로컬 · 전역 코스트맵 `ClearEntireCostmap` → 15 s 재관측 ④ `job489_gridcmp.py <NAME>g 0 /global_costmap/costmap` · `… l 0 /local_costmap/costmap`(LETHAL 개수 · 앞 0.3~1.6 m 의 y 분포, JSON 저장) ⑤ `job248_audit.py`(BOX_HINT) 의 상자 · 최소폭 · 전역 근거 줄 ⑥ `top -b -n2 -d10` 두 번째 화면에서 이름이 depth_relay · python3 · nvblox · controller · planner · realsense 인 줄의 %CPU ⑦ 전 프로세스 %CPU 합.
- **출력**: [`j520_n61_static.txt`](../debug_log/2026-09-22/outputs/j520_n61_static.txt)(앞에 prep 출력이 붙어 있음) · `grid_n61{N,S}{g,l}_costmap.json`. 비교 [`j521_g1.txt`](../debug_log/2026-09-22/outputs/j521_g1.txt)(N/S 전역 · 로컬 LETHAL 을 '우측 벽 · 좌측 가구 · 상자 · 기타' 로 나눔 — 그 비교 스크립트는 저장 안 됨).
- **쓰인 곳**: §5.1 G1(앞면 동일 · 띠만큼 확장) · G2(212 = 212).
- **알려진 결함**: top 의 COMMAND 가 `python3` 라 릴레이를 이름으로 못 고른다(§6-3) — 09-23 `job531` 은 `ps -o args=` 로 고쳐 depth_relay · sensor_conditioner 를 구분. G2 의 'STVL 갱신 0' 은 planner %CPU(11.5 → 9.9)로만 간접 판단.
- **지금 다시 쓸 수 있나**: 모드 전환이 `job488`(N3 판 → N6-0 판)에 의존 — 지금 구성이면 prep 으로 모드를 바꾸는 편이 낫다.

### 9.6 `job522_goalprobe.py` — 목표 부근에 무엇이 있나 (09-22 §5.1 ~ 09-23) ★ 유령 셀을 판별한 도구 · 게이트 M 의 엔진
- **실행 위치 · 형태**: Jetson 호스트 `python3 /tmp/job522_goalprobe.py`(인자 없음, 로버 정지 가정). `run_j523.sh` · `run_j524.sh` · `job505`(09-23 M) · `job532` 가 부른다.
- **왜**: n61a 게이트의 '목표 풋프린트 ↔ LETHAL 0.000' 이 진짜 물체인지 nvblox 가 만든 것인지 — 같은 구역을 네 원천으로 동시에 보려고.
- **하는 일**: 구역 = **base_link 기준 x 1.5~2.3, |y| < 0.45**(목표 2 m 앞 둘레, 상수). 구독 `/scan`(sensor QoS) · `/camera/camera/depth/color/points` · `/nvblox_node/static_map_slice`(`nvblox_msgs/DistanceMapSlice`) · `/global_costmap/costmap` · `/local_costmap/costmap`(TRANSIENT_LOCAL · RELIABLE) — 다섯 개가 다 올 때까지 최대 12 s, TF 버퍼 최대 6 s. ① 라이다: 각 빔을 `base_link ← laser` 변환(yaw · 평행이동만)으로 옮겨 구역 안 점 수와 앞 10 개 좌표 ② 카메라: 점군 전체를 `base_link ← 카메라 광학` 회전행렬 + 평행이동으로 옮겨 구역 안 · **z 0.03~0.6** 점 수와 x · y · z 범위 ③ 슬라이스: 각 칸 중심을 그 프레임(odom)에서 base_link 로 바꿔 구역 안 칸 수 · 미지(`unknown_value`) 수 · **거리 ≤ 0(장애물 안) 칸 수** · 최소 거리, ≤0 칸 좌표 12 개 ④ 전역(map) · 로컬(odom) 코스트맵: 구역 안 칸 수 · 100(LETHAL) · 99 · −1 수, LETHAL 좌표 12 개.
- **출력**: 화면 → `j523_intdist` · `j524_probe` · `j524b_probe` · `j525*` · `j527_int14`(09-22), `j531_b1_c1` · `j538_tape_off`(09-23, 일부 줄만).
- **쓰인 곳**: 유령 셀의 '라이다 0 · 카메라 점 높이 · 슬라이스 ≤0 · 코스트맵 LETHAL' 대조(§5.2 전 단계), 게이트 M 판정(09-23 §2 · §9 · §10), H1(§4).
- **계보**: 09-17 `job377_goalclear.py`(목표 여유 한 줄) → 이 도구(원천별 분해). 게이트 M 으로 승격(`job505` 09-23). 지금 상시 도구 `chk_drive_gate.py` 에는 같은 검사가 없다.
- **알려진 결함**: ① 구역이 **로버 기준 상수**라 로버가 출발 자세가 아니면 엉뚱한 곳을 본다(n62c 첫 prep 의 M 불합격이 그런 경우로 보임, 추정). ② 라이다 근거를 칸별이 아니라 구역 전체 개수로만 냄 → 게이트 M 이 '구역 라이다 0' 일 때만 불합격(§6-5). ③ 좌표 출력은 앞 10~12 개만. ④ `j523b` 처럼 TF 가 아직 없으면 예외로 끝남(재시도 없음 — 라이다 단계만 `lookup_transform` 을 바로 부름). ⑤ 카메라 점은 한 프레임만.
- **지금 다시 쓸 수 있나**: W1 코스(목표 2 m 앞) 정지 상태에서만. 순회 구성에서는 목표 좌표를 인자로 받게 고쳐야 한다.

### 9.7 `run_j523.sh` · `run_j524.sh` · `job526_parmchk.sh` — 유령 셀 반복 탐침 (09-22 §5.2)
| 도구 | 형태 | 하는 일 | 출력 | 결함 |
|---|---|---|---|---|
| `run_j523.sh` | PC `bash run_j523.sh BX BY [확인 문자열='esdf_slice_min_height: 0.12']` | 스크래치패드 `n61_src/nvblox_local.yaml` 을 Jetson 소스에 넣고 원격 스크립트(`/tmp/job523_remote.sh` 를 heredoc 으로 만들어 전송)로 → colcon → 설치본에 확인 문자열 개수 → `job488 nvblox`(래퍼가 새 yaml 로 노드 재시작) → 컨테이너에서 `esdf_slice_min_height · esdf_slice_height · projective_integrator_max_integration_distance_m · tsdf_decay_factor` 실효값 → 전역 클리어 · 25 s → `job522` → `job505 node`(J · K · L) → `job377_goalclear.py 2.0 0.0` | `j523_intdist` · `j523b_minheight` · `j525b_minh12` · `j527_int14` | 판마다 고쳐 쓴 단일 파일(저장판은 마지막 판). 실효값 줄이 sed 따옴표 오류로 빔(j525b · j527) · 첫 0.12 시도는 구문 오류로 실행 안 됨(실수 ③) · j523 의 job377 은 인자 없이 불려 오류 |
| `run_j524.sh` | PC `bash run_j524.sh BX BY` | 재배포 없이 `job522` + `job505 node` + `job377 2.0 0.0` | `j524_probe` · `j524b_probe` | — |
| `job526_parmchk.sh` | Jetson, 인자 없음 | 설치 yaml · `/tmp/nvblox_active.yaml` 의 `esdf_slice_min_height` 줄 · 노드 실효값(최소 · 대표 높이) · 노드 기동 후 경과 s | **출력 원문 없음** | SUMMARY §5.2 가 '실효값 확인' 근거로 인용하지만 값이 남지 않음 |

### 9.8 `job505_modeN_gate.sh` — 모드 N 게이트 J · K · L(09-22) → + M · N(09-23)
- **형태**: Jetson `bash /tmp/job505_modeN_gate.sh <LOGNAME> <BX> <BY>`(LOGNAME = `/tmp/nvblox_<LOGNAME>.log`; N6-0 뒤엔 `node` → `/tmp/nvblox_node.log`). `SKIP_MN=1` 이면 M · N 생략. 불합격이면 exit 1.
- **J · K · L(09-22 판)**: 본체 해설은 [Phase N 전반 카드](nvblox-migration-n0-n4.md). 요약 — J: 컨테이너 안 노드 정확히 1, 로그의 `NVBlox Rates` 블록 뒤 7 줄에서 `ros/depth_image_callback` ≥ 10 Hz · `ros/update_esdf` ≥ 9 Hz, `NVBlox Delays` 의 `esdf_integration` ≤ 0.15 s. K: `ros2 param get /local_costmap/local_costmap plugins` 에 `nvblox_layer`. L: 컨테이너 안 `job474_n0_measure.py gate 8 BX BY`(8 s) — 상자 띠 ≤0 칸/프레임 ≥ 8 · 카메라 0.45 m 안 ≤0 칸이 있는 프레임 0 · 프레임 ≥ 30.
- **M(09-23 추가)**: `job522` 출력에서 '라이다: 구역 안 점 N' 과 '전역 코스트맵 … LETHAL(100) G' 를 읽어 **G ≠ 0 이고 N = 0 이면 불합격**.
- **N(09-23 추가)**: 카메라 쪽 = `job248_audit.py`(BOX_HINT) 의 '상자 … y 구간 [lo, hi]' 의 hi(상자 왼쪽 가장자리), 코스트맵 쪽 = `job315_boxcells.py BX BY` 를 1 s 간격 3 번 돌린 최대 y 의 중앙값 → 차이 ≥ −0.025 m 면 통과.
- **출력**: '`J …` / `K …` / `L …` / `M …` / `N …` / `== 모드 N 게이트 … 통과`' 줄 — 09-23 의 거의 모든 prep · 배포 출력에 들어 있다(`j510_prep_*` · `j531*` · `j533` · `j537` · `j538`).
- **쓰인 곳**: N6-0 V1 · V5, N6-1 탐침 전부, 09-23 B1 · §6 · §9(M 이 테이프 유령 검출) · §10.
- **계보**: 09-22 판(J · K · L, L 문턱 10 → 8 정정) → 09-23 판(M · N, N 의 job315 인자 수정 포함). 지금은 `Docs/tools/chk_drive_gate.py`(B · C · G2)와 `chk_prep.py` 가 주행 전 검사를 맡고, J~N 은 상시 도구로 옮겨지지 않았다.
- **알려진 결함**: N 은 값이 비면 통과(fail-open, §6-6). M 은 구역 단위 라이다 개수만 봄(§6-5). L 은 상자 띠 **위치**를 판정하지 않음(§6-10). M 의 구역은 로버 기준 상수(§9.6 ①).
- **지금 다시 쓸 수 있나**: W1 코스 · 모드 N 에서만. 순회 구성엔 맞지 않음.

### 9.9 `job531_pcl_toggle.sh` — C1 점군 끄기 정지 A/B (09-23 §3)
- **형태**: Jetson `bash /tmp/job531_pcl_toggle.sh`(인자 없음).
- **왜**: 모드 N 에서 점군 생성을 끄면 CPU 가 얼마나 주나(C1 기준: realsense ≤ 10 %, 릴레이 ≤ 1 %, 깊이 15 Hz · 게이트 J 유지).
- **하는 일**: 처음에 `pointcloud.enable` 과 `pointcloud__neon_.enable` 두 파라미터 값을 출력 → A(현재) · B(`ros2 param set /camera/camera pointcloud__neon_.enable false` → 6 s) · C(true 로 복구 → 6 s) 마다 `meas`: 점군 · 깊이 · 릴레이 출력 Hz(`ros2 topic hz` 7 s) → `top -b -n2 -d10` 두 번째 화면에서 %CPU > 0.5 인 줄 → COMMAND 가 `python3` 면 `ps -o args=` 로 depth_relay · sensor_conditioner · stuck_monitor · jobNNN 을 구분 → realsense · depth_relay · sensor_conditioner · nvblox · controller · planner 출력, > 3 % 상위 목록, nvblox 로그의 깊이 콜백 Hz, 합.
- **출력**: 1 차 [`j531_b1_c1.txt`](../debug_log/2026-09-23/outputs/j531_b1_c1.txt)(B · C 의 set 이 `pointcloud.enable` 미선언으로 실패), 2 차 [`j531b_pcl.txt`](../debug_log/2026-09-23/outputs/j531b_pcl.txt)(B 제목만 고치고 명령은 옛 이름 — 실패, C 만 성공), 3 차 [`j531c_pcl.txt`](../debug_log/2026-09-23/outputs/j531c_pcl.txt)(성공).
- **쓰인 곳**: §3 수치(realsense 15.3 → 13.9, 릴레이 3.7 → 0, 합 201 → 195) → launch `camera_pointcloud` 연동 → §7 에서 계측 의존으로 기본 keep.
- **알려진 결함**: 저장판은 3 차 판. top 20 s 한 번이라 1 차 · 2 차(실질 같은 조건)의 합 199~202 가 잡음 폭.
- **지금 다시 쓸 수 있나**: 예(카메라 노드 이름 `/camera/camera` · neon 필터판 realsense-ros 가 같으면).

### 9.10 `job532_slice_h.sh` — H1 슬라이스 최소 높이 0.03 vs 0.06 (09-23 §4)
- **형태**: Jetson `bash /tmp/job532_slice_h.sh <BX> <BY>`.
- **왜**: 09-22 의 '통합 1.4 안에서는 0.03 으로 되돌려도 될 것' 추정 확인(H1: 0.03 에서 유령 0 · 가장자리 차 ≤ 2.5 cm 면 0.03 채택).
- **하는 일**: 설치본 `nvblox_local.yaml` 을 `/tmp/nvblox_local.orig.yaml` 로 백업 → `sample h06`: 활성 사본과 노드 실효 최소 높이, 표본 3 번(8 s 간격)마다 컨테이너 `job474 … h 6`(6 s)의 '프레임당 셀'(L) · `job522` 의 슬라이스 ≤0 · 전역 LETHAL · `job315` 최대 y, 끝에 `job248` 의 카메라 상자 y 구간 → 설치본 위에 sed 로 0.03 을 덮어쓰고 `job488 nvblox` · 40 s → `sample h03` → 원본 복구 · 재기동 · 35 s → 복구 실효값.
- **출력**: [`j532_slice_h.txt`](../debug_log/2026-09-23/outputs/j532_slice_h.txt).
- **쓰인 곳**: §4 표 → 0.06 유지.
- **알려진 결함**: `job315` 를 인자 없이 불러 `IndexError` → 가장자리 차를 못 잼(§6-9). 설치본(심볼릭 링크 설치)을 직접 덮어쓰므로 중간에 끊기면 소스가 바뀐 채 남을 수 있다(`--symlink-install` 이면 설치본 = 소스 파일 — 이번엔 복구 확인 줄 '0.06' 있음). 이 위험은 뒤 시기의 'prep 의 `sed -i` 가 설치본 링크를 끊음' 사건과 같은 계열(설치본 = 소스 링크라는 점을 잊고 직접 고침).
- **지금 다시 쓸 수 있나**: 주의해서 — 소스를 직접 덮는 방식은 피하고 별도 yaml 을 래퍼 인자로 주는 편이 안전.

### 9.11 `run_xfer_all_h.sh` · `run_jx.sh` — 재전송 · 범용 실행 (09-22 · 09-23)
| 도구 | 하는 일 | 지금 |
|---|---|---|
| `run_xfer_all_h.sh` | 재부팅 뒤 `/tmp` 작업 스크립트 일괄 재전송 — 옛 `run_xfer_all.sh` 의 IP 를 `JETSON_HOST` 변수로(09-23 §0), 3 회 재시도, 원격에서 CR 제거 · `chmod` · `py_compile`. 목록 24 개(없는 파일 건너뜀) | 원본 경로가 `82ce61d4…` 스크래치패드(09-28 자동 소실) → **쓸 수 없음**. 지금은 `Docs/tools/up_tools.sh` |
| `run_jx.sh` | 스크래치패드의 Jetson 쪽 파일 하나를 CR 제거 · 전송 · 실행(.py 면 python3). 09-23 판은 `JETSON_HOST` 가 없으면 192.168.0.101 → 172.30.1.8 순으로 핑해 응답하는 쪽 | 같은 역할의 상시 도구 = 실행 감싸개 `run_jn.sh`(09-29, 메모리 '실행 투명성') |

### 9.12 저장소 코드 — `depth_relay.py` lazy 와 `navigation.launch.py` 의 두 인자
- `depth_relay.py` 62~65 줄: `if self.pub.get_subscription_count() == 0: self.n_skip += 1; return`. 구독은 유지하므로 메시지 수신 · 역직렬화 비용(3.7~4.7 %)은 남는다 — [깊이 점군 카드 '이후'](depth-relay-artifacts.md) 에 상세.
- `navigation.launch.py`: `camera_layer`(기본 nvblox) — 로컬 · 전역 plugins 교체 + nvblox 면 `nvblox.launch.py` 포함. `camera_pointcloud`(기본 keep) — 위 §4.3.

### 9.13 이 시기에 내부에서 부른 앞 시기 도구 (본체 해설은 다른 카드)
| 도구 | 이 시기에 한 일 | 해설 |
|---|---|---|
| `job488_layer_ab.sh` | N6-0 판: 설치 yaml 대신 `camera_layer:=<MODE>` 로 Nav2 재기동(`setsid nohup ros2 launch …` — 원인 ① 의 출처) | [Phase N 전반](nvblox-migration-n0-n4.md) |
| `job489_gridcmp.py` | 3 번째 인자 TOPIC 추가(전역 `/global_costmap/costmap`, 커밋 `384c1eb6`) | 같은 카드 |
| `job474_n0_measure.py` | 게이트 L · H1 의 상자 띠 · 근거리 자취(컨테이너 안) | 같은 카드 |
| `job508_modeN.sh` · `job511_modeS.sh` · `run_j509_analyze.sh` | N4 의 팔 준비 · bag 분석 — N6-1 G3 분석(`j509_n61*`)에도 같은 러너 | 같은 카드 |
| `job240_clean.sh` · `job254_s4run.sh` · `job453_runmeta.sh` | prep 정리 목록에 `nvblox_up.sh` · 러너 게이트 J · 메타에 yaml sha256 | 같은 카드 · [회피 주행 계측](avoid-run-metrics.md) |
| `job248_audit.py` · `job315_boxcells.py` · `job377_goalclear.py` · `job322_snap.py` | 상자 · 창 · 목표 여유 · 컬러 스냅샷(점군 · 코스트맵 입력) | [회피 주행 계측](avoid-run-metrics.md) · [깊이 점군 카드](depth-relay-artifacts.md) |
| `job125_avoid3.py` | 러너(09-23 `REFIX_MAX` 0.06) | [회피 주행 계측 §9.1 · §7.2](avoid-run-metrics.md) |
| `job545_slipyaw.py` · `job546_scanrot.py` | 09-23 §12.1 미끄러짐 검증 | [F0 회전 옆 미끄러짐](f0-rotation-side-slip.md) |
| `job528_dynchk.sh` | (읽기 전용) nvblox 3.2 의 동적 · 사람 분리 모드 설정 · 필요 패키지 조사 — N7 로드맵 검토용, 출력 원문 없음 | 09-22 §6 · `NAV2_EXPLORATION_PLAN.md §7` |

## 10. 용어
- **TSDF / ESDF**: TSDF(절단 부호 거리장) = 복셀마다 '가장 가까운 표면까지의 부호 있는 거리' 를 표면 근처(절단 거리 안)만 저장하고 관측마다 가중 평균하는 3D 지도. ESDF(유클리드 부호 거리장) = TSDF 의 표면에서 모든 칸까지의 거리를 다시 계산한 것. nvblox 는 ESDF 의 한 높이 대역을 2D **슬라이스**(`static_map_slice`)로 내고, 호스트 `nvblox_layer` 가 거리 ≤ 0 칸을 이진 치명으로 코스트맵에 올린다.
- **통합 거리(integration distance, `projective_integrator_max_integration_distance_m`)**: 카메라에서 이보다 먼 깊이는 TSDF 에 넣지 않는다. 멀수록 스테레오 깊이 잡음이 커지므로 '원거리 잡음 필터' 역할. 09-22 2.0 → 1.4, 지금 2.0.
- **슬라이스 높이(`esdf_slice_min_height` · `esdf_slice_max_height` · `esdf_slice_height`)**: 2D 슬라이스로 접을 높이 대역(odom z = base_link 원점 기준, 바닥은 약 −0.026)과 대표 높이. 복셀 0.05 m 라 실제 경계는 0.05 단위 행. 지금 0.06 / 0.30 / 0.10.
- **유령 셀(ghost cell)**: 그 자리에 실물이 없는데(라이다 0 · 사람이 본 장면에 물체 없음) 코스트맵에 찍힌 치명 칸. 이 카드에선 바닥 깊이 잡음(최소 높이 0.03)과 반사성 바닥 테이프가 만든 것.
- **광선 소거**: 카메라가 어떤 칸을 '통과해서' 더 먼 표면을 보면 그 칸을 빈 공간으로 갱신하는 것. 간헐 유령이 사라졌다 다시 나타나는 이유.
- **게이트 J · K · L · M · N**: 모드 N 주행 전 검사(`TEST_COURSE_AND_GATES.md` v2.2). J 노드 · 주기, K 층 실효값, L 상자 커버 · 근거리 자취, **M 목표 부근 근거 없는 치명 셀**(전역 코스트맵 x 1.5~2.3 · |y|<0.45, 라이다 0 인데 LETHAL 이면 불합격), N 코스트맵 상자 통과 측 과소 마킹 ≤ 2.5 cm.
- **lazy 구독(lazy subscription)**: 발행자가 '내 토픽을 듣는 구독자가 있을 때만' 계산 · 발행하는 방식. `depth_relay` 는 입력 구독은 유지하고 콜백 첫 줄에서 출력 구독자 수를 봐 0 이면 버린다 — 계산은 안 하지만 수신 비용은 남는다.
- **모드 N / 모드 S**: `camera_layer:=nvblox`(기본) / `camera_layer:=stvl`(Phase S 대조군 — STVL + depth_relay).
- **계측 부하**: 주행 스택이 아니라 시험 도구가 쓰는 CPU — bag 기록기(ros2), 러너(job125), 점군 생성 · 릴레이. 09-23 부터 CPU 판정에 '계측 제외' 값을 함께 적는다.
- **래퍼(`nvblox_up.sh`)**: 호스트 launch 와 컨테이너 안 노드 사이의 셸. `docker exec` 는 신호를 넘기지 않으므로 이 셸이 신호 · 부모 소멸을 대신 감지해 컨테이너 안 노드를 정리한다.
- **SigIgn**: `/proc/<pid>/status` 의 '무시 중인 신호' 비트마스크. 비트 k−1 이 신호 k(1 HUP · 2 INT · 3 QUIT). 비대화 bash 는 시작할 때 이미 무시된 신호를 trap 으로 되살릴 수 없다.
