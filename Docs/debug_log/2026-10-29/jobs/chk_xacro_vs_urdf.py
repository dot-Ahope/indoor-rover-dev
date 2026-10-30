#!/usr/bin/env python3
"""chk_xacro_vs_urdf — rover.urdf.xacro 를 펼쳐(인자 기본값 · property · ${식} · 매크로) rover.urdf 와 관절(joint)별로 비교 (10-30, PC).
  xacro 패키지 없이 쓰는 작은 전개기: $(arg x) · ${식}(math 함수) · <xacro:macro> 한 단계 호출만 지원 — 이 파일 정도면 충분.
  비교: 관절 이름 집합 · parent/child · origin xyz/rpy(허용 1e-4) · 링크 이름 집합.
  인자: [xacro 경로] [urdf 경로] (기본 = 저장소 rover_description/urdf)"""
import sys, re, math
import xml.etree.ElementTree as ET
from pathlib import Path

D = Path(__file__).resolve().parents[4] / 'ros2_ws/src/rover_description/urdf'
XA = Path(sys.argv[1]) if len(sys.argv) > 1 else D / 'rover.urdf.xacro'
UR = Path(sys.argv[2]) if len(sys.argv) > 2 else D / 'rover.urdf'
NS = '{http://www.ros.org/wiki/xacro}'
root = ET.parse(XA).getroot()
args = {a.get('name'): a.get('default') for a in root.iter(NS + 'arg')}
props = {}
def ev(s, local=None):
    env = {k: getattr(math, k) for k in dir(math) if not k.startswith('_')}
    env.update(props); env.update(local or {})
    s = re.sub(r'\$\(arg (\w+)\)', lambda m: args[m.group(1)], s)
    def rep(m):
        v = eval(m.group(1), {'__builtins__': {}}, env)
        return repr(v) if isinstance(v, float) else str(v)
    while '${' in s: s = re.sub(r'\$\{([^{}]*)\}', rep, s)
    return s
for p in root.iter(NS + 'property'):
    v = ev(p.get('value'))
    try: v = float(v)
    except ValueError: pass
    props[p.get('name')] = v
macros = {m.get('name'): m for m in root.iter(NS + 'macro')}
def expand(el, local=None):
    out = []
    for c in list(el):
        if c.tag.startswith(NS):
            nm = c.tag[len(NS):]
            if nm in macros:
                loc = dict(local or {}); loc.update({k: (float(v) if re.match(r'^-?[\d.]+$', v) else v) for k, v in c.attrib.items()})
                out += expand(macros[nm], loc)
            continue
        n = ET.Element(c.tag, {k: ev(v, local) for k, v in c.attrib.items()})
        for g in expand(c, local): n.append(g)
        out.append(n)
    return out
X = ET.Element('robot'); [X.append(e) for e in expand(root)]
U = ET.parse(UR).getroot()
def joints(r):
    J = {}
    for j in r.findall('joint'):
        o = j.find('origin')
        J[j.get('name')] = (j.find('parent').get('link'), j.find('child').get('link'),
                            [float(v) for v in o.get('xyz').split()], [float(v) for v in o.get('rpy').split()])
    return J
jx, ju = joints(X), joints(U)
lx, lu = {l.get('name') for l in X.findall('link')}, {l.get('name') for l in U.findall('link')}
print('링크: xacro %d · urdf %d · 한쪽에만 %s' % (len(lx), len(lu), sorted(lx ^ lu) or '없음'))
print('관절: xacro %d · urdf %d · 한쪽에만 %s' % (len(jx), len(ju), sorted(set(jx) ^ set(ju)) or '없음'))
bad = 0
for n in sorted(set(jx) & set(ju)):
    a, b = jx[n], ju[n]; dx = max(abs(p - q) for p, q in zip(a[2] + a[3], b[2] + b[3]))
    ok = a[0] == b[0] and a[1] == b[1] and dx < 1e-4; bad += not ok
    print('  %-22s %s  xacro xyz %s rpy %s | urdf xyz %s rpy %s | 최대 차 %.2e' % (
        n, 'OK ' if ok else 'BAD', ['%.5f' % v for v in a[2]], ['%.5f' % v for v in a[3]],
        ['%.5f' % v for v in b[2]], ['%.5f' % v for v in b[3]], dx))
print('판정: %s' % ('같음' if bad == 0 and lx == lu and set(jx) == set(ju) else '다름 %d' % bad))
