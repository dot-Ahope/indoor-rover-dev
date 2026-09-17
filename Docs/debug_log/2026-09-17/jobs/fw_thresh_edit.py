import sys, re
root = sys.argv[1]; NL = chr(10)
def rd(p): return open(root + p, encoding='utf-8').read()
def wr(p, s): open(root + p, 'w', encoding='utf-8', newline=NL).write(s); print('edited', p)

# ---- 1) rover_platform.h ----
p = '/App/app/rover_platform.h'; s = rd(p)
i0 = s.index('#define MIN_WHEEL_SPEED_MPS'); i1 = s.index('#define WHEEL_SPEED_EPS_MPS'); i2 = s.index(NL, i1) + 1
block = NL.join([
'/* ---- 저속·정지 문턱 체계 (2026-09-17: 세 파일에 흩어져 있던 값을 이 헤더 한 곳으로 모음) ----',
' * 같은 휠 속도 축을 세 층이 나눠 쓴다. 한 값만 바꾸면 층 사이가 어긋나므로 반드시 여기서 함께 본다.',
' *   WHEEL_SPEED_EPS         microros_task  : |휠 지령| < EPS  → 0 (의도된 정지)',
' *   MIN_WHEEL_SPEED         microros_task  : EPS ≤ |휠 지령| < MIN → MIN 으로 승격(부호 보존)',
' *   SPEED_CTRL_STOP_THRESH  speed_controller: |목표| < STOP → 정지 명령(감속 ramp 후 출력·적분 0,',
' *                                             windup·전류 누설 방지 — F4 2026-05-21 도입, 05-27 능동 제동 진입점)',
' *   STALL_TARGET_THRESH     safety_monitor : |목표| > 이 값일 때만 스톨 판정 (= STOP, 따로 두지 않는다)',
' * 불변식: EPS < STOP ≤ MIN (아래 #error 로 컴파일 시 검사).',
' *',
' * 사고(2026-09-17 mp6·mp8, debug_log/2026-09-17 §7): 09-07 에 MIN 을 0.010(구 스케일)→0.008(실 스케일)로',
' *   환산하면서 STOP(당시 speed_controller.c 의 TARGET_THRESH 0.010)은 그대로 둬 MIN < STOP 이 됨 →',
' *   휠 지령 3~10 mm/s 가 승격돼도 정지로 처리, MPPI 가 목표 앞에서 9 mm/s 로 기어가려다 51 s 무한 정지.',
' *   STOP 0.010 의 원래 전제(구 모터 AM2861·PWM 50 Hz 에서 저속 제어 불가)는 새 모터·20 kHz 에서 유효하지 않다.',
' *   조치: STOP·STALL 0.010 → 0.005 (사용자 결정 09-17 — 승격값을 올리는 대신 저속 분해능 보존).',
' *   TODO(측정): 새 펌웨어로 정지 상태에서 8 mm/s 출발(직진·제자리 회전) 바닥 실측 — 아래 MIN 의 미검증 구간.',
' *',
' * 정수 µm/s 로 정의하는 이유: 전처리기 #if 비교(부동소수는 #if 에서 쓸 수 없음). */',
'#define WHEEL_SPEED_EPS_UMPS          3000   /* 3 mm/s — 이하는 사실상 0(정지 의도) */',
'#define SPEED_CTRL_STOP_THRESH_UMPS   5000   /* 5 mm/s — 2026-09-17: 10 → 5 */',
'',
'/* 기동 데드밴드 보상 이력 (2026-09-02 도입):',
' *  |휠속도 명령| 이 최소 기동치 미만이면 모터가 반응하지 않아 상위 제어기(Nav2)가 미세 명령을 반복하며 영구 정체',
' *  (09-02 실측: ω=0.05 rad/s, 휠 ±6 mm/s 68 초 무반응). 보상: EPS ≤ |v| < MIN 은 MIN 으로 승격.',
' *  09-03: 기동 임계 0.012~0.016 → 0.020 채택. ※ PWM 50 Hz 조건 측정 — 09-07 에 폐기.',
' *  09-07 (8fd7618, PWM 20 kHz): 데드밴드 재실측용으로 0.010 임시 하향.',
' *  09-07 바닥 스윕 job44a (새 모터 CHR-GM37 1:90, 20 kHz, 스텝마다 정지 후 출발·3 s 유지):',
' *    지령 5/10/15/20/30 mm/s(구 스케일) → FG 10/10/15/20/30, duty 41/41/43/45/50 %, L/R 대칭, 전 스텝 기동.',
' *    지령 5 는 당시 MIN 0.010 으로 승격돼 10 으로 돌았으므로 **구 10 mm/s(=실 7.8 mm/s) 미만은 미검증**',
' *    (debug_log/2026-09-07 SUMMARY §데드밴드 스윕).',
' *  09-07 (50444d5, 휠 둘레 0.16130→0.12533): 0.010(구) × 0.777 = 0.0078 → **0.008 은 환산값**(직접 지령한 값 아님).',
' *  한계: 승격 구간은 지령 크기와 무관하게 같은 속도 → 저속 분해능 상실.',
' *  TODO(improve): 고정 하한 대신 기동 보조(정지 감지 시 순간 승격 후 목표 복귀), 또는 전압 연동 하한. */',
'#define MIN_WHEEL_SPEED_UMPS          8000   /* 8 mm/s */',
'',
'#define WHEEL_SPEED_EPS_MPS          ((float)WHEEL_SPEED_EPS_UMPS * 1.0e-6f)',
'#define SPEED_CTRL_STOP_THRESH_MPS   ((float)SPEED_CTRL_STOP_THRESH_UMPS * 1.0e-6f)',
'#define MIN_WHEEL_SPEED_MPS          ((float)MIN_WHEEL_SPEED_UMPS * 1.0e-6f)',
'#define STALL_TARGET_THRESH_MPS      SPEED_CTRL_STOP_THRESH_MPS',
'',
'#if !(WHEEL_SPEED_EPS_UMPS < SPEED_CTRL_STOP_THRESH_UMPS)',
'#error "rover_platform.h: WHEEL_SPEED_EPS 는 SPEED_CTRL_STOP_THRESH 보다 작아야 한다 (EPS 이상 지령이 정지로 먹힘)"',
'#endif',
'#if !(SPEED_CTRL_STOP_THRESH_UMPS <= MIN_WHEEL_SPEED_UMPS)',
'#error "rover_platform.h: MIN_WHEEL_SPEED 가 SPEED_CTRL_STOP_THRESH 보다 작다 — 승격된 지령이 정지로 처리됨 (2026-09-17 mp8 사고)"',
'#endif',
''])
# 기존 '기동 데드밴드 보상' 주석 블록 시작점 찾기 (MIN define 바로 위의 /* 기동 데드밴드 보상 ... */)
j0 = s.rindex('/* 기동 데드밴드 보상', 0, i0)
s = s[:j0] + block + s[i2:]
wr(p, s)

# ---- 2) speed_controller.c ----
p = '/App/app/speed_controller.c'; s = rd(p)
old = '#include "motor_config.h"   /* MOTOR_TYPE — 게인/deadzone 모델별 분리 */'
assert s.count(old) == 1
s = s.replace(old, old + NL + '#include "rover_platform.h"  /* SPEED_CTRL_STOP_THRESH_MPS — 저속·정지 문턱은 한 곳에서 관리 (2026-09-17) */')
old = '#define TARGET_THRESH  0.01f      /* m/s — 이하면 정지 명령으로 간주 */'
assert s.count(old) == 1
s = s.replace(old, '/* 정지 명령 문턱은 rover_platform.h SPEED_CTRL_STOP_THRESH_MPS (2026-09-17: 여기 있던 TARGET_THRESH 0.01 이동·0.005 로 변경) */')
n = s.count('TARGET_THRESH'); s = s.replace('fabsf(target_mps) < TARGET_THRESH', 'fabsf(target_mps) < SPEED_CTRL_STOP_THRESH_MPS').replace('fabsf(p->target_mps) < TARGET_THRESH', 'fabsf(p->target_mps) < SPEED_CTRL_STOP_THRESH_MPS')
assert 'TARGET_THRESH)' not in s and s.count('SPEED_CTRL_STOP_THRESH_MPS') == 3, s.count('SPEED_CTRL_STOP_THRESH_MPS')
wr(p, s)

# ---- 3) safety_monitor.c ----
p = '/App/app/safety_monitor.c'; s = rd(p)
old = '#include "speed_controller.h"'
assert s.count(old) == 1
s = s.replace(old, old + NL + '#include "rover_platform.h"   /* STALL_TARGET_THRESH_MPS (= 정지 문턱, 2026-09-17 한 곳으로) */')
old = '#define V_TARGET_THRESH    0.010f /* 정지 지령(speed_controller TARGET_THRESH) 제외용 */'
assert s.count(old) == 1
s = s.replace(old, '/* 정지 지령 제외 문턱은 rover_platform.h STALL_TARGET_THRESH_MPS (= SPEED_CTRL_STOP_THRESH_MPS). 2026-09-17: 0.010 → 0.005 */')
assert s.count('fabsf(tgt) > V_TARGET_THRESH') == 1
s = s.replace('fabsf(tgt) > V_TARGET_THRESH', 'fabsf(tgt) > STALL_TARGET_THRESH_MPS')
assert 'V_TARGET_THRESH' not in s.replace('STALL_TARGET_THRESH_MPS', '')
wr(p, s)
