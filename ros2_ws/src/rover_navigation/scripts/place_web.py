#!/usr/bin/env python3
"""place_web — 휴대폰 브라우저용 명령 창구 (F2.5, 2026-10-28 §16 — 설계 Docs/07_language/F25_PLACE_LLM_DESIGN.md §3.4 · §8-3 사용자 결정).

place_cmd.py 와 같은 길(/place/command 발행 · /place/status 구독)로 place_server 에 명령을 넣는다. 새 이동 로직 없음.
  · 장소 버튼(등록부 places.yaml 의 이름) → 한 번 더 눌러 확인해야 보냄(주머니 속 오터치로 출발하지 않게)
  · 정지 버튼은 확인 없이 바로 'stop' — 화면 아래 고정
  · 직접 입력 칸: place_server 명령 그대로(go_to B · return · where …). S5 에서 intent_node(문장 해석) 앞단으로 바꿀 자리
  · 상태: 최근 /place/status · 배터리 전압 · 서버 응답 시각(1 s 마다 조회, 끊기면 화면 빨간 띠)
HTTP: 표준 라이브러리 ThreadingHTTPServer(새 의존성 없음), 기본 0.0.0.0:8080.
접근 키: ~/.config/rover_web/key (없으면 만들어 0600) — 주소에 ?k=<키> 를 붙여 연다. 키는 저장소에 넣지 않는다.
  TODO(improve): 같은 망의 누구나 키만 알면 로버를 움직일 수 있다 — 평문 HTTP · 키 하나. 사무실 망 안 개인 시험용 한정.
⚠ 휴대폰 정지는 '보조' 정지 수단이다: Wi-Fi 가 끊기면 닿지 않는다. 1 차는 펌웨어 워치독 · nav_guard · 보드 정지 수단(CLAUDE.md §2).
⚠ DDS 참여자 1 개를 더 만든다 — 주행 30 s 전에는 새로 띄우지 않는다(09-21 규칙). prep 뒤 · 러너 전 상주로 띄울 것.
인자(ROS 파라미터): port(8080) · places_file(기본 = 패키지 share/config/places.yaml)
"""
import json, os, secrets, threading, time, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import yaml
import rclpy
import rclpy.executors
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from std_msgs.msg import String
from sensor_msgs.msg import BatteryState

KEY_FILE = os.path.expanduser('~/.config/rover_web/key')


def load_key():
    if not os.path.exists(KEY_FILE):
        os.makedirs(os.path.dirname(KEY_FILE), exist_ok=True)
        with open(KEY_FILE, 'w') as f: f.write(secrets.token_urlsafe(9))
        os.chmod(KEY_FILE, 0o600)
    return open(KEY_FILE).read().strip()


class PlaceWeb(Node):
    def __init__(self):
        super().__init__('place_web')
        try:
            from ament_index_python.packages import get_package_share_directory
            dflt = os.path.join(get_package_share_directory('rover_navigation'), 'config', 'places.yaml')
        except Exception:
            dflt = ''
        self.declare_parameter('port', 8080); self.declare_parameter('places_file', dflt)
        reg = yaml.safe_load(open(self.get_parameter('places_file').value, encoding='utf-8'))
        self.places = [p['name'] for p in reg['places']]; self.home = reg.get('home', '')
        self.lock = threading.Lock(); self.log = []; self.batt = None; self.seq = 0
        self.pub = self.create_publisher(String, '/place/command', 10)
        self.create_subscription(String, '/place/status', self.on_status, 10)
        self.create_subscription(BatteryState, '/battery', lambda m: setattr(self, 'batt', (time.time(), m.voltage)), qos_profile_sensor_data)

    def on_status(self, m):
        try: d = json.loads(m.data)
        except ValueError: return
        with self.lock:
            self.seq += 1; d['t'] = time.time(); d['seq'] = self.seq; self.log.append(d); del self.log[:-40]

    def send(self, text, src):
        rid = 'w' + uuid.uuid4().hex[:7]; msg = String(); msg.data = '%s|%s' % (rid, text)
        self.pub.publish(msg); self.get_logger().info('[%s] %s ← %s · 구독자 %d' % (rid, text, src, self.pub.get_subscription_count()))
        return rid


PAGE = r'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>로버 명령</title>
<style>
:root{--bg:#f4f6f5;--card:#fff;--ink:#17201c;--ink2:#56625c;--line:#d9dfdc;--acc:#1f6f54;--accbg:#e3f1eb;--stop:#c62828;--warn:#b26a00}
@media (prefers-color-scheme:dark){:root{--bg:#121715;--card:#1b2220;--ink:#e6ece9;--ink2:#9aa7a1;--line:#2c3532;--acc:#5cc59a;--accbg:#173328;--stop:#ef5350;--warn:#f0a63a}}
*{box-sizing:border-box}html,body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.4 system-ui,-apple-system,"Malgun Gothic",sans-serif}
main{padding:12px 16px 120px;max-width:560px;margin:0 auto;display:grid;gap:14px}
header{display:flex;justify-content:space-between;align-items:baseline;gap:8px}
h1{font-size:20px;margin:0}.meta{color:var(--ink2);font-size:13px;font-variant-numeric:tabular-nums;text-align:right}
#net{display:none;background:var(--stop);color:#fff;padding:8px 12px;border-radius:8px;font-weight:600}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
button{font:inherit;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:12px;padding:16px 10px;min-height:58px;font-weight:600}
button:focus-visible{outline:3px solid var(--acc);outline-offset:2px}
button.armed{background:var(--accbg);border-color:var(--acc);color:var(--acc)}
button.home{grid-column:1/-1}
.row{display:flex;gap:8px}.row input{flex:1;font:inherit;padding:12px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--ink);min-width:0}
.row button{min-height:0;padding:12px 16px}
h2{font-size:13px;letter-spacing:.06em;color:var(--ink2);margin:4px 0 0;font-weight:600}
#log{display:grid;gap:6px}.ev{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 10px;font-size:14px}
.ev b{font-weight:700}.ev .d{color:var(--ink2);font-size:12.5px;word-break:break-all}.ev .tm{color:var(--ink2);font-size:12px;float:right;font-variant-numeric:tabular-nums}
.s-arrived b,.s-checked b{color:var(--acc)}.s-rejected b,.s-failed b,.s-canceled b{color:var(--stop)}.s-moving b,.s-accepted b{color:var(--warn)}
#stopbar{position:fixed;left:0;right:0;bottom:0;padding:10px 16px calc(10px + env(safe-area-inset-bottom,0px));background:linear-gradient(transparent,var(--bg) 30%)}
#stop{width:100%;max-width:560px;display:block;margin:0 auto;background:var(--stop);color:#fff;border:none;font-size:22px;min-height:70px;letter-spacing:.1em}
.hint{color:var(--ink2);font-size:12.5px;margin:0}
</style></head><body><main>
<header><h1>로버 명령</h1><div class="meta" id="meta">연결 중…</div></header>
<div id="net">서버 응답 없음 — 정지 버튼이 닿지 않을 수 있음</div>
<h2>장소로 이동 · 한 번 더 눌러 확인</h2>
<div class="grid" id="places"></div>
<h2>직접 입력</h2>
<div class="row"><input id="cmd" placeholder="go_to B · return · where" autocomplete="off" enterkeyhint="send"><button id="send">보내기</button></div>
<p class="hint">지금은 place_server 명령을 그대로 보냅니다. 문장 해석(규칙 · 온디바이스 모델)은 아직 연결 전입니다.</p>
<h2>상태</h2><div id="log"></div>
</main>
<div id="stopbar"><button id="stop">정지</button></div>
<script>
const K=new URLSearchParams(location.search).get('k')||'';let armed=null,armT=0,last=0;
const H={'X-Rover-Key':K,'Content-Type':'application/json'};
async function post(text){try{const r=await fetch('api/cmd',{method:'POST',headers:H,body:JSON.stringify({text})});if(!r.ok)throw 0;poll()}catch(e){net(false)}}
function net(ok){document.getElementById('net').style.display=ok?'none':'block'}
function disarm(){armed=null;document.querySelectorAll('#places button').forEach(b=>{b.classList.remove('armed');b.textContent=b.dataset.label})}
function placeBtn(name,label,cmd,cls){const b=document.createElement('button');b.dataset.label=label;b.textContent=label;if(cls)b.className=cls;
 b.onclick=()=>{if(armed===b&&Date.now()-armT<4000){disarm();post(cmd)}else{disarm();armed=b;armT=Date.now();b.classList.add('armed');b.textContent=label+' — 확인';setTimeout(()=>{if(armed===b)disarm()},4000)}};return b}
function fmt(t){const d=new Date(t*1000);return d.toTimeString().slice(0,8)}
async function poll(){try{const r=await fetch('api/state?after='+last,{headers:H});if(!r.ok)throw 0;const s=await r.json();net(true);
 document.getElementById('meta').textContent=(s.batt?s.batt.toFixed(2)+' V · ':'')+'서버 '+fmt(s.now)+' · 구독 '+s.subs;
 const L=document.getElementById('log');for(const e of s.log){last=Math.max(last,e.seq);const d=document.createElement('div');d.className='ev s-'+e.state;
  d.innerHTML='<span class="tm"></span><b></b> <span class="p"></span><div class="d"></div>';d.querySelector('.tm').textContent=fmt(e.t);d.querySelector('b').textContent=e.state;
  d.querySelector('.p').textContent=e.place||'';d.querySelector('.d').textContent=e.detail||'';L.prepend(d)}
 while(L.children.length>30)L.lastChild.remove()}catch(e){net(false)}}
fetch('api/places',{headers:H}).then(r=>r.json()).then(p=>{const g=document.getElementById('places');
 for(const n of p.places){if(n!==p.home)g.appendChild(placeBtn(n,n,'go_to '+n))}g.appendChild(placeBtn(p.home,'돌아와 ('+p.home+')','return','home'))}).catch(()=>net(false));
document.getElementById('stop').onclick=()=>{disarm();post('stop')};
const c=document.getElementById('cmd');document.getElementById('send').onclick=()=>{if(c.value.trim()){post(c.value.trim());c.value=''}};
c.addEventListener('keydown',e=>{if(e.key==='Enter')document.getElementById('send').click()});
poll();setInterval(poll,1000);
</script></body></html>'''


def make_handler(node, key):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a): pass   # 1 s 조회가 로그를 덮지 않게 — 명령만 노드 로그로 남김

        def out(self, code, body, ctype='application/json; charset=utf-8'):
            b = body.encode('utf-8') if isinstance(body, str) else body
            self.send_response(code); self.send_header('Content-Type', ctype); self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)

        def ok_key(self):
            q = parse_qs(urlparse(self.path).query)
            return secrets.compare_digest(self.headers.get('X-Rover-Key', '') or (q.get('k') or [''])[0], key)

        def do_GET(self):
            u = urlparse(self.path)
            if not self.ok_key(): return self.out(403, '{"error":"key"}')
            if u.path in ('/', '/index.html'): return self.out(200, PAGE, 'text/html; charset=utf-8')
            if u.path == '/api/places': return self.out(200, json.dumps({'places': node.places, 'home': node.home}, ensure_ascii=False))
            if u.path == '/api/state':
                after = int((parse_qs(u.query).get('after') or ['0'])[0] or 0)
                with node.lock: log = [d for d in node.log if d['seq'] > after]
                b = node.batt[1] if node.batt and time.time() - node.batt[0] < 5 else None
                return self.out(200, json.dumps({'now': time.time(), 'batt': b, 'subs': node.pub.get_subscription_count(), 'log': log}, ensure_ascii=False))
            self.out(404, '{}')

        def do_POST(self):
            if not self.ok_key(): return self.out(403, '{"error":"key"}')
            if urlparse(self.path).path != '/api/cmd': return self.out(404, '{}')
            try: text = str(json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0)) or 0) or b'{}').get('text', '')).strip()[:120]
            except (ValueError, AttributeError): return self.out(400, '{}')
            if not text or '|' in text: return self.out(400, '{"error":"text"}')
            self.out(200, json.dumps({'id': node.send(text, self.client_address[0])}))
    return H


def main():
    rclpy.init(); n = PlaceWeb(); key = load_key(); port = int(n.get_parameter('port').value)
    srv = ThreadingHTTPServer(('0.0.0.0', port), make_handler(n, key)); srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    n.get_logger().info('place_web: http://<Jetson IP>:%d/?k=<키 — %s>  · 장소 %d 곳' % (port, KEY_FILE, len(n.places)))
    try: rclpy.spin(n)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException): pass
    finally: srv.shutdown(); n.destroy_node(); rclpy.try_shutdown()


if __name__ == '__main__':
    main()
