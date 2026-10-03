# S11: s8 규칙을 전 역(SIN 외 13개 + SIN 잔여)으로 확장. 기본 dry-run, --apply 시 JSON·HTML 동기화. 재실행 가능.
import json,re,sys,collections,os
sys.path.insert(0,'claude')
from s8_score import pages,kws,KB
J='board-info.json';H='장비구성뷰_v3_시안.html'
AMB={'fan','ps','cb','ems','ifc','computer','ats','ups','twc','psd','ftgs','ato','olm','svk','n레벨','n_level_panel','ems_relay','ftgs_distributor','terminal_map_sin051','amp_module','loop_coil','ats_avr_unit','rectifier_unit','output_distribution'}
apply='--apply' in sys.argv
b=json.load(open(J,encoding='utf-8')); P={}; left=[]; n=0
def verdict(x,r):
    if x['id'].startswith('FTGS_') or x['id']=='SICAS_N_LEVEL_PANEL': return 'img','FTGS/N레벨 도면 제목·이미지 확인 필요'
    ks=kws(x)
    if ks[0] in AMB or ks[0].split('_')[0]=='cb' or x['id']=='ATOLOOP_CB': return 'img','핵심어 범용/모호'
    pre=x['id'].split('_')[0]; sic=r['doc'].startswith('SICAS')
    if not((pre in('SICAS','ECDSTT') and sic) or (pre in('LZB','ATOLOOP') and not sic)): return 'img','보드 계통↔도면 종류 불일치'
    if r['doc'] not in P: P[r['doc']]=pages(r['doc'])
    if not P[r['doc']]: return 'img','도면 쪽 텍스트 없음(KB 폴더 없음)'
    miss=[p for p in r['pages'] if p not in P[r['doc']]]
    if miss: return 'img','쪽 텍스트 없음 %s'%miss
    h=[sum(P[r['doc']][p].count(k) for k in set(ks)) for p in r['pages']]
    return ('ok','') if min(h)>=2 else ('img','일부 쪽 핵심어 1회 이하')
for l in b['boards'].values():
    for x in l:
        for s,lst in (x.get('relatedDrawings') or {}).items():
            for r in lst:
                if r.get('confirmed'): continue
                v,why=verdict(x,r)
                if v=='ok':
                    n+=1
                    if apply: r['confirmed']=True; r.pop('note',None)
                else: left.append(dict(board=x['id'],stn=s,doc=r['doc'],pages=r['pages'],reason=why,note=r.get('note','')))
print('confirm',n,'left',len(left))
print(collections.Counter(x['reason'][:14] for x in left))
print(collections.Counter(x['stn'] for x in left))
print('docs without KB:',sorted({x['doc'] for x in left if not os.path.isdir(os.path.join(KB,'01_pages',x['doc'])) and not os.path.isdir(os.path.join(KB,'03_ocr',x['doc']))}))
if apply:
    MSG='2026-10-03(S11): 전 역 확인필요 도면 항목 %d건 확정(S8 규칙: 핵심어 전 쪽 2회 이상·계통 일치). 남은 항목은 claude/s11_남은목록.json.'%n
    if not any(m.startswith('2026-10-03(S11)') for m in b['changelog']): b['changelog'].append(MSG)
    open(J,'w',encoding='utf-8',newline='\r\n').write(json.dumps(b,ensure_ascii=False,indent=2))
    h=open(H,encoding='utf-8').read()
    h2,k=re.subn(r'^var BOARDINFO_RAW = \{\n.*?^\};\n',lambda m:'var BOARDINFO_RAW = '+json.dumps(b,ensure_ascii=False,indent=2)+';\n',h,count=1,flags=re.S|re.M); assert k==1
    open(H,'w',encoding='utf-8',newline='\r\n').write(h2)
    json.dump(left,open('claude/s11_남은목록.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
