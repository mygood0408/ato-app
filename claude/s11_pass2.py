# S11 2차: s11_final 규칙 보강(구성개요 쪽 허용, ventilator=팬, UPS/IFC 개요 라벨) 후 원래 남은 439건 재판정·병합. GF계전기 PCB↔AR계전기 인터페이스 쪽 연결 제거. --apply 시 동기화.
import json,re,sys
src=open('claude/s11_final.py',encoding='utf-8').read().split('b=json.load')[0]
sys.path.insert(0,'claude'); exec(src)
J='board-info.json';H='장비구성뷰_v3_시안.html'
b=json.load(open(J,encoding='utf-8'));B={x['id']:x for l in b['boards'].values() for x in l}
items=json.load(open('claude/s11_pass2_input.json',encoding='utf-8'))
add=0;new=0;apply='--apply' in sys.argv
for it in items:
    keep=[p for p in it['pages'] if ok(it['board'],it['doc'],p)]
    if not keep: continue
    lst=B[it['board']].setdefault('relatedDrawings',{}).setdefault(it['stn'],[])
    e=next((r for r in lst if r['doc']==it['doc']),None)
    if e is None:
        new+=1
        if apply: lst.append(dict(doc=it['doc'],pages=sorted(keep),confirmed=True))
    else:
        ex=set(e['pages']); more=set(keep)-ex
        if more:
            add+=len(more)
            if apply: e['pages']=sorted(ex|more); e['confirmed']=True
gf=B['FTGS_GF_RELAY_PCB']['relatedDrawings']; g=sum(len(v) for v in gf.values())
if apply:
    for s in gf: gf[s]=[]
print('new links',new,'pages added to existing',add,'GF links removed',g)
if apply:
    b['changelog'].append('2026-10-03(S11): 2차 보강 — 구성개요 쪽·ventilator(팬)·UPS/IFC 개요 라벨 반영해 연결 %d건 추가·기존 연결에 %d쪽 추가, GF계전기 PCB↔AR계전기 연동 인터페이스 쪽 연결 제거(다른 장치).'%(new,add))
    open(J,'w',encoding='utf-8',newline='\r\n').write(json.dumps(b,ensure_ascii=False,indent=2))
    h=open(H,encoding='utf-8').read()
    h2,k=re.subn(r'^var BOARDINFO_RAW = \{\n.*?^\};\n',lambda m:'var BOARDINFO_RAW = '+json.dumps(b,ensure_ascii=False,indent=2)+';\n',h,count=1,flags=re.S|re.M);assert k==1
    open(H,'w',encoding='utf-8',newline='\r\n').write(h2)
