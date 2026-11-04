# anal_src_strip_md5 — 주석(# · """ · <!-- -->)을 뺀 파일 내용의 md5 앞 8 자. 인자: 뿌리 폴더 + 상대 경로들. PC · Jetson 양쪽에서 같은 코드로 저장소 판과 Jetson src 를 비교(11-04). 로버 안 움직임.
import sys,re,hashlib
for f in sys.argv[2:]:
    s=open(sys.argv[1]+'/'+f,encoding='utf-8',errors='replace').read().replace('\r','')
    s=re.sub(r'<!--.*?-->','',s,flags=re.S)
    if not f.endswith('.xml'):
        s=re.sub(r'(?m)\s*#.*$','',s); s=re.sub(r'(?s)""".*?"""','',s)
    s='\n'.join(l.rstrip() for l in s.split('\n') if l.strip())
    print(hashlib.md5(s.encode()).hexdigest()[:8], f)
