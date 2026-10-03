import json,os,re,sys,collections
sys.path.insert(0,'claude')
from s8_score import KB,kws
d=json.load(open('claude/s11_남은목록.json',encoding='utf-8'))
b=json.load(open('board-info.json',encoding='utf-8'));B={x['id']:x for l in b['boards'].values() for x in l}
def pg(doc,p):
    t=''
    for sub,fn in(('01_pages','page_%04d.md'),('03_ocr','page_%d.txt')):
        f=os.path.join(KB,sub,doc,fn%p)
        if os.path.exists(f): t+=open(f,encoding='utf-8',errors='ignore').read()
    return t
def lab(t,ks):
    n=0;eq=0;ctx=[]
    for l in t.split('\n'):
        s=l.strip().lower()
        if any(s.startswith(k) or re.search(r'\b'+re.escape(k)+r'\b',s) for k in ks):
            if '=' in s or len(s)>40: eq+=1
            else: n+=1; ctx.append(s[:30])
    return n,eq,ctx[:2]
if __name__=='__main__':
    stn=sys.argv[1]
    for x in d:
        if x['stn']!=stn: continue
        ks=set(kws(B[x['board']]))
        r=[(p,)+lab(pg(x['doc'],p),ks) for p in x['pages']]
        print(x['board'],x['doc'][:4],' '.join('%d:%d/%d'%(p,n,e) for p,n,e,c in r))
