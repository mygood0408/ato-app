# S11: 남은 확인필요 항목을 쪽 단위로 판정. 쪽 제목 종류(목차·구성개요·케이블경로 제외) + 보드 고유 라벨(짧은 줄 정규식). --apply 시 JSON/HTML 동기화.
# 판정 결과: 라벨 쪽만 남겨 confirmed:true(note 삭제), 라벨 쪽 없으면 항목 삭제. 계통 불일치(LZB_/ATOLOOP_↔SICAS 문서)는 삭제.
import json,re,sys,collections
sys.path.insert(0,'claude')
from s11_lines import pg
J='board-info.json';H='장비구성뷰_v3_시안.html'
K={'SICAS_VENUS3':r'venus3','SICAS_KOMDA2':r'komda ?2','SICAS_OLM':r'\bolm\b','ECDSTT_OLM':r'\bolm\b','ECDSTT_STEKOP':r'stekop','ECDSTT_DEWEMO':r'dewemo','ECDSTT_DESIMO':r'desimo','ECDSTT_PLATTER':r'platter','ECDSTT_PS':r'sv ?2602',
'LZB_FTGS_DISTRIBUTOR':r'distribut','LZB_SVK2402':r'svk ?2402','LZB_FAN':r'\bfan\b|ventilator','ATOLOOP_FAN':r'\bfan\b|ventilator','IFC_COMPUTER':r'\bifc\b|interface computer','IFC_EMS_RELAY':r'\bems\b|emergency stop','FTGS_GF_RELAY_PCB':r'\bgf\b|gf.?relay',
'ATOLOOP_FUUELL':r'fuuell','ATOLOOP_REMEMO':r'rememo','ATOLOOP_CB':r'ato positioning loop','TWC_AMP_MODULE':r'line amplifier','TWC_LOOP_COIL':r'to loop twc|loop twc','PSD_TERMINAL_MAP_SIN051':r'\bpsd\b',
'UPS_ATS_AVR_UNIT':r'\bats\b|\bavr\b','UPS_RECTIFIER_UNIT':r'rectifier|inverter|^ups$|/ups$','UPS_OUTPUT_DISTRIBUTION':r'\btbl\d|\btbm|output distribution'}
SKIP=re.compile(r'list of documents|cable routing|cable  routing',re.I)
def title(t):
    L=[l.strip() for l in t.split('\n') if l.strip()]
    for i,l in enumerate(L):
        if l.startswith('METRO SEOUL'): return ' '.join(L[max(0,i-5):i])
    return ''
def ok(bid,doc,p):
    t=pg(doc,p)
    if SKIP.search(title(t)): return False
    if bid.startswith(('LZB_','ATOLOOP_')) and doc.startswith('SICAS'): return False
    if bid.startswith(('SICAS_','ECDSTT_')) and not doc.startswith('SICAS'): return False
    # ECDSTT는 EC/DSTT 캐비닛·신호/전철기 도면, SICAS_OLM은 SICAS 캐비닛 쪽만
    tt=title(t)
    if bid=='SICAS_OLM' and 'EC/DSTT' in tt: return False
    if bid=='ECDSTT_OLM' and 'SICAS' in tt: return False
    return any(re.search(K[bid],l.strip().lower()) for l in t.split('\n') if 0<len(l.strip())<45)
b=json.load(open(J,encoding='utf-8'))
st=collections.defaultdict(lambda:[0,0,0,0]) # keep items, trimmed pages, deleted items, total pages dropped
nk=nd=0
for l in b['boards'].values():
    for x in l:
        if x['id'] not in K: continue
        for s,lst in (x.get('relatedDrawings') or {}).items():
            for r in list(lst):
                if r.get('confirmed'): continue
                keep=[p for p in r['pages'] if ok(x['id'],r['doc'],p)]
                a=st[x['id']]; a[3]+=len(r['pages'])-len(keep)
                if keep:
                    a[0]+=1; nk+=1
                    if apply:=('--apply' in sys.argv): r['pages']=keep; r['confirmed']=True; r.pop('note',None)
                else:
                    a[2]+=1; nd+=1
                    if '--apply' in sys.argv: lst.remove(r)
print('keep',nk,'delete',nd)
for k,v in sorted(st.items()): print(k,'keep',v[0],'del',v[2],'pages dropped',v[3])
if '--apply' in sys.argv:
    b['changelog'].append('2026-10-03(S11): 남은 확인필요 도면 항목 쪽 단위 판정 — 보드 라벨이 보이는 쪽만 남겨 %d건 확정, 라벨 쪽 없거나 계통 불일치 %d건 삭제.'%(nk,nd))
    open(J,'w',encoding='utf-8',newline='\r\n').write(json.dumps(b,ensure_ascii=False,indent=2))
    h=open(H,encoding='utf-8').read()
    h2,k=re.subn(r'^var BOARDINFO_RAW = \{\n.*?^\};\n',lambda m:'var BOARDINFO_RAW = '+json.dumps(b,ensure_ascii=False,indent=2)+';\n',h,count=1,flags=re.S|re.M);assert k==1
    open(H,'w',encoding='utf-8',newline='\r\n').write(h2)
