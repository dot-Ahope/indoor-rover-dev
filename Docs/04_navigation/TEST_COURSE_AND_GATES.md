# 시험 코스·게이트·주행 절차 — v2.2 (Phase N: STVL ↔ nvblox 층 A/B), 2026-09-23

**적용 범위**: Phase N 의 "중앙 상자 회피 코스" 주행. 로컬 코스트맵의 카메라 층만 **모드 S(STVL 층, Phase S 기준선 구성)** 와 **모드 N(nvblox 층, 이진, 09-21 floor 수정 포크)** 로 바꿔 같은 코스에서 비교한다. 전역 코스트맵·계획기·MPPI CostCritic·러너는 두 모드에서 같다. v1.0(Phase S, 2026-09-21)을 절 단위로 검토해 고쳤고, **바뀐 곳은 굵게 "N:" 표시**. 근거 날짜의 `Docs/debug_log/<날짜>/SUMMARY.md` 가 원문이다. v1.0 원문은 git 이력(커밋 16fce63 이전)과 `Docs/debug_log/2026-09-21/BASELINE_STVL.md`.
**Phase 전환 규칙**(유지): Phase 가 바뀌면 이 문서를 그대로 따르지 말고 절 단위로 검토해 새 판을 쓴다. 검토 항목에 **bag 프로파일(§5)** 을 반드시 포함한다(09-21 사용자 질의: 전환 시 bag 절차가 지시되어 있지 않았음).

## 0. v1.0 → v2.0 절 단위 검토 결과
| 절 | 판정 | 이유 |
|---|---|---|
| §1 배치 | 유지 | 코스 기하는 층과 무관. 상자 검출·게이트 hint 는 카메라 점군(층 아님)으로 재므로 모드에 영향 없음 |
| §2 절차 | **수정** | 컨테이너·nvblox 노드·층 전환 단계 추가, prep 뒤 nvblox 재시작 규칙, bag 프로파일 인자 |
| §3 게이트 | **수정** | A~I 유지. E·F 는 nvblox 띠(표면 뒤)와의 관계를 확인해 유지. **J·K·L 추가**(nvblox 노드·층 실효값·슬라이스 커버) |
| §4 운영 규칙 | **추가** | nvblox 지도는 odom 고정 → 손 배치·prep 뒤 반드시 nvblox 재시작. 모드 전환은 Nav2 만 재기동 |
| §5 산출물 | **수정** | `BAG_PROFILE=nvblox` 토픽·용량, nvblox 통계 로그, GPU 기록 |

## 1. 배치 (물리) — v1.0 유지
```
        좌측 가구(LETHAL 선, base y ≈ +0.58~+0.67, x ≈ 1.26~1.34)
  ─────────────────────────────────────────────────────────────
                     통로 폭 0.55~0.60 (전역 코스트맵 LETHAL 기준)
  [로버]  ─────► 진행 방향(+x)          ┌───┐ 상자 18(폭)×11(깊이)×14(높이) cm
  앞단=테이프 앞선                       └───┘ 전면 = 앞단에서 +0.90 m, 중심 = 중심선 우측 0.09~0.11 m
  ●base_link 원점(앞단 −0.25)                                   ◎ 목표 = base_link +2.00 m 직진(테이프 앞선에서 +1.75 m)
```
| 항목 | 물리 정의 | base_link 좌표(게이트가 재는 값) | 근거 |
|---|---|---|---|
| 출발점 | **바닥 테이프 — 로버 앞단을 테이프 앞선에 맞춤**(사용자, 09-21) | 원점. 앞단 = x +0.25, 카메라 = x +0.234·y +0.044·z +0.143 | URDF |
| 상자 | 전면이 앞단에서 0.90 m, 중심이 로버 중심선 우측 0.09~0.11 m, 긴 변(18 cm)이 진행 방향에 직각 | 전면 x 1.14~1.16, 중심 y −0.07~−0.11 (게이트 hint 로 넘김, 허용 ±0.06) | 09-11 s4r3, dy·cc 실측, 09-22 §0(1.151/−0.069) |
| 목표 | base_link 기준 2.0 m 직진, yaw 0 | (2.0, 0) map | 09-14 (D=2.0) |
| 통로 | 상자 좌측 끝 ↔ 좌측 가구 LETHAL 0.55~0.60 m | 09-21 job448 | |
| 거리 규약 | **정지 측정(S2 류)은 "물체 전면 ↔ 로버 앞단"**, 코스 게이트는 base_link 원점 기준 — 문서에 어느 기준인지 반드시 적는다 | 카메라 = 앞단 −0.016 m | 09-21 §5 |
- **N: 코스트맵에서 상자가 보이는 모양은 모드마다 다르다.** 모드 S 는 앞면 껍질(깊이 0.10~0.15), 모드 N 은 앞면 + 표면 뒤 절단 띠(절단 4.0 이면 깊이 0.25, 2.0 이면 §09-22 §1 결과). 앞면 위치는 두 모드 같다(≤1 셀). 게이트·러너는 카메라 점군으로 상자를 재므로 영향 없다(09-21 §10.3~10.5).

## 2. 절차 (한 회차)
| 단계 | 명령(PC, WSL) | 확인 | 근거 |
|---|---|---|---|
| 0 | 로버·상자를 §1 대로 손 배치, 관찰자는 카메라 시야(로버 앞 2 m 부채꼴) 밖·로버에서 ≥0.30 m | — | 09-14 §2.20, 09-18 dy3 |
| 1 | (재부팅 직후만) `run_j434.sh` 또는 `run_mp9prep.sh` 가 base 를 띄움 → **사용자 보드 리셋** → `/wheel_odom` ≈25 Hz. **N: 컨테이너 복구 `run_j499.sh`(정지된 컨테이너는 `docker start`, 없으면 job472 재생성) + 09-21 세트 재전송** | agent 1, 컨테이너 Up, nvblox 패키지 8 | 09-18 §10, 09-22 §0 |
| 2 | **손 배치 뒤엔 반드시** `JETSON_HOST=… run_mp9prep.sh` — 센서·SLAM·Nav2 재기동(SLAM 원점 = 현재 자세) + 게이트 A~D. Nav2 는 **설치 YAML 의 `plugins` 줄 상태대로** 뜬다(직전에 job488 로 바꿨으면 그 모드) | §3, 로컬 plugins 실행값 확인 | 09-11 job240, 09-14 |
| 2N | **N(v2.1): 모드는 launch 인자** — `navigation.launch.py camera_layer:=nvblox\|stvl`(기본 **nvblox**, N5 결정). prep(job240)이 그대로 기본값으로 띄우므로 모드 N 은 별도 단계가 없다. 모드 S(대조군) 또는 전환만 할 때 `job488_layer_ab.sh stvl\|nvblox <BX> <BY>`(Nav2 만 재기동, 설치 YAML 무변경). nvblox 노드는 `nvblox.launch.py` → `scripts/nvblox_up.sh` 가 컨테이너 안에 띄우고(정지 컨테이너는 `docker start`), launch 가 끝나면 2 s 안에 정리한다. 32 s 뒤 게이트 J(`/tmp/nvblox_node.log`) | 게이트 J·K·L(`job505_modeN_gate.sh node <BX> <BY>`) | 09-22 §4 N6-0 V1~V5 |
| 3 | (관찰자 흔적이 남았을 때) `run_j442.sh job442_clearwait.sh` — 로컬·전역 클리어 후 8 s 재관측. **N: 모드 N 에서는 클리어 뒤 nvblox 슬라이스(9.5 Hz)가 바로 다시 채우므로 8 s 면 충분, 흔적은 TSDF 감쇠로도 사라짐(모드 N yaml `nvblox_n0_t2d99.yaml` 은 `tsdf_decay_factor` 0.99 @ 5 Hz → 관측 끊김 후 ≈81 s, 09-22 §2.1)** | 띠 셀 0 | 09-18 §13.3, 09-21 §9 |
| 4 | 게이트만 시험: `run_drive_gateonly.sh …` / 출발 자세만: `run_j440.sh` | §3 E~G | 09-18 |
| 5 | **주행 30 s 전부터 DDS 참여자를 만들거나 없애는 명령 금지**(`ros2 param/topic list·echo`, 임시 노드, 스냅샷). **N: 게이트 K(param get)·L(슬라이스 구독)도 30 s 전에 끝낸다** | — | 09-21 cc1(미달 18) |
| 6 | 사용자 "시작" 후에만: `STAGE='<단계>' NOTE='<바꾼 것>' GIT_HEAD=$(git rev-parse --short HEAD) [BAG_PROFILE=nvblox] run_drive_nohup.sh <이름> 2.0 <BX> <BY> 0.06 0` — 게이트 A~G 재검사 → bag·top·tegrastats·RSS 기록 → 주행 → 메타 스냅샷(bag 종료 뒤). **N: 모드 N 주행은 `BAG_PROFILE=nvblox` 필수, STAGE 에 모드·절단값을 적는다(예 `N4-N2` = nvblox 절단 2.0·감쇠 0.99)** | 결과 SUCCEEDED, ①~⑥, 재고정 요약 | 09-15 러너 v2, 09-18 §17, 09-21 §6·§10.1 |
| 7 | 회수: `run_post3.sh <이름>` → bag.tgz(로컬 보관)·csv·refix.csv·nav2 구간 로그·top·tegra·rss·meta·params. **N: `/tmp/nvblox_<이름>.log`(통계) 도 회수** | "OK" 8 종 | 09-18 §12, 09-21 §6 |
| 8 | 분석: `run_j435*.sh`(job416 코스트맵 여유·job426 로컬/전역 상자·job431/431b SLAM 보정·게걸음), `job446_pathdecomp.py`, `job462_baghz.py`, `job463_tegra.py`(GPU 열 포함), 정지·CPU 요약. **N: 모드 S 회차와 같은 표로 나란히** | SUMMARY 표 | 09-17~22 |
| 9 | 기록·커밋: `Docs/debug_log/<날짜>/{SUMMARY.md, jobs/, outputs/}`, 비밀번호 `<PW>` 가림, 게이트 `git grep --cached -l "<비밀번호>" \| wc -l` = 0. 푸시는 지시 시(origin 브랜치 + personal) | — | CLAUDE.md §1 |

## 3. 게이트 표 (전부 통과해야 주행; 실패 시 러너가 "주행하지 않음" 으로 멈춘다)
| # | 게이트 | 문턱 | 측정 도구 | 실패 시 | 근거 |
|---|---|---|---|---|---|
| A | 프로세스 중복·누락 | 14 종 각 정확히 1 개(에이전트 컨테이너·robot_state_publisher 포함). **N: nvblox_node 는 `--pid=host` 컨테이너라 호스트 pgrep 에 보이지만 14 종에 넣지 않는다 — J 로 센다** | `job254_s4run.sh`(pgrep) | 재기동(job240) | 09-11 |
| B | 보드 세션 | `/wheel_odom` 발행(≈25 Hz) | job254 | 에이전트 살아 있으면 두고 보드 리셋 요청 | 09-11 |
| C | SLAM 생존 | map→odom ≥ 수십 개/5 s, 최대 간격 ≤0.2 s | `job386_slamalive.py` | 재기동 | 09-17 mp7 |
| D | 상자 검출·위치 | 검출 성공(≥40 점) 그리고 \|dx\|,\|dy\| ≤ 0.06 m (hint 대비) | `job248_audit.py`(카메라 점군) | 로버/상자 위치 재조정 → 2 단계부터 | 09-11 s4r3 |
| E | 통로 띠 근거 없는 LETHAL 셀 | ≤1 (x 0.3~1.6, y −0.10~+0.50, 센서 점 8 cm 안에 근거 없는 셀). **N: nvblox 절단 띠는 표면 뒤(상자는 +x·−y)로만 자라 통로 띠(y −0.10~+0.50)에 들어오지 않으므로 그대로 적용. 09-22 t4 감사: 99 셀 중 근거 없는 것 1~2** | job248 감사 + `job315_boxcells.py` | 클리어 8 s(3 단계) 후 재검사 | 09-14, 09-21 §10.3, 09-22 §1 |
| F | 통과 창 | ≥0.20 m = 좌측 경계 − (상자 셀 최대 y + 0.195). **N: 상자 셀 최대 y 는 두 모드 같다(앞면·왼쪽 가장자리 ≤1 셀)** | job315(상자 셀 3 표본 중앙값) | 상자/로버 재배치 | 09-14, 09-21 §10.5 |
| G1 | 목표 여유 | 목표 풋프린트 ↔ LETHAL ≥0.20 m | `job377_goalclear.py` | 목표 거리 조정 | 09-17 |
| G2 | 출발 자세 | 로컬 LETHAL(100) 셀·라이다 점 ↔ 차체 외곽 모두 ≥0.10 m. **N: 모드 N 에서 로버 주변은 nvblox 미지(카메라 시야 밖)라 라이다 층만 남는다 — 라이다 점 조건이 실질 게이트** | `job440_startclear.py` | 로버 주변 물체·사람 치움 | 09-18 dy3·dy5, 09-21 §10.3 |
| H | 러너 파라미터 readback | temperature·critics·PathFollow 등 실행 값 = YAML | `job403_critics_rb.sh`, `job451`(주행 뒤) | YAML 재배포·재기동 | 09-17, 09-18 |
| I | 배터리 | 전압 기록(문턱 없음, 12.1~12.2 V 에서 주행해 옴) | prep | — | — |
| **J** | **N: nvblox 노드** | 컨테이너 안 `nvblox_node` 정확히 1 개, 시작 32 s 뒤 통계의 `ros/depth_image_callback` ≥ 10 Hz(실측 15.1), `ros/update_esdf` ≥ 9 Hz(9.5~9.6), `esdf_integration` 지연 ≤ 0.15 s(0.10~0.12) | `job473_nvblox_run.sh status`, `/tmp/nvblox_*.log` Rates/Delays 블록(Rates 헤더 뒤 7 줄만 — Delays 블록에 같은 이름 있음) | 노드 재시작(실행 파일 PID 로 정지 → 확인 → 시작), 깊이 토픽·TF 확인 | 09-21 §9, job483, 09-22 §1 |
| **K** | **N: 층 실효값** | `ros2 param get /local_costmap/local_costmap plugins` = 의도한 모드(`nvblox_layer` 또는 `stvl_layer`). 주행 30 s 전에 끝낼 것 | job488 출력 "실행값" | job488 로 다시 전환 | 09-21 §10.2 |
| **L** | **N: 슬라이스 커버** | 상자 구역(base x 0.9~1.5, y −0.35~+0.15)에 슬라이스 ≤0 셀 **≥ 8**(절단 2.0 기하 = 폭 4 셀 × 띠 2~3 셀; 처음 10 으로 썼다가 09-22 n4n2 배치에서 9 로 근소 불합격 → 사용자 승인으로 정정), 근거리(카메라 0.45 m 안) ≤0 셀 0 | `job474_n0_measure.py <이름> 20 <BX> <BY>`(컨테이너 안, 20 s) | 노드 재시작·상자 위치 확인 | 09-21 §9 N0 (ii), 09-22 §1 |
| **M** | **N: 목표 부근 근거 없는 치명 셀** | 전역 코스트맵 x 1.5~2.3·\|y\|<0.45 의 LETHAL 중 라이다 점 근거 없는 셀 = 0 (09-22 유령 셀 재발 방지; 09-23 반사성 바닥 테이프 위 유령 셀을 실제로 검출) | `job505_modeN_gate.sh`(내부 `job522_goalprobe.py`) | 클리어 8 s 후 재검사 → 지속이면 스냅샷(`job322_snap.py`)으로 원인 물체 확인 | 09-23 §9~10 |
| **N** | **N: 상자 통과 측 과소 마킹** | 코스트맵 상자 셀 최대 y − 카메라 점군 상자 왼쪽 가장자리 ≥ −0.025 m | `job505`(내부 job315 3 표본 중앙값 + job248 y 구간) | 슬라이스 높이·층 설정 확인 | 09-23 §1 |
- 게이트 출력 파서 취약점(유지): 감사 출력이 불완전하면 창이 `nan`/음수로 계산돼 안전하게 거부된다. 재실행으로 해결.

## 4. 운영 규칙 (게이트가 못 잡는 것)
1. **주행은 사용자의 "시작" 지시로만.** 게이트 통과 = 준비 완료이지 주행 허가가 아니다.
2. 관찰자: 배치 후 카메라 시야 밖·로버 ≥0.30 m. 사람 흔적은 STVL 에 로컬 120 s/전역 180 s 남는다. **N: nvblox 에는 다른 각도에서 다시 보거나 감쇠(0.99 @ 5 Hz, ≈81 s)될 때까지 남는다 — 3 단계 클리어로 확인. 감쇠 0.95(벤더 기본)는 17 s 만에 상자를 잊어 이 코스에 못 쓴다(09-22 §2.1).**
3. 손으로 로버를 옮기면 반드시 2 단계(prep 재실행). 상자만 옮겼으면 3 단계(클리어 8 s) 후 게이트 재검사면 된다.
4. 주행 30 s 전 DDS 참여자 생성·소멸 금지.
5. 같은 코스 판정은 상자 상대 위치(±6 cm)로 한다. map 원점은 SLAM 보정으로 회차마다 물리적으로 다른 자리가 된다.
6. 판정 기준은 주행 **전에** SUMMARY 에 선언한다. 사후 변경은 "정정" 으로 남긴다.
7. 러너 인자 `STAGE`(모드·절단값 포함)·`NOTE`·`GIT_HEAD` 필수 — 개선 전후 비교용.
8. 배치·기록에 쓰는 거리 기준(앞단 / base_link / 카메라)을 문장마다 적는다.
9. **N: nvblox 지도는 `odom` 프레임에 고정**(계획서 §3: map→odom 점프가 TSDF 를 번지게 하므로). prep 은 EKF 를 재기동해 odom 원점이 바뀌므로 prep 뒤 nvblox 도 새로 떠야 한다 — **v2.1 부터는 Nav2 launch 가 nvblox 를 함께 띄우고 끝내므로 자동**(09-22 N6-0 V5: prep 뒤 노드 PID 교체 확인). 반경 3 m 밖은 자동 소거(`map_clearing_radius_m`).
10. **N: 모드 전환(job488)은 Nav2 만 재기동**하고 센서·SLAM·에이전트는 건드리지 않는다. 전환 직후 첫 10 s 의 감사값은 과도 상태(09-21 §10.2 의 0.10 m)일 수 있으니 3 표본 뒤 값을 쓴다.
11. **N: 층 결함 수정본(round→floor)은 Jetson 포크의 미커밋 diff 다.** 재빌드·리셋 전에 `git -C ~/workspaces/isaac_ros-dev/src/isaac_ros_nvblox diff --stat` 로 살아 있는지 확인(사라지면 `job493_fixfloor.sh` 재적용).
12. **N: A/B 는 같은 세션·같은 배치에서 S→N→S 순으로 짝지어** 돌린다. 모드 S 회차가 대조군이며, 판정은 `BASELINE_STVL.md` 지표(중단 0, 통과 측 여유, 중단·미달, CPU/GPU/전력)로 한다. 셀 수가 STVL 과 같아지는 것은 목표가 아니다.
13. **Wi-Fi 재연결(인터페이스 다운/업)이 있었으면 주행 전 스택 전체 재기동**(prep). 이미 떠 있던 DDS 노드가 재발견·재전송 부하로 CPU 를 2~3 배 쓴다(09-23 n62b: 합 422 %, EKF·SLAM 3 배 → 재기동 뒤 321 %). 끊김 기록: Jetson `/var/log/wifi_mon/mon.log`(15 s LINK·`ARP_DUP`), 필요 시 `job540_trace.sh`(2 s 게이트웨이 핑).
14. **카메라 점군은 끄지 않는다**(`navigation.launch.py camera_pointcloud:=keep`, 기본). 게이트 D·E·F·N 과 러너 상자 모델이 `/camera/camera/depth/color/points` 를 입력으로 쓴다 — 끄면 상자 검출이 비어 주행이 거부된다(09-23 §7). `off` 는 계측 없는 운용 전용.
15. **러너 재고정**: `job125_avoid3.py` 는 출발 뒤 상자 재검출이 게이트 hint 에서 0.06 m 넘게 튀면 버린다(`REFIX_MAX` 0.30→0.06, 09-23). 러너 ① 과 bag 횡변위 기반 여유가 2 cm 넘게 다르면 `<이름>_refix.csv` 를 확인한다.

## 5. 산출물 (회차당)
| 파일 | 내용 | 생성 |
|---|---|---|
| `bags/bag_<이름>.tgz`(로컬만) | 기본: /tf·/scan·/plan·/plan_smoothed·/unsmoothed_plan·코스트맵·odom·cmd_vel·status + `run_meta.txt`·`params.txt`. **N: `BAG_PROFILE=nvblox` 추가분 `/nvblox_node/static_map_slice`·`/nvblox_node/combined_occupancy_grid`·`/camera/camera/depth/image_rect_raw`(160×120, ≈0.6 MB/s)·`camera_info`** | job231 |
| `outputs/<이름>.csv`, `<이름>_refix.csv` | 러너 0.1 s 계측(전진·횡·여유·계획·상자 비용·명령), 상자 재고정 기록 | job125 |
| `outputs/j379_<이름>.txt`, `nav2_<이름>.log` | Nav2 사건(미달·실패·클리어) 원문 | job379 |
| `outputs/top_*.log`(bags/), `tegra_<이름>.log`, `rss_<이름>.txt` | CPU/GPU/전력/온도/메모리 — **N: GPU 열(GR3D_FREQ)이 비교 지표** | job231 |
| `outputs/meta_<이름>.txt`, `params_<이름>.txt` | 재현 메타(STAGE·NOTE·GIT_HEAD·기록 토픽·배포 sha256)·실행 파라미터 | job453/451 |
| `outputs/j435_<이름>_verify.txt`, `j446_<이름>.txt` | 여유·드리프트·경로 분해 | run_j435*, job446 |
| **N: `outputs/nvblox_<이름>.log`** | nvblox 통계(Rates/Delays/Timings) — 게이트 J 근거 | job473/job501 |
- **Phase 전환 체크리스트(bag)**: 새 phase 의 판정 지표를 bag 만으로 재생할 수 있는지 묻고, 필요한 토픽을 `BAG_PROFILE` 로 추가한다. 기본 목록은 전후 비교 연속성을 위해 유지한다. 용량 증가·STAGE 표기를 함께 적는다.

## 6. 변경 이력
- v1.0 2026-09-21: 09-11~09-21 규칙 통합. 기준선 `Docs/debug_log/2026-09-21/BASELINE_STVL.md`, 러너 원본 `Docs/debug_log/2026-09-21/jobs/`.
- v2.0 2026-09-22: Phase N 판. §0 검토표, §2 컨테이너·nvblox·모드 전환 단계(1·2N·3·5·6·7), §3 게이트 J·K·L, §4 규칙 9~12, §5 bag 프로파일·nvblox 로그·전환 체크리스트. 근거 `Docs/debug_log/2026-09-21/SUMMARY.md §9~10`, `2026-09-22/SUMMARY.md §0~1`.
- v2.2 2026-09-23(N6-2): 게이트 M·N 추가, 운영 규칙 13(Wi-Fi 재연결 뒤 재기동)·14(점군 유지)·15(러너 재고정 0.06). 근거 `Docs/debug_log/2026-09-23/SUMMARY.md §1~13`.
- v2.1 2026-09-22 저녁(N6-0): 모드 선택을 launch 인자 `camera_layer`(기본 nvblox)로, nvblox 기동·정리를 `nvblox.launch.py`/`nvblox_up.sh` 로 자동화. §2-2N·§4-9 갱신, 게이트 A 뒤 J 자동(job254), 메타에 활성 YAML sha256. 근거 `2026-09-22/SUMMARY.md §4`.
- v2.0.1 2026-09-22 저녁: N5 결정(로컬 층 nvblox 채택) 반영 — 모드 N 이 채택 구성, 모드 S 는 N6(전역 이전) A/B 의 대조군으로 유지. 게이트 L 문턱 ≥ 8 정정, 감쇠 0.99 표기. 결과 요약 `Docs/05_nvblox/PHASE_N_RESULTS.md`.
