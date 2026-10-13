#!/usr/bin/env python3
"""anal_rtps_acklag — 한 토픽의 쓰는 쪽이 보낸 HEARTBEAT(가진 표본 번호 범위)와 읽는 쪽들이 보낸 ACKNACK(어디까지 받았나)을 시간순으로 맞춰,
  어느 읽는 쪽의 확인이 뒤처졌는지 본다. (2026-10-13)
  왜: 포화는 /tf 발행자가 갑자기 HEARTBEAT 을 쏟아내며 시작됐다(anal_rtps_onset). Fast DDS 는 쓰는 쪽 보관함(history, /tf 는 100 개)이 가득 차면
      매 발행마다 모든 읽는 쪽에 HEARTBEAT 을 보낸다(추정) — 보관함은 '아직 확인 안 한 읽는 쪽'이 있으면 비워지지 않는다.
  출력: 쓰는 쪽마다, HEARTBEAT 시각·first~last 번호(보관 개수), 그 뒤 1 s 안의 ACKNACK 중 가장 뒤처진 읽는 쪽 3 곳(last − 확인 번호).
  사용: anal_rtps_acklag.py CAP.pcap HH:MM:SS 길이(s) [--netlog net.log] [--topic rt/tf]"""
import sys, time, struct, collections, argparse, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anal_rtps_pcap import packets, submessages, sedp_topic

ap = argparse.ArgumentParser(); ap.add_argument('pcap'); ap.add_argument('start'); ap.add_argument('dur', type=float); ap.add_argument('--netlog'); ap.add_argument('--topic', default='rt/tf'); a = ap.parse_args()
pid2 = {}
if a.netlog:
    for l in open(a.netlog, errors='replace'):
        f = l.split()
        if len(f) >= 4 and f[0] == 'MAP': pid2[int(f[2]) & 0xffff] = f[3]
def pn(p): return '%s[%s]' % (pid2.get(p[4] | (p[5] << 8), '?'), p.hex()[8:16])
def sn(b, e): hi, lo = struct.unpack(e + 'iI', b); return (hi << 32) | lo
topics = {}; t0 = None
for t, ol, dport, pl in packets(a.pcap):
    if t0 is None: t0 = t
    if dport % 2 == 1 or pl[:4] != b'RTPS': continue
    for k, body, fl, src, dst in (submessages(pl) or []):
        if k == 'DATA' and len(body) >= 12 and body[8:12].hex() in ('000003c2', '000004c2'):
            r = sedp_topic(body, fl)
            if r: topics[r[0]] = r[1]
W = {g for g, n in topics.items() if n == a.topic and g[15] in (0x02, 0x03)}
ts = time.mktime(time.strptime(time.strftime('%Y-%m-%d ', time.localtime(t0)) + a.start, '%Y-%m-%d %H:%M:%S'))
HB = collections.defaultdict(list); ACK = collections.defaultdict(list); nread = collections.defaultdict(set)
for t, ol, dport, pl in packets(a.pcap):
    if t < ts: continue
    if t >= ts + a.dur: break
    for k, body, fl, src, dst in (submessages(pl) or []):
        e = '<' if fl & 1 else '>'
        if k == 'HEARTBEAT' and len(body) >= 24 and (src + body[4:8]) in W:
            HB[src + body[4:8]].append((t, sn(body[8:16], e), sn(body[16:24], e), bool(fl & 2)))
        elif k == 'ACKNACK' and dst and len(body) >= 20 and (dst + body[4:8]) in W:
            nb = struct.unpack(e + 'I', body[16:20])[0]; ACK[dst + body[4:8]].append((t, src + body[0:4], sn(body[8:16], e), nb)); nread[dst + body[4:8]].add(src + body[0:4])
for w in W:
    hb = HB[w]; ack = ACK[w]
    print('== 쓰는 쪽 %s · HEARTBEAT %d 개 · ACKNACK %d 개 · 확인을 보낸 읽는 쪽 %d 곳' % (pn(w[:12]), len(hb), len(ack), len(nread[w])))
    # 같은 (first,last) 가 여러 목적지로 나가므로 0.05 s 안의 것은 한 묶음
    last_t = -9; shown = 0
    for t, f1, l1, final in hb:
        if t - last_t < 0.25: continue
        last_t = t; shown += 1
        if shown > 14: print('   … (이후 생략: HEARTBEAT 폭주 구간)'); break
        got = {}
        for ta, rd, base, nb in ack:
            if t <= ta < t + 1.0: got[rd] = (base - 1, nb, ta - t)   # base = 아직 못 받은 첫 번호 → base−1 까지 받음
        lag = sorted(((l1 - v[0], rd, v) for rd, v in got.items()), key=lambda x: -x[0])
        print('  %s.%02d HB first %d ~ last %d (보관 %d 개)%s | 1 s 안 확인 %d 곳 | 가장 뒤처진 곳: %s' % (
            time.strftime('%H:%M:%S', time.localtime(t)), int((t % 1) * 100), f1, l1, l1 - f1 + 1, ' final' if final else '', len(got),
            ' · '.join('%s −%d(누락 표시 %d, +%.2f s)' % (pn(rd[:12]), d, v[1], v[2]) for d, rd, v in lag[:3]) or '-'))
