import json,os,re,sys,collections
sys.path.insert(0,'claude')
from s8_score import KB,kws
d=json.load(open('claude/s11_남은목록.json',encoding='utf-8'))
b=json.load(open('board-info.json',encoding='utf-8'));B={x['id']:x for l in b['boards'].values() for x in l}
stn=sys.argv[1]
def pg(doc,p):
    t=''
    for sub,fn in(('01_pages','page_%04d.md'),('03_ocr','page_%d.txt')):
        f=os.path.join(KB,sub,doc,fn%p)
        if os.path.exists(f): t+=open(f,encoding='utf-8',errors='ignore').read()
    return t
def title(t):
    L=[l.strip() for l in t.split('\n') if l.strip()]
    for i,l in enumerate(L):
        if l.startswith('METRO SEOUL'): return ' / '.join(L[max(0,i-5):i])[:90]
    return ''
for x in d:
    if x['stn']!=stn: continue
    ks=set(kws(B[x['board']]))
    print('##',x['board'],x['doc'][:5],len(x['pages']))
    for p in x['pages']:
        t=pg(x['doc'],p); tl=t.lower()
        print(' ',p,sum(tl.count(k) for k in ks),title(t))
