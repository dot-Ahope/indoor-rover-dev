#!/usr/bin/env python3
"""anal_rtps_pcap — 루프백 캡처(pcap)에서 DDS(RTPS) 패킷을 종류·보낸 쪽·받는 쪽별로 센다. (2026-10-13)
  왜: 포화 때 UDP 수신이 5,300 → 6~8 만 개/s 로 늘어나는데(10-12 §9.2) 그 패킷이 무엇이고 누가 보내는지는 재지 못했다.
  입력: tcpdump -i lo -s 512 -w <pcap> udp 로 잡은 파일. 표준 라이브러리만 쓴다(Jetson 에서 그대로 실행).
  동작: 1 차 = 2 s 칸마다 패킷 수(포화 시작 = 평상 중앙값의 4 배를 넘는 칸이 3 칸 이어지는 첫 칸. --onset 으로 지정 가능)
        2 차 = '평상 창'(시작 전 20 s)과 '포화 창'(시작 뒤 20 s)의 패킷을 풀어 집계:
          · 하위 메시지 종류(DATA · DATA_FRAG · HEARTBEAT · ACKNACK · NACK_FRAG · GAP · HEARTBEAT_FRAG …)
          · 쓰는 쪽 끝점(참여자 + writer id → 토픽 이름: 캡처에 들어온 탐색 정보(SEDP)로 붙임, 없으면 id 그대로)
          · 받는 쪽 포트(→ 프로세스: --netlog 의 소켓·프로세스 표로 붙임)
  사용: anal_rtps_pcap.py CAP.pcap [--netlog net_<이름>.log] [--onset HH:MM:SS] [--win 20]
  한계: 참여자 → 프로세스 대응은 Fast DDS 가 GUID 에 넣는 pid 로 추정한다(컨테이너 안 프로세스는 pid 가 달라 '?' 로 남는다).
        -s 512 로 잘린 패킷은 앞부분만 본다(종류·끝점 판별에는 충분, 탐색 정보의 토픽 이름은 잘리면 못 읽음)."""
import sys, struct, time, collections, argparse

KIND = {0x06: 'ACKNACK', 0x07: 'HEARTBEAT', 0x08: 'GAP', 0x09: 'INFO_TS', 0x0c: 'INFO_SRC', 0x0e: 'INFO_DST', 0x12: 'NACK_FRAG',
        0x13: 'HEARTBEAT_FRAG', 0x15: 'DATA', 0x16: 'DATA_FRAG', 0x01: 'PAD', 0x0d: 'INFO_REPLY_IP4', 0x0f: 'INFO_REPLY'}
WRITER_SIDE = ('DATA', 'DATA_FRAG', 'HEARTBEAT', 'GAP', 'HEARTBEAT_FRAG'); READER_SIDE = ('ACKNACK', 'NACK_FRAG')
BUILTIN = {'000100c2': '(탐색: 참여자 알림)', '000003c2': '(탐색: 발행 끝점 목록)', '000004c2': '(탐색: 구독 끝점 목록)', '000200c2': '(생존 신호)',
           '000100c7': '(탐색: 참여자 알림)', '000003c7': '(탐색: 발행 끝점 목록)', '000004c7': '(탐색: 구독 끝점 목록)', '000200c7': '(생존 신호)'}


def packets(path):
    """(t, 원래 길이, UDP dst 포트, UDP 페이로드) 를 차례로 낸다."""
    with open(path, 'rb') as f:
        gh = f.read(24)
        if len(gh) < 24: return
        magic = gh[:4]
        if magic in (b'\xd4\xc3\xb2\xa1', b'\x4d\x3c\xb2\xa1'): end, ns = '<', magic == b'\x4d\x3c\xb2\xa1'
        elif magic in (b'\xa1\xb2\xc3\xd4', b'\xa1\xb2\x3c\x4d'): end, ns = '>', magic == b'\xa1\xb2\x3c\x4d'
        else: raise SystemExit('pcap 형식이 아님(pcapng 이면 tcpdump -w 로 다시)')
        link = struct.unpack(end + 'I', gh[20:24])[0]; l2 = {1: 14, 113: 16, 276: 20, 0: 4, 101: 0}.get(link)
        if l2 is None: raise SystemExit('모르는 링크 종류 %d' % link)
        rh = struct.Struct(end + 'IIII')
        while True:
            h = f.read(16)
            if len(h) < 16: return
            s, us, incl, orig = rh.unpack(h); d = f.read(incl)
            if len(d) < incl: return
            ip = d[l2:]
            if len(ip) < 28 or (ip[0] >> 4) != 4 or ip[9] != 17: continue
            ihl = (ip[0] & 15) * 4; udp = ip[ihl:]
            if len(udp) < 8: continue
            yield s + us / (1e9 if ns else 1e6), orig, struct.unpack('>H', udp[2:4])[0], udp[8:]


def submessages(p):
    """RTPS 페이로드 → (종류, 본문, 보낸 참여자, 받는 참여자) 목록. 잘린 패킷은 읽을 수 있는 데까지."""
    if len(p) < 20 or p[:4] != b'RTPS': return None
    src = p[8:20]; dst = None; pos = 20; out = []
    while pos + 4 <= len(p):
        sid, fl = p[pos], p[pos + 1]; ln = struct.unpack('<H' if fl & 1 else '>H', p[pos + 2:pos + 4])[0]
        body = p[pos + 4:pos + 4 + ln] if ln else p[pos + 4:]
        k = KIND.get(sid, 'x%02x' % sid)
        if k == 'INFO_DST' and len(body) >= 12: dst = body[:12]
        elif not k.startswith('INFO') and k != 'PAD': out.append((k, body, fl, src, dst))
        if ln == 0: break
        pos += 4 + ln
    return out


def sedp_topic(body, fl):
    """탐색 DATA(발행·구독 끝점 목록)에서 (끝점 GUID 16 B, 토픽 이름) 을 꺼낸다. 못 읽으면 None."""
    try:
        o2q = struct.unpack('<H' if fl & 1 else '>H', body[2:4])[0]; pos = 4 + o2q; e = '<' if fl & 1 else '>'
        if fl & 2:   # 인라인 QoS 건너뜀
            while pos + 4 <= len(body):
                pid, ln = struct.unpack(e + 'HH', body[pos:pos + 4]); pos += 4 + ln
                if pid == 1: break
        enc = body[pos:pos + 2]; pe = '<' if enc == b'\x00\x03' else '>'; pos += 4; guid = topic = None
        while pos + 4 <= len(body):
            pid, ln = struct.unpack(pe + 'HH', body[pos:pos + 4]); v = body[pos + 4:pos + 4 + ln]; pos += 4 + ln
            if pid == 1: break
            if pid == 0x005a and len(v) >= 16: guid = v[:16]
            elif pid == 0x0005 and len(v) >= 4:
                n = struct.unpack(pe + 'I', v[:4])[0]; topic = v[4:4 + n].rstrip(b'\0').decode('ascii', 'replace')
        return (guid, topic) if guid and topic else None
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('pcap'); ap.add_argument('--netlog'); ap.add_argument('--onset'); ap.add_argument('--win', type=float, default=20.0)
    a = ap.parse_args()
    # 1 차: 2 s 칸
    bins = collections.Counter(); byts = collections.Counter(); t0 = None; n = 0
    for t, ol, dport, pl in packets(a.pcap):
        if t0 is None: t0 = t
        b = int((t - t0) // 2); bins[b] += 1; byts[b] += ol; n += 1
    if not n: raise SystemExit('UDP 패킷 없음')
    ks = sorted(bins); rate = [bins[k] / 2 for k in ks]; med = sorted(rate)[len(rate) // 2]
    print('캡처 %s ~ %s (%.0f s), 패킷 %d 개, 2 s 칸 중앙 %.0f 개/s' % (time.strftime('%H:%M:%S', time.localtime(t0)), time.strftime('%H:%M:%S', time.localtime(t0 + 2 * (ks[-1] + 1))), 2 * (ks[-1] + 1), n, med))
    onset = None
    if a.onset:
        lt = time.localtime(t0); onset = time.mktime(time.strptime(time.strftime('%Y-%m-%d ', lt) + a.onset, '%Y-%m-%d %H:%M:%S'))
    else:
        for i in range(len(ks) - 2):
            if all(bins[ks[i] + j] / 2 > 4 * med for j in range(3)): onset = t0 + 2 * ks[i]; break
    print('2 s 칸(개/s · kB/s): ' + ' '.join('%s %d·%d' % (time.strftime('%M:%S', time.localtime(t0 + 2 * k)), bins[k] / 2, byts[k] / 2000) for k in ks))
    if onset is None:
        print('포화 시작을 못 찾음(4 배가 3 칸 이어지는 곳 없음) → 캡처 전체를 한 창으로 집계'); wins = [('전체', t0, t0 + 2 * (ks[-1] + 1))]
    else:
        print('포화 시작 %s' % time.strftime('%H:%M:%S', time.localtime(onset))); wins = [('평상(시작 전 %.0f s)' % a.win, onset - a.win - 4, onset - 4), ('포화(시작 뒤 %.0f s)' % a.win, onset + 2, onset + 2 + a.win)]
    # 프로세스 대응표
    port2proc = {}; pid2proc = {}
    if a.netlog:
        ino2 = {}; socks = {}
        for l in open(a.netlog, errors='replace'):
            f = l.split()
            if len(f) >= 4 and f[0] == 'MAP': ino2[f[1]] = f[3]; pid2proc[int(f[2]) & 0xffff] = f[3]
            elif len(f) >= 5 and f[1] == 'SOCK': socks[int(f[2].split(':')[-1], 16)] = f[4]
        port2proc = {p: ino2.get(i, '?') for p, i in socks.items()}
    def pname(prefix):
        if prefix is None: return '(모두)'
        pid = prefix[4] | (prefix[5] << 8); return '%s[%s]' % (pid2proc.get(pid, '?'), prefix.hex()[8:])
    # 2 차: 창 집계
    topics = {}; agg = {w[0]: dict(kind=collections.Counter(), kbytes=collections.Counter(), wr=collections.Counter(), rd=collections.Counter(), dst=collections.Counter(), n=0, nb=0, nr=0) for w in wins}
    for t, ol, dport, pl in packets(a.pcap):
        sm = None
        w = next((x for x in wins if x[1] <= t < x[2]), None)
        if w is None and (dport % 2 == 1 or pl[:4] != b'RTPS'): continue   # 창 밖에서는 탐색 포트(짝수)만 읽어 토픽 이름을 모음
        sm = submessages(pl)
        if sm is None:
            if w: agg[w[0]]['nr'] += 1
            continue
        for k, body, fl, src, dst in sm:   # 토픽 이름은 캡처 전체에서 모음
            if k == 'DATA' and len(body) >= 12 and body[8:12].hex() in ('000003c2', '000004c2'):
                r = sedp_topic(body, fl)
                if r: topics[r[0]] = r[1]
        if w is None: continue
        A = agg[w[0]]; A['n'] += 1; A['nb'] += ol; A['dst'][port2proc.get(dport, 'port %d' % dport)] += 1
        for k, body, fl, src, dst in sm:
            A['kind'][k] += 1
            if len(body) < 12: continue
            if k in WRITER_SIDE:
                off = 4 if k in ('DATA', 'DATA_FRAG') else 0; wid = body[off + 4:off + 8]; A['wr'][(k, src + wid)] += 1
                if k in ('DATA', 'DATA_FRAG'): A['kbytes'][(src + wid)] += ol
            elif k in READER_SIDE:
                wid = body[4:8]; A['rd'][(k, src, (dst + wid) if dst else None)] += 1
    def ename(g):
        if g is None: return '?'
        e = g[12:16].hex(); return '%s %s' % (pname(g[:12]), topics.get(g, BUILTIN.get(e, 'entity ' + e)))
    print('탐색 정보로 읽은 토픽 이름 %d 개' % len(topics))
    for name, t1, t2 in wins:
        A = agg[name]; dur = t2 - t1
        print('\n== %s: RTPS 패킷 %.0f 개/s · %.0f kB/s (RTPS 아닌 UDP %.0f 개/s)' % (name, A['n'] / dur, A['nb'] / dur / 1000, A['nr'] / dur))
        tot = sum(A['kind'].values()) or 1
        print('  하위 메시지 종류(개/s · 비율): ' + ' · '.join('%s %.0f (%.0f %%)' % (k, v / dur, 100 * v / tot) for k, v in A['kind'].most_common(8)))
        print('  쓰는 쪽이 보낸 것 상위(개/s):')
        for (k, g), v in A['wr'].most_common(14): print('    %7.0f  %-14s %s' % (v / dur, k, ename(g)))
        print('  읽는 쪽이 보낸 것 상위(개/s) — 누가 → 어느 발행 끝점에:')
        for (k, src, g), v in A['rd'].most_common(10): print('    %7.0f  %-10s %s → %s' % (v / dur, k, pname(src), ename(g)))
        print('  받는 프로세스 상위(패킷/s): ' + ' · '.join('%s %.0f' % (k, v / dur) for k, v in A['dst'].most_common(10)))


if __name__ == '__main__':
    main()
