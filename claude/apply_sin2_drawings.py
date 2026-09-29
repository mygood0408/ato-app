import json,re,sys
sys.path.insert(0,'claude')
from match_sin2_drawings import pages,match
p='board-info.json'
d=json.load(open(p,encoding='utf-8'))
P={doc:pages(doc) for doc in ('ATP_HW_Design_SIN2','SICAS_HW_Design_SIN2')}
stat={'SIN1':0,'SIN2':0,'auto':0,'manual':0,'nohit':[]}
for g,l in d['boards'].items():
    for b in l:
        rd=b.get('relatedDrawings')
        if not isinstance(rd,list): continue
        new={'SIN1':[],'SIN2':[]}
        for r in rd: new['SIN2' if r['doc'].endswith('SIN2') else 'SIN1'].append(r)
        for r in list(new['SIN1']):
            doc2=r['doc'].replace('SIN1','SIN2')
            if doc2 not in P or not r['note'].startswith('자동매칭'): continue
            if any(x['doc']==doc2 for x in new['SIN2']): stat['manual']+=1; continue
            m=match(b,P[doc2])
            if not m: stat['nohit'].append((b['id'],doc2)); continue
            new['SIN2'].append({'doc':doc2,'pages':m[:15],'totalPagesFound':len(m),'note':'자동매칭(키워드 검색), 시각확인 필요 · SIN1 기준 키워드 그대로 적용, 내용 동일 여부 미확인'}); stat['auto']+=1
        b['relatedDrawings']=new
        stat['SIN1']+=len(new['SIN1']); stat['SIN2']+=len(new['SIN2'])
s=json.dumps(d,ensure_ascii=False,indent=2)
open(p,'w',encoding='utf-8',newline='').write(s+'\n' if open(p,encoding='utf-8').read().endswith('\n') else s)
h='장비구성뷰_v3_시안.html'
t=open(h,encoding='utf-8').read()
m=re.search(r'(var BOARDINFO_RAW = )\{.*?\n\};',t,re.S)
t=t[:m.start()]+m.group(1)+s+';'+t[m.end():]
open(h,'w',encoding='utf-8',newline='').write(t)
print(stat)
