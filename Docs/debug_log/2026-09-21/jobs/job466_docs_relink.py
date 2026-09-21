#!/usr/bin/env python3
"""Docs 폴더 재구성(2026-09-21)에 따른 링크·경로 수정. 인자: REPO_ROOT [MEMORY_DIR]
  1) 'Docs/<옛이름>' / 'docs/<옛이름>' 형태의 경로 → 'Docs/<새폴더>/<옛이름>' (모든 대상 파일)
  2) 이동한 md 안의 상대 링크 ](target) 는 옛 위치(Docs/) 기준으로 풀고, 이동표를 거쳐 새 위치 기준으로 다시 상대화
  3) debug_log 는 손대지 않는다(날짜 기록 원문). INDEX.md 는 따로 새로 쓴다.
  마지막에 debug_log 밖 모든 md 의 상대 링크 존재 여부를 검사해 깨진 것을 출력.
"""
import os, re, sys, io
ROOT = sys.argv[1]; MEM = sys.argv[2] if len(sys.argv) > 2 else None
D = os.path.join(ROOT, 'Docs')
MOVES = {}   # 옛 경로(리포 기준) → 새 경로
for f in ['FIRMWARE_DEV_PLAN.md', 'F0_CUBEMX_SETUP.md', 'F1_VERIFICATION.md', 'F2_VERIFICATION.md', 'F3_VERIFICATION.md', 'F4_VERIFICATION.md',
          'F5a_MICROROS_LIB.md', 'F5b_VERIFICATION.md', 'F5c_VERIFICATION.md', 'F6_VERIFICATION.md', 'F7.5_VERIFICATION.md', 'F7_VERIFICATION.md',
          'F8_VERIFICATION.md', 'BUILD_AND_FLASH_GUIDE.md', 'F103_to_G474_pin_migration.md', 'ICM-20948_magnetometer_SPI.md', 'STM32BD']:
    MOVES['Docs/' + f] = 'Docs/01_firmware/' + f
MOVES['ROVER_SERIAL_PROTOCOL_v1.0.md'] = 'Docs/01_firmware/legacy/ROVER_SERIAL_PROTOCOL_v1.0.md'
for f in ['WT600_UPDATE_BRIEF.md', 'rover.urdf', 'rover.urdf.xacro', 'rover_top_down_layout.svg', 'MOTOR_1TO90_MIGRATION_PLAN.md']:
    MOVES['Docs/' + f] = 'Docs/02_hardware/' + f
for f in ['JETSON_SETUP_BRIEF.md', 'Jetson']:
    MOVES['Docs/' + f] = 'Docs/03_jetson/' + f
for f in ['NAV2_EXPLORATION_PLAN.md', 'PASSAGE_PROBLEM_ANALYSIS_2026-09-16.md', 'TEST_COURSE_AND_GATES.md']:
    MOVES['Docs/' + f] = 'Docs/04_navigation/' + f
MOVES['Docs/NVBLOX_MIGRATION_PLAN.md'] = 'Docs/05_nvblox/NVBLOX_MIGRATION_PLAN.md'
NEW_OF_OLD = {k: v for k, v in MOVES.items()}
MOVED_NEW = set(MOVES.values())


def norm(p):
    return p.replace('\\', '/')


def rel(from_dir, to_path):
    return norm(os.path.relpath(to_path, from_dir))


def fix_abs_paths(s):
    """'Docs/<옛>' 또는 'docs/<옛>' (앞에 ./ 가능) → 새 경로. 이미 새 폴더가 붙은 것은 건드리지 않음."""
    n = 0
    for old, new in MOVES.items():
        if not old.startswith('Docs/'):
            continue
        base = old[len('Docs/'):]
        pat = re.compile(r'(?<![\w/])(\./)?[Dd]ocs/' + re.escape(base) + r'(?![\w.-])')
        s, k = pat.subn(lambda m: (m.group(1) or '') + new, s); n += k
    # 루트의 옛 프로토콜 문서
    pat = re.compile(r'(?<![\w/])(\./)?ROVER_SERIAL_PROTOCOL_v1\.0\.md')
    s, k = pat.subn(lambda m: (m.group(1) or '') + 'Docs/01_firmware/legacy/ROVER_SERIAL_PROTOCOL_v1.0.md', s); n += k
    return s, n


LINK = re.compile(r'(\]\()([^)\s#]+)(#[^)]*)?(\))')


def fix_rel_links(s, old_dir_repo, new_dir_repo):
    """이동한 md 의 상대 링크: 옛 디렉토리 기준으로 풀어 이동표 적용 후 새 디렉토리 기준 상대경로로."""
    n = 0

    def repl(m):
        nonlocal n
        t = m.group(2)
        if re.match(r'^[a-z]+:', t) or t.startswith('/'):
            return m.group(0)
        tgt = norm(os.path.normpath(os.path.join(old_dir_repo, t)))
        if tgt in NEW_OF_OLD:
            tgt = NEW_OF_OLD[tgt]
        elif tgt.startswith('Docs/') and tgt not in MOVED_NEW:
            # 옛 Docs/ 안 상대 링크였으나 이동표에 없음(예: debug_log/…, INDEX.md) → 그대로 재상대화
            pass
        newt = rel(new_dir_repo, tgt)
        if newt != t:
            n += 1
        return m.group(1) + newt + (m.group(3) or '') + m.group(4)
    return LINK.sub(repl, s), n


def process(path_repo, old_dir=None):
    p = os.path.join(ROOT, path_repo)
    s = io.open(p, encoding='utf-8', newline='').read(); s0 = s
    s, a = fix_abs_paths(s)
    b = 0
    if old_dir is not None and path_repo.endswith('.md'):
        s, b = fix_rel_links(s, old_dir, norm(os.path.dirname(path_repo)))
    if s != s0:
        io.open(p, 'w', encoding='utf-8', newline='').write(s)
    return a, b


targets = ['CLAUDE.md', 'PROJECT_OVERVIEW.md', 'ros2_ws/README.md', 'ros2_ws/src/rover_description/launch/description.launch.py']
for t in targets:
    if os.path.exists(os.path.join(ROOT, t)):
        print('%-70s abs %d' % (t, process(t)[0]))
for old, new in MOVES.items():
    if new.endswith('.md') and os.path.exists(os.path.join(ROOT, new)):
        a, b = process(new, old_dir=norm(os.path.dirname(old)) or '.')
        print('%-70s abs %d rel %d' % (new, a, b))
# 이동하지 않은 Docs 상위 md(INDEX 제외)는 없음. 메모리
if MEM:
    for f in sorted(os.listdir(MEM)):
        if f.endswith('.md'):
            p = os.path.join(MEM, f); s = io.open(p, encoding='utf-8', newline='').read(); s2, n = fix_abs_paths(s)
            if n:
                io.open(p, 'w', encoding='utf-8', newline='').write(s2); print('memory %-40s abs %d' % (f, n))
# 링크 검사
print('== 깨진 상대 링크 (debug_log 제외)')
bad = 0
for dp, dn, fn in os.walk(ROOT):
    dpn = norm(dp)
    if '/.git' in dpn or 'debug_log' in dpn or 'Docs_Beginner' in dpn or '전자회로기초' in dpn or 'firmware/rover_jupiter_fw' in dpn:
        continue
    for f in fn:
        if not f.endswith('.md'):
            continue
        p = os.path.join(dp, f); s = io.open(p, encoding='utf-8', errors='replace').read()
        for m in LINK.finditer(s):
            t = m.group(2)
            if re.match(r'^[a-z]+:', t) or t.startswith('/') or t.startswith('#'):
                continue
            if not os.path.exists(os.path.normpath(os.path.join(dp, t))):
                bad += 1; print('  %s -> %s' % (norm(os.path.relpath(p, ROOT)), t))
print('깨진 링크 %d' % bad)
