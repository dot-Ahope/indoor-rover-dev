import sys, re
p = sys.argv[1]; NL = chr(10)
s = open(p, encoding='utf-8').read()
def sub1(pat, rep):
    global s
    n = len(re.findall(pat, s)); assert n == 1, (pat, n)
    s = re.sub(pat, rep, s)
note = ("      # ★ 2026-09-17 mp8 (09-17 SUMMARY §7): 목표 0.24 m 옆에서 정지. 경로 크리틱이 목표 0.6/0.4 m 안에서 꺼져 GoalCritic(5) 만 남고," + NL +
        "      #   상자 모서리 때문에 늦게 시작한 중심선 복귀가 끊겼다. 오프라인 MPPI 시뮬(job355, 펌웨어 데드밴드 모델, bag_mp8 t=33 s 12 s):" + NL +
        "      #   현재 0.234 m(실측 0.243 재현) / 문턱 0.2 → 0.144 / 문턱 0.2 + GoalCritic 10 → 0.116 m (xy tol 0.15) → 둘 다 적용." + NL)
sub1(r"(\n)(\s+GoalCritic: \{enabled: true, cost_power: 1, )cost_weight: 5\.0", lambda m: m.group(1) + note + m.group(2) + "cost_weight: 10.0")
sub1(r"(PathAlignCritic: \{[^}]*threshold_to_consider: )0\.40", r"\g<1>0.20")
sub1(r"(PathFollowCritic: \{[^}]*threshold_to_consider: )0\.6", r"\g<1>0.2")
sub1(r"(PathAngleCritic: \{[^}]*threshold_to_consider: )0\.4\b", r"\g<1>0.2")
open(p, 'w', encoding='utf-8', newline=NL).write(s); print('yaml edited')
