"""board-info.json 의 relatedDrawings({SIN1:[..],SIN2:[..]})를 갱신하고 HTML 내장 BOARDINFO_RAW 도 같이 교체.
멱등: 몇 번 돌려도 같은 결과. 옛 배열 구조가 남아 있으면 doc 접미사(SIN1/SIN2)로 나눠 변환.
- SIN1 항목은 손대지 않는다.
- SIN2 의 note 가 '자동매칭'으로 시작하는 항목만 SIN1 자동매칭 항목의 키워드 규칙으로 다시 만든다. 수동 항목은 유지.
사용: python claude/sync_related_drawings.py"""
import json,re,os
KB=r'C:\Users\김영추\Desktop\2호선 PDF 자료\PDF_Knowledge_Base'
HTML='장비구성뷰_v3_시안.html'; JS='board-info.json'
NOTE='자동매칭(키워드 검색), 시각확인 필요 · SIN1 기준 키워드 그대로 적용, 내용 동일 여부 미확인'
def pages(doc):
    out={}
    for sub,ext in (('01_pages','md'),('03_ocr','txt')):
        d=os.path.join(KB,sub,doc)
        if not os.path.isdir(d): continue
        for f in os.listdir(d):
            m=re.match(r'page_(\d+)\.'+ext+'$',f)
            if m: out[int(m.group(1))]=out.get(int(m.group(1)),'')+open(os.path.join(d,f),encoding='utf-8',errors='ignore').read().lower()
    return out
def kws(b):
    k=[(b['id'].split('_',1)[1] if '_' in b['id'] else b['id']).lower()]
    w=re.split(r'[\s(/]',b.get('name',''))[0]
    if len(w)>=3: k.append(w.lower())
    return k
def match(b,P): ks=kws(b); return sorted(p for p,t in P.items() if any(k in t for k in ks))
def main():
    d=json.load(open(JS,encoding='utf-8')); P={}; st={'auto':0,'nohit':[]}
    for l in d['boards'].values():
        for b in l:
            rd=b.get('relatedDrawings')
            if rd is None: continue
            if isinstance(rd,list):
                rd={'SIN1':[r for r in rd if not r['doc'].endswith('SIN2')],'SIN2':[r for r in rd if r['doc'].endswith('SIN2')]}
            s2=[r for r in rd['SIN2'] if not r['note'].startswith('자동매칭')]
            for r in rd['SIN1']:
                if not r['note'].startswith('자동매칭'): continue
                doc2=r['doc'].replace('SIN1','SIN2')
                if any(x['doc']==doc2 for x in s2): continue
                if doc2 not in P: P[doc2]=pages(doc2)
                m=match(b,P[doc2])
                if not m: st['nohit'].append((b['id'],doc2)); continue
                s2.append({'doc':doc2,'pages':m[:15],'totalPagesFound':len(m),'note':NOTE}); st['auto']+=1
            b['relatedDrawings']={'SIN1':rd['SIN1'],'SIN2':s2}
    s=json.dumps(d,ensure_ascii=False,indent=2)
    open(JS,'w',encoding='utf-8',newline='').write(s+'\n')
    t=open(HTML,encoding='utf-8').read()
    i=t.index('var BOARDINFO_RAW = ')+len('var BOARDINFO_RAW = ')
    _,e=json.JSONDecoder().raw_decode(t[i:])
    open(HTML,'w',encoding='utf-8',newline='').write(t[:i]+s+t[i+e:])
    print(st)
if __name__=='__main__': main()
