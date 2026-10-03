# S11: 계통 불일치 오매칭 삭제 — 같은 보드 이름의 반대 계통 보드가 같은 역·문서·쪽을 이미 confirmed로 가졌을 때만. --apply 시 동기화.
import json,re,sys,collections
J='board-info.json';H='장비구성뷰_v3_시안.html'
b=json.load(open(J,encoding='utf-8'));B={x['id']:x for l in b['boards'].values() for x in l}
def tw(i): return i.split('_',1)[1]
pair={'SICAS':'LZB','LZB':'SICAS'}
rem=collections.Counter();keep=collections.Counter();n=0
for x in B.values():
    pre=x['id'].split('_')[0]
    if pre not in pair: continue
    o=B.get(pair[pre]+'_'+tw(x['id']))
    for s,lst in (x.get('relatedDrawings') or {}).items():
        for r in list(lst):
            if r.get('confirmed'): continue
            sic=r['doc'].startswith('SICAS')
            if (pre=='SICAS')==sic: continue  # 계통 일치 항목은 건드리지 않음
            ok=o and any(q.get('confirmed') and q['doc']==r['doc'] and q['pages']==r['pages'] for q in (o.get('relatedDrawings') or {}).get(s,[]))
            if ok:
                n+=1; rem[x['id']]+=1
                if '--apply' in sys.argv: lst.remove(r)
            else: keep[x['id']]+=1
print('delete',n,dict(rem));print('keep',sum(keep.values()),dict(keep))
if '--apply' in sys.argv:
    b['changelog'].append('2026-10-03(S11): 반대 계통 오매칭 %d건 삭제(같은 보드의 맞는 계통 항목이 같은 역·문서·쪽으로 이미 확정됨).'%n)
    open(J,'w',encoding='utf-8',newline='\r\n').write(json.dumps(b,ensure_ascii=False,indent=2))
    h=open(H,encoding='utf-8').read()
    h2,k=re.subn(r'^var BOARDINFO_RAW = \{\n.*?^\};\n',lambda m:'var BOARDINFO_RAW = '+json.dumps(b,ensure_ascii=False,indent=2)+';\n',h,count=1,flags=re.S|re.M);assert k==1
    open(H,'w',encoding='utf-8',newline='\r\n').write(h2)
