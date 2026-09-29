import json,re,os,sys
KB=r'C:\Users\김영추\Desktop\2호선 PDF 자료\PDF_Knowledge_Base'
def pages(doc):
    out={}
    for sub,ext in (('01_pages','md'),('03_ocr','txt')):
        d=os.path.join(KB,sub,doc)
        if not os.path.isdir(d): continue
        for f in os.listdir(d):
            m=re.match(r'page_(\d+)\.'+ext,f)
            if m: out[int(m.group(1))]=out.get(int(m.group(1)),'')+open(os.path.join(d,f),encoding='utf-8',errors='ignore').read().lower()
    return out
def kws(b):
    k=[]
    s=b['id'].split('_',1)[1] if '_' in b['id'] else b['id']
    k.append(s.lower())
    w=re.split(r'[\s(/]',b.get('name',''))[0]
    if len(w)>=3: k.append(w.lower())
    return k
def match(b,P):
    ks=kws(b); return sorted(p for p,t in P.items() if any(k in t for k in ks))
if __name__=='__main__':
    d=json.load(open('board-info.json',encoding='utf-8'))
    for doc in sys.argv[1:]:
        P=pages(doc); print(doc,len(P))
        for g,l in d['boards'].items():
            for b in l:
                old=[r for r in b.get('relatedDrawings',[]) if r['doc']==doc]
                if old:
                    m=match(b,P); print(b['id'],'old',old[0]['pages'],'new',m[:12],len(m))
