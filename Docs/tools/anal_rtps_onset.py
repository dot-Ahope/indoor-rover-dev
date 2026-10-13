#!/usr/bin/env python3
"""anal_rtps_onset — 포화가 시작되는 몇 초를 잘게(기본 0.2 s) 나눠, 어느 읽는 쪽이 먼저 뒤처졌는지 본다. (2026-10-13)
  왜: anal_rtps_pcap 으로 포화의 정체(/tf 발행자 2 곳의 HEARTBEAT 폭주)는 봤지만 '누가 먼저'는 창 평균으로는 안 보인다.
  출력: 칸마다 ① /tf 로 간 DATA·HEARTBEAT 수(발행자별) ② ACKNACK 을 가장 많이 보낸 읽는 쪽 3 곳 ③ HEARTBEAT 이 가장 많이 향한 읽는 쪽 3 곳.
        첫 칸들에서 혼자 튀는 읽는 쪽이 방아쇠 후보다.
  사용: anal_rtps_onset.py CAP.pcap HH:MM:SS 길이(s) [--step 0.2] [--netlog net.log] [--topic rt/tf]
  anal_rtps_pcap.py 와 같은 폴더에 있어야 한다(읽기 함수 공유)."""
import sys, time, collections, argparse, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anal_rtps_pcap import packets, submessages, sedp_topic

ap = argparse.ArgumentParser(); ap.add_argument('pcap'); ap.add_argument('start'); ap.add_argument('dur', type=float)
ap.add_argument('--step', type=float, default=0.2); ap.add_argument('--netlog'); ap.add_argument('--topic', default='rt/tf'); a = ap.parse_args()
pid2 = {}
if a.netlog:
    for l in open(a.netlog, errors='replace'):
        f = l.split()
        if len(f) >= 4 and f[0] == 'MAP': pid2[int(f[2]) & 0xffff] = f[3]
def pn(p): return '%s[%s]' % (pid2.get(p[4] | (p[5] << 8), '?'), p.hex()[8:16]) if p else '(모두)'
# 1 차: 토픽 이름(탐색 정보는 캡처 어디에나 있을 수 있어 전체를 훑되 탐색 포트만)
topics = {}; t0 = None
for t, ol, dport, pl in packets(a.pcap):
    if t0 is None: t0 = t
    if dport % 2 == 1 or pl[:4] != b'RTPS': continue
    for k, body, fl, src, dst in (submessages(pl) or []):
        if k == 'DATA' and len(body) >= 12 and body[8:12].hex() in ('000003c2', '000004c2'):
            r = sedp_topic(body, fl)
            if r: topics[r[0]] = r[1]
W = {g for g, n in topics.items() if n == a.topic and g[15] in (0x02, 0x03)}   # 쓰는 쪽 끝점(entity kind 0x02/0x03)
ts = time.mktime(time.strptime(time.strftime('%Y-%m-%d ', time.localtime(t0)) + a.start, '%Y-%m-%d %H:%M:%S'))
print('%s 의 쓰는 쪽 %d 곳: %s' % (a.topic, len(W), ', '.join(pn(g[:12]) for g in W)))
B = collections.defaultdict(lambda: dict(d=collections.Counter(), hb=collections.Counter(), ack=collections.Counter(), hbto=collections.Counter(), n=0))
for t, ol, dport, pl in packets(a.pcap):
    if t < ts: continue
    if t >= ts + a.dur: break
    b = B[int((t - ts) / a.step)]; b['n'] += 1
    for k, body, fl, src, dst in (submessages(pl) or []):
        if len(body) < 12: continue
        if k in ('DATA', 'DATA_FRAG') and (src + body[8:12]) in W: b['d'][src] += 1
        elif k == 'HEARTBEAT' and (src + body[4:8]) in W: b['hb'][src] += 1; b['hbto'][dst] += 1
        elif k == 'ACKNACK' and dst and (dst + body[4:8]) in W: b['ack'][src] += 1
print('칸 시작   전체pkt | /tf DATA(발행자별) | /tf HEARTBEAT | ACKNACK 상위 3 (보낸 읽는 쪽) | HEARTBEAT 이 향한 곳 상위 3')
for i in sorted(B):
    b = B[i]; f = lambda c, n=3: ' '.join('%s %d' % (pn(k), v) for k, v in c.most_common(n))
    print('%s.%d %6d | %s | %s | %s | %s' % (time.strftime('%H:%M:%S', time.localtime(ts + i * a.step)), int(((ts + i * a.step) % 1) * 10), b['n'],
          ' '.join('%s %d' % (pn(k).split('[')[0][:6], v) for k, v in b['d'].most_common(2)) or '-', sum(b['hb'].values()), f(b['ack']) or '-', f(b['hbto']) or '-'))
