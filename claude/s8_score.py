# S8: SIN1/SIN2 확인필요 도면 항목 점수화. 출력은 요약만, 상세는 claude/s8_score.json
import json,re,os,sys
sys.path.insert(0,'claude')
KB=r'C:\Users\김영추\Desktop\2호선 PDF 자료\PDF_Knowledge_Base'
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
if __name__=='__main__':
    b=json.load(open('board-info.json',encoding='utf-8')); P={}; res=[]
    for l in b['boards'].values():
        for x in l:
            for s in ('SIN1','SIN2'):
                for r in (x.get('relatedDrawings') or {}).get(s,[]):
                    if r.get('confirmed'): continue
                    if r['doc'] not in P: P[r['doc']]=pages(r['doc'])
                    ks=kws(x); h=[sum(P[r['doc']].get(p,'').count(k) for k in ks) for p in r['pages']]
                    res.append(dict(board=x['id'],stn=s,doc=r['doc'],pages=r['pages'],kw=ks,hits=h,note=r.get('note','')))
    json.dump(res,open('claude/s8_score.json','w',encoding='utf-8'),ensure_ascii=False)
    print(len(res))
    for r in res: print(r['board'],r['stn'],r['doc'][:5],r['kw'],'min',min(r['hits']),'zero',r['hits'].count(0),'/',len(r['hits']),'med',sorted(r['hits'])[len(r['hits'])//2])
