import sys
sp = sys.argv[1]; root = 'F:/6_Indoor_Rover/Rover/'
# 1) 러너: 감사 출력이 잘리면(최소폭 줄 없음) 한 번 재시도
p = sp + '/run_drive_nohup.sh'
s = open(p, encoding='utf-8').read()
old = '''A=$(timeout 150 sshpass -p <PW> ssh $O $J "source /opt/ros/humble/setup.bash; BOX_HINT='$BX $BY' python3 /tmp/job248_audit.py 2>&1")
'''
new = '''A=$(timeout 150 sshpass -p <PW> ssh $O $J "source /opt/ros/humble/setup.bash; BOX_HINT='$BX $BY' python3 /tmp/job248_audit.py 2>&1")
# 09-16: 감사 출력이 간혹 표 없이 잘린다(run_gate 1회) → 최소폭 줄이 없으면 한 번 재시도
echo "$A" | grep -aq '최소폭' || { echo "  (감사 출력 불완전 — 재시도)"; A=$(timeout 150 sshpass -p <PW> ssh $O $J "source /opt/ros/humble/setup.bash; BOX_HINT='$BX $BY' python3 /tmp/job248_audit.py 2>&1"); }
'''
assert s.count(old) == 1
open(p, 'w', encoding='utf-8', newline='\n').write(s.replace(old, new)); print('runner patched')
# 2) SUMMARY §1.12
p = root + 'Docs/debug_log/2026-09-16/SUMMARY.md'
s = open(p, encoding='utf-8').read()
add = '''### 1.12 A 계획 정지 A/B (job340, 재기동 후 상자 1.085/−0.008, 목표 1.8/0, 주행 없음) → inflation 0.70 + SmoothPath 채택·배포
| 변형 | 입구(x=0.64) 접선 | 최대 진행방향 | 0.1 m 창 최대 꺾임 | 차선변경 x | 통로 계획횡 | 상자셀 최소 |
|---|---|---|---|---|---|---|
| navfn (inflation 0.55) | +30.9° | +64°(사선) / −119°(복귀) | 78.0° | 0.43→0.92 | +0.412 | 0.269 |
| navfn + smooth | +30.3° | +64° / −88° | 76.7° | 0.45→0.92 | +0.412 | 0.269 |
| navfn @ inflation 0.70 | +28.5° | **+37°** / −56° | 50.8° | 0.40→0.86 | +0.390 | 0.265 |
| navfn @ 0.70 + smooth | +28.3° | +35° / −46° | **16.6°** | 0.40→0.86 | +0.385 | 0.260 |
- 읽기: 입구 접선각은 기하 한계(횡 0.40 m 를 0.64 m 안에 끝내야 함 → 평균 32°) 때문에 어느 변형도 28~31°. 대신 **격자 사선의 봉우리(+64°)가 +37° 로, 0.1 m 안 꺾임이 78° → 16.6°** 로 내려가 "제자리 회전에 가까운 꺾임" 이 사라진다. 상자 뒤 복귀 모서리(−119° → −46°)도 완만. 상자셀 최소거리는 0.269 → 0.260(−0.9 cm), 통로 계획횡은 +0.412 → +0.385(상자 쪽으로 2.7 cm; 좌측 inflation 이 커져 밀림 — 창 중앙 +0.43 대비 4.5 cm 상자 쪽. 물리 여유 ≈ 6 cm, pd 주행 4~8 cm 범위).
- SmoothPath 단독은 거의 효과 없음(사선은 그대로) → 둘을 함께 채택. 한 번에 두 손잡이를 바꾸는 이유: 각각의 효과가 위 표에 분리돼 있고, 목표 지표(꺾임 16.6°)는 결합에서만 나온다.
- 배포: 전역 `inflation_radius 0.70`, BT `Sequence(ComputePathToPose → ForceSuccess(SmoothPath simple_smoother, check_for_collisions))`. 스무딩 실패 시 원 경로 유지(RecoveryNode 클리어 유발 방지). readback: inflation 0.7, SmoothPath 1, bt_navigator 오류 0.
- 재기동 readback: 10 Hz·model_dt 0.1·32 step·visualize, decay 120/180, relay max_range 4.0, 릴레이 CPU 19 %, 릴레이 1개.
- 게이트(상자 1.085/−0.008): 띠 근거 없는 셀 0, 상자 셀 0.122(3표본 일치), 좌측 0.55 → 창 0.233 m. (run_gate 1회는 감사 출력이 잘려 좌측 경계가 비었다 → 러너에 재시도 추가.)

'''
anchor = '## 2. 다음'
assert s.count(anchor) == 1
open(p, 'w', encoding='utf-8', newline='\n').write(s.replace(anchor, add + anchor)); print('summary ok')
