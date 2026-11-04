# nvblox 전역 층의 TF 조회 실패 처리 결함 — 실패 순간 odom 슬라이스를 단위 변환으로 map 에 적음 (9 기: 10-27 §15 ~ §21 · §25 · §26, 10-28 §0 ~ §4)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **해결(결함 확정 · 수정 · 수정 경로 실주행 확인 1 회)** — 원인은 상위 `nvblox_nav2` 층 코드(조회 예외를 잡고도 return 하지 않음)로 소스 · bag 으로 확정, catch 에 `return;` 한 줄. f2tf1 에서 층 경고 28 번이 났는데 틀어진 전역 장 **0**(수정 전 f2st1 경고 22 번 · 틀어진 장 **3**). 방아쇠(SLAM map→odom stamp 정체)는 10-27 §21 transform_timeout 1.5 로 끊겨 f2tt1 · f2tt2 주행 창 경고 0. 남은 것: 수정은 Jetson 포크의 미커밋 diff + 저장소 패치 파일뿐 · 상위 보고 안 함 · 실패 순간 전역 카메라 층은 직전 슬라이스로 늦음(최대 한 갱신 주기, 추정) · 10-08 ~ 10-27 주행의 '가짜 막힘' 재해석 안 함 | 10-27 §15(관찰 · 원인) → §16(부하와의 관계) → §17(수정 · 빌드 · 정지 확인) → §18 · §19(f2tf1 확인) → §21.2 · §25(방아쇠 정정 · 차단) → 10-28 §0 · §4(f2tt2 반복) | [10-27 §15](../debug_log/2026-10-27/SUMMARY.md) 사용자 "20초 부근 문 공간이 막혔다 안 막힘 · 31초 상자가 벽 쪽으로 갔다 돌아옴 · 입구도 막힘 → 코스트맵이 2개 띄워져 있었는가?"(f2st1 복귀 상자 멈춤 영상 `videos/f2st1_box_stop_light.mp4`, git 제외) | Jetson 호스트 포크 `~/workspaces/isaac_ros-dev/src/isaac_ros_nvblox/nvblox_nav2/src/nvblox_costmap_layer.cpp` `sliceCallback()` catch 에 1 줄(저장소에는 원본 대비 차이만: [`Docs/05_nvblox/nvblox_nav2_rover.patch`](../05_nvblox/nvblox_nav2_rover.patch) 5~10 행, 커밋 `8e5ec16a`). 빌드는 `~/ros2_ws`(src 의 `nvblox_nav2` 는 포크로의 심볼릭 — 09-21 [`job484_hostbuild.sh`](../debug_log/2026-09-21/jobs/job484_hostbuild.sh) 13 행). 영상 도구 [`Docs/tools/fig_rviz_video.py`](../tools/fig_rviz_video.py) 에 `FIG_FOV` · `FIG_BOX`(§20) | [SLAM map→odom 시각 정체](slam-stamp-freeze.md)(방아쇠 — 같은 실패를 컨트롤러 쪽에서 본 카드) · [nvblox 층 round → floor](nvblox-layer-round-floor.md)(같은 파일의 첫 결함 · 같은 패치) · [낮은 상자 기억 · 전역 nvblox](low-box-global-memory.md)(전역 층을 map 프레임으로 둔 10-08 결정 — 이 결함이 걸리는 조건) · [복귀 길 상자 칸](box-return-cells.md)(f2tf1 접촉 — 이 결함과 무관) · [PathBlockedAhead 99/100 · only_new](pathblocked-only-new.md)(틀어진 장이 만든 가짜 막힘) · [Smac Hybrid 채택](smac-hybrid-adoption.md)(f2st1 · f2tf1 · f2tt 의 계획 구성) · [주행 전 검사 정리](drive-gate-consolidation.md)(f2tt1 · f2tt2 게이트) · [Phase N 후반 · 유령 셀](nvblox-n6-global-ghosts.md)(전역 nvblox 첫 도입) · [W3 떨림 · TF 지연](tf-lag-w3-wobble.md) · [상자 옆 정지 — 기전](box-side-stall-cause.md) · [MPPI 굽은 곳 · PathAlign 28/5](mppi-corner-cut-pathalign.md) (9 기) |

**한 줄**: f2st1 복귀 영상에서 전역 코스트맵이 한 장씩 '문이 막히고 상자가 벽 쪽으로' 갔다가 돌아왔다. 코스트맵은 하나였고, 튄 장은 nvblox 슬라이스(odom 좌표)를 **map→odom 변환 없이** map 격자에 적은 것과 맞았다(최적 변환 yaw 0.0° · 이동 (−0.02, 0.00) — 실제 map→odom 은 (0.43, 0.35, −7.5°)). 층 소스는 `lookupTransform(map, odom, 슬라이스 stamp)` 가 예외를 내면 경고만 찍고 그대로 진행해 기본 생성 Transform(단위)을 저장한다. catch 에 `return;` 을 넣어 그 슬라이스를 버리게 하자, 같은 경고가 28 번 난 f2tf1 에서 틀어진 장이 0 이었다. 실패의 방아쇠는 처음 '부하' 로 추정했다가(§16) SLAM map→odom stamp 정체로 정정됐고(§21.2), transform_timeout 1.5 뒤 두 주행(f2tt1 · f2tt2)은 주행 중 층 경고 자체가 0 이었다. 같은 주행(f2tf1)의 복귀 상자 접촉은 이 결함과 무관하다 — 슬라이스 원본에 상자가 없었다(카메라 시야 밖).

## 1. 증상
- **10-27 §15**(f2st1 복귀, 영상 1 배속 11:24:25 시작): 20 s ≈ 11:24:45 문 틈이 막혔다 풀림, 31 s ≈ 11:24:56 상자가 남쪽 벽 쪽으로 갔다 돌아오고 입구도 막힘. 바탕은 `/global_costmap/costmap`(약 1 Hz)의 그 시각 최신 메시지.
- 같은 때 **로컬 코스트맵(odom)은 정상**(§15.1 2, [`chk_gcm_rot_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_gcm_rot_f2st1.txt) 로컬 줄 모두 '최적 +0.0° (+0.00, +0.00)').
- §14 의 미확인 ③ '전역 P 값이 57 ↔ 99 로 깜빡임, 로컬은 안 깜빡임' 도 같은 시각(11:24:44~45 · 11:24:55~56) — §15.2 가 이 결함으로 묶음.
- PathBlockedAhead 11:24:37.91 '(2.22, −0.84) 99' · 11:24:43.89 '(2.17, −0.49) 99'(문 쪽)가 층 경고 11:24:37.85 · 11:24:43.60 직후 — 2 s 를 못 버텨 중단은 안 됐지만 가짜 막힘(§15.2).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-27 §15.1 ① | 코스트맵이 둘인가 | `/global_costmap/costmap` 연결 1 개 · 원점 (−5.29, −6.96) · 333×242 모두 같음 · 수신 − stamp 0.00 s. 튄 장 11:24:43.89 · 11:24:54.89 는 '직전과 다른 칸' 3699 · 3402(평소 481~1994), 상자 영역 치명 0(평소 2) | **아님**(측정) | [`chk_gcm_msgs_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_gcm_msgs_f2st1.txt) · 도구 [`chk_gcm_msgs.py`](../debug_log/2026-10-27/jobs/chk_gcm_msgs.py) |
| §15.1 ②③ | 연속 장 그림 · 통째 회전/이동 탐색(±40° · ±0.3 m) | 3 m 안 치명의 약 90 % 는 그대로(11:24:43.89 칸 1613 중 1388), 최적 회전 0° · 0 m. 새로 생김 276 · 268, 사라짐 213 · 185 | SLAM 점프 같은 통째 이동 **아님** | [`chk_gcm_rot_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_gcm_rot_f2st1.txt) · 그림 [`gcm_frames_f2st1_a.png`](../debug_log/2026-10-27/figures/gcm_frames_f2st1_a.png) · [`_b.png`](../debug_log/2026-10-27/figures/gcm_frames_f2st1_b.png) |
| §15.1 ④ | 새 칸이 라이다 · 정적 지도인가 | 그 사이 스캔과 안 겹침, `/map` 에선 258/276 · 254/268 이 빈 칸 | 라이다 · SLAM 지도 **아님** | [`chk_gcm_static_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_gcm_static_f2st1.txt) · 그림 [`gcm_diff_f2st1.png`](../debug_log/2026-10-27/figures/gcm_diff_f2st1.png) |
| §15.1 ⑤ | 슬라이스 원본 · EKF | 이웃 슬라이스와 회전 0° 로 거의 전부 겹침, 원점 · 크기 일정, odom→base_link 0.1 s 당 ≤ 1.3° | nvblox 출력은 **멀쩡** | [`chk_slice_tf_112442.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_slice_tf_112442.txt) · [`_112453.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_slice_tf_112453.txt) |
| §15.1 ⑥ | 새 칸을 만드는 slice→map 변환 탐색(yaw ±12° · 이동 ±0.8 m) | 11:24:43.89 최적 yaw 0.0° · (−0.02, −0.00) 겹침 186/276, 11:24:54.89 0.4° · (0.00, −0.01) 206/268. 정상 칸은 실제 값 근처(−5.5°, (0.38, 0.30)) | 새 칸 = **슬라이스를 단위 변환으로 적은 것**(측정) — 장애물 전체가 약 0.55 m · 7.5° 틀어진 자리에: 상자 (1.1, 0.0) → (0.7, −0.26) | [`chk_gcm_fit_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_gcm_fit_f2st1.txt) · 도구 [`chk_gcm_fit.py`](../debug_log/2026-10-27/jobs/chk_gcm_fit.py) |
| §15.1 ⑦ | 층 소스 읽기(Jetson 읽기만) · 경고 | `sliceCallback` catch 가 경고만 찍고 계속(아래 §3). nav2 로그 'Can't transform' 11:24:43.60 · 11:24:54.51 = 튄 장 0.3 s 전, 모두 global_costmap | **상위 코드 결함**(소스 + 시각). 로컬은 슬라이스와 같은 odom 이라 조회를 안 함 | [`nvlayer_src_tf.txt`](../debug_log/2026-10-27/outputs/block_cell/nvlayer_src_tf.txt) · [`nvlayer_tf_warn_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/nvlayer_tf_warn_f2st1.txt)(원천 `bags/logs_f2st1/nav2.log`, 사본 [`nav2_f2st1.log`](../debug_log/2026-10-27/outputs/drives/f2st1/nav2_f2st1.log)) |
| §15.2 | 결론 · 고칠 곳 | — | 'catch 에서 return 1 줄 + 재빌드' 제안(대안: 조회에 0.05 s 대기). 결정은 사용자 | SUMMARY §15.2 |
| §16 | 사용자 "수정한다고 해결되는가? 부하가 문제 아닌가?" | 층 경고 22 중 **20 번이 ±0.5 s 안 'Control loop missed'**(무작위 11 %). map→odom 은 20 Hz 로 끊김 없음(최대 0.187 s) · stamp 는 스캔 처리 때만 바뀜(최대 0.913 s) · 평소 슬라이스 stamp 는 최신 map→odom stamp 보다 0.51 s 뒤. bag 재구성 '슬라이스 앞섬' > 0 은 22 중 8 | 방아쇠 = 부하(**추정**), 결과가 '틀어진 장애물' 이 되는 것은 결함 — 둘은 따로. ⚠ **§21.2 에서 정정**: CPU 포화가 아니라 SLAM stamp 정체 | [`chk_tf_lag_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_tf_lag_f2st1.txt) · 도구 [`chk_tf_lag.py`](../debug_log/2026-10-27/jobs/chk_tf_lag.py) |
| §17 | 수정 · 빌드 · 정지 120 s 확인(판정 선언 뒤) | 빌드 rc 0 · 40 s, `libnvblox_nav2.so` 14:46:20 · sha 2a387c45575d. PREP_OK +90 s. 전역 74 장 일치율 중앙 · 최소 **1.000**, 0.8 미만 0, 층 경고 0 줄 | ①②③ ✔ — 단 TF 실패가 한 번도 안 나 **고친 경로 자체는 안 탐**(SUMMARY 가 한계로 적음) | [`prep_nvlayer_tffix_1027.txt`](../debug_log/2026-10-27/outputs/setup/prep_nvlayer_tffix_1027.txt) · [`run_tffix_chk_1027.txt`](../debug_log/2026-10-27/outputs/setup/run_tffix_chk_1027.txt) · 커밋 `8e5ec16a` |
| §18 · §19 | **f2tf1**(no5, f2st1 과 같은 구성 + 수정 층만 바뀜) | 8/8 · ABORT 0. 층 경고 **28** · Control loop missed 84 · 전역 264 장 중 서명 **0**. 같은 검출기로 f2st1: 경고 22 · 서명 **3**(11:24:37.91 · 43.89 · 54.89) | 판정 ② ✔ **수정 경로 확인** — 검출기가 수정 전 서명을 잡으므로 0 은 의미 있음. 판정 ③ 상자 복귀 −1.0 cm ✘ 는 이 결함과 무관(아래) | [`anal_tffix_sig_f2tf1.txt`](../debug_log/2026-10-27/outputs/tffix/anal_tffix_sig_f2tf1.txt) · [`_f2st1.txt`](../debug_log/2026-10-27/outputs/tffix/anal_tffix_sig_f2st1.txt) · 러너 [`run_f2tf1.txt`](../debug_log/2026-10-27/outputs/drives/f2tf1/run_f2tf1.txt) · bag `bags/bag_f2tf1.tgz` |
| §19 · §20 · §21.1 | f2tf1 복귀 상자 접촉(사용자 확인 '접촉 · 밀림') | 복귀 15:06:20~50 **슬라이스에 상자 자리 장애 칸 0**, 슬라이스 자체는 정상 갱신(약 9.5 개/s · 지연 0.11 s). 상자 방위 +41~+49° → +55° 이상(시야 ±43° 가장자리 · 밖). 시야 안엔 새로 알게 된 칸 7~93 · 새 장애 0~12 /s(벽 등) | 카메라는 정상, 상자만 시야 밖 — **수정과 무관**(슬라이스 원본 단계에서 이미 없음). 본체는 [복귀 길 상자 칸](box-return-cells.md) | [`chk_slice_health_f2tf1.txt`](../debug_log/2026-10-27/outputs/drives/f2tf1/box/chk_slice_health_f2tf1.txt) · [`chk_cam_fov_f2tf1_return.txt`](../debug_log/2026-10-27/outputs/drives/f2tf1/box/chk_cam_fov_f2tf1_return.txt) · [`anal_contact_f2tf1_d30.txt`](../debug_log/2026-10-27/outputs/drives/f2tf1/anal_contact_f2tf1_d30.txt) · 영상 `videos/f2tf1_return_light.mp4`(git 제외, 기록 [`fig_light_f2tf1_return.txt`](../debug_log/2026-10-27/outputs/fig_video/fig_light_f2tf1_return.txt)) |
| §21.2 · §21.3 | TF 지연의 정체 · 조치(→ [SLAM stamp 카드](slam-stamp-freeze.md)) | CPU 68.5 %(사건 초 73 %) — 포화 아님. nav2 odom→map 실패 33/33(층 28 + 컨트롤러 5) 전부 'SLAM stamp 정체로 미래 여유가 다 깎인 창' 안(f2st1 23/23) | §16 '부하' 추정 **정정**. SLAM 위치 추정 transform_timeout 0.5 → 1.5 | [`anal_load_f2tf1.txt`](../debug_log/2026-10-27/outputs/load/anal_load_f2tf1.txt) · [`anal_slam_freeze_f2tf1.txt`](../debug_log/2026-10-27/outputs/load/anal_slam_freeze_f2tf1.txt) · [`_f2st1.txt`](../debug_log/2026-10-27/outputs/load/anal_slam_freeze_f2st1.txt) · `ros2_ws/src/rover_bringup/launch/slam.launch.py` 72~77 행 |
| §25 · §26 | **f2tt1**(수정 층 + timeout 1.5 + 게이트 정리판) | 주행 창 층 경고 **0** · 서명 0 · Control loop missed 43. 로그의 층 경고 2 줄은 15:49:14~15 prep 기동 중 'extrapolation into the **past**'. 복귀 상자 14.4 cm, 사용자 "상자는 테이프 자리 · 접촉 없음"(§26) | 방아쇠가 끊김(1 회) | [`anal_tffix_sig_f2tt1.txt`](../debug_log/2026-10-27/outputs/tffix/anal_tffix_sig_f2tt1.txt) · [`nav2_f2tt1.log`](../debug_log/2026-10-27/outputs/drives/f2tt1/nav2_f2tt1.log) · [`anal_slam_freeze_f2tt1.txt`](../debug_log/2026-10-27/outputs/load/anal_slam_freeze_f2tt1.txt) |
| 10-28 §0 | 하루 시작 점검(밤사이 재부팅) | 포크 소스에 '2026-10-27 수정' 표시 1 줄 남음 · transform_timeout 1.5 | 재부팅으로 수정이 안 사라짐(소스 기준 — 빌드 산출물은 이날 따로 안 봄) | [`chk_day_start_1028.txt`](../debug_log/2026-10-28/outputs/chk_day_start_1028.txt) 5 행 · 도구 [`chk_day_start_1028.sh`](../debug_log/2026-10-28/jobs/chk_day_start_1028.sh) 6 행 |
| 10-28 §1 ~ §2 | 확인 주행 선언 · prep | 판정 ② 'nav2 odom→map 외삽 실패 0 · TF 외삽 → 중단 0'. PREP_OK +86 s · prep 스크립트 blob 모두 PC HEAD 와 같음 | — | [`prep_smac_1028_1.txt`](../debug_log/2026-10-28/outputs/prep_smac_1028_1.txt) |
| 10-28 §3 | f2tt2 첫 시도 — PC 쪽 출력 0 B · WSL 'E_FAIL' | 'grep: write error: No medium found' 뒤 `wsl -l -v` 전부 Stopped | '러너는 시작 안 됨, 로버 안 움직였을 것' — ⚠ **틀림(§3.1)**: Jetson 러너는 setsid nohup 으로 끝까지 돌았음 | `outputs/drives/f2tt2/run_f2tt2.txt`(0 B) · SUMMARY §3 · §3.1 |
| 10-28 §4 | **f2tt2** 결과(Jetson 에서 직접 회수) | 8/8. 주행 창 층 경고 **0** · 서명 0 · 컨트롤러 TF 중단 0 · Control loop missed 70. SLAM 정체 > 0.5 s 31 번 · 최대 0.996 s · 미래 여유 최소 1.003 s | 2/2 에서 TF 실패 0 → timeout 1.5 · 수정 층 운용 확정 근거(2 회) | [`anal_tffix_sig_f2tt2.txt`](../debug_log/2026-10-28/outputs/drives/f2tt2/anal_tffix_sig_f2tt2.txt) · [`anal_slam_freeze_f2tt2.txt`](../debug_log/2026-10-28/outputs/drives/f2tt2/anal_slam_freeze_f2tt2.txt) · 러너 원문 [`f0_f2tt2.log`](../debug_log/2026-10-28/outputs/drives/f2tt2/f0_f2tt2/f0_f2tt2.log) · 회수 [`get_f2tt2.sh`](../debug_log/2026-10-28/jobs/get_f2tt2.sh) |

## 3. 기전 — 코드로 본 것
### 3.1 층이 하는 일(호스트 `nvblox_nav2` 3.2, 상위 release-3.2 `7908a18`)
- 컨테이너 안 nvblox 가 `/nvblox_node/static_map_slice`(DistanceMapSlice, **odom** 프레임, 약 9.5 Hz)를 낸다. 호스트 Nav2 의 `NvbloxCostmapLayer` 가 그것을 코스트맵 칸에 옮긴다.
- 슬라이스 콜백(Jetson 소스 읽기 원문 [`nvlayer_src_tf.txt`](../debug_log/2026-10-27/outputs/block_cell/nvlayer_src_tf.txt) 12~33 행 · 63~71 행, 수정 전):
  ```cpp
  if (nav2_costmap_global_frame_ != slice_frame) {
    ...
    geometry_msgs::msg::Transform T_G_S_msg;          // 기본 생성 = 이동 0 · 회전 단위
    try {
      T_G_S_msg =
        tf_buffer_->lookupTransform(nav2_costmap_global_frame_, slice_frame, timestamp).transform;
    } catch (tf2::TransformException & e) {
      RCLCPP_WARN_STREAM_THROTTLE(..., kWarnMessagePeriodMs,   // 1000 ms 에 한 번만 찍음
        "[NvbloxCostmapLayer] Can't transform: " ...);
    }                                                  // ← return 없음
    ...
    T_G_S_ = Eigen::Isometry2f(Eigen::Translation2f(T_G_S_msg.translation.x, T_G_S_msg.translation.y) *
                               Eigen::Rotation2Df(azimuth_angle_rad));
  }
  slice_ = slice;
  ```
  → 조회가 실패해도 `T_G_S_` 가 단위 변환으로 덮이고 `slice_` 는 새 슬라이스로 바뀐다. 다음 코스트맵 갱신은 odom 좌표 칸을 map 칸에 그대로 적는다.
- **어느 층이 걸리나**(코드 조건 `nav2_costmap_global_frame_ != slice_frame`): 층 프레임이 슬라이스 프레임(odom)과 다를 때만 조회한다.
  - 로컬 코스트맵: `local_frame` 기본 odom(`navigation.launch.py` 68 · 211 행) → 조회 안 함 → **영향 없음**. (`local_frame:=map` A/B(10-02 §12) 때는 조회 경로를 탔을 것 — 그 시험의 경고 수는 안 봄.)
  - 전역 코스트맵: `global_camera:=nvblox` 일 때만 층이 들어가고(`navigation.launch.py` 88~97 행), 97 행이 층 프레임을 map 으로 넣는다(10-08 §3.3). 그 전(09-22 N6-1 ~ 10-01 §8.24)의 전역 nvblox 층은 프레임 줄이 없어 기본 odom — 조회를 안 했으므로 이 결함이 아니라 '0.3 m 밀림' 이라는 다른 결함이었다([낮은 상자 기억 카드](low-box-global-memory.md) 실수 ③). **즉 이 결함이 주행에 닿을 수 있던 기간은 10-08 ~ 10-27**(코드 추론, 측정 아님 — 아래 §6 기록 어긋남 4).
- **틀어진 장이 코스트맵에 보이는 길이**(추정): 전역 코스트맵은 `update_frequency: 1.0` · `publish_frequency: 1.0`(`nav2_params.yaml` 532~533 행). 갱신 순간의 `T_G_S_` 가 단위 변환이면 그 갱신 한 번이 통째로 틀어지고 다음 갱신(1 s 뒤)까지 남는다. f2st1 경고 22 번(1 s 에 1 줄로 줄여 찍힘 — 실제 실패 수는 그 이상) 중 서명 장 3 이었던 것은, 대부분의 실패가 다음 슬라이스(약 0.1 s 뒤) 성공으로 갱신 전에 덮였다는 뜻으로 읽힌다(갱신 루프 코드는 기록에서 안 읽음 — 추정).

### 3.2 고친 것(10-27 §17)
- [`Docs/05_nvblox/nvblox_nav2_rover.patch`](../05_nvblox/nvblox_nav2_rover.patch) 5~10 행:
  ```diff
  @@ -254,6 +254,7 @@ void NvbloxCostmapLayer::sliceCallback(
           "[NvbloxCostmapLayer] Can't transform: "
             << nav2_costmap_global_frame_ << " to " << slice_frame
             << ". Error: " << e.what());
  +      return;  // 2026-10-27 수정: 조회 실패 시 이 슬라이스를 버림(직전 slice_ · T_G_S_ 유지). …(rover 10-27 §15)
       }
  ```
- 효과(코드 추론): `slice_` · `T_G_S_` 가 둘 다 직전 성공 값으로 남아 **짝이 맞는** 직전 슬라이스를 계속 쓴다. 대가는 그 순간 전역 카메라 층이 직전 슬라이스만큼 늦는 것(정체 창 안에서 실패가 이어지면 그 창 길이만큼). 로컬 · MPPI 는 원래 영향 없음. 경고 줄은 그대로 찍힌다(검출에 씀).
- 기각한 대안(§15.2): 조회에 대기 시간(예 0.05 s) — 콜백이 실행기를 막을 수 있고 정체가 0.5 s 넘으면 어차피 실패. 결정 기록은 '대안' 언급뿐, 시험 안 함.

## 4. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 코스트맵 노드 · 발행자가 둘 | bag 연결 · 원점 · 크기(§15.1 ①) | 연결 1 · 모두 같음 | **기각** |
| SLAM 보정 점프로 지도 전체가 돌았다 | 직전 장 대비 회전 · 이동 탐색(§15.1 ③) | 90 % 그대로 · 최적 0° 0 m | **기각** |
| 새 칸은 라이다 · 정적 지도 물체 | 스캔 · `/map` 대조(§15.1 ④) | 안 겹침 · /map 빈 칸 258/276 | **기각** |
| nvblox 출력(슬라이스) 자체가 튐 | 이웃 슬라이스 회전 탐색 · EKF 튐(§15.1 ⑤) | 회전 0° · EKF 매끄러움 | **기각** |
| 층이 슬라이스를 단위 변환으로 적음 | 변환 탐색(§15.1 ⑥) + 소스(⑦) + 경고 0.3 s 뒤 튐 | yaw 0.0° · 0.4°, 이동 ≤ 0.02 m · catch 에 return 없음 | **지지(측정 + 소스)** |
| 방아쇠 = 부하(CPU) | 경고 ↔ Control loop missed 겹침(§16) → 코어 사용률 · 프로세스(§21.2) | 20/22 겹침 → 그러나 CPU 68.5 %, 사건 초 73 % · 실패 전부 stamp 정체 창 안 | §16 **추정** → §21.2 **기각**(겹침은 같은 원인의 두 증상으로 읽음) — 본체 [SLAM stamp 카드](slam-stamp-freeze.md) |
| return 수정이 정상 경로를 깨지 않는다 | 정지 120 s 로컬 ↔ 전역 치명 일치(§17 ③) | 중앙 · 최소 1.000 | **지지** — TF 실패 0 이라 고친 경로 미검증 |
| return 수정이 실패 순간의 틀어진 장을 없앤다 | f2tf1 서명 검출(§19 ②) · 같은 검출기의 수정 전 대조 | 경고 28 · 서명 0 / 수정 전 22 · 3 | **지지(실주행 1 회)** |
| f2tf1 복귀 접촉도 이 결함 탓 | 슬라이스 원본 상자 칸 · 시야(§19 · §21.1) | 슬라이스 상자 칸 0 · 시야 밖 · 로컬도 0 칸 | **기각** — 시야 문제([복귀 상자 카드](box-return-cells.md)) |

## 5. 조치와 효과
### 5.1 판정 · 결과 표
| 주행 · 시험 | 층 | timeout | 층 경고(주행 창) | 서명 장(§15) | 컨트롤러 TF 중단 | 비고 |
|---|---|---|---|---|---|---|
| f2st1(10-27 §11) | 원본 | 0.5 | 22 | **3** | 1 | 수정 전. 가짜 막힘 2 번(문 쪽) |
| 정지 120 s(§17) | 수정 | 0.5 | 0 | — | — | 일치율 1.000(고친 경로 안 탐) |
| f2tf1(§19) | 수정 | 0.5 | **28** | **0** | 5 | 고친 경로를 탐 · 문 앞 5.1 s 정지는 컨트롤러 TF(이 결함 아님) |
| f2tt1(§25) | 수정 | 1.5 | 0 | 0 | 0 | 로그 전체엔 prep 때 'past' 2 줄 |
| f2tt2(10-28 §4) | 수정 | 1.5 | 0 | 0 | 0 | 로그 전체엔 10:06 스택 기동 때 2 줄 |

### 5.2 판단에 쓴 핵심 줄 · 출력
- **틀어진 장 = 단위 변환(§15.1 ⑥)** — [`chk_gcm_fit.py`](../debug_log/2026-10-27/jobs/chk_gcm_fit.py) 35~43 행: 슬라이스 장애(≤ 0) 칸을 (yaw ±12° 0.5° 간격, 이동 ±0.8 m 0.05 간격)로 옮겨 '새로 생긴 치명 칸' 과 겹침 최대.
  ```python
  for yd in np.arange(yc - 12, yc + 12.01, 0.5):
      a = math.radians(yd); R = np.c_[math.cos(a) * S[:, 0] - math.sin(a) * S[:, 1], math.sin(a) * S[:, 0] + math.cos(a) * S[:, 1]]
      for tx in np.arange(xc0 - 0.8, xc0 + 0.81, 0.05):
          for ty in np.arange(yc0 - 0.8, yc0 + 0.81, 0.05):
              n = len(target & key(R + [tx, ty]))
  ```
  출력([`chk_gcm_fit_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_gcm_fit_f2st1.txt)):
  ```
  11:24:43.89 전역 · 슬라이스 장애 256 칸 · 실제 map→odom (0.427, 0.346, -7.50°)
     새로 생긴 276 칸 최적: 겹침 186 · yaw 0.0° t (-0.02, -0.00)
     직전과 같은 칸 최적: 겹침 151 · yaw -5.5° t (0.38, 0.30)
  11:24:54.89 전역 · 슬라이스 장애 276 칸 · 실제 map→odom (0.455, 0.385, -8.12°)
     새로 생긴 268 칸 최적: 겹침 206 · yaw 0.4° t (0.00, -0.01)
  ```
- **경고 ↔ 튐 시각** — [`nvlayer_tf_warn_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/nvlayer_tf_warn_f2st1.txt)(원천 nav2.log 줄 번호 붙음):
  ```
  257:[planner_server-5] [WARN] [1793067536.576268138] [global_costmap.global_costmap]: [NvbloxCostmapLayer] Can't transform: map to odom. Error: Lookup would require extrapolation into the future.  Requested time 1793067536.463438 but the latest data is at time
  ```
  (1793067536.58 = 11:18:56.58 KST. 튄 장 앞 경고는 [`anal_tffix_sig_f2st1.txt`](../debug_log/2026-10-27/outputs/tffix/anal_tffix_sig_f2st1.txt) 끝 '경고 11:24:43.60 → 다음 전역 장 11:24:43.89' · '경고 11:24:54.51 → 다음 전역 장 11:24:54.89'.)
- **수정 확인 검출기(§19 ②)** — [`anal_tffix_sig.py`](../debug_log/2026-10-27/jobs/anal_tffix_sig.py) 35~42 행: 전역 장마다 새로 생긴 치명 칸 A(≥ 50 칸만), 직전 슬라이스 장애 칸을 (가) 단위 변환 (나) 그 시각 실제 map→odom 으로 옮긴 칸과의 겹침 a · b, `a ≥ 0.5·|A| 이고 a > b` 면 서명.
  ```python
  J, I = np.nonzero(g & ~p)
  if len(I) < 50: continue
  ...
  a, b = len(A & key(S)), len(A & key(R))
  if a >= 0.5 * len(A) and a > b: sig.append((ts, len(A), a, b))
  ```
  출력 — 수정 전 f2st1 · 수정 후 f2tf1 · 1.5 뒤 f2tt1 · f2tt2:
  ```
  전역 메시지 275 · 새 칸 ≥ 50 인 장 211 · **§15 서명 장 3**
    서명 11:24:37.91 새 칸 238 · 단위 겹침 168 · 실제 3
    서명 11:24:43.89 새 칸 276 · 단위 겹침 186 · 실제 3
    서명 11:24:54.89 새 칸 268 · 단위 겹침 206 · 실제 6
  bag 창 11:18:14.58~11:25:30.89: 층 경고 22 번 · Control loop missed 70 번
  ---
  전역 메시지 264 · 새 칸 ≥ 50 인 장 195 · **§15 서명 장 0**
  bag 창 15:00:03.61~15:07:02.55: 층 경고 28 번 · Control loop missed 84 번
  ---
  전역 메시지 274 · 새 칸 ≥ 50 인 장 207 · **§15 서명 장 0**
  bag 창 15:55:19.72~16:02:20.41: 층 경고 0 번 · Control loop missed 43 번
  ---
  전역 메시지 268 · 새 칸 ≥ 50 인 장 202 · **§15 서명 장 0**
  bag 창 10:22:23.36~10:29:24.80: 층 경고 0 번 · Control loop missed 70 번
  ```
  (차례로 [`_f2st1.txt`](../debug_log/2026-10-27/outputs/tffix/anal_tffix_sig_f2st1.txt) · [`_f2tf1.txt`](../debug_log/2026-10-27/outputs/tffix/anal_tffix_sig_f2tf1.txt) · [`_f2tt1.txt`](../debug_log/2026-10-27/outputs/tffix/anal_tffix_sig_f2tt1.txt) · [`_f2tt2.txt`](../debug_log/2026-10-28/outputs/drives/f2tt2/anal_tffix_sig_f2tt2.txt).) f2st1 의 비서명 후보(`후보 11:20:37.88 새 칸 65 · 단위 겹침 23 · 실제 변환 겹침 39`)는 단위가 실제보다 낮아 걸러짐 — 문턱이 무엇을 가르는지 보여 주는 줄.
- **정지 확인(§17 ③)** — [`chk_nvlayer_tffix_1027.py`](../debug_log/2026-10-27/jobs/chk_nvlayer_tffix_1027.py) 41~48 행: 로컬 치명 칸(odom → 그 순간 map→odom 으로 map)을 로버 2.5 m 안만, 전역 ±1 칸 안 치명이면 일치. 출력([`run_tffix_chk_1027.txt`](../debug_log/2026-10-27/outputs/setup/run_tffix_chk_1027.txt)):
  ```
  == 층 라이브러리: 2026-10-27 14:46:20 · 로드 오류 0
  전역 메시지 74 장 · 로버 2.5 m 안 로컬 치명 칸 중앙 238 · 전역 일치율 중앙 1.000 · 최소 1.000 · 0.8 미만 장 0
  nav2.log [NvbloxCostmapLayer] 줄 0 (Can't transform 0 · must be 2d 0)
  ```
- **부하 겹침(§16)** — [`chk_tf_lag.py`](../debug_log/2026-10-27/jobs/chk_tf_lag.py) 45~47 행(무작위 2000 시각 ±0.5 s 안 missed 확률이 우연 기준). 출력([`chk_tf_lag_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_tf_lag_f2st1.txt)):
  ```
  슬라이스 4129 개 · 슬라이스 stamp − 최신 map→odom stamp: 중앙 -0.512 · 95% -0.310 · 최대 +0.510 s · 앞선(>0) 비율 1.0 %
  주행 창 경고 22 번 · Control loop missed 70 번(창 436 s) · 경고 ±0.5 s 안에 missed 있음 20/22
    우연 기준(무작위 시각 ±0.5 s 안 missed 확률) 11 %
  ```

### 5.3 과거 주행의 층 경고 수(이 카드 작성 11-04, 저장소 nav2 로그를 grep — 결과 파일 없음, 발췌가 전부)
- 명령: `grep -c "NvbloxCostmapLayer\] Can't transform" <nav2 로그>`(로그 전체 = prep 기동부터, 1 s 에 1 줄로 줄인 수). 모두 `global_costmap` 줄.
  ```
  2026-10-22 nav2_f2pr1 31 · f2sm3 34 · f2pi1 32 · f2lp1 54(두 바퀴) · f2dr1 2
  2026-10-23 nav2_f2pa1 28 · f2pa2 27 · f2von1 22 · f2von2 20 · f2rp1 24 · f2rp2 25 · f2rp3 30 · f2rp4 25 · f2rp5 23
  2026-10-26 nav2_f2sa1 20 · f2sa2 19 · f2sa3 17 · f2sh1 22 · f2sh2 23
  2026-10-27 nav2_f2st1 23 · f2tf1 28 · f2tt1 2(prep 'past')
  2026-10-28 nav2_f2tt2 2 · f2pl1 · f2pl2 · f2pl4 · f2pl5 각 2(같은 10:06 기동 로그)
  ```
  (10-12 ~ 10-14 는 발췌 로그만 남아 `f2f1_navlog.txt` 7 · `navlog_f2o1.txt` 4 · `navlog_f2s1.txt` 2 — 전체 수 아님.)
- 읽기: 전역 nvblox 층을 map 프레임으로 쓴 순회 주행은 timeout 0.5 시기 **매 주행 17~54 번** 층 조회가 실패했다(줄인 수라 하한). 그 각각이 틀어진 장으로 이어졌는지는 bag 마다 `anal_tffix_sig.py` 를 돌려야 알 수 있다 — **미측정**. 로컬 층은 영향이 없으므로 이 시기의 접촉(10-22 f2lp1 — 로컬도 상자 0 칸)과 상자 옆 근접은 이 결함으로 설명되지 않는다(코드 조건에서의 추론).

### 5.4 한계
- 수정 경로 확인은 f2tf1 **1 회**(경고 28 번). 그 뒤 두 주행은 방아쇠가 없어(경고 0) 수정 경로를 다시 타지 않았다.
- 검출기는 '단위 변환' 하나만 본다 — 다른 잘못된 변환(예: 오래된 map→odom)으로 적힌 장은 못 잡는다. 지금 코드에선 실패 때 직전 짝을 쓰므로 생길 수 없는 꼴이지만, 측정으로 배제한 것은 아니다.
- 실패 순간 전역 카메라 층이 얼마나 늦는지(직전 슬라이스 나이)는 재지 않았다.

### 5.5 지금 코드 영향(11-04 확인)
- 저장소에 층 소스는 없다(`git ls-files` 에 `nvblox_nav2` 쪽은 패치 파일 하나). 패치: [`nvblox_nav2_rover.patch`](../05_nvblox/nvblox_nav2_rover.patch) 5~10 행(이 결함) · 13~18 행(09-21 floor). Jetson 포크에 적용돼 있는지의 마지막 확인은 10-28 §0(`chk_day_start_1028.txt` 5 행 `nvblox 층 return 수정: 1` — 소스 표시만, 설치 `.so` 해시는 10-27 §17 의 2a387c45575d 이후 안 봄). 포크를 다시 받거나 상위 판을 바꾸면 `git apply` + `colcon build --packages-select nvblox_nav2` 필요([round → floor 카드](nvblox-layer-round-floor.md) 머리말).
- 이 결함이 걸리는 층: 전역 `nvblox_layer` — `navigation.launch.py` 207 행 `global_camera` 기본은 **obstacle**(층 없음), 표준 순회 prep 이 `Docs/tools/prep_patrol.sh` 17 행 `global_camera:=nvblox` 를 붙여 켬 → 88~97 행이 플러그인과 `nav2_costmap_global_frame = map`(97 행)을 넣음. 원본 YAML 블록 `config/nav2_params.yaml` 565~572 행(프레임 줄 없음 · 563 행 주석이 전제를 적음, 11-03 보강). 로컬 층은 `local_frame` 기본 odom(68 · 211 행)이라 조회 경로 밖.
- 방아쇠 차단: `ros2_ws/src/rover_bringup/launch/slam.launch.py` 72~77 행 transform_timeout 1.5(위치 추정 모드만). 정체가 1.5 s 를 넘으면 다시 실패하지만, 그때도 층은 이제 슬라이스를 버린다.
- CLAUDE.md §6 '10-27 구성 변경 ②' 에 이 수정이 적혀 있다(패치 경로 포함) — 지금 코드와 맞음.

## 6. 내 실수 · 기록 어긋남
1. **§16 '방아쇠는 부하'** — 하려 한 것: 층 경고가 왜 나나 · 본 것: 경고 20/22 가 Control loop missed 와 겹침(우연 11 %) · 처음 추론: 순간 부하로 TF 처리가 늦음 · 의심한 이유: (§21.2) 코어 평균 68.5 %, 사건 초 73 % — 포화 아님 · 판별: 실패한 조회의 프레임 쌍 · map→odom stamp 창 · 결론: SLAM stamp 정체(겹침은 같은 원인의 두 증상) · 다음에 알아보는 법: '겹친다' 는 원인이 아니라 공통 원인 후보 — CPU 를 말하기 전에 코어 사용률 · 대상 TF 의 stamp 간격을 먼저 · 데이터: [`chk_tf_lag_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_tf_lag_f2st1.txt) → [`anal_load_f2tf1.txt`](../debug_log/2026-10-27/outputs/load/anal_load_f2tf1.txt) · [`anal_slam_freeze_f2tf1.txt`](../debug_log/2026-10-27/outputs/load/anal_slam_freeze_f2tf1.txt). 칸 형식 원문은 [10-27 정리 페이지](../debug_log/2026-10-27/figures/day_summary_1027.html) '바로잡은 내 오류', 본체는 [SLAM stamp 카드](slam-stamp-freeze.md) §5.
2. **§17 `.so` 갱신 확인을 옛 이름으로**(09-21 실수 반복) — `prep_nvlayer_tffix_1027.sh` 25 · 27 행이 `libnvblox_costmap_layer.so` 를 봐서 'NO (09:00:00)'. 실제 `libnvblox_nav2.so` 는 `chk_nvlayer_so.sh` 로 14:46:20 갱신 확인. 판단엔 영향 없음 → [round → floor 카드 §6.4](nvblox-layer-round-floor.md).
3. **10-28 §3 '러너는 시작 안 됨, 로버 안 움직였을 것'** — PC 쪽 출력이 'No medium found' 로 죽은 것을 러너 미실행으로 읽음. 실제는 Jetson `job551` 이 setsid nohup 으로 끝까지 돌았다. 칸 형식 원문 [10-28 SUMMARY §3.1](../debug_log/2026-10-28/SUMMARY.md). 다음에 알아보는 법: '안 움직였다' 전에 Jetson `/tmp/f0_<이름>.log` · `pgrep job551`, 안 되면 '모름' + 현장 확인. 이 카드에서의 뜻: PC 연결이 끊긴 주행은 PC 에서 못 멈춘다 — [온보드 정지 수단](onboard-stop-nav-guard.md) 쪽 근거.
4. **§19 1 s top 중복 기록** — 러너가 이미 2 s top · /proc 를 남기는데 따로 켬(§19 본문이 스스로 적음). 결과에 영향 없음.
5. **기록 어긋남**:
   1. **§15.1 ② '튀는 메시지는 두 장뿐'** ↔ 같은 bag 을 주행 전체로 본 [`anal_tffix_sig_f2st1.txt`](../debug_log/2026-10-27/outputs/tffix/anal_tffix_sig_f2st1.txt) 는 **3 장**(11:24:37.91 추가, §19 본문이 적음). §15 는 영상 창(11:24:40~11:25:00, [`chk_gcm_msgs_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_gcm_msgs_f2st1.txt) 첫 줄 11:24:40.90)만 봤다. 10-27 정리 페이지엔 11-03 정정 표시가 있으나([11-02 SUMMARY](../debug_log/2026-11-02/SUMMARY.md) 92 행 목록) SUMMARY §15 본문엔 없음.
   2. **§15.1 ⑦ '이 주행 전체 23 번'** ↔ §16 · §19 '22 번' — 23 은 nav2 로그 전체(첫 줄 [`nvlayer_tf_warn_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/nvlayer_tf_warn_f2st1.txt) 148 행, 1793067066 = 11:11:06 prep 중 'only time … in the buffer'), 22 는 bag 창. 둘 다 맞고 범위 표시만 없음.
   3. **§18 선언 서명 기준 ↔ 구현** — 선언은 '최적 yaw |·| ≤ 1° · 이동 ≤ 0.1 m · 겹침 ≥ 새 칸의 50 %'(변환 탐색), [`anal_tffix_sig.py`](../debug_log/2026-10-27/jobs/anal_tffix_sig.py) 5 · 42 행은 탐색 없이 '정확히 단위 변환 겹침 ≥ 50 % 이고 실제 변환 겹침보다 큼'. 선언보다 좁은 판이지만 수정 전 3 장(§15 의 0.4° 장 포함)을 잡아 검출력은 확인됨. SUMMARY §19 는 이 차이를 적지 않음.
   4. **§23 함의 ② '전역 nvblox 층을 켠 09-22 이후 주행 전체에 영향을 줬을 수 있음'** ↔ 코드 조건(§3.1): 층 프레임이 map 일 때만 조회한다 — 09-22 ~ 10-01 전역 층은 프레임 기본 odom(조회 없음), 10-01 §8.24 ~ 10-08 은 전역 층 자체가 없음(`navigation.launch.py` 40~43 행 주석). 영향 가능 기간은 **10-08(§3.3 프레임 지정) ~ 10-27**. 11-02 확인 대조([11-02 SUMMARY](../debug_log/2026-11-02/SUMMARY.md) 104 행)는 97 행 프레임만 짚고 이 함의는 안 고침.
   5. **§15.2 '다음 정상 슬라이스(약 0.1 s 뒤)가 들어오면 돌아온다' · §16 '0.1~0.5 s 늦을 뿐'** — 층 상태는 0.1 s 뒤 돌아오지만 전역 코스트맵 칸은 1 Hz 갱신(`nav2_params.yaml` 532 행)이라 틀어진 장은 다음 갱신까지 1 s 남는다(영상 '다음 장에서 원래대로' 와 맞음). 추정 — 갱신 루프 코드는 안 읽음.
   6. **§17 정지 120 s · 전역 74 장** — 1 Hz 발행이면 약 120 장. 차이 원인은 기록에 없음(도구가 `spin_once` 한 번에 콜백 하나라 50 Hz `/tf` 에 밀려 depth 1 구독이 장을 놓쳤을 수 있음 — 추정). 일치율 판정 자체엔 영향 작음.
   7. **10-28 §4 '층 경고 0'** 은 bag 창 값 — [`nav2_f2tt2.log`](../debug_log/2026-10-28/outputs/drives/f2tt2/nav2_f2tt2.log) 에는 10:06 스택 기동 때 층 경고 2 줄('at time …' · 'into the past')이 있다. f2tt1 §25 는 같은 꼴을 따로 적었는데 10-28 §4 는 안 적음.
   8. (다른 카드) [SLAM stamp 카드](slam-stamp-freeze.md) 흐름 표 10-27 §15 행 '튄 장 2 장' — 위 1 과 같은 어긋남.

## 7. 남은 것 (10-28 시점)
- **상위 보고 안 함**(09-21 floor 결함과 같은 상태). 상위 더 새 판에서 고쳐졌는지 확인 안 함.
- 수정은 Jetson 포크 미커밋 diff + 저장소 패치 파일. 포크 재클론 · 판 바꿈 때 사라짐 — 재적용 절차는 [round → floor 카드](nvblox-layer-round-floor.md) 머리말.
- **10-08 ~ 10-27 주행의 '가짜 막힘' 재해석 안 함**(10-27 §26 사용자: '더 중요한 문제부터' — SLAM 처리 지연 우선). 그 시기 매 주행 층 경고 17~54 번(§5.3). PathBlockedAhead 막힘 · Smac 실패 · 이상 경로(10-14 §24 f2u2 등) 중 틀어진 장 위에서 계획한 것이 있었는지 미확인 — 도구는 있음(`anal_tffix_sig.py` 를 bag 마다).
- 방아쇠(SLAM 정합 비용 · stamp 정체)는 그대로 — [SLAM stamp 카드](slam-stamp-freeze.md). 정체가 1.5 s 를 넘으면 층은 다시 실패한다(이제 버림 · 지연으로).
- 같은 꼴(조회 실패에도 진행)이 층의 다른 곳(예: 3D 판정 경고 `must be 2d` 뒤에도 진행)에 있는지 — 경고만 찍고 진행하는 것은 같으나 그쪽은 변환 값 자체는 받은 상태라 결과가 다르다(코드 읽기, 시험 안 함).

## 8. 이후 (10-29 ~)
- 다음 시기에서 채움. 알려진 것: 11-04 까지 이 층 · 패치를 바꾼 기록 없음(11-02 ~ 11-04 SUMMARY 에 `nvblox_nav2` 수정 없음 — 11-03 은 `nav2_params.yaml` 563 행 주석만).

## 9. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2st1(10-27) | 수정 전 — 틀어진 장 3 · 층 경고 22 | 러너 [`run_f2st1.txt`](../debug_log/2026-10-27/outputs/drives/f2st1/run_f2st1.txt) · nav2 [`nav2_f2st1.log`](../debug_log/2026-10-27/outputs/drives/f2st1/nav2_f2st1.log) · `outputs/block_cell/` · bag `2026-10-27/bags/bag_f2st1.tgz` · 영상 `videos/f2st1_box_stop_light.mp4`(git 제외) |
| 정지 확인(10-27 §17) | 수정 층 · 정지 120 s | [`outputs/setup/run_tffix_chk_1027.txt`](../debug_log/2026-10-27/outputs/setup/run_tffix_chk_1027.txt) |
| f2tf1(10-27) | 수정 후 — 경고 28 · 서명 0 · 복귀 접촉(무관) | [`outputs/drives/f2tf1/`](../debug_log/2026-10-27/outputs/drives/f2tf1/run_f2tf1.txt) · `outputs/tffix/` · bag `bags/bag_f2tf1.tgz` · 로그 `bags/logs_f2tf1/` · 영상 `videos/f2tf1_return_light.mp4` |
| f2tt1(10-27) · f2tt2(10-28) | 수정 + timeout 1.5 — 경고 0 | [`anal_tffix_sig_f2tt1.txt`](../debug_log/2026-10-27/outputs/tffix/anal_tffix_sig_f2tt1.txt) · [`2026-10-28/outputs/drives/f2tt2/`](../debug_log/2026-10-28/outputs/drives/f2tt2/anal_tffix_sig_f2tt2.txt) · bag `2026-10-27/bags/bag_f2tt1.tgz` · `2026-10-28/bags/bag_f2tt2.tgz` |
| 원인 찾기 도구(§15 · §16) | `chk_gcm_msgs.py` · `chk_gcm_odd.py` · `chk_gcm_rot.py` · `chk_gcm_static.py` · `chk_gcm_fit.py` · `chk_slice_tf.py` · `fig_gcm_frames.py` · `fig_gcm_diff.py` · `chk_tf_lag.py` | `2026-10-27/jobs/` → `outputs/block_cell/` · `figures/gcm_*` |
| 수정 · 확인 도구(§17 · §19) | `prep_nvlayer_tffix_1027.sh` · `chk_nvlayer_so.sh` · `up_tffix_chk_1027.sh` · `run_tffix_chk_1027.sh` · `chk_nvlayer_tffix_1027.py` · `anal_tffix_sig.py` | `2026-10-27/jobs/` → `outputs/setup/` · `outputs/tffix/` |
| 상자 · 시야(§19 ~ §21.1) | `chk_slice_health.py` · `chk_cam_fov.py` · `anal_block_cell.py` · `Docs/tools/fig_rviz_video.py`(FIG_FOV · FIG_BOX) | `outputs/drives/f2tf1/box/` · `outputs/fig_video/` |
| 회수 · 점검 | `get_logs_f2tf1.sh` · 10-28 `get_f2tt2.sh` · `chk_day_start_1028.sh` | `2026-10-27/jobs/` · `2026-10-28/jobs/` |

## 10. 도구 해설
공통: `chk_*` · `anal_*` · `fig_*` 의 `.py` 는 PC(Git Bash · Python `rosbags` AnyReader, Humble 타입 + `nvblox_msgs/DistanceMapSlice` 를 손으로 등록), 입력은 PC 로컬 `bags/bag_<이름>.tgz` 를 푼 폴더. 시각 인자는 KST `HH:MM:SS(.ff)`. 칸 비교는 5 cm 칸 `floor(위치/0.05)` 집합. OccupancyGrid 100 = 치명. Jetson 쪽(`prep_*` · `run_*` · `up_*` · `chk_nvlayer_*`)은 PC(WSL) 래퍼가 `sshpass -p <PW>` 로 `/tmp` 에 올려 `run_jn.sh` 로 실행(비밀번호는 래퍼가 `run_jn.sh` 에서 읽고 출력 안 함). 로버는 어느 도구로도 안 움직임.

### chk_gcm_msgs.py — 전역 코스트맵 메시지를 하나씩 (10-27 §15.1 ①)
- 부른 형태: `chk_gcm_msgs.py bag 11:24:40 11:25:00 [토픽]`.
- 왜: 사용자 질문 '코스트맵이 2 개였나'.
- 하는 일: 토픽 연결(발행자) 목록 · 메시지마다 수신 시각 · header stamp · 원점 · 크기 · 치명 전체 · 상자 영역 치명 · 직전과 다른 칸 수.
- 출력: [`chk_gcm_msgs_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_gcm_msgs_f2st1.txt)(`11:24:43.89 연결 4 … 상자 영역 0 · 직전과 다른 칸 3699`). 쓰인 곳 §15.1 ① ②. 한계: 창이 영상 구간만이라 11:24:37.91 장을 못 봄(§6 어긋남 1).

### chk_gcm_odd.py — 이상 장 앞뒤 /map · map→odom (§15)
- 부른 형태: `chk_gcm_odd.py bag 시작 끝`. 하는 일: `/map` 수신 시각 · 원점 · 점유 수, map→odom 변화, 이상 장 vs 직전 장 치명 칸의 최적 (dx, dy) 칸 이동. 출력 [`chk_gcm_odd_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_gcm_odd_f2st1.txt) — /map 은 10 s 마다 같은 원점(SLAM 지도 갱신은 원인 아님). SUMMARY 본문엔 직접 인용 없음(탐색 단계).

### chk_gcm_rot.py — 통째 회전 · 이동인가 (§15.1 ③)
- 부른 형태: `chk_gcm_rot.py bag 시작 끝`. 하는 일: 전역 · 로컬 각 메시지에서 로버 3 m 안 치명 칸을 직전 장 기준 로버 중심 회전(±40° · 0.5°) + 이동(±0.3 m) 탐색 → 겹침 최대. 로컬은 odom 그대로(TF 안 씀).
- 출력: [`chk_gcm_rot_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_gcm_rot_f2st1.txt)(`11:24:43.89 칸 1613(직전 1527) · 그대로 1388 · 최적 1388 +0.0° (+0.00, +0.00)`). '통째 이동 아님 · 일부 칸만 새로' 의 근거.

### chk_gcm_static.py · fig_gcm_diff.py · fig_gcm_frames.py — 새 칸의 출처 · 그림 (§15.1 ② ④)
- `chk_gcm_static.py bag 시각…`: 새로 생긴 · 그대로 · 사라진 치명 칸이 `/map` 에서 점유 · 빈 칸 · 미지 중 무엇인지 셈 → [`chk_gcm_static_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_gcm_static_f2st1.txt)(`새로 생긴 치명 276 → /map 점유(100) 16 · 비움(0) 258`). 정상 장 11:24:46.89 대조(새 72 중 57 빈 칸 — 정상 갱신도 빈 칸에 생김, 크기가 다름).
- `fig_gcm_diff.py bag 출력.png 창 시각…`: 새로 생긴 · 사라진 칸 + 그 사이 라이다 스캔(map) 겹친 그림 → [`gcm_diff_f2st1.png`](../debug_log/2026-10-27/figures/gcm_diff_f2st1.png).
- `fig_gcm_frames.py bag 출력.png 창 시각…`: 연속 장을 밝은 색표(fig_rviz_video light 와 같음)로 나란히 + 같은 시각 로컬 → [`gcm_frames_f2st1_a.png`](../debug_log/2026-10-27/figures/gcm_frames_f2st1_a.png) · [`_b.png`](../debug_log/2026-10-27/figures/gcm_frames_f2st1_b.png).

### chk_slice_tf.py — 슬라이스 원본 · EKF (§15.1 ⑤)
- 부른 형태: `chk_slice_tf.py bag 11:24:42 11:24:45`(그리고 53~56). 하는 일: 슬라이스(odom)마다 수신 · stamp · 원점 · 크기 · 장애 칸, 직전 슬라이스 대비 최적 회전(±30° · 1°), odom→base_link 0.1 s 간격 yaw · 위치 튐.
- 출력: [`chk_slice_tf_112442.txt`](../debug_log/2026-10-27/outputs/block_cell/chk_slice_tf_112442.txt)(`11:24:43.18 stamp 11:24:43.07(+0.11) … 장애 250 · 겹침 249 · 최적 +0° (249)`). '원본은 멀쩡' 의 근거.

### chk_gcm_fit.py ★ — 틀어진 장을 만드는 변환 (§15.1 ⑥)
- 부른 형태: `chk_gcm_fit.py bag 11:24:43.89 11:24:54.89`.
- 왜: 새 칸이 '어떤 변환으로 옮긴 슬라이스' 인지 — 실제 map→odom 인지, 단위인지, 과거 어느 map→odom 인지.
- 하는 일: 그 장의 '새로 생긴 치명' 과 '직전과 같은 치명' 집합 각각에 대해, 가장 가까운 슬라이스의 장애 칸을 (yaw 실제±12° 0.5°, 이동 실제±0.8 m 0.05) 격자 탐색해 겹침 최대 변환. 지난 120 s map→odom 중 그 변환과 가장 비슷한 값도.
- 출력: §5.2 발췌. 결정적 판단(새 칸 = 단위 변환, 정상 칸 = 실제 근처)을 낸 도구. 한계: 탐색 범위가 실제 map→odom ±0.8 m 라 단위 변환(0, 0)이 그 안에 든 경우만 찾을 수 있음(이번은 0.43 · 0.35 m 라 들어감).

### chk_tf_lag.py — 부하와의 관계 (§16)
- 부른 형태: `chk_tf_lag.py bag nav2.log`.
- 하는 일: map→odom 수신 간격 · stamp 간격 · 수신 − stamp, 슬라이스마다 '그때까지 받은 map→odom 최신 stamp' 대비 앞섬, nav2 로그의 global_costmap 'Can't transform' 시각 vs 'Control loop missed' ±0.5 s 겹침(우연 기준 = 무작위 2000 시각).
- 출력: §5.2 발췌 + 경고별 줄(`11:24:43.60 공백 0.055 s … 앞섬 +0.043 s · missed ±0.25 s`). 쓰인 곳: §16 '방아쇠 = 부하(추정)' — §21.2 에서 정정. 결함: '앞섬' 은 bag 기록기가 받은 시각 기준이라 코스트맵 노드의 TF 버퍼와 다를 수 있음(§16 이 스스로 적음). 계보 → `anal_slam_freeze.py`(§21.2, 여유 소진 창 — [SLAM stamp 카드](slam-stamp-freeze.md)).

### prep_nvlayer_tffix_1027.sh ★ — 수정 · 재빌드 (Jetson, §17)
- 하는 일: 9 행 수정 전 catch 부분 출력 → 10~21 행 Python 으로 정확한 문자열(`<< ". Error: " << e.what());\n    }\n`)이 **한 번만** 있을 때만 `return;` 줄 삽입(표시 '// 2026-10-27 수정' 이 이미 있으면 건너뜀) → 23 행 포크 `git diff`(두 hunk = 패치 파일 내용) → 26 행 `colcon build --symlink-install --packages-select nvblox_nav2 … Release` · rc · 소요 → 27 행 `.so` 갱신(옛 이름 — §6 실수 2). 되돌리기: 표시 줄 삭제 후 재빌드(머리 주석 5 행).
- 출력: [`prep_nvlayer_tffix_1027.txt`](../debug_log/2026-10-27/outputs/setup/prep_nvlayer_tffix_1027.txt)(`빌드 rc 0 · 소요 40 s` · 끝 두 줄 `libnvblox_nav2.so 2026-10-27 14:46:20 sha 2a387c45575d 링크→ …/build/nvblox_nav2/libnvblox_nav2.so` · `<library path="nvblox_nav2">` 는 `chk_nvlayer_so.sh` 3 · 4 행의 출력 꼴 — 같은 파일에 이어 붙인 것으로 보임). 실행 중 Nav2 는 옛 `.so` → 다음 prep 으로 반영.

### up_tffix_chk_1027.sh · run_tffix_chk_1027.sh · chk_nvlayer_tffix_1027.py — 정지 확인 (§17 ③)
- `up_tffix_chk_1027.sh`(PC · WSL): `chk_nvlayer_tffix_1027.py` · `prep_smac_1027.sh` 를 CR 제거 뒤 Jetson `/tmp` 로, `JX_WHY` 를 달아 `run_jn.sh run_tffix_chk_1027.sh`.
- `run_tffix_chk_1027.sh`(Jetson): prep(f2st1 과 같은 구성) → 층 라이브러리 시각 · nav2.log 로드 오류 수 → `chk_nvlayer_tffix_1027.py 120`.
- `chk_nvlayer_tffix_1027.py`(Jetson, ROS 노드 1 개 — 정지 중이라 DDS 참여자 규칙과 무관): 전역 · 로컬 코스트맵 · /tf 구독, 전역 장마다 로컬 치명(2.5 m 안)을 map 으로 옮겨 전역 ±1 칸 치명 비율, 끝에 nav2.log 의 층 경고 수. 출력 §5.2 발췌. 한계: TF 실패가 없으면 고친 경로를 못 봄(§17 이 적음) · 74 장(§6 어긋남 6).

### anal_tffix_sig.py ★ — §15 서명 검출(주행 전체) (§19 · §25 · 10-28 §4)
- 부른 형태: `anal_tffix_sig.py bag nav2.log`.
- 왜: 수정 경로를 탔는지 — 경고가 났는데 틀어진 장이 없어야 한다.
- 하는 일: §5.2 발췌(35~42 행). 끝에 bag 창 안 층 경고 · Control loop missed 수와 경고마다 '다음 전역 장' 시각.
- 출력: `outputs/tffix/anal_tffix_sig_{f2st1,f2tf1,f2tt1}.txt` · 10-28 `outputs/drives/f2tt2/anal_tffix_sig_f2tt2.txt`. 쓰인 곳: §19 판정 ② ✔ · §25 · 10-28 §4 판정 ②. 결함 · 한계: 선언 기준과 다른 좁은 판(§6 어긋남 3) · 직전 슬라이스 하나만 봄 · 단위 변환만. 지금 다시 쓸 수 있음 — 과거 주행 재해석(§7)에 그대로 쓸 도구.

### chk_slice_health.py · chk_cam_fov.py · anal_block_cell.py — 상자를 왜 못 봤나 (§19 · §21.1 · §14)
- `chk_slice_health.py bag 시작 끝`: 2 s 마다 슬라이스 수 · stamp 지연 · 원점 · 크기 · 장애 칸 · 2 s 변화 비율 · 로버 위치 → [`chk_slice_health_f2tf1.txt`](../debug_log/2026-10-27/outputs/drives/f2tf1/box/chk_slice_health_f2tf1.txt)(`15:00:12 슬라이스 19 개 · 지연 0.13 s …`). 'nvblox 는 멈추지 않았다' 의 근거.
- `chk_cam_fov.py bag 시작 끝 [반각 43] [R 2.0]`: 1 s 마다 camera_link 기준 시야 부채꼴 안 슬라이스 칸(아는 · 장애 · 새로 앎 · 값 바뀜 · 새 장애) + 시야 안 라이다 점. 깊이 원본은 bag 에 없어 통합 결과로만 판단(머리말 6 행). 출력 `chk_cam_fov_f2tf1_{return,out}.txt`(`15:06:45 | (1.39, 0.13) +177° | 아는 717 · 장애 96 · 새로 앎 38 · 바뀜 40 · 새 장애 12`). 쓰인 곳 §21.1 '상자만 못 봄'. 한계: 43° 는 D455 깊이 수평 87° 사양의 반, 실제 유효 시야 미측정(§20).
- `anal_block_cell.py`(§14 판 — 본래는 f2st1 막힘 칸 대조, [PathBlockedAhead 카드](pathblocked-only-new.md) 쪽): 0.5 s 마다 칸 P 기준 전역 · 로컬 · nvblox · 라이다 최근접. f2tf1 에도 돌려 [`anal_block_cell_f2tf1.txt`](../debug_log/2026-10-27/outputs/drives/f2tf1/box/anal_block_cell_f2tf1.txt)(복귀 15:06:20~45 전역 '치명 없음' · nv 거리 0.61~0.66).

### Docs/tools/fig_rviz_video.py FIG_FOV · FIG_BOX — 복귀 영상 (§20)
- 10-27 §20 에 환경 `FIG_FOV=43,2.0`(camera_link 기준 부채꼴) · `FIG_BOX=1.151,1.261,-0.20,-0.02`(기록 상자 점선) 추가(도구 125~132 행). 출력 `videos/f2tf1_return_light.mp4`(git 제외, 67 s), 기록 [`fig_light_f2tf1_return.txt`](../debug_log/2026-10-27/outputs/fig_video/fig_light_f2tf1_return.txt)(`저장 videos/f2tf1_return_light.mp4 프레임 670 · 경로 11`). 상시 도구 — 지금 다시 쓸 수 있음.

### get_logs_f2tf1.sh · get_f2tt2.sh · chk_day_start_1028.sh — 회수 · 점검
- `get_logs_f2tf1.sh`(PC · WSL): Jetson `/tmp/{nav2,slam,sensors,top_f2tf1}.*` 를 다음 prep 이 덮기 전에 회수 → `bags/logs_f2tf1/`(git 제외), nav2 사본은 `outputs/drives/f2tf1/nav2_f2tf1.log`.
- `get_f2tt2.sh`(10-28 §4): PC 쪽 러너 폴링이 끊겨 자동 회수가 안 된 f2tt2 의 러너 산출물 · bag · 로그를 Jetson `/tmp` 에서 직접 회수.
- `chk_day_start_1028.sh`(읽기만): 가동 시간 · Wi-Fi · `/tmp` prep 스크립트 · 스택 프로세스 · transform_timeout · `grep -c '2026-10-27 수정'` 포크 소스(6 행) · 디스크.

## 11. 용어
- **DistanceMapSlice(슬라이스)**: nvblox 가 높이 띠(z 0.06~0.30)의 ESDF 를 2D 격자로 잘라 낸 메시지. 칸 값 = 가장 가까운 장애물까지 거리(≤ 0 = 장애). 우리 구성에선 odom 프레임.
- **T_G_S_**: 층이 기억하는 '슬라이스 프레임 → 코스트맵 전역 프레임' 2D 변환. 코스트맵 칸 중심을 이 변환의 역으로 슬라이스에 찾아간다.
- **단위 변환(identity)**: 이동 0 · 회전 0. 여기선 odom 좌표를 map 좌표인 척 그대로 쓰는 것 — map→odom 보정(이번 0.43 · 0.35 m · −7.5°)만큼 장애물이 틀어진다.
- **§15 서명**: 전역 장에서 새로 생긴 치명 칸이 실제 변환보다 단위 변환으로 옮긴 슬라이스와 더 잘 겹치는 장(`anal_tffix_sig.py` 판정).
- **미래 여유**: SLAM 이 map→odom stamp 를 '마지막 스캔 시각 + transform_timeout' 으로 미래에 찍어 두는 몫. 정체가 이 몫을 넘으면 '지금' 조회가 외삽 실패 — 본체 [SLAM stamp 카드](slam-stamp-freeze.md).
- **경고 줄임(THROTTLE)**: `RCLCPP_WARN_STREAM_THROTTLE(…, 1000)` — 1 s 에 한 줄만 찍음. 로그의 경고 수는 실패 수의 하한.
