# S11 3차: 기능·연결 기준으로 LZB_SVK2402 / LZB_FTGS_DISTRIBUTOR / FTGS_GF_RELAY_PCB 도면 연결 + 매뉴얼 쪽(사용자 지정).
#  SVK2402: ATP 캐비닛 Disposition의 SV-24V(S25790-B119-D1) 랙·SV 24V 전면 쪽 + ±60V DC 전원 인입(Power suply Module) 쪽
#  FTGS Distributor: 'ATP Cabinet +L0x to FTGS Cabinet' 연결 회로도 + Disposition의 FTGS-terminal 쪽
#  GF계전기 PCB: 계전기 보드 S25533-B36-A7 가 AR계전기를 구동하는 SICAS 'AR1.x-Relays Cabinet' 쪽
import json,os,re,sys
sys.path.insert(0,'claude')
from s11_lines import pg
from s8_score import KB
J='board-info.json';H='장비구성뷰_v3_시안.html'
b=json.load(open(J,encoding='utf-8'));B={x['id']:x for l in b['boards'].values() for x in l}
docs={'ATP':{},'SICAS':{}}
for x in B.values():
    for s,v in (x.get('relatedDrawings') or {}).items():
        for r in v: docs['ATP' if r['doc'].startswith('ATP') else 'SICAS'][s]=r['doc']
def npages(d): return max(int(m.group(1)) for f in os.listdir(os.path.join(KB,'01_pages',d)) if (m:=re.match(r'page_(\d+)\.md',f)))
def title(t):
    L=[l.strip() for l in t.split('\n') if l.strip()]
    i=[k for k,l in enumerate(L) if l.startswith('METRO SEOUL')]
    return ' '.join(L[max(0,i[0]-4):i[0]]) if i else ''
def short(t,pat): return any(re.search(pat,l.strip(),re.I) for l in t.split('\n') if 0<len(l.strip())<45)
def svk(t): return short(t,r'sv-?24v|sv 24v') or (short(t,r'[+-]60v dc') and short(t,r'power su'))
def dist(t): return 'to ftgs cabinet' in title(t).lower() or short(t,r'ftgs ?-?terminal')
def gf(t): return 's25533-b36-a7' in t.lower()
RULES=[('LZB_SVK2402','ATP',svk),('LZB_FTGS_DISTRIBUTOR','ATP',dist),('FTGS_GF_RELAY_PCB','SICAS',gf)]
tot={}
for bid,fam,fn in RULES:
    rd={}
    for s,d in docs[fam].items():
        ps=[p for p in range(1,npages(d)+1) if fn(pg(d,p))]
        if bid=='LZB_FTGS_DISTRIBUTOR':  # 연결도는 회로별 동일 구조 수십 쪽 → 시리즈(같은 제목 연속 구간)마다 첫 쪽만, Disposition 쪽은 전부
            keep=[];prev=None
            for q in ps:
                t=title(pg(d,q))
                if 'to ftgs cabinet' in t.lower():
                    if t!=prev or (keep and q!=keep[-1]+1 and False): keep.append(q)
                    prev=t
                else: keep.append(q); prev=None
            ps=keep
        rd[s]=[dict(doc=d,pages=ps,confirmed=True)] if ps else []
    B[bid]['relatedDrawings']=rd; tot[bid]=sum(len(v[0]['pages']) for v in rd.values() if v)
    print(bid,'stations',sum(1 for v in rd.values() if v),'pages',tot[bid],'EUL',rd.get('EUL') and rd['EUL'][0]['pages'][:12])
NOTE='사용자 지정(2026-10-03)'
B['LZB_SVK2402']['guidePages']=[dict(doc='LZB_유지보수_매뉴얼',pages=[103,104,105,106,107],note=NOTE)]
B['LZB_FTGS_DISTRIBUTOR']['guidePages']=[dict(doc='LZB_유지보수_매뉴얼',pages=[116,117],note=NOTE)]
B['FTGS_GF_RELAY_PCB']['guidePages']=[dict(doc='2호선_신호업무_지침서',pages=[11,18,26],note=NOTE),dict(doc='FTGS_유지보수_매뉴얼',pages=[16,27],note=NOTE)]
if '--apply' in sys.argv:
    b['changelog'].append('2026-10-03(S11): 기능·연결 기준 재검색 — LZB_SVK2402(ATP SV-24V 랙·±60V 인입 쪽), LZB_FTGS_DISTRIBUTOR(ATP→FTGS 캐비닛 연결도), FTGS_GF_RELAY_PCB(계전기 보드 S25533-B36-A7 쪽) 도면 연결 및 매뉴얼·지침서 쪽 연결. UPS_* 는 자료 없음으로 비움.')
    open(J,'w',encoding='utf-8',newline='\r\n').write(json.dumps(b,ensure_ascii=False,indent=2))
    h=open(H,encoding='utf-8').read()
    h2,k=re.subn(r'^var BOARDINFO_RAW = \{\n.*?^\};\n',lambda m:'var BOARDINFO_RAW = '+json.dumps(b,ensure_ascii=False,indent=2)+';\n',h,count=1,flags=re.S|re.M);assert k==1
    open(H,'w',encoding='utf-8',newline='\r\n').write(h2)
