"""보드별 SIN1 vs SIN2 도면(자동매칭 쪽수) 텍스트 유사도. 읽기 전용, 결과는 표준출력.
각 SIN1 쪽마다 SIN2 매칭 쪽 중 토큰 자카드 최댓값을 구해 평균(sim)과 쪽수비를 낸다. 낮을수록 '고유 내용 후보'."""
import json,re,os
KB=r'C:\Users\김영추\Desktop\2호선 PDF 자료\PDF_Knowledge_Base\01_pages'
_c={}
def toks(doc,p):
    k=(doc,p)
    if k not in _c:
        t=open(os.path.join(KB,doc,'page_%04d.md'%p),encoding='utf-8',errors='ignore').read()
        t=t.split('## 추출 텍스트',1)[-1].lower()
        _c[k]=set(re.findall(r'[a-z0-9가-힣][a-z0-9가-힣./+-]*',t))
    return _c[k]
def jac(a,b): return len(a&b)/len(a|b) if a|b else 1.0
def main():
    d=json.load(open('board-info.json',encoding='utf-8')); rows=[]
    for g,l in d['boards'].items():
        for b in l:
            rd=b.get('relatedDrawings')
            if not isinstance(rd,dict): continue
            for r1 in rd['SIN1']:
                doc2=r1['doc'].replace('SIN1','SIN2')
                r2=next((x for x in rd['SIN2'] if x['doc']==doc2),None)
                if not r2: rows.append((b['id'],r1['doc'][:4],None,len(r1['pages']),0,r1.get('totalPagesFound',len(r1['pages'])),0)); continue
                s=[max(jac(toks(r1['doc'],p),toks(doc2,q)) for q in r2['pages']) for p in r1['pages']]
                rows.append((b['id'],r1['doc'][:4],sum(s)/len(s),len(r1['pages']),len(r2['pages']),r1.get('totalPagesFound',len(r1['pages'])),r2.get('totalPagesFound',len(r2['pages']))))
    rows.sort(key=lambda x:(x[2] is not None,x[2] or 0))
    print('board,doc,sim,p1,p2,tot1,tot2')
    for r in rows: print(r[0],r[1],'-' if r[2] is None else '%.2f'%r[2],*r[3:],sep=',')
if __name__=='__main__': main()
