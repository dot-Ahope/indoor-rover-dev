#!/usr/bin/env python3
"""place_cmd — place_server 에 명령을 보내고 결과를 기다리는 창구 (F2.5 S1, 2026-10-28).
  사용: place_cmd.py "go_to B" | "return" | "stop" | "list" | "where"   [--wait 초] [--no-wait]
        여러 명령을 한 프로세스로(DDS 참여자 1 개 — 10-13 §2.1: 명령마다 새 참여자 = 탐색 통신 급증): "go_to B; go_to C; return"
        명령 뒤 '@stopN' = 이동이 시작(moving)되고 N 초 뒤 stop 을 보냄(정지 시험) — 그 명령은 canceled 가 정상.
        'wait N' = N 초 쉼.
  --wait: 명령 하나당 끝 상태를 기다리는 최대 초(기본 go_to · return 300, 나머지 5). --no-wait: accepted 까지만.
  출력: 받은 /place/status 를 순서대로 + 명령마다 소요. 끝 상태(arrived · checked · failed · canceled · rejected · info)에서 다음 명령.
  종료 코드: 모든 명령이 기대 상태(go_to · return → arrived/checked, @stop → canceled, stop → canceled, list · where → info)면 0.
  기대와 다르면 거기서 멈추고 1(뒤 명령을 보내지 않음 — 실패 뒤 이동을 이어 가지 않게)."""
import sys, json, time, uuid
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

argv = sys.argv[1:]; nowait = '--no-wait' in argv; WAIT = None
if '--wait' in argv:
    i = argv.index('--wait'); WAIT = float(argv[i + 1]); del argv[i:i + 2]
argv = [a for a in argv if a != '--no-wait']
cmds = [c.strip() for c in ' '.join(argv).split(';') if c.strip()]
rclpy.init(); n = Node('place_cmd_%s' % uuid.uuid4().hex[:6]); got = []
n.create_subscription(String, '/place/status', lambda m: got.append(m.data), 10)
pub = n.create_publisher(String, '/place/command', 10)
T0 = time.time()
# 10-28 §10: 명령 쪽(우리 → 서버)만 연결 확인하고 바로 보냈더니 f2pl3 에서 첫 'where' 가 서버에 닿지 않음(서버 로그에 수신 흔적 없음).
# → 양방향(서버의 /place/status 발행자까지) 연결을 확인하고 1 s 더 기다린 뒤 보낸다.
while (pub.get_subscription_count() == 0 or n.count_publishers('/place/status') == 0) and time.time() - T0 < 10: rclpy.spin_once(n, timeout_sec=0.1)
if pub.get_subscription_count() == 0 or n.count_publishers('/place/status') == 0: print('place_server 없음(명령 구독 %d · 상태 발행 %d)' % (pub.get_subscription_count(), n.count_publishers('/place/status'))); sys.exit(1)
te = time.time() + 1.0
while time.time() < te: rclpy.spin_once(n, timeout_sec=0.1)


def send(text):
    rid = uuid.uuid4().hex[:8]; m = String(); m.data = '%s|%s' % (rid, text); pub.publish(m); return rid


rc = 0
for c in cmds:
    if c.startswith('wait '):
        te = time.time() + float(c.split()[1])
        while time.time() < te: rclpy.spin_once(n, timeout_sec=0.1)
        continue
    stop_after = None
    if '@stop' in c: c, s = c.split('@stop'); c = c.strip(); stop_after = float(s)
    head = c.split()[0].lower() if c else ''
    wait = WAIT if WAIT else (300.0 if head in ('go_to', 'return') else 5.0)
    want = ('canceled',) if (stop_after is not None or head == 'stop') else (('arrived', 'checked') if head in ('go_to', 'return') else ('info',))
    rid = send(c); t0 = time.time(); last = None; t_move = None; stop_sent = False
    print('>> %s%s' % (c, ' (@stop %g s)' % stop_after if stop_after is not None else ''), flush=True)
    while time.time() - t0 < wait:
        rclpy.spin_once(n, timeout_sec=0.1)
        if head in ('where', 'list') and last is None and time.time() - t0 > 2.0 and not stop_sent:
            rid = send(c); stop_sent = True; print('   %.1f s  (응답 없음 — 한 번 다시 보냄, 조회 명령만)' % (time.time() - t0), flush=True)   # 조회는 되풀이해도 무해
        if stop_after is not None and t_move and not stop_sent and time.time() - t_move >= stop_after:
            send('stop'); stop_sent = True; print('   %.1f s  (stop 보냄)' % (time.time() - t0), flush=True)
        while got:
            try: d = json.loads(got.pop(0))
            except ValueError: continue
            if d.get('id') != rid: continue
            print('   %.1f s  %s  %s  %s' % (time.time() - t0, d['state'], d.get('place') or '', d.get('detail') or ''), flush=True)
            last = d['state']
            if last == 'moving': t_move = time.time()
        if last in ('arrived', 'checked', 'failed', 'canceled', 'rejected', 'info') or (nowait and last == 'accepted'): break
    ok = (last in want) or (nowait and last == 'accepted')
    print('<< %s → %s (%s) %.1f s' % (c, last or '끝 상태 없음', '기대대로' if ok else '기대 %s' % '/'.join(want), time.time() - t0), flush=True)
    if not ok: rc = 1; break
rclpy.shutdown(); sys.exit(rc)
